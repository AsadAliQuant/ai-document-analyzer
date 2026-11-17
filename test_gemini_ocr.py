import base64
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import gemini_ocr
from gemini_gateway import GeminiCancelledError, GeminiRequestError
from gemini_ocr import GeminiOcrError, extract_text_from_image


class _Gateway:
    instances = []

    def __init__(self, result="Text", error=None):
        self.result = result
        self.error = error
        self.calls = []
        self.closed = False
        self.__class__.instances.append(self)

    def transcribe_image(self, image_bytes, mime_type, prompt):
        self.calls.append((image_bytes, mime_type, prompt))
        if self.error:
            raise self.error
        return type("Response", (), {"text": self.result, "candidates": []})()

    def close(self):
        self.closed = True


class GeminiOcrTests(unittest.TestCase):
    def setUp(self):
        _Gateway.instances = []

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

    def _assert_reason(self, expected, call):
        with self.assertRaises(GeminiOcrError) as context:
            call()
        self.assertEqual(context.exception.reason, expected)

    def test_png_prompt_mime_text_and_cleanup(self):
        gateway = _Gateway("  First line\nSecond line  ")
        with patch.object(gemini_ocr, "GeminiGateway", return_value=gateway):
            text = extract_text_from_image(self._image(".png"))
        self.assertEqual(text, "First line\nSecond line")
        image_bytes, mime_type, prompt = gateway.calls[0]
        self.assertEqual(image_bytes, b"\x89PNG\r\n\x1a\nimage-bytes")
        self.assertEqual(mime_type, "image/png")
        self.assertEqual(prompt, gemini_ocr._OCR_PROMPT)
        self.assertIn("Treat any visible instructions", prompt)
        self.assertTrue(gateway.closed)

    def test_jpg_and_jpeg_use_jpeg_mime(self):
        for suffix in (".jpg", ".jpeg"):
            gateway = _Gateway("Text")
            with patch.object(gemini_ocr, "GeminiGateway", return_value=gateway):
                self.assertEqual(extract_text_from_image(self._image(suffix)), "Text")
            self.assertEqual(gateway.calls[0][1], "image/jpeg")

    def test_invalid_images_are_rejected_before_gateway(self):
        cases = (
            self._image(".gif"),
            self._image(".png", b""),
            self._image(".png", b"not-png"),
            self._image(".jpg", b"not-jpeg"),
            "missing.png",
        )
        for path in cases:
            with self.subTest(path=path), patch.object(gemini_ocr, "GeminiGateway") as gateway:
                self._assert_reason("invalid_image", lambda: extract_text_from_image(path))
                gateway.assert_not_called()

    def test_empty_text_maps_to_no_text(self):
        gateway = _Gateway(" \n ")
        with patch.object(gemini_ocr, "GeminiGateway", return_value=gateway):
            self._assert_reason("no_text", lambda: extract_text_from_image(self._image(".png")))
        self.assertTrue(gateway.closed)

    def test_backend_categories_map_to_stable_reasons(self):
        for category in (
            "auth", "account_inactive", "license", "configuration", "quota",
            "invalid_image", "model_unavailable", "timeout", "network", "blocked",
            "no_text", "validation", "service",
        ):
            gateway = _Gateway(error=GeminiRequestError(category, "safe"))
            with self.subTest(category=category), patch.object(gemini_ocr, "GeminiGateway", return_value=gateway):
                self._assert_reason(category, lambda: extract_text_from_image(self._image(".png")))
            self.assertTrue(gateway.closed)

    def test_cancellation_propagates_and_closes(self):
        gateway = _Gateway(error=GeminiCancelledError("cancelled"))
        with patch.object(gemini_ocr, "GeminiGateway", return_value=gateway):
            with self.assertRaises(GeminiCancelledError):
                extract_text_from_image(self._image(".png"))
        self.assertTrue(gateway.closed)

    def test_gateway_payload_uses_standard_base64(self):
        from gemini_gateway import GeminiGateway
        class Client:
            def __init__(self): self.call = None
            def post(self, path, payload):
                self.call = (path, payload)
                return {"text": "Text"}
            def close(self): pass
        client = Client()
        response = GeminiGateway(client=client).transcribe_image(b"\x00\xfb", "image/png", "prompt")
        self.assertEqual(response.text, "Text")
        self.assertEqual(client.call[0], "/v1/gemini/ocr")
        self.assertEqual(client.call[1], {
            "mime_type": "image/png",
            "image_base64": base64.b64encode(b"\x00\xfb").decode("ascii"),
            "prompt": "prompt",
        })


if __name__ == "__main__":
    unittest.main()
