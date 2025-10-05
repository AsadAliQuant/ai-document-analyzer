"""
Simple lock system that checks online status from a CSV file.
"""
import base64
import hashlib
import os
import urllib.request
from cryptography.fernet import Fernet, InvalidToken
from PyQt6.QtCore import QTimer, QObject, pyqtSignal


class LockManager(QObject):
    """Checks lock status from online CSV file every 60 seconds."""
    lock_status_changed = pyqtSignal(bool)  # True = locked, False = unlocked
    
    def __init__(self, csv_url: str, state_file: str = "lock_state.txt"):
        super().__init__()
        self.csv_url = csv_url

        # Ensure state file is in a writable location
        if not os.path.isabs(state_file):
            try:
                appdata = os.getenv("APPDATA") or os.path.expanduser("~")
                state_dir = os.path.join(appdata, "AI Document Analyzer")
                os.makedirs(state_dir, exist_ok=True)
                self.state_file = os.path.join(state_dir, state_file)
            except:
                self.state_file = state_file
        else:
            self.state_file = state_file

        self._fernet = self._init_cipher()
        self.is_locked = False
        print(f"[LockManager] State file location: {self.state_file}")

        # Load last known state
        self._load_local_state()
        
        # Setup timer to check every 6 seconds (change to 60000 for production)
        self.timer = QTimer(self)  # Parent is important for Qt objects
        self.timer.timeout.connect(self._check_lock_status)
        self.timer.start(60000)  # 60 seconds for testing (use 60000 for 60 seconds in production)
        
        # Check immediately on startup
        self._check_lock_status()
    
    def _init_cipher(self) -> Fernet:
        """Create the Fernet cipher used for encrypting lock state."""
        env_key = os.getenv("AI_DOC_LOCK_KEY", "").strip()
        if env_key:
            try:
                return Fernet(env_key.encode("utf-8"))
            except Exception as exc:
                print(f"[LockManager] Invalid env lock key, falling back to default: {exc}")

        secret = b"AI Document Analyzer Lock v1"
        default_key = base64.urlsafe_b64encode(hashlib.sha256(secret).digest())
        return Fernet(default_key)

    def _load_local_state(self):
        """Load the last known lock state from local file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "rb") as f:
                    encrypted = f.read()
                decrypted = self._fernet.decrypt(encrypted)
                value = decrypted.decode("utf-8").strip()
                self.is_locked = (value == '1')
                print(f"[LockManager] Loaded state from file: {'LOCKED' if self.is_locked else 'UNLOCKED'}")
            except InvalidToken:
                self.is_locked = True
                print("[LockManager] State file tampered or corrupted; defaulting to LOCKED")
                try:
                    self._save_local_state(True)
                except Exception as save_exc:
                    print(f"[LockManager] Failed to rewrite tampered state file: {save_exc}")
            except Exception as e:
                print(f"[LockManager] Error loading state: {e}")
                self.is_locked = False
        else:
            print("[LockManager] No previous state file found, starting unlocked")

    def _save_local_state(self, locked: bool):
        """Save the current lock state to local file."""
        try:
            value = b'1' if locked else b'0'
            encrypted = self._fernet.encrypt(value)
            with open(self.state_file, "wb") as f:
                f.write(encrypted)
            print(f"[LockManager] Saved state to file: {'LOCKED' if locked else 'UNLOCKED'}")
        except Exception as e:
            print(f"[LockManager] Error saving state: {e}")

    def _check_lock_status(self):
        """Check the CSV file for lock status."""
        try:
            print("[LockManager] Checking lock status from CSV...")

            # Create request with cache-busting headers
            import time
            cache_buster = str(int(time.time()))
            url_with_cache_bust = f"{self.csv_url}&_={cache_buster}"
            req = urllib.request.Request(url_with_cache_bust)
            req.add_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            req.add_header('Pragma', 'no-cache')
            req.add_header('Expires', '0')
            
            # Fetch CSV from URL
            with urllib.request.urlopen(req, timeout=10) as response:
                csv_data = response.read().decode('utf-8')
            
            print(f"[LockManager] Raw CSV data: {repr(csv_data[:100])}")
            
            # Get first line, first value (A1)
            lines = csv_data.strip().split('\n')
            if lines:
                first_value = lines[0].split(',')[0].strip()
                # Remove quotes if present
                first_value = first_value.strip('"').strip("'")
                new_locked = (first_value == '1')
                
                print(f"[LockManager] Parsed value: '{first_value}', Locked: {new_locked}")
                
                # Save state locally
                self._save_local_state(new_locked)
                
                # Emit signal if status changed
                if new_locked != self.is_locked:
                    self.is_locked = new_locked
                    print(f"[LockManager] *** LOCK STATUS CHANGED TO: {'LOCKED' if new_locked else 'UNLOCKED'} ***")
                    self.lock_status_changed.emit(self.is_locked)
                else:
                    print(f"[LockManager] Lock status unchanged: {'LOCKED' if self.is_locked else 'UNLOCKED'}")
        except Exception as e:
            # If offline or error, keep using last known state
            print(f"[LockManager] Error checking lock status: {e}")
            import traceback
            traceback.print_exc()
    
    def get_current_status(self) -> bool:
        """Return current lock status (True = locked)."""
        return self.is_locked
