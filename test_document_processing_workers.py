import os
import tempfile
import unittest
from unittest.mock import patch

from gemini_ocr import GEMINI_OCR_PIPELINE_VERSION, GeminiOcrError
from main_window import LargeDocProcessWorker, MainWindow, PastedTextProcessWorker


class _Signal:
    def __init__(self):
        self.calls = []

    def emit(self, *args):
        self.calls.append(args)


class _Manager:
    def __init__(self):
        self.calls = []

    def prepare_document(self, doc_key, source, text, api_key=None):
        self.calls.append((doc_key, source, text, api_key))
        return 3


class _Window:
    def __init__(self, extracted_text="Exact\nOCR text", extraction_error=None):
        self.large_doc_manager = _Manager()
        self.manager_requests = 0
        self.extracted_text = extracted_text
        self.extraction_error = extraction_error
        self.extraction_calls = []

    def _get_large_doc_manager(self):
        self.manager_requests += 1
        return self.large_doc_manager

    def extract_text_from_file(self, file_path, gemini_key=""):
        self.extraction_calls.append((file_path, gemini_key))
        if self.extraction_error is not None:
            raise self.extraction_error
        return self.extracted_text


class _CachedImageManager:
    def __init__(self):
        self.doc_key_calls = []
        self.prepare_calls = []

    def compute_document_key(self, file_path, processing_version=None):
        self.doc_key_calls.append((file_path, processing_version))
        return "cached-image-key"

    def has_vector_store(self, doc_key):
        return doc_key == "cached-image-key"


class _TextValue:
    def __init__(self, value):
        self.value = value

    def currentText(self):
        return self.value


class _Tabs:
    def currentIndex(self):
        return 0


class _Ui:
    def __init__(self):
        self.tabs = _Tabs()
        self.modelSourceCombo = _TextValue("Online (Google Gemini)")
        self.availableModelCombo = _TextValue("gemini-2.5-flash")


class DocumentProcessingWorkerTests(unittest.TestCase):
    def _image_path(self):
        temporary_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        temporary_file.write(b"\x89PNG\r\n\x1a\nimage")
        temporary_file.close()
        self.addCleanup(lambda: os.path.exists(temporary_file.name) and os.remove(temporary_file.name))
        return temporary_file.name

    def test_image_transcription_reaches_prepare_document_unchanged(self):
        window = _Window(" First line\nSecond line ")
        worker = LargeDocProcessWorker(
            window,
            self._image_path(),
            "image-key",
            "api-key",
            7,
            is_image=True,
        )
        worker.finished = _Signal()
        worker.error = _Signal()

        worker.run()

        self.assertEqual(window.extraction_calls[0][1], "api-key")
        self.assertEqual(window.manager_requests, 1)
        self.assertEqual(
            window.large_doc_manager.calls,
            [("image-key", window.extraction_calls[0][0], " First line\nSecond line ", "api-key")],
        )
        self.assertEqual(worker.finished.calls, [("image-key", 3, 7)])
        self.assertEqual(worker.error.calls, [])

    def test_cached_image_reuses_index_without_ocr(self):
        image_path = self._image_path()
        manager = _CachedImageManager()
        window = MainWindow.__new__(MainWindow)
        window.ui = _Ui()
        window.large_doc_manager = manager
        window._current_lang = "en"
        window._qa_vector_doc_key = ""
        window._pending_analysis_params = None
        window._session_id = 1
        window._get_selected_file_path = lambda: image_path
        window._get_gemini_key = lambda: "api-key"
        window._set_status = lambda _message: None
        window._set_qa_group_enabled = lambda _enabled: None
        window._stop_qa_typing_indicator = lambda: None
        window._clear_chat = lambda: None
        window.is_image_file = lambda _path: True

        with patch.object(window, "_start_large_doc_processing") as start_processing, patch.object(
            window,
            "extract_text_from_image_ocr",
        ) as extract_ocr, patch.object(window, "_start_background_analysis") as start_analysis:
            window.analyze_document()

        self.assertEqual(
            manager.doc_key_calls,
            [(image_path, GEMINI_OCR_PIPELINE_VERSION)],
        )
        start_processing.assert_not_called()
        extract_ocr.assert_not_called()
        start_analysis.assert_called_once()
        self.assertEqual(window._qa_vector_doc_key, "cached-image-key")

    def test_image_ocr_failure_stops_before_indexing(self):
        window = _Window(extraction_error=GeminiOcrError("quota"))
        worker = LargeDocProcessWorker(
            window,
            self._image_path(),
            "image-key",
            "api-key",
            8,
            is_image=True,
        )
        worker.finished = _Signal()
        worker.error = _Signal()

        worker.run()

        self.assertEqual(window.large_doc_manager.calls, [])
        self.assertEqual(window.manager_requests, 0)
        self.assertEqual(worker.finished.calls, [])
        self.assertEqual(worker.error.calls, [("gemini_ocr:quota", 8)])

    def test_pasted_text_passes_captured_key_to_embedding(self):
        window = _Window()
        worker = PastedTextProcessWorker(window, "paste-key", " pasted text ", "api-key", 9)
        worker.finished = _Signal()
        worker.error = _Signal()

        worker.run()

        self.assertEqual(window.manager_requests, 1)
        self.assertEqual(
            window.large_doc_manager.calls,
            [("paste-key", "pasted:paste-key", "pasted text", "api-key")],
        )
        self.assertEqual(worker.finished.calls, [("paste-key", 3, 9)])
        self.assertEqual(worker.error.calls, [])


if __name__ == "__main__":
    unittest.main()
