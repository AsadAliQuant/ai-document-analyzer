import unittest

from gemini_fallback import (
    GEMINI_MODEL_FALLBACKS,
    call_with_model_fallback,
    is_unavailable_error,
)


class _FakeApiError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


class GeminiFallbackTests(unittest.TestCase):
    def test_models_are_tried_in_requested_order(self):
        calls = []

        def call_model(model):
            calls.append(model)
            if model != GEMINI_MODEL_FALLBACKS[-1]:
                raise _FakeApiError(503, "Service unavailable")
            return "success"

        response, model = call_with_model_fallback(call_model)

        self.assertEqual(response, "success")
        self.assertEqual(model, "gemini-3.5-flash-lite")
        self.assertEqual(calls, list(GEMINI_MODEL_FALLBACKS))

    def test_model_not_found_advances_to_next_model(self):
        calls = []

        def call_model(model):
            calls.append(model)
            if len(calls) == 1:
                raise _FakeApiError(404, "Model not found")
            return "success"

        _response, model = call_with_model_fallback(call_model)

        self.assertEqual(model, "gemini-3.1-flash-lite")
        self.assertEqual(calls, list(GEMINI_MODEL_FALLBACKS[:2]))

    def test_non_unavailable_errors_do_not_fall_back(self):
        for error in (
            _FakeApiError(400, "Invalid image data"),
            _FakeApiError(401, "API key not valid"),
            _FakeApiError(429, "RESOURCE_EXHAUSTED"),
            TimeoutError("request timed out"),
            ConnectionError("network connection failed"),
        ):
            with self.subTest(error=error):
                calls = []

                def call_model(model):
                    calls.append(model)
                    raise error

                with self.assertRaises(type(error)):
                    call_with_model_fallback(call_model)
                self.assertEqual(calls, [GEMINI_MODEL_FALLBACKS[0]])

    def test_high_demand_message_without_numeric_code_is_unavailable(self):
        self.assertTrue(
            is_unavailable_error(
                RuntimeError("This model is currently experiencing high demand.")
            )
        )

    def test_unknown_status_code_can_still_use_unavailable_message(self):
        self.assertTrue(
            is_unavailable_error(
                _FakeApiError(499, "This model is currently experiencing high demand.")
            )
        )


if __name__ == "__main__":
    unittest.main()
