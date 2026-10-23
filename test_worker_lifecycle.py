import unittest
from unittest.mock import MagicMock, patch

from main_window import MainWindow


class _FakeSignal:
    def __init__(self):
        self.targets = []
        self.disconnect_calls = 0

    def connect(self, target):
        self.targets.append(target)

    def disconnect(self):
        self.disconnect_calls += 1


class _FakeThread:
    def __init__(self):
        self.started = _FakeSignal()
        self.finished = _FakeSignal()
        self.start_calls = 0
        self.interruption_calls = 0
        self.quit_calls = 0
        self.wait_calls = []
        self.delete_calls = 0

    def start(self):
        self.start_calls += 1

    def isRunning(self):
        return True

    def requestInterruption(self):
        self.interruption_calls += 1

    def quit(self):
        self.quit_calls += 1

    def wait(self, timeout):
        self.wait_calls.append(timeout)
        return True

    def deleteLater(self):
        self.delete_calls += 1


class _FakeWorker:
    def __init__(self):
        self.finished = _FakeSignal()
        self.error = _FakeSignal()
        self.moved_to = None
        self.delete_calls = 0

    def moveToThread(self, thread):
        self.moved_to = thread

    def run(self):
        pass

    def deleteLater(self):
        self.delete_calls += 1


def _target_names(signal):
    return [getattr(target, "__name__", "") for target in signal.targets]


class WorkerLifecycleTests(unittest.TestCase):
    def test_analysis_worker_wires_quit_deletion_and_reference_cleanup(self):
        window = MainWindow.__new__(MainWindow)
        window._session_id = 3
        window._set_loading = MagicMock()
        thread = _FakeThread()
        worker = _FakeWorker()

        with patch("main_window.QThread", return_value=thread), patch(
            "main_window._AnalysisWorker",
            return_value=worker,
        ):
            window._start_background_analysis({"gemini_key": "key"})

        self.assertIs(worker.moved_to, thread)
        self.assertEqual(thread.start_calls, 1)
        self.assertIn("run", _target_names(thread.started))
        self.assertIn("quit", _target_names(worker.finished))
        self.assertIn("quit", _target_names(worker.error))
        self.assertIn("deleteLater", _target_names(worker.finished))
        self.assertIn("deleteLater", _target_names(worker.error))
        self.assertIn("deleteLater", _target_names(thread.finished))
        self.assertIn("_clear_analysis_worker_refs", _target_names(thread.finished))

    def test_processing_worker_wires_success_and_error_cleanup(self):
        window = MainWindow.__new__(MainWindow)
        thread = _FakeThread()
        worker = _FakeWorker()
        window._processing_thread = thread
        window._processing_worker = worker

        window._start_processing_worker()

        self.assertIs(worker.moved_to, thread)
        self.assertEqual(thread.start_calls, 1)
        self.assertIn("quit", _target_names(worker.finished))
        self.assertIn("quit", _target_names(worker.error))
        self.assertIn("deleteLater", _target_names(worker.finished))
        self.assertIn("deleteLater", _target_names(worker.error))
        self.assertIn("deleteLater", _target_names(thread.finished))
        self.assertIn("_clear_processing_worker_refs", _target_names(thread.finished))

    def test_qa_worker_wires_quit_deletion_and_reference_cleanup(self):
        class QuestionEdit:
            def text(self):
                return "Question?"

            def clear(self):
                pass

        window = MainWindow.__new__(MainWindow)
        window.ui = type("Ui", (), {"questionLineEdit": QuestionEdit()})()
        window._last_summary_text = "summary"
        window._qa_vector_doc_key = "doc-key"
        window._qa_document_text = "document"
        window._last_input_text_for_qa = ""
        window._qa_messages = []
        window._session_id = 4
        window._get_gemini_key = lambda: "captured-key"
        window._append_chat = lambda *_args: None
        window._append_history = lambda role, content: window._qa_messages.append(
            {"role": role, "content": content}
        )
        window._set_qa_controls_enabled = lambda *_args: None
        window._start_qa_typing_indicator = lambda: None
        thread = _FakeThread()
        worker = _FakeWorker()

        with patch("main_window.QThread", return_value=thread), patch(
            "main_window._QAWorker",
            return_value=worker,
        ):
            window._send_question()

        self.assertIs(worker.moved_to, thread)
        self.assertEqual(thread.start_calls, 1)
        self.assertIn("quit", _target_names(worker.finished))
        self.assertIn("quit", _target_names(worker.error))
        self.assertIn("deleteLater", _target_names(worker.finished))
        self.assertIn("deleteLater", _target_names(worker.error))
        self.assertIn("deleteLater", _target_names(thread.finished))
        self.assertIn("_clear_qa_worker_refs", _target_names(thread.finished))

    def test_cancel_all_background_work_interrupts_waits_and_clears_every_worker(self):
        window = MainWindow.__new__(MainWindow)
        pairs = [(_FakeThread(), _FakeWorker()) for _index in range(3)]
        (window._analysis_thread, window._analysis_worker) = pairs[0]
        (window._processing_thread, window._processing_worker) = pairs[1]
        (window._qa_thread, window._qa_worker) = pairs[2]
        window._pending_analysis_params = {"pending": True}

        window._cancel_all_background_work()

        self.assertIsNone(window._pending_analysis_params)
        self.assertIsNone(window._analysis_thread)
        self.assertIsNone(window._analysis_worker)
        self.assertIsNone(window._processing_thread)
        self.assertIsNone(window._processing_worker)
        self.assertIsNone(window._qa_thread)
        self.assertIsNone(window._qa_worker)
        for thread, worker in pairs:
            self.assertEqual(thread.interruption_calls, 1)
            self.assertEqual(thread.quit_calls, 1)
            self.assertEqual(thread.wait_calls, [2000])
            self.assertEqual(worker.finished.disconnect_calls, 1)
            self.assertEqual(worker.error.disconnect_calls, 1)

    def test_stale_analysis_and_qa_signals_do_not_update_ui(self):
        window = MainWindow.__new__(MainWindow)
        window._session_id = 20
        window._set_loading = MagicMock()
        window._append_chat = MagicMock()
        window._set_qa_controls_enabled = MagicMock()
        window._stop_qa_typing_indicator = MagicMock()

        window._on_analysis_error("status", "error", 19)
        window._on_qa_finished("answer", 19)

        window._set_loading.assert_not_called()
        window._append_chat.assert_not_called()
        window._set_qa_controls_enabled.assert_not_called()
        window._stop_qa_typing_indicator.assert_not_called()


if __name__ == "__main__":
    unittest.main()
