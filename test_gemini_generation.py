import types
import unittest
from unittest.mock import patch

import main_window
from gemini_fallback import GEMINI_MODEL_FALLBACKS
from gemini_gateway import GeminiCancelledError, GeminiGateway, GeminiRequestError
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


class _FakeEmbedContentConfig:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _FakePart:
    @staticmethod
    def from_text(text):
        return types.SimpleNamespace(text=text)


class _FakeModels:
    def __init__(self, failures):
        self.failures = failures
        self.requests = []
        self.embedding_requests = []

    def generate_content(self, **kwargs):
        self.requests.append(kwargs)
        error = self.failures.get(kwargs["model"])
        if error is not None:
            raise error
        return types.SimpleNamespace(text="generated text")

    def embed_content(self, **kwargs):
        self.embedding_requests.append(kwargs)
        raise _FakeApiError(503, "Service unavailable")


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
            EmbedContentConfig=_FakeEmbedContentConfig,
            Part=_FakePart,
            Content=lambda **kwargs: types.SimpleNamespace(**kwargs),
        )
        return client, fake_genai, fake_types

    def test_generation_falls_back_for_unavailable_models(self):
        failures = {
            GEMINI_MODEL_FALLBACKS[0]: _FakeApiError(503, "Service unavailable"),
            GEMINI_MODEL_FALLBACKS[1]: _FakeApiError(404, "Model not found"),
        }
        client, fake_genai, fake_types = self._fake_sdk(failures)

        with patch.object(main_window, "GeminiGateway", lambda key: GeminiGateway(key, sdk=fake_genai, types_module=fake_types)):
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

        with patch.object(main_window, "GeminiGateway", lambda key: GeminiGateway(key, sdk=fake_genai, types_module=fake_types)):
            with self.assertRaises(GeminiRequestError) as context:
                self._window()._generate_gemini_text("prompt", "key")

        self.assertEqual(context.exception.category, "quota")
        self.assertNotIn("RESOURCE_EXHAUSTED", str(context.exception))
        self.assertEqual(len(client.models.requests), 1)
        self.assertTrue(client.closed)

    def test_cancelled_operation_does_not_start_a_request(self):
        client, fake_genai, fake_types = self._fake_sdk({})
        gateway = GeminiGateway("key", client=client, types_module=fake_types)
        with patch("PyQt6.QtCore.QThread.currentThread") as current_thread:
            current_thread.return_value.isInterruptionRequested.return_value = True
            with self.assertRaises(GeminiCancelledError):
                gateway.generate_text("prompt")
        self.assertEqual(client.models.requests, [])
        gateway.close()

    def test_cancellation_after_response_discards_result(self):
        client, fake_genai, fake_types = self._fake_sdk({})
        gateway = GeminiGateway("key", client=client, types_module=fake_types)
        with patch.object(GeminiGateway, "check_cancelled", side_effect=[None, GeminiCancelledError()]):
            with self.assertRaises(GeminiCancelledError):
                gateway.generate_text("prompt")
        self.assertEqual(len(client.models.requests), 1)
        gateway.close()

    def test_client_uses_shared_timeout(self):
        client, fake_genai, fake_types = self._fake_sdk({})
        seen = {}
        def create_client(**kwargs):
            seen.update(kwargs)
            return client
        fake_genai.Client = create_client
        gateway = GeminiGateway("key", sdk=fake_genai, types_module=fake_types)
        self.assertEqual(seen["http_options"].timeout, 60_000)
        gateway.close()

    def test_embedding_errors_do_not_fall_back_to_generation_models(self):
        client, fake_genai, fake_types = self._fake_sdk(
            {GEMINI_MODEL_FALLBACKS[0]: _FakeApiError(503, "Service unavailable")}
        )
        gateway = GeminiGateway("key", client=client, types_module=fake_types)
        with self.assertRaises(GeminiRequestError):
            gateway.embed_contents(["document text"], 768)
        self.assertEqual(len(client.models.requests), 0)
        self.assertEqual(len(client.models.embedding_requests), 1)
        gateway.close()


if __name__ == "__main__":
    unittest.main()
