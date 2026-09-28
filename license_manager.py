"""
License verification service — checks /me/licenses on login and every 10 minutes.
Stores encrypted cache locally with machine-specific key.
"""
import base64
import hashlib
import json
import os
import platform
import time
import uuid
from datetime import datetime

import requests
from cryptography.fernet import Fernet, InvalidToken
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from auth import AuthState

_CACHE_EXPIRY_SECONDS = 48 * 3600  # 48 hours
_CHECK_INTERVAL_MS = 10 * 60 * 1000  # 10 minutes


class LicenseManager(QObject):
    """Validates user license against backend on login and periodically."""

    license_valid = pyqtSignal()
    license_invalid = pyqtSignal(dict)  # {status, expires_at, days_expired, license_type, reason}
    license_warning = pyqtSignal(int)   # days_remaining (fired when <= 7 days left)

    def __init__(self, api_base: str):
        super().__init__()
        self.api_base = api_base.rstrip("/") if api_base else ""
        self._cached_info: dict = {}

        # Cache file path
        try:
            appdata = os.getenv("APPDATA") or os.path.expanduser("~")
            state_dir = os.path.join(appdata, "AI Document Analyzer")
            os.makedirs(state_dir, exist_ok=True)
            self._cache_file = os.path.join(state_dir, "license_cache.dat")
        except Exception:
            self._cache_file = "license_cache.dat"

        self._fernet = self._init_cipher()
        print(f"[LicenseManager] Cache file: {self._cache_file}")

        # Load last known state from disk
        cached = self._load_cache()
        if cached:
            self._cached_info = cached

        # Periodic check every 10 minutes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._periodic_check)
        self.timer.start(_CHECK_INTERVAL_MS)

        # Defer first check so signal connections in main_window.py are established first
        if AuthState.access_token:
            QTimer.singleShot(0, self.check_now)

    def _init_cipher(self) -> Fernet:
        """Derive a machine-specific Fernet key so cache cannot be copied between machines."""
        try:
            node = platform.node().encode("utf-8", errors="replace")
            mac = str(uuid.getnode()).encode("utf-8")
            key_bytes = hashlib.sha256(node + mac).digest()
            return Fernet(base64.urlsafe_b64encode(key_bytes))
        except Exception as e:
            print(f"[LicenseManager] Cipher init error, using fallback key: {e}")
            fallback = base64.urlsafe_b64encode(hashlib.sha256(b"AI_Doc_License_v1").digest())
            return Fernet(fallback)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_now(self):
        """Perform an immediate license check against the backend API."""
        if not AuthState.access_token:
            print("[LicenseManager] No access token — skipping check")
            return

        print("[LicenseManager] Checking license status...")
        try:
            resp = requests.get(
                f"{self.api_base}/me/licenses",
                headers={"Authorization": f"Bearer {AuthState.access_token}"},
                timeout=15,
            )
            if resp.status_code == 401:
                print("[LicenseManager] Token rejected (401) — will retry after re-auth")
                return
            if resp.status_code != 200:
                print(f"[LicenseManager] Unexpected status {resp.status_code}, using cache")
                self._use_cache_fallback()
                return

            licenses = resp.json().get("licenses", [])
            self._process_licenses(licenses)

        except Exception as e:
            print(f"[LicenseManager] Network error: {e}")
            self._use_cache_fallback()

    def get_cached_info(self) -> dict:
        """Return the last known license info dict."""
        return dict(self._cached_info)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _periodic_check(self):
        """Called by QTimer every 10 minutes."""
        if AuthState.access_token:
            self.check_now()

    def _process_licenses(self, licenses: list):
        """Find the best active license and emit appropriate signals."""
        now = datetime.now()

        active_license = None
        expired_license = None  # keep for overlay info if no active found

        for lic in licenses:
            status = lic.get("status", "")
            expires_raw = lic.get("expires_at", "") or ""

            try:
                # Backend returns "YYYY-MM-DD HH:MM:SS" or ISO format
                expires_dt = datetime.fromisoformat(expires_raw.replace(" ", "T"))
            except Exception:
                expires_dt = None

            if status == "active" and expires_dt and expires_dt > now:
                active_license = lic
                active_license["_expires_dt"] = expires_dt
                break  # first valid active license is enough

            if status in ("active", "expired") and expires_dt and expires_raw:
                if expired_license is None:
                    expired_license = lic
                    expired_license["_expires_dt"] = expires_dt

        if active_license:
            expires_dt = active_license["_expires_dt"]
            days_remaining = (expires_dt - now).days

            info = {
                "status": "active",
                "expires_at": expires_dt.strftime("%B %d, %Y"),
                "days_remaining": days_remaining,
                "license_type": active_license.get("type", "standard"),
                "license_key": active_license.get("key", ""),
                "reason": "active",
                "checked_at": int(time.time()),
            }
            self._cached_info = info
            self._save_cache(info)
            print(f"[LicenseManager] License VALID — {days_remaining} days remaining")

            self.license_valid.emit()

            if 0 < days_remaining <= 7:
                self.license_warning.emit(days_remaining)
        else:
            # Determine best info to show in overlay
            ref = expired_license or (licenses[0] if licenses else {})
            raw_status = ref.get("status", "none") if ref else "none"

            if raw_status == "revoked":
                reason = "revoked"
                title_status = "revoked"
            elif raw_status in ("active", "expired") and ref.get("expires_at"):
                reason = "expired"
                title_status = "expired"
            else:
                reason = "no_license"
                title_status = "none"

            expires_at_str = ""
            days_expired = 0
            if ref and ref.get("_expires_dt"):
                expires_dt = ref["_expires_dt"]
                expires_at_str = expires_dt.strftime("%B %d, %Y")
                days_expired = max(0, (now - expires_dt).days)

            info = {
                "status": title_status,
                "expires_at": expires_at_str,
                "days_expired": days_expired,
                "license_type": ref.get("type", "") if ref else "",
                "license_key": ref.get("key", "") if ref else "",
                "reason": reason,
                "checked_at": int(time.time()),
            }
            self._cached_info = info
            self._save_cache(info)
            print(f"[LicenseManager] License INVALID — reason: {reason}")
            self.license_invalid.emit(info)

    def _use_cache_fallback(self):
        """Use encrypted cache when API is unreachable."""
        cached = self._load_cache()
        if cached is None:
            print("[LicenseManager] No valid cache — treating as invalid (offline)")
            info = {
                "status": "none",
                "expires_at": "",
                "days_expired": 0,
                "license_type": "",
                "license_key": "",
                "reason": "offline",
                "checked_at": 0,
            }
            self.license_invalid.emit(info)
            return

        print(f"[LicenseManager] Using cached state: {cached.get('status')} / {cached.get('reason')}")
        self._cached_info = cached
        if cached.get("status") == "active":
            self.license_valid.emit()
            days_remaining = cached.get("days_remaining", 0)
            if isinstance(days_remaining, int) and 0 < days_remaining <= 7:
                self.license_warning.emit(days_remaining)
        else:
            self.license_invalid.emit(cached)

    def _save_cache(self, data: dict):
        """Encrypt and persist license info to disk."""
        try:
            payload = json.dumps(data).encode("utf-8")
            encrypted = self._fernet.encrypt(payload)
            with open(self._cache_file, "wb") as f:
                f.write(encrypted)
        except Exception as e:
            print(f"[LicenseManager] Failed to save cache: {e}")

    def _load_cache(self) -> dict | None:
        """Decrypt and validate the local cache. Returns None if missing, expired, or tampered."""
        if not os.path.exists(self._cache_file):
            print("[LicenseManager] No cache file found")
            return None

        try:
            with open(self._cache_file, "rb") as f:
                encrypted = f.read()
            payload = self._fernet.decrypt(encrypted)
            data = json.loads(payload.decode("utf-8"))
        except InvalidToken:
            print("[LicenseManager] Cache tampered or from different machine — treating as invalid")
            # Overwrite with invalid state so app blocks until online check passes
            bad = {
                "status": "invalid",
                "expires_at": "",
                "days_expired": 0,
                "license_type": "",
                "license_key": "",
                "reason": "tampered",
                "checked_at": 0,
            }
            try:
                self._save_cache(bad)
            except Exception:
                pass
            return bad
        except Exception as e:
            print(f"[LicenseManager] Cache read error: {e}")
            return None

        # Check cache age
        checked_at = data.get("checked_at", 0)
        age = time.time() - checked_at
        if age < 0 or age > _CACHE_EXPIRY_SECONDS:
            print(f"[LicenseManager] Cache expired (age={age:.0f}s) — will require fresh check")
            return None

        return data
