"""
Simple full-screen overlay widget for locked state.
"""
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class LockOverlay(QFrame):
    """Full-screen overlay shown when application is locked."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Grey semi-transparent background to show disabled state
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(50, 50, 50, 200);
            }
        """)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        # Setup layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        # Main lock title
        title = QLabel("Application Locked")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; background: transparent;")

        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Detailed message
        message = QLabel(
            "This application is temporarily disabled.\nPlease contact the developer to restore access."
        )
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("color: rgb(220, 220, 220); background: transparent;")

        body_font = QFont()
        body_font.setPointSize(14)
        message.setFont(body_font)
        layout.addWidget(message)

        self.hide()
    
    def show_overlay(self):
        """Show overlay covering entire parent window."""
        if self.parent():
            self.setGeometry(self.parent().rect())
            self.raise_()
            self.show()
    
    def hide_overlay(self):
        """Hide the overlay."""
        self.hide()
