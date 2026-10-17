import types
import unittest
from unittest.mock import patch

import main_window
from gemini_fallback import GEMINI_MODEL_FALLBACKS
from main_window import MainWindow


class _FakeApiError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


class _FakeHttpOptions:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _FakeGenerateContentConfig:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _FakeModels:
    def __init__(self, failures):
        self.failures = failures
        self.requests = []

    def generate_content(self, **kwargs):
        self.requests.append(kwargs)
        error = self.failures.get(kwargs["model"])
        if error is not None:
            raise error
        return types.SimpleNamespace(text="generated text")


class _FakeClient:
    def __init__(self, failures):
        self.models = _FakeModels(failures)
        self.closed = False

    def close(self):
        self.closed = True


class GeminiGenerationFallbackTests(unittest.TestCase):
    def _window(self):
        return MainWindow.__new__(MainWindow)

    def _fake_sdk(self, failures):
        client = _FakeClient(failures)
        fake_genai = types.SimpleNamespace(
            Client=lambda **_kwargs: client,
        )
        fake_types = types.SimpleNamespace(
            HttpOptions=_FakeHttpOptions,
            GenerateContentConfig=_FakeGenerateContentConfig,
        )
        return client, fake_genai, fake_types

    def test_generation_falls_back_for_unavailable_models(self):
        failures = {
            GEMINI_MODEL_FALLBACKS[0]: _FakeApiError(503, "Service unavailable"),
            GEMINI_MODEL_FALLBACKS[1]: _FakeApiError(404, "Model not found"),
        }
        client, fake_genai, fake_types = self._fake_sdk(failures)

        with patch.object(main_window, "genai", fake_genai), patch.object(
            main_window, "genai_types", fake_types
        ):
            text = self._window()._generate_gemini_text(
                "prompt",
                "key",
                system_instruction="system",
            )

        self.assertEqual(text, "generated text")
        self.assertEqual(
            [request["model"] for request in client.models.requests],
            list(GEMINI_MODEL_FALLBACKS),
        )
        self.assertEqual(
            client.models.requests[0]["config"].system_instruction,
            "system",
        )
        self.assertTrue(client.closed)

    def test_generation_does_not_fall_back_for_quota(self):
        error = _FakeApiError(429, "RESOURCE_EXHAUSTED")
        client, fake_genai, fake_types = self._fake_sdk(
            {GEMINI_MODEL_FALLBACKS[0]: error}
        )

        with patch.object(main_window, "genai", fake_genai), patch.object(
            main_window, "genai_types", fake_types
        ):
            with self.assertRaises(_FakeApiError):
                self._window()._generate_gemini_text("prompt", "key")

        self.assertEqual(len(client.models.requests), 1)
        self.assertTrue(client.closed)


if __name__ == "__main__":
    unittest.main()
