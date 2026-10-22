import unittest
from unittest.mock import MagicMock, patch

from gemini_fallback import GEMINI_MODEL_FALLBACK_LABEL
from gemini_gateway import GeminiCancelledError
from main_window import MainWindow, _AnalysisWorker, _QAWorker


class _Signal:
    def __init__(self):
        self.calls = []

    def emit(self, *args):
        self.calls.append(args)


class OllamaRemovalTests(unittest.TestCase):
    def test_analysis_worker_always_uses_gemini_even_with_stale_provider_data(self):
        class Window:
            def __init__(self):
                self.summaries = []

            def summarize_text_gemini(self, model, text, key):
                self.summaries.append((model, text, key))
                return "summary"

        window = Window()
        worker = _AnalysisWorker(window, {
            "provider": "ollama",  # Stale caller data cannot select a local backend.
            "model": "gemini-2.5-flash",
            "input_text": "document text",
            "gemini_key": "captured-key",
        }, 4)
        worker.finished = _Signal()
        worker.error = _Signal()

        worker.run()

        self.assertEqual(window.summaries, [("gemini-2.5-flash", "document text", "captured-key")])
        self.assertEqual(worker.finished.calls[0][0], "summary")
        self.assertEqual(worker.error.calls, [])

    def test_analysis_worker_treats_ocr_cancellation_as_cancellation(self):
        class Window:
            def extract_text_from_file(self, file_path, key):
                raise GeminiCancelledError("cancelled")

            def summarize_text_gemini(self, model, text, key):
                self.fail("summary must not run after cancellation")

        worker = _AnalysisWorker(Window(), {
            "model": "gemini-2.5-flash",
            "file_path": "image.png",
            "input_text": "",
            "gemini_key": "captured-key",
        }, 4)
        worker.finished = _Signal()
        worker.error = _Signal()

        with patch("main_window.os.path.exists", return_value=True):
            worker.run()

        self.assertEqual(worker.finished.calls, [])
        self.assertEqual(worker.error.calls, [])

    def test_qa_worker_uses_gemini_after_intent_classification(self):
        class Window:
            def __init__(self):
                self.classifications = []
                self.answers = []

            def _classify_question_intent(self, question, model, key):
                self.classifications.append((question, model, key))
                return {"operation": "semantic_qa"}

            def answer_question_gemini(self, model, messages, summary, text, key, doc_key):
                self.answers.append((model, messages, summary, text, key, doc_key))
                return "answer"

        window = Window()
        messages = [{"role": "user", "content": "What is the conclusion?"}]
        worker = _QAWorker(window, {
            "model": "gemini-2.5-flash",
            "messages": messages,
            "summary": "summary",
            "input_text": "document",
            "gemini_key": "captured-key",
            "doc_key": "",
        }, 5)
        worker.finished = _Signal()
        worker.error = _Signal()

        worker.run()

        self.assertEqual(window.classifications, [("What is the conclusion?", "gemini-2.5-flash", "captured-key")])
        self.assertEqual(window.answers, [("gemini-2.5-flash", messages, "summary", "document", "captured-key", "")])
        self.assertEqual(worker.finished.calls, [("answer", 5)])
        self.assertEqual(worker.error.calls, [])

    def test_analysis_without_model_controls_requires_gemini_key(self):
        class Tabs:
            def currentIndex(self):
                return 1

        class Ui:
            tabs = Tabs()

        window = MainWindow.__new__(MainWindow)
        window.ui = Ui()
        window._get_input_text = lambda: "pasted text"
        window._get_selected_file_path = lambda: ""
        window._get_gemini_key = lambda: ""
        window._get_large_doc_manager = lambda: self.fail("document manager must not be created")

        with patch("main_window.QMessageBox.warning") as warning:
            window.analyze_document()

        warning.assert_called_once()
        self.assertIn("Missing GOOGLE_API_KEY", warning.call_args.args[2])

    def test_qa_without_model_controls_requires_gemini_key(self):
        class Value:
            def text(self):
                return "Question?"

        class Ui:
            questionLineEdit = Value()

        window = MainWindow.__new__(MainWindow)
        window.ui = Ui()
        window._last_summary_text = "summary"
        window._get_gemini_key = lambda: ""
        with patch("main_window.QMessageBox.warning") as warning:
            window._send_question()
        warning.assert_called_once()
        self.assertIn("Missing GOOGLE_API_KEY", warning.call_args.args[2])

    def test_qa_without_model_controls_uses_automatic_gemini_fallback(self):
        class QuestionEdit:
            def text(self):
                return "Question?"

            def clear(self):
                pass

        window = MainWindow.__new__(MainWindow)
        window.ui = type("Ui", (), {"questionLineEdit": QuestionEdit()})()
        window._last_summary_text = "summary"
        window._qa_vector_doc_key = ""
        window._qa_document_text = "document"
        window._last_input_text_for_qa = ""
        window._qa_messages = [{"role": "user", "content": "Question?"}]
        window._session_id = 3
        window._get_gemini_key = lambda: "captured-key"
        window._append_chat = lambda *_args: None
        window._append_history = lambda *_args: None
        window._set_qa_controls_enabled = lambda *_args: None
        window._start_qa_typing_indicator = lambda: None

        with patch("main_window.QThread") as thread_class, patch("main_window._QAWorker") as worker_class:
            thread_class.return_value = MagicMock()
            worker_class.return_value = MagicMock()
            window._send_question()

        params = worker_class.call_args.args[1]
        self.assertEqual(params["model"], GEMINI_MODEL_FALLBACK_LABEL)
        self.assertEqual(params["gemini_key"], "captured-key")
        thread_class.return_value.start.assert_called_once()


if __name__ == "__main__":
    unittest.main()
