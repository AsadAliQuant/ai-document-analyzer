import re
from typing import Callable, Tuple, TypeVar


GEMINI_MODEL_FALLBACKS = (
    "gemini-2.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
)
GEMINI_MODEL_FALLBACK_LABEL = "Automatic: Gemini 2.5 → 3.1 → 3.5 Flash-Lite"
GEMINI_GENERATION_TIMEOUT_MS = 60_000

_ResponseT = TypeVar("_ResponseT")


def call_with_model_fallback(
    call_model: Callable[[str], _ResponseT],
) -> Tuple[_ResponseT, str]:
    """Call Gemini models in order, advancing only when a model is unavailable."""
    for index, model in enumerate(GEMINI_MODEL_FALLBACKS):
        try:
            return call_model(model), model
        except Exception as exc:
            is_last_model = index == len(GEMINI_MODEL_FALLBACKS) - 1
            if is_last_model or not is_unavailable_error(exc):
                raise

    raise RuntimeError("No Gemini fallback models are configured.")


def is_unavailable_error(exc: Exception) -> bool:
    """Return whether an API failure should advance to the next Gemini model."""
    code = _status_code(exc)
    if code == 404 or (code is not None and 500 <= code <= 599):
        return True
    if code in {400, 401, 403, 408, 409, 415, 422, 429}:
        return False

    status = str(getattr(exc, "status", "") or "")
    message = str(getattr(exc, "message", "") or exc)
    lowered = f"{status} {message}".lower()
    return any(
        phrase in lowered
        for phrase in (
            "currently experiencing high demand",
            "service unavailable",
            "temporarily unavailable",
            "model unavailable",
            "model is unavailable",
            "model not found",
            "model is not found",
            "not found for api version",
            "not supported for generatecontent",
            "statuscode.unavailable",
        )
    )


def _status_code(exc: Exception):
    for attribute in ("code", "status_code"):
        value = getattr(exc, attribute, None)
        if callable(value):
            try:
                value = value()
            except Exception:
                value = None
        code = _coerce_status_code(value)
        if code is not None:
            return code

    response = getattr(exc, "response", None)
    code = _coerce_status_code(getattr(response, "status_code", None))
    if code is not None:
        return code

    text = f"{getattr(exc, 'status', '')} {exc}"
    match = re.search(r"\b([45]\d{2})\b", text)
    return int(match.group(1)) if match else None


def _coerce_status_code(value):
    if isinstance(value, int):
        return value
    enum_value = getattr(value, "value", None)
    if isinstance(enum_value, int):
        return enum_value
    if isinstance(enum_value, tuple) and enum_value and isinstance(enum_value[0], int):
        return enum_value[0]
    try:
        text = str(value or "").strip()
        return int(text) if text.isdigit() else None
    except Exception:
        return None
