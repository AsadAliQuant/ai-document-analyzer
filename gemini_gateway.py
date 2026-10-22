"""Internal, replaceable boundary for Gemini SDK requests."""

from gemini_fallback import GEMINI_GENERATION_TIMEOUT_MS, is_unavailable_error


class GeminiRequestError(RuntimeError):
    def __init__(self, category, message):
        super().__init__(message)
        self.category = category


class GeminiCancelledError(RuntimeError):
    pass


class GeminiGateway:
    """Owns one operation-scoped Google Gen AI client and its request policy."""

    def __init__(self, api_key, client=None, sdk=None, types_module=None):
        key = (api_key or "").strip()
        if not key:
            raise RuntimeError("A Gemini API key is required. Add it in Settings and try again.")
        if client is None:
            if sdk is None or types_module is None:
                try:
                    from google import genai as sdk
                    from google.genai import types as types_module
                except Exception as exc:
                    raise RuntimeError("The Google Gen AI SDK is unavailable. Install 'google-genai'.") from exc
            try:
                client = sdk.Client(
                    api_key=key,
                    http_options=types_module.HttpOptions(timeout=GEMINI_GENERATION_TIMEOUT_MS),
                )
            except Exception as exc:
                raise _safe_request_error(exc) from None
        self._client = client
        self._types = types_module

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

    def _generate_with_fallback(self, make_request):
        from gemini_fallback import GEMINI_MODEL_FALLBACKS
        for index, model in enumerate(GEMINI_MODEL_FALLBACKS):
            self.check_cancelled()
            try:
                result = make_request(model)
                self.check_cancelled()
                return result
            except GeminiCancelledError:
                raise
            except Exception as exc:
                if index == len(GEMINI_MODEL_FALLBACKS) - 1 or not is_unavailable_error(exc):
                    raise _safe_request_error(exc) from None
        raise GeminiRequestError("service", "Gemini is temporarily unavailable. Try again shortly.")

    def generate_text(self, prompt, system_instruction=None, response_schema=None):
        config_kwargs = {"system_instruction": system_instruction}
        if response_schema is not None:
            config_kwargs.update(response_mime_type="application/json", response_json_schema=response_schema)
        try:
            config = self._types.GenerateContentConfig(**config_kwargs)
        except Exception as exc:
            raise _safe_request_error(exc) from None
        response = self._generate_with_fallback(
            lambda model: self._client.models.generate_content(model=model, contents=prompt, config=config)
        )
        return getattr(response, "text", None)

    def transcribe_image(self, image_bytes, mime_type, prompt):
        return self._generate_with_fallback(
            lambda model: self._client.models.generate_content(
                model=model,
                contents=[prompt, self._types.Part.from_bytes(data=image_bytes, mime_type=mime_type)],
                config=self._types.GenerateContentConfig(temperature=0),
            )
        )

    def embed_contents(self, contents, output_dimension):
        """Embed plain text inputs while keeping all SDK types inside the adapter."""
        self.check_cancelled()
        try:
            sdk_contents = [
                self._types.Content(
                    role="user",
                    parts=[self._types.Part.from_text(text=content)],
                )
                for content in contents
            ]
            result = self._client.models.embed_content(
                model="gemini-embedding-2",
                contents=sdk_contents,
                config=self._types.EmbedContentConfig(output_dimensionality=output_dimension),
            )
            self.check_cancelled()
            return result
        except GeminiCancelledError:
            raise
        except Exception as exc:
            raise _safe_request_error(exc) from None

    def close(self):
        try:
            self._client.close()
        except Exception:
            pass


def _safe_request_error(exc):
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    try:
        code = int(code)
    except (TypeError, ValueError):
        code = None
    detail = f"{getattr(exc, 'status', '')} {getattr(exc, 'message', '')} {exc}".lower()
    if code in {401, 403} or any(term in detail for term in ("unauthenticated", "api key", "permission denied")):
        return GeminiRequestError("auth", "Gemini rejected the API key. Check the key in Settings.")
    if code == 429 or "quota" in detail or "resource_exhausted" in detail:
        return GeminiRequestError("quota", "Gemini usage limit reached. Wait a while and try again.")
    if code == 404 or "model not found" in detail:
        return GeminiRequestError("model_unavailable", "The selected Gemini model is unavailable.")
    if code == 400 and any(term in detail for term in ("invalid image", "image data", "unsupported image")):
        return GeminiRequestError("invalid_image", "The image could not be processed. Check the image and try again.")
    if "timeout" in detail or "timed out" in detail or "deadline exceeded" in detail:
        return GeminiRequestError("timeout", "Gemini took too long to respond. Please try again.")
    if any(term in detail for term in ("connection", "network", "dns")):
        return GeminiRequestError("network", "Could not connect to Gemini. Check your internet connection.")
    return GeminiRequestError("service", "Gemini request failed. Please try again shortly.")
