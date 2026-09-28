import time
import requests
import keyring

SERVICE = "ai_document_analyzer"
KEY_NAME = "refresh_token"

class AuthState:
    access_token = None
    access_expiry_ts = 0
    user = None

def set_tokens(access_token, access_expires_in, refresh_token, user):
    AuthState.access_token = access_token
    AuthState.access_expiry_ts = int(time.time()) + int(access_expires_in or 0)
    AuthState.user = user
    if refresh_token:
        try:
            keyring.set_password(SERVICE, KEY_NAME, refresh_token)
        except Exception:
            # If secure storage is unavailable, skip persisting the refresh token
            pass

def get_stored_refresh_token():
    try:
        return keyring.get_password(SERVICE, KEY_NAME)
    except Exception:
        return None

def clear_tokens():
    AuthState.access_token = None
    AuthState.access_expiry_ts = 0
    AuthState.user = None
    try:
        keyring.delete_password(SERVICE, KEY_NAME)
    except Exception:
        pass

def login(base_url, email, password):
    _HEADERS = {
        "User-Agent": "AIDocumentAnalyzer/1.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    try:
        r = requests.post(
            f"{base_url}/login",
            json={"email": email, "password": password},
            headers=_HEADERS,
            timeout=15,
        )
    except Exception as e:
        # Network / connection errors
        raise RuntimeError("Unable to reach the server. Please check your internet connection and try again.") from e

    # --- diagnostic logging (safe to leave; writes to %APPDATA%/AI Document Analyzer/auth_debug.log) ---
    try:
        import os, datetime
        _log_dir = os.path.join(os.getenv("APPDATA") or os.getcwd(), "AI Document Analyzer")
        os.makedirs(_log_dir, exist_ok=True)
        _log_path = os.path.join(_log_dir, "auth_debug.log")
        with open(_log_path, "a", encoding="utf-8") as _f:
            _f.write(f"\n--- {datetime.datetime.now().isoformat()} ---\n")
            _f.write(f"POST {base_url}/login  status={r.status_code}\n")
            _f.write(f"Response headers: {dict(r.headers)}\n")
            _f.write(f"Response body (first 2000 chars):\n{r.text[:2000]}\n")
    except Exception:
        pass
    # --- end diagnostic logging ---

    # Map known HTTP error responses to clear messages using backend JSON `error` when available
    if r.status_code >= 400:
        backend_error = ""
        try:
            data = r.json()
            backend_error = str(data.get("error", "") or "").strip()
        except Exception:
            backend_error = ""

        if r.status_code == 400:
            message = backend_error or "Username and password are required."
        elif r.status_code == 401:
            if backend_error:
                message = backend_error
            else:
                # Server returned 401 but no JSON error — likely a WAF/proxy issue
                snippet = r.text[:200].strip() if r.text else "(empty)"
                message = (
                    "Invalid username or password.\n\n"
                    "If your credentials are correct, the server may be blocking this request. "
                    "Please check auth_debug.log in your AppData folder and contact support."
                )
        elif r.status_code == 403:
            message = backend_error or "Your account has been disabled. Please contact support."
        else:
            message = backend_error or f"Login failed with status code {r.status_code}."
        raise RuntimeError(message)

    data = r.json()
    set_tokens(data.get("access_token"), data.get("access_expires_in"), data.get("refresh_token"), data.get("user"))
    return data.get("user")

def refresh(base_url):
    rt = get_stored_refresh_token()
    if not rt:
        raise RuntimeError("No refresh token")
    r = requests.post(f"{base_url}/token/refresh", json={"refresh_token": rt}, timeout=15)
    r.raise_for_status()
    data = r.json()
    set_tokens(data.get("access_token"), data.get("access_expires_in"), data.get("refresh_token"), data.get("user"))
    return data.get("user")
