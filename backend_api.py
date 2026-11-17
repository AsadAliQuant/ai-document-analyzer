"""Authenticated desktop client for the backend v1 API."""

import json
import os
import sys
import threading
import time
import uuid
from typing import Callable, Optional

import requests

import auth


DEFAULT_API_BASE_URL = "https://ssma.sa/console/api"
DEFAULT_TIMEOUT = (10, 275)
_REFRESH_EARLY_SECONDS = 30
_REFRESH_LOCK = threading.Lock()


class BackendApiError(RuntimeError):
    """A safe, structured failure returned by the backend API client."""

    def __init__(
        self,
        error_code: str,
        message: str,
        *,
        status_code: Optional[int] = None,
        request_id: str = "",
        retryable: bool = False,
        retry_after_seconds: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.status_code = status_code
        self.request_id = request_id
        self.retryable = bool(retryable)
        self.retry_after_seconds = retry_after_seconds


def _config_base_url(path: str) -> str:
    try:
        if not path or not os.path.isfile(path):
            return ""
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        value = data.get("API_BASE_URL") if isinstance(data, dict) else None
        return str(value or "").strip().rstrip("/")
    except Exception:
        return ""


def resolve_api_base_url(
    *,
    appdata_dir: Optional[str] = None,
    bundled_dir: Optional[str] = None,
    development_dir: Optional[str] = None,
) -> str:
    """Resolve API_BASE_URL using AppData, bundle, development, then default."""
    if appdata_dir is None:
        appdata_dir = os.getenv("APPDATA") or os.path.expanduser("~")
    if bundled_dir is None:
        if getattr(sys, "frozen", False):
            bundled_dir = getattr(sys, "_MEIPASS", None) or os.path.dirname(sys.executable)
        else:
            bundled_dir = os.path.dirname(os.path.abspath(__file__))
    if development_dir is None:
        development_dir = os.getcwd()

    candidates = (
        os.path.join(appdata_dir, "AI Document Analyzer", "config.json"),
        os.path.join(bundled_dir, "config.json"),
        os.path.join(development_dir, "config.json"),
    )
    for path in candidates:
        base_url = _config_base_url(path)
        if base_url:
            return base_url
    return DEFAULT_API_BASE_URL


class BackendApiClient:
    """Operation-scoped authenticated client for the backend v1 envelope."""

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        session=None,
        timeout=DEFAULT_TIMEOUT,
        cancellation_check: Optional[Callable[[], None]] = None,
    ) -> None:
        self.base_url = (base_url or resolve_api_base_url()).rstrip("/")
        self._session = session or requests.Session()
        self._owns_session = session is None
        self._timeout = timeout
        self._cancellation_check = cancellation_check or (lambda: None)
        self._closed = False

    def post(self, path: str, payload: dict) -> dict:
        self._cancellation_check()
        token = self._ensure_current_token()
        response = self._dispatch(path, payload, token)
        envelope = self._parse_envelope(response)

        error = envelope.get("error") if isinstance(envelope, dict) else None
        if (
            response.status_code == 401
            and isinstance(error, dict)
            and error.get("code") == "AUTH_REQUIRED"
        ):
            self._cancellation_check()
            token = self._refresh_after_unauthorized(token)
            self._cancellation_check()
            response = self._dispatch(path, payload, token)
            envelope = self._parse_envelope(response)

        self._cancellation_check()
        return self._success_data(response, envelope)

    def _ensure_current_token(self) -> str:
        token = str(auth.AuthState.access_token or "").strip()
        expiry = int(getattr(auth.AuthState, "access_expiry_ts", 0) or 0)
        if token and expiry > int(time.time()) + _REFRESH_EARLY_SECONDS:
            return token
        return self._refresh_token(token)

    def _refresh_after_unauthorized(self, rejected_token: str) -> str:
        return self._refresh_token(rejected_token, force_if_same=True)

    def _refresh_token(self, observed_token: str, force_if_same: bool = False) -> str:
        with _REFRESH_LOCK:
            self._cancellation_check()
            current = str(auth.AuthState.access_token or "").strip()
            expiry = int(getattr(auth.AuthState, "access_expiry_ts", 0) or 0)
            fresh = bool(current and expiry > int(time.time()) + _REFRESH_EARLY_SECONDS)
            if current != observed_token and fresh:
                return current
            if not force_if_same and fresh:
                return current
            try:
                auth.refresh(self.base_url)
            except Exception:
                raise BackendApiError(
                    "AUTH_REQUIRED",
                    "Your session has expired. Please sign in again.",
                    status_code=401,
                ) from None
            current = str(auth.AuthState.access_token or "").strip()
            if not current:
                raise BackendApiError(
                    "AUTH_REQUIRED",
                    "Your session has expired. Please sign in again.",
                    status_code=401,
                )
            return current

    def _dispatch(self, path: str, payload: dict, token: str):
        self._cancellation_check()
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "AIDocumentAnalyzer/1.0",
            "X-Request-ID": str(uuid.uuid4()),
        }
        try:
            return self._session.post(
                f"{self.base_url}/{path.lstrip('/')}",
                json=payload,
                headers=headers,
                timeout=self._timeout,
            )
        except requests.Timeout:
            raise BackendApiError(
                "NETWORK_TIMEOUT",
                "The AI service took too long to respond. Please try again.",
                retryable=True,
            ) from None
        except requests.RequestException:
            raise BackendApiError(
                "NETWORK_ERROR",
                "Could not connect to the AI service. Check your internet connection.",
                retryable=True,
            ) from None
        except Exception:
            raise BackendApiError(
                "NETWORK_ERROR",
                "Could not connect to the AI service. Check your internet connection.",
                retryable=True,
            ) from None

    @staticmethod
    def _parse_envelope(response) -> dict:
        try:
            envelope = response.json()
        except Exception:
            raise BackendApiError(
                "INVALID_RESPONSE",
                "The AI service returned an invalid response. Please try again.",
                status_code=getattr(response, "status_code", None),
            ) from None
        if not isinstance(envelope, dict) or not isinstance(envelope.get("ok"), bool):
            raise BackendApiError(
                "INVALID_RESPONSE",
                "The AI service returned an invalid response. Please try again.",
                status_code=getattr(response, "status_code", None),
            )
        return envelope

    @staticmethod
    def _success_data(response, envelope: dict) -> dict:
        request_id = str(envelope.get("request_id") or "")
        if response.status_code < 400 and envelope.get("ok") is True:
            data = envelope.get("data")
            if isinstance(data, dict):
                return data
            raise BackendApiError(
                "INVALID_RESPONSE",
                "The AI service returned an invalid response. Please try again.",
                status_code=response.status_code,
                request_id=request_id,
            )

        error = envelope.get("error")
        if not isinstance(error, dict):
            raise BackendApiError(
                "INVALID_RESPONSE",
                "The AI service returned an invalid response. Please try again.",
                status_code=response.status_code,
                request_id=request_id,
            )
        retry_after = error.get("retry_after_seconds")
        try:
            retry_after = int(retry_after) if retry_after is not None else None
        except (TypeError, ValueError):
            retry_after = None
        raise BackendApiError(
            str(error.get("code") or "SERVICE_ERROR"),
            "The AI service could not complete the request.",
            status_code=response.status_code,
            request_id=request_id,
            retryable=bool(error.get("retryable")),
            retry_after_seconds=retry_after,
        )

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._owns_session:
            try:
                self._session.close()
            except Exception:
                pass
