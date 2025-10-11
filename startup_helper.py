"""
Startup helper module for background initialization and loading overlay.
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer, Qt


class InitializationWorker(QObject):
    """Worker thread for heavy initialization tasks."""
    progress = pyqtSignal(str)
    finished = pyqtSignal()
    offline_progress = pyqtSignal(float, str)
    offline_state_ready = pyqtSignal(dict)
    
    def __init__(self, window):
        super().__init__()
        self.window = window
    
    @pyqtSlot()
    def run(self):
        """Perform heavy initialization in background."""
        try:
            # Step 1: Initialize language
            self.progress.emit("Initializing language")
            # Language will be applied by the main thread if needed
            
            # Step 2: Initialize document manager (heavy - loads Qdrant)
            self.progress.emit("Loading document manager")
            from large_doc_manager import LargeDocumentManager
            self.window.large_doc_manager = LargeDocumentManager(self.window.app_config_dir)
            
            # Step 2.1: Prepare offline assets (HF embeddings cache, EasyOCR weights)
            try:
                self.progress.emit("Preparing offline models")
                from offline_bootstrap import prepare_offline_assets

                def _progress_callback(percent: float, message: str) -> None:
                    self.offline_progress.emit(percent, message)

                state = prepare_offline_assets(
                    self.window.large_doc_manager.models_dir,
                    state_path=getattr(self.window, "offline_state_path", None),
                    progress_callback=_progress_callback,
                )
                self.offline_state_ready.emit(state)
            except Exception as e:
                # Non-fatal; app can still operate, but OCR/embeddings may download later if online
                print(f"Offline bootstrap warning: {e}")

            # Step 3: Initialize state variables
            self.progress.emit("Initializing state")
            self.window._qa_vector_doc_key = ""
            self.window._pending_analysis_params = None
            self.window._processing_thread = None
            self.window._processing_worker = None
            self.window._ocr_reader = None
            
            # Step 4: Set up model list
            self.progress.emit("Loading models")
            self.window.online_models_gemini = [
                "gemini-2.5-flash",
                "gemini-flash-lite-latest",
                "gemini-flash-latest",
                "gemini-2.5-pro",
                "gemini-2.5-flash-lite",
            ]    
            
            # Step 5/6: Defer any UI population and model refresh to main thread
            self.progress.emit("Loading available models")
            
            # All done
            self.progress.emit("Ready")
            
        except Exception as e:
            print(f"Initialization error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.finished.emit()


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
    
    @pyqtSlot(str)
    def _on_init_progress(self, message: str):
        """Update loading overlay with initialization progress."""
        if getattr(self, "_keep_loading_message_constant", False):
            self._loading_message_base = getattr(self, "_initial_loading_message", message)
        else:
            self._loading_message_base = message
        self._loading_dots = 0
    
    @pyqtSlot()
    def _on_init_finished(self):
        """Handle completion of background initialization."""
        print("Initialization complete")
        self._init_in_progress = False
        
        # Hide loading overlay
        self._hide_loading_overlay()
        
        # Re-enable UI
        self.setEnabled(True)
        
        # Populate model source and available models combos on the main thread
        try:
            if hasattr(self.ui, 'modelSourceCombo'):
                self.ui.modelSourceCombo.clear()
                self.ui.modelSourceCombo.addItems(["Online (Google Gemini)", "Offline (Ollama LLaMA)"])
                self.ui.modelSourceCombo.setCurrentIndex(0)
                self.ui.modelSourceCombo.setEnabled(True)
                # Ensure the signal is connected on the main thread
                try:
                    self.ui.modelSourceCombo.currentIndexChanged.connect(self.on_model_source_changed)
                except Exception:
                    pass
            if hasattr(self.ui, 'availableModelCombo'):
                self.ui.availableModelCombo.clear()
        except Exception:
            pass
        
        # Kick off initial model refresh on the main thread
        try:
            self.on_model_source_changed()
        except Exception:
            pass
        
        # Connect Q&A signals now
        try:
            self.ui.questionLineEdit.returnPressed.connect(self._send_question)
            self.ui.sendQuestionButton.clicked.connect(self._send_question)
            self.ui.clearChatButton.clicked.connect(self._clear_chat)
        except Exception as e:
            print(f"Error connecting Q&A signals: {e}")
        
        # Set ready status
        self._set_status("Ready")
