import builtins
import sys
import threading
import types
import unittest
from unittest.mock import patch

from main_window import MainWindow, PastedTextProcessWorker
from startup_helper import LoadingOverlayMixin


class _Signal:
    def __init__(self):
        self.calls = []

    def emit(self, *args):
        self.calls.append(args)


class _RecordingManager:
    def __init__(self):
        self._lock = threading.Lock()
        self.prepare_calls = []

    def prepare_document(self, doc_key, source, text, api_key=None):
        with self._lock:
            self.prepare_calls.append((doc_key, source, text, api_key))
        return 1


class LazyDocumentManagerTests(unittest.TestCase):
    def _window(self):
        window = MainWindow.__new__(MainWindow)
        window.large_doc_manager = None
        window._large_doc_manager_lock = threading.Lock()
        window.app_config_dir = "unused"
        return window

    def _worker(self, window, doc_key, session_id):
        worker = PastedTextProcessWorker(
            window,
            doc_key,
            "synthetic text",
            "api-key",
            session_id,
        )
        worker.finished = _Signal()
        worker.error = _Signal()
        return worker

    def test_startup_completion_does_not_import_or_construct_document_manager(self):
        fake_module = types.ModuleType("large_doc_manager")
        constructor_calls = []

        class _ForbiddenManager:
            def __init__(self, _base_dir):
                constructor_calls.append(True)

        fake_module.LargeDocumentManager = _ForbiddenManager
        window = types.SimpleNamespace(
            app_config_dir="unused",
            large_doc_manager=None,
            _init_in_progress=True,
            _hide_loading_overlay=lambda: None,
            setEnabled=lambda _enabled: None,
            _set_status=lambda _status: None,
        )
        imported = []
        real_import = builtins.__import__

        def guarded_import(name, *args, **kwargs):
            if name == "large_doc_manager":
                imported.append(name)
            return real_import(name, *args, **kwargs)

        with patch.dict(sys.modules, {"large_doc_manager": fake_module}), patch(
            "builtins.__import__",
            side_effect=guarded_import,
        ):
            LoadingOverlayMixin._on_init_finished(window)

        self.assertEqual(imported, [])
        self.assertEqual(constructor_calls, [])
        self.assertIsNone(window.large_doc_manager)
        self.assertFalse(window._init_in_progress)

    def test_concurrent_workers_construct_document_manager_once(self):
        window = self._window()
        manager = _RecordingManager()
        first_entered = threading.Event()
        second_entered = threading.Event()
        release = threading.Event()
        constructor_calls = []
        constructor_guard = threading.Lock()

        def construct(_base_dir):
            with constructor_guard:
                constructor_calls.append(True)
                if len(constructor_calls) == 1:
                    first_entered.set()
                else:
                    second_entered.set()
            release.wait(2.0)
            return manager

        workers = [self._worker(window, f"doc-{index}", index) for index in (1, 2)]
        barrier = threading.Barrier(3)

        def run(worker):
            barrier.wait()
            worker.run()

        threads = [threading.Thread(target=run, args=(worker,)) for worker in workers]
        with patch("large_doc_manager.LargeDocumentManager", side_effect=construct):
            for thread in threads:
                thread.start()
            barrier.wait()
            self.assertTrue(first_entered.wait(2.0))
            self.assertFalse(second_entered.wait(0.2))
            release.set()
            for thread in threads:
                thread.join(2.0)

        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(len(constructor_calls), 1)
        self.assertIs(window.large_doc_manager, manager)
        self.assertEqual([worker.error.calls for worker in workers], [[], []])
        self.assertEqual(
            sorted(call[0] for call in manager.prepare_calls),
            ["doc-1", "doc-2"],
        )

    def test_failed_construction_is_reported_and_next_worker_retries(self):
        window = self._window()
        manager = _RecordingManager()
        first = self._worker(window, "doc-first", 1)
        second = self._worker(window, "doc-second", 2)

        with patch(
            "large_doc_manager.LargeDocumentManager",
            side_effect=[RuntimeError("manager unavailable"), manager],
        ) as constructor:
            first.run()
            self.assertEqual(
                first.error.calls,
                [("Processing failed: manager unavailable", 1)],
            )
            self.assertIsNone(window.large_doc_manager)

            second.run()

        self.assertEqual(constructor.call_count, 2)
        self.assertEqual(second.error.calls, [])
        self.assertEqual(second.finished.calls, [("doc-second", 1, 2)])
        self.assertIs(window.large_doc_manager, manager)

    def test_preinjected_manager_bypasses_lock_and_constructor(self):
        window = MainWindow.__new__(MainWindow)
        manager = _RecordingManager()
        window.large_doc_manager = manager

        with patch("large_doc_manager.LargeDocumentManager") as constructor:
            result = window._get_large_doc_manager()

        self.assertIs(result, manager)
        constructor.assert_not_called()


if __name__ == "__main__":
    unittest.main()
