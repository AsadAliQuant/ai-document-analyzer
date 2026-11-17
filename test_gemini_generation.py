import threading
import time
import unittest
from unittest.mock import patch

import auth
import main_window
from backend_api import BackendApiClient, BackendApiError
from gemini_gateway import GeminiCancelledError, GeminiGateway, GeminiRequestError
from main_window import MainWindow


class _Response:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class _Session:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.closed = False

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.responses.pop(0)

    def close(self):
        self.closed = True


class GeminiGenerationTests(unittest.TestCase):
    def setUp(self):
        auth.AuthState.access_token = "access-token"
        auth.AuthState.access_expiry_ts = int(time.time()) + 3600

    def _gateway(self, responses):
        session = _Session(responses)
        client = BackendApiClient(base_url="https://api.example.test/root/", session=session)
        return GeminiGateway(client=client), session

    def test_generation_sends_exact_authenticated_backend_request(self):
        gateway, session = self._gateway([
            _Response(payload={"ok": True, "request_id": "req-1", "data": {"text": "generated"}})
        ])
        schema = {"type": "object"}

        text = gateway.generate_text("prompt", system_instruction="system", response_schema=schema)

        self.assertEqual(text, "generated")
        url, request = session.calls[0]
        self.assertEqual(url, "https://api.example.test/root/v1/gemini/generate")
        self.assertEqual(request["json"], {
            "prompt": "prompt",
            "system_instruction": "system",
            "response_schema": schema,
        })
        self.assertEqual(request["headers"]["Authorization"], "Bearer access-token")
        self.assertEqual(request["headers"]["Accept"], "application/json")
        self.assertIn("X-Request-ID", request["headers"])
        self.assertNotIn("model", request["json"])
        self.assertNotIn("api_key", request["json"])
        self.assertNotIn("timeout", request["json"])
        self.assertEqual(len(session.calls), 1)

    def test_auth_required_refreshes_and_replays_once(self):
        gateway, session = self._gateway([
            _Response(401, {"ok": False, "request_id": "req-old", "error": {"code": "AUTH_REQUIRED", "message": "hidden", "retryable": False}}),
            _Response(200, {"ok": True, "request_id": "req-new", "data": {"text": "ok"}}),
        ])

        def refresh(_base_url):
            auth.AuthState.access_token = "new-token"
            auth.AuthState.access_expiry_ts = int(time.time()) + 3600

        with patch("backend_api.auth.refresh", side_effect=refresh) as refresh_call:
            self.assertEqual(gateway.generate_text("prompt"), "ok")

        refresh_call.assert_called_once()
        self.assertEqual(len(session.calls), 2)
        self.assertEqual(session.calls[1][1]["headers"]["Authorization"], "Bearer new-token")

    def test_non_auth_failure_is_not_replayed_and_metadata_is_preserved(self):
        gateway, session = self._gateway([
            _Response(429, {"ok": False, "request_id": "safe-id", "error": {
                "code": "RATE_LIMITED", "message": "raw secret body", "retryable": True,
                "retry_after_seconds": 60,
            }})
        ])
        with self.assertRaises(GeminiRequestError) as context:
            gateway.generate_text("secret prompt")
        error = context.exception
        self.assertEqual(error.category, "quota")
        self.assertEqual(error.error_code, "RATE_LIMITED")
        self.assertEqual(error.request_id, "safe-id")
        self.assertTrue(error.retryable)
        self.assertEqual(error.retry_after_seconds, 60)
        self.assertNotIn("secret", str(error).lower())
        self.assertEqual(len(session.calls), 1)

    def test_malformed_envelope_is_safe(self):
        gateway, _session = self._gateway([_Response(200, ValueError("raw secret body"))])
        with self.assertRaises(GeminiRequestError) as context:
            gateway.generate_text("secret prompt")
        self.assertEqual(context.exception.category, "service")
        self.assertNotIn("secret", str(context.exception).lower())

    def test_cancellation_before_and_after_request(self):
        gateway, session = self._gateway([
            _Response(payload={"ok": True, "request_id": "req", "data": {"text": "discard"}})
        ])
        with patch.object(GeminiGateway, "check_cancelled", side_effect=GeminiCancelledError("cancelled")):
            with self.assertRaises(GeminiCancelledError):
                gateway.generate_text("prompt")
        self.assertEqual(session.calls, [])

        with patch.object(GeminiGateway, "check_cancelled", side_effect=[None, GeminiCancelledError("cancelled")]):
            with self.assertRaises(GeminiCancelledError):
                gateway.generate_text("prompt")
        self.assertEqual(len(session.calls), 1)

    def test_close_is_idempotent(self):
        class Client:
            def __init__(self): self.close_count = 0
            def close(self): self.close_count += 1
        client = Client()
        gateway = GeminiGateway(client=client)
        gateway.close()
        gateway.close()
        self.assertEqual(client.close_count, 1)

    def test_concurrent_expired_token_refresh_is_coalesced(self):
        auth.AuthState.access_expiry_ts = 0
        sessions = [
            _Session([_Response(200, {"ok": True, "request_id": str(i), "data": {"value": i}})])
            for i in range(2)
        ]
        barrier = threading.Barrier(2)
        refresh_count = 0
        refresh_lock = threading.Lock()

        def refresh(_base_url):
            nonlocal refresh_count
            with refresh_lock:
                refresh_count += 1
            time.sleep(0.03)
            auth.AuthState.access_token = "refreshed"
            auth.AuthState.access_expiry_ts = int(time.time()) + 3600

        errors = []
        def run(session):
            try:
                barrier.wait()
                BackendApiClient(base_url="https://api.test", session=session).post("/test", {})
            except Exception as exc:
                errors.append(exc)

        with patch("backend_api.auth.refresh", side_effect=refresh):
            threads = [threading.Thread(target=run, args=(session,)) for session in sessions]
            for thread in threads: thread.start()
            for thread in threads: thread.join()

        self.assertEqual(errors, [])
        self.assertEqual(refresh_count, 1)

    def test_summary_and_qa_prompts_remain_keyless_and_localized(self):
        window = MainWindow.__new__(MainWindow)
        for language in ("en", "ar"):
            with self.subTest(language=language):
                window._current_lang = language
                calls = []
                window._generate_gemini_text = lambda prompt, **kwargs: calls.append((prompt, kwargs)) or "answer"
                window.summarize_text_gemini("ignored", "Unique document body")
                self.assertIn("Unique document body", calls[-1][0])
                messages = [{"role": "user", "content": "Current question"}]
                answer = window.answer_question_gemini("ignored", messages, "summary", "Unique source context")
                self.assertEqual(answer, "answer")
                self.assertIn("Unique source context", calls[-1][0])


if __name__ == "__main__":
    unittest.main()
