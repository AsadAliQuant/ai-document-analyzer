"""Replaceable boundary for authenticated backend Gemini requests."""

import base64
import types

from backend_api import BackendApiClient, BackendApiError


class GeminiRequestError(RuntimeError):
    def __init__(
        self,
        category,
        message,
        *,
        error_code="",
        request_id="",
        retryable=False,
        retry_after_seconds=None,
    ):
        super().__init__(message)
        self.category = category
        self.error_code = error_code
        self.request_id = request_id
        self.retryable = bool(retryable)
        self.retry_after_seconds = retry_after_seconds


class GeminiCancelledError(RuntimeError):
    pass


class GeminiGateway:
    """Owns one operation-scoped authenticated backend client."""

    def __init__(self, client=None):
        self._client = client or BackendApiClient(cancellation_check=self.check_cancelled)
        self._closed = False

    @staticmethod
    def check_cancelled():
        try:
            from PyQt6.QtCore import QThread
            if QThread.currentThread().isInterruptionRequested():
                raise GeminiCancelledError("Gemini request cancelled.")
        except GeminiCancelledError:
            raise
        except Exception:
            return

    def generate_text(self, prompt, system_instruction=None, response_schema=None):
        self.check_cancelled()
        try:
            data = self._client.post(
                "/v1/gemini/generate",
                {
                    "prompt": prompt,
                    "system_instruction": system_instruction,
                    "response_schema": response_schema,
                },
            )
            text = data.get("text")
            if not isinstance(text, str):
                raise GeminiRequestError("service", "The AI service returned an invalid response. Please try again.")
            self.check_cancelled()
            return text
        except GeminiCancelledError:
            raise
        except GeminiRequestError:
            raise
        except BackendApiError as exc:
            raise _safe_request_error(exc) from None

    def transcribe_image(self, image_bytes, mime_type, prompt):
        self.check_cancelled()
        try:
            data = self._client.post(
                "/v1/gemini/ocr",
                {
                    "mime_type": mime_type,
                    "image_base64": base64.b64encode(image_bytes).decode("ascii"),
                    "prompt": prompt,
                },
            )
            text = data.get("text")
            if not isinstance(text, str):
                raise GeminiRequestError("service", "The AI service returned an invalid response. Please try again.")
            self.check_cancelled()
            return types.SimpleNamespace(text=text)
        except GeminiCancelledError:
            raise
        except GeminiRequestError:
            raise
        except BackendApiError as exc:
            raise _safe_request_error(exc) from None

    def embed_contents(self, contents, output_dimension):
        self.check_cancelled()
        try:
            data = self._client.post(
                "/v1/gemini/embed",
                {"contents": list(contents), "output_dimension": output_dimension},
            )
            vectors = data.get("vectors")
            if not isinstance(vectors, list):
                raise GeminiRequestError("service", "The AI service returned an invalid embedding response. Please try again.")
            result = types.SimpleNamespace(
                embeddings=[types.SimpleNamespace(values=vector) for vector in vectors]
            )
            self.check_cancelled()
            return result
        except GeminiCancelledError:
            raise
        except GeminiRequestError:
            raise
        except BackendApiError as exc:
            raise _safe_request_error(exc) from None

    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            self._client.close()
        except Exception:
            pass


def _safe_request_error(exc):
    code = str(getattr(exc, "error_code", "") or "").upper()
    mappings = {
        "AUTH_REQUIRED": ("auth", "Your session has expired. Please sign in again."),
        "ACCOUNT_INACTIVE": ("account_inactive", "Your account is inactive. Please contact support."),
        "LICENSE_REQUIRED": ("license", "An active license is required. Please contact support."),
        "GEMINI_KEY_NOT_CONFIGURED": ("configuration", "The AI service is not configured. Contact an administrator."),
        "KEY_INVALID": ("configuration", "The AI service is not configured correctly. Contact an administrator."),
        "RATE_LIMITED": ("quota", "AI usage limit reached. Wait a while and try again."),
        "CONCURRENCY_LIMITED": ("quota", "The AI service is busy. Wait a moment and try again."),
        "GEMINI_QUOTA_EXHAUSTED": ("quota", "AI usage limit reached. Wait a while and try again."),
        "GEMINI_MODEL_UNAVAILABLE": ("model_unavailable", "The AI service is temporarily unavailable. Try again shortly."),
        "GEMINI_TIMEOUT": ("timeout", "The AI service took too long to respond. Please try again."),
        "NETWORK_TIMEOUT": ("timeout", "The AI service took too long to respond. Please try again."),
        "GEMINI_NETWORK_ERROR": ("network", "Could not connect to the AI service. Check your internet connection."),
        "NETWORK_ERROR": ("network", "Could not connect to the AI service. Check your internet connection."),
        "INVALID_IMAGE": ("invalid_image", "The image could not be processed. Check the image and try again."),
        "UNSUPPORTED_MEDIA_TYPE": ("invalid_image", "The image format is not supported."),
        "OCR_BLOCKED": ("blocked", "The AI service blocked the OCR output."),
        "OCR_NO_TEXT": ("no_text", "The AI service returned no transcription."),
        "REQUEST_CANCELLED": ("cancelled", "The request was cancelled."),
        "VALIDATION_FAILED": ("validation", "The AI request was invalid."),
        "INVALID_JSON": ("validation", "The AI request was invalid."),
        "PAYLOAD_TOO_LARGE": ("validation", "The AI request is too large."),
    }
    category, message = mappings.get(
        code,
        ("service", "The AI service could not complete the request. Please try again shortly."),
    )
    if category == "cancelled":
        raise GeminiCancelledError(message)
    return GeminiRequestError(
        category,
        message,
        error_code=code,
        request_id=str(getattr(exc, "request_id", "") or ""),
        retryable=bool(getattr(exc, "retryable", False)),
        retry_after_seconds=getattr(exc, "retry_after_seconds", None),
    )
