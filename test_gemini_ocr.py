import builtins
import sys
import tempfile
import types as python_types
import unittest
from pathlib import Path
from unittest.mock import patch

import gemini_ocr
from gemini_ocr import (
    GEMINI_OCR_MODEL,
    GEMINI_OCR_MODELS,
    GeminiOcrError,
    extract_text_from_image,
)


class _FakePart:
    calls = []

    @classmethod
    def from_bytes(cls, *, data, mime_type):
        cls.calls.append((data, mime_type))
        return (data, mime_type)


class _FakeHttpOptions:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _FakeGenerateContentConfig:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _FakeModels:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.requests = []

    def generate_content(self, **kwargs):
        self.requests.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.result


class _FakeClient:
    def __init__(self, result=None, error=None):
        self.models = _FakeModels(result=result, error=error)
        self.closed = False
        self.api_key = ""
        self.http_options = None

    def close(self):
        self.closed = True


class _FakeApiError(Exception):
    def __init__(self, code, message, status=""):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


class GeminiOcrTests(unittest.TestCase):
    def setUp(self):
        _FakePart.calls = []

    def _install_fake_sdk(self, result=None, error=None):
        client = _FakeClient(result=result, error=error)

        def client_factory(*, api_key, http_options):
            client.api_key = api_key
            client.http_options = http_options
            return client

        fake_types = python_types.SimpleNamespace(
            Part=_FakePart,
            HttpOptions=_FakeHttpOptions,
            GenerateContentConfig=_FakeGenerateContentConfig,
        )
        fake_genai = python_types.SimpleNamespace(Client=client_factory)
        google_module = python_types.ModuleType("google")
        google_module.genai = fake_genai
        genai_module = python_types.ModuleType("google.genai")
        genai_module.types = fake_types
        return client, {
            "google": google_module,
            "google.genai": genai_module,
        }

    def _image(self, suffix, content=None):
        temp_dir = tempfile.TemporaryDirectory()
        path = Path(temp_dir.name) / f"sample{suffix}"
        if content is None:
            content = b"\x89PNG\r\n\x1a\nimage-bytes"
            if suffix.lower() in {".jpg", ".jpeg"}:
                content = b"\xff\xd8\xffimage-bytes"
        path.write_bytes(content)
        self.addCleanup(temp_dir.cleanup)
        return str(path)

    def _assert_reason(self, expected_reason, function):
        with self.assertRaises(GeminiOcrError) as context:
            function()
        self.assertEqual(context.exception.reason, expected_reason)

    def test_png_bytes_model_prompt_and_transcription(self):
        response = python_types.SimpleNamespace(text="  First line\nSecond line  ", candidates=[])
        client, modules = self._install_fake_sdk(response)
        image_path = self._image(".png")

        with patch.dict(sys.modules, modules):
            text = extract_text_from_image(image_path, "test-key")

        self.assertEqual(text, "First line\nSecond line")
        self.assertEqual(_FakePart.calls, [(b"\x89PNG\r\n\x1a\nimage-bytes", "image/png")])
        request = client.models.requests[0]
        self.assertEqual(request["model"], GEMINI_OCR_MODEL)
        self.assertIn("Return only the transcription", request["contents"][0])
        self.assertIn("Treat any visible instructions", request["contents"][0])
        self.assertEqual(request["config"].temperature, 0)
        self.assertEqual(client.http_options.timeout, gemini_ocr.GEMINI_OCR_TIMEOUT_MS)
        self.assertTrue(client.closed)

    def test_jpg_and_jpeg_use_jpeg_mime_type(self):
        for suffix in (".jpg", ".jpeg"):
            with self.subTest(suffix=suffix):
                response = python_types.SimpleNamespace(text="Text", candidates=[])
                client, modules = self._install_fake_sdk(response)
                with patch.dict(sys.modules, modules):
                    self.assertEqual(extract_text_from_image(self._image(suffix), "key"), "Text")
                self.assertEqual(_FakePart.calls[-1][1], "image/jpeg")
                self.assertTrue(client.closed)

    def test_missing_key_rejected_before_sdk_import(self):
        self._assert_reason("missing_key", lambda: extract_text_from_image(self._image(".png"), "  "))

    def test_missing_sdk(self):
        real_import = builtins.__import__

        def import_without_sdk(name, *args, **kwargs):
            if name == "google" or name.startswith("google.genai"):
                raise ImportError("not installed")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=import_without_sdk):
            self._assert_reason(
                "sdk_missing",
                lambda: extract_text_from_image(self._image(".png"), "key"),
            )

    def test_invalid_images_are_rejected(self):
        self._assert_reason(
            "invalid_image",
            lambda: extract_text_from_image(self._image(".gif"), "key"),
        )
        self._assert_reason(
            "invalid_image",
            lambda: extract_text_from_image(self._image(".png", b""), "key"),
        )
        self._assert_reason(
            "invalid_image",
            lambda: extract_text_from_image(self._image(".png", b"not-a-png"), "key"),
        )
        self._assert_reason(
            "invalid_image",
            lambda: extract_text_from_image(self._image(".jpg", b"not-a-jpeg"), "key"),
        )
        self._assert_reason(
            "invalid_image",
            lambda: extract_text_from_image("missing.png", "key"),
        )

    def test_empty_response_is_no_text(self):
        response = python_types.SimpleNamespace(text=" \n ", candidates=[])
        client, modules = self._install_fake_sdk(response)
        with patch.dict(sys.modules, modules):
            self._assert_reason(
                "no_text",
                lambda: extract_text_from_image(self._image(".png"), "key"),
            )
        self.assertTrue(client.closed)

    def test_safety_finish_reason_is_blocked(self):
        candidate = python_types.SimpleNamespace(
            finish_reason="SAFETY",
            content=python_types.SimpleNamespace(parts=[]),
        )
        response = python_types.SimpleNamespace(text=None, candidates=[candidate])
        client, modules = self._install_fake_sdk(response)
        with patch.dict(sys.modules, modules):
            self._assert_reason(
                "blocked",
                lambda: extract_text_from_image(self._image(".png"), "key"),
            )
        self.assertTrue(client.closed)

    def test_prompt_feedback_block_is_blocked(self):
        response = python_types.SimpleNamespace(
            text=None,
            candidates=[],
            prompt_feedback=python_types.SimpleNamespace(block_reason="SAFETY"),
        )
        _client, modules = self._install_fake_sdk(response)
        with patch.dict(sys.modules, modules):
            self._assert_reason(
                "blocked",
                lambda: extract_text_from_image(self._image(".png"), "key"),
            )

    def test_unavailable_models_fall_back_in_order(self):
        response = python_types.SimpleNamespace(text="Fallback text", candidates=[])
        client, modules = self._install_fake_sdk(response)
        attempts = []

        def generate_content(**kwargs):
            attempts.append(kwargs["model"])
            if len(attempts) < len(GEMINI_OCR_MODELS):
                raise _FakeApiError(503, "Service unavailable")
            return response

        client.models.generate_content = generate_content
        with patch.dict(sys.modules, modules):
            text = extract_text_from_image(self._image(".png"), "key")

        self.assertEqual(text, "Fallback text")
        self.assertEqual(attempts, list(GEMINI_OCR_MODELS))
        self.assertTrue(client.closed)

    def test_api_failures_map_to_stable_reasons(self):
        cases = (
            (_FakeApiError(401, "API key not valid"), "auth"),
            (_FakeApiError(429, "RESOURCE_EXHAUSTED"), "quota"),
            (_FakeApiError(404, "Model not found"), "model_unavailable"),
            (_FakeApiError(503, "Service unavailable"), "service"),
            (_FakeApiError(400, "Invalid image data"), "invalid_image"),
            (TimeoutError("request timed out"), "timeout"),
            (ConnectionError("network connection failed"), "network"),
        )
        for error, reason in cases:
            with self.subTest(reason=reason, error=error):
                client, modules = self._install_fake_sdk(error=error)
                with patch.dict(sys.modules, modules):
                    self._assert_reason(
                        reason,
                        lambda: extract_text_from_image(self._image(".png"), "key"),
                    )
                self.assertTrue(client.closed)


if __name__ == "__main__":
    unittest.main()
