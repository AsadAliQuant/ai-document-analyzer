import unittest
from unittest.mock import patch

from gemini_gateway import GeminiCancelledError
from main_window import MainWindow, _AnalysisWorker, _QAWorker, _RefreshWorker


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

    def test_refresh_worker_only_returns_gemini_models(self):
        class Window:
            online_models_gemini = ["gemini-2.5-flash"]

            def _get_gemini_key(self):
                return "captured-key"

        worker = _RefreshWorker(Window())
        worker.finished = _Signal()
        worker.error = _Signal()

        worker.run()

        self.assertEqual(worker.finished.calls, [(["gemini-2.5-flash"], "")])
        self.assertEqual(worker.error.calls, [])

    def test_offline_selector_is_rejected_before_document_manager_use(self):
        class Value:
            def __init__(self, value):
                self.value = value

            def currentText(self):
                return self.value

        class Tabs:
            def currentIndex(self):
                return 1

        class Ui:
            tabs = Tabs()
            modelSourceCombo = Value("Offline (Ollama LLaMA)")
            availableModelCombo = Value("llama3.2")

        window = MainWindow.__new__(MainWindow)
        window.ui = Ui()
        window._get_input_text = lambda: "pasted text"
        window._get_selected_file_path = lambda: ""
        window._get_gemini_key = lambda: ""
        window._get_large_doc_manager = lambda: self.fail("document manager must not be created")

        with patch("main_window.QMessageBox.warning") as warning:
            window.analyze_document()

        warning.assert_called_once()
        self.assertIn("Offline mode unavailable", warning.call_args.args[1])

    def test_qa_rejects_legacy_offline_selector(self):
        class Value:
            def __init__(self, value):
                self.value = value
            def currentText(self):
                return self.value
            def text(self):
                return "Question?"

        class Ui:
            questionLineEdit = Value("")
            modelSourceCombo = Value("Offline (Ollama LLaMA)")
            availableModelCombo = Value("llama3.2")

        window = MainWindow.__new__(MainWindow)
        window.ui = Ui()
        window._last_summary_text = "summary"
        with patch("main_window.QMessageBox.warning") as warning:
            window._send_question()
        warning.assert_called_once()
        self.assertIn("Offline mode unavailable", warning.call_args.args[1])


if __name__ == "__main__":
    unittest.main()
