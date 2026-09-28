"""
Full-screen blocking overlay shown when the user's license is expired, revoked, or missing.
"""
from PyQt6.QtCore import Qt, QEvent, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class LicenseOverlay(QFrame):
    """Covers the entire window when license is invalid. Cannot be dismissed by the user."""

    logout_requested = pyqtSignal()

    def __init__(self, parent=None, support_email: str = "support@ssma.sa"):
        super().__init__(parent)
        self.support_email = support_email

        self.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 250);
            }
        """)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)
        layout.setContentsMargins(48, 48, 48, 48)

        # Lock icon
        icon_label = QLabel("🔒")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 52px; background: transparent;")
        layout.addWidget(icon_label)

        # Title — updated dynamically
        self._title_label = QLabel("License Expired")
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_label.setStyleSheet("color: #ffffff; background: transparent;")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        self._title_label.setFont(title_font)
        layout.addWidget(self._title_label)

        # Subtitle — updated dynamically
        self._subtitle_label = QLabel("Your license has expired.")
        self._subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._subtitle_label.setWordWrap(True)
        self._subtitle_label.setStyleSheet("color: #cccccc; background: transparent;")
        sub_font = QFont()
        sub_font.setPointSize(13)
        self._subtitle_label.setFont(sub_font)
        layout.addWidget(self._subtitle_label)

        # Expiry detail line — updated dynamically
        self._expiry_label = QLabel("")
        self._expiry_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._expiry_label.setWordWrap(True)
        self._expiry_label.setStyleSheet("color: #f0a050; background: transparent;")
        expiry_font = QFont()
        expiry_font.setPointSize(12)
        self._expiry_label.setFont(expiry_font)
        layout.addWidget(self._expiry_label)

        # Separator
        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: rgba(255,255,255,40);")
        layout.addWidget(sep)
        layout.addSpacing(8)

        # Support section label
        support_header = QLabel("For renewal or support, contact:")
        support_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        support_header.setStyleSheet("color: #aaaaaa; background: transparent;")
        hdr_font = QFont()
        hdr_font.setPointSize(11)
        support_header.setFont(hdr_font)
        layout.addWidget(support_header)

        # Support email — selectable
        email_label = QLabel(support_email)
        email_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        email_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        email_label.setStyleSheet("color: #f0e060; background: transparent; font-weight: bold;")
        email_font = QFont()
        email_font.setPointSize(13)
        email_label.setFont(email_font)
        layout.addWidget(email_label)

        layout.addSpacing(20)

        # Logout button
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logout_btn = QPushButton("Log Out")
        logout_btn.setFixedWidth(160)
        logout_btn.setFixedHeight(38)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #b91c1c; }
            QPushButton:pressed { background-color: #991b1b; }
        """)
        logout_btn.clicked.connect(self.logout_requested)
        btn_row.addWidget(logout_btn)
        layout.addLayout(btn_row)

        # Track parent resize
        if parent is not None:
            parent.installEventFilter(self)

        self.hide()

    def eventFilter(self, obj, event):
        if obj is self.parent() and event.type() == QEvent.Type.Resize:
            try:
                self.setGeometry(self.parent().rect())
            except Exception:
                pass
        return super().eventFilter(obj, event)

    def update_info(self, info: dict):
        """Refresh dynamic labels based on license info dict from LicenseManager."""
        status = info.get("status", "none")
        reason = info.get("reason", "")
        expires_at = info.get("expires_at", "")
        days_expired = info.get("days_expired", 0)
        license_type = info.get("license_type", "")

        # Title
        if reason == "revoked" or status == "revoked":
            self._title_label.setText("License Revoked")
        elif reason == "no_license" or status == "none":
            self._title_label.setText("No License Found")
        elif reason == "offline":
            self._title_label.setText("License Verification Failed")
        elif reason == "tampered":
            self._title_label.setText("License Data Corrupted")
        else:
            self._title_label.setText("License Expired")

        # Subtitle
        type_str = f"{'Trial' if license_type == 'trial' else 'Standard'} license" if license_type else "License"
        if reason == "revoked":
            self._subtitle_label.setText(
                f"Your {type_str} has been revoked by an administrator.\n"
                "All features are locked until a new license is assigned."
            )
        elif reason == "no_license":
            self._subtitle_label.setText(
                "No license is currently assigned to your account.\n"
                "Please contact support to get started."
            )
        elif reason == "offline":
            self._subtitle_label.setText(
                "Unable to verify your license (offline for too long).\n"
                "Please connect to the internet and restart the application."
            )
        elif reason == "tampered":
            self._subtitle_label.setText(
                "The local license data could not be read.\n"
                "Please connect to the internet to re-verify your license."
            )
        else:
            self._subtitle_label.setText(
                f"Your {type_str} has expired and all features are locked.\n"
                "Contact support to renew and restore access."
            )

        # Expiry detail line
        if expires_at and reason not in ("no_license", "offline", "tampered"):
            if days_expired > 0:
                self._expiry_label.setText(
                    f"Expired on: {expires_at}  ({days_expired} day{'s' if days_expired != 1 else ''} ago)"
                )
            else:
                self._expiry_label.setText(f"Expired on: {expires_at}")
            self._expiry_label.setVisible(True)
        else:
            self._expiry_label.setVisible(False)

    def show_overlay(self):
        """Show overlay covering the entire parent window."""
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.raise_()
        self.show()

    def hide_overlay(self):
        """Hide the overlay."""
        self.hide()
