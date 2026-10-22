"""
Startup loading overlay and ready-state helper.
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSlot, QTimer, Qt


class LoadingOverlayMixin:
    """Mixin to add loading overlay functionality to QMainWindow."""
    
    def _create_loading_overlay(self):
        """Create semi-transparent loading overlay widget."""
        self._loading_overlay = QFrame(self)
        self._loading_overlay.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 150);
                border-radius: 10px;
            }
        """)
        self._loading_overlay.setFrameShape(QFrame.Shape.StyledPanel)
        
        # Create layout for overlay
        overlay_layout = QVBoxLayout(self._loading_overlay)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Loading label
        self._loading_label = QLabel("Loading")
        self._loading_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self._loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(self._loading_label)
        
        # Hide initially
        self._loading_overlay.hide()

    def _show_loading_overlay(self, message: str = "Loading"):
        """Show the loading overlay with animated dots."""
        if not self._loading_overlay:
            return

        # Update geometry to cover entire window
        self._loading_overlay.setGeometry(self.rect())
        self._loading_overlay.raise_()
        self._loading_overlay.show()
        
        # Set base message
        self._loading_message_base = message
        self._initial_loading_message = message
        self._loading_dots = 0

        # Start animation timer
        if self._loading_timer is None:
            self._loading_timer = QTimer(self)
            self._loading_timer.timeout.connect(self._update_loading_animation)
        self._loading_timer.start(400)

    def _update_loading_animation(self):
        """Update loading animation (dots)."""
        if not self._loading_label:
            return

        # Always animate dots; if a constant base is requested, don't change the base text
        base = getattr(self, "_initial_loading_message", self._loading_message_base)
        # Cycle dots from 1..3 so at least one dot is always visible
        dots = "." * ((self._loading_dots % 3) + 1)
        self._loading_label.setText(f"{base}{dots}")
        self._loading_dots += 1

    def _hide_loading_overlay(self):
        """Hide the loading overlay."""
        if self._loading_timer:
            self._loading_timer.stop()
        if self._loading_overlay:
            self._loading_overlay.hide()
    
    def resizeEvent(self, event):
        """Handle window resize to adjust overlay."""
        super().resizeEvent(event)
        if self._loading_overlay and self._loading_overlay.isVisible():
            self._loading_overlay.setGeometry(self.rect())
    
    @pyqtSlot()
    def _on_init_finished(self):
        """Finish startup after the window has had a chance to paint."""
        self._init_in_progress = False
        
        # Hide loading overlay
        self._hide_loading_overlay()
        
        # Re-enable UI
        self.setEnabled(True)
        
        # Set ready status
        self._set_status("Ready")
