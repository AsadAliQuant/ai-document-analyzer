# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Document Analyzer is a PyQt6-based Windows desktop application for Gemini-powered document analysis. Gemini is the only AI provider for OCR, embeddings, summaries, intent classification, and semantic Q&A. Embedded Qdrant stores document indexes locally for RAG; it is not a local inference backend.

## Development Environment

- **Python**: 3.11 — use `.venv311` virtual environment
- **Activate venv**: `.venv311\Scripts\activate`
- **Reference snapshot**: `ai-document-analyzer_AfterPhase2Delivered/` is a frozen, non-active backup of the Phase 2 deliverable. Do not edit or use it as current setup guidance; active code and build inputs live in the project root.

## Development Commands

```bash
# Run the application
python main.py

# Install dependencies
pip install -r requirements.txt

# Run the complete regression suite
python -B -m unittest discover -s . -p "test_*.py" -v

# Verify installed dependency metadata
python -B -m pip check

# Canonical one-folder build consumed by installer.nsi
build_folder.bat

# Alternate single-file build with Gemini/Qdrant import checks
build_exe.bat

# Alternate single-file build driven by app.spec
build_complete.bat

# Console-enabled diagnostic single-file build
build_debug.bat

# Clear local Qdrant vector store
clear_vector_store.bat
```

`update_all_prompts.py` is a retired compatibility entry point and does not modify source code.

## Architecture

### Startup Flow
`main.py` sets required environment flags before relevant imports, then:
1. Loads `config.json` from `%APPDATA%/AI Document Analyzer/` (falls back to local `config.json`)
2. Attempts silent sign-in via the stored refresh token (`auth.py`)
3. Creates `MainWindow`, showing `LoginOverlay` when not signed in

Qdrant is not initialized during normal startup. `MainWindow._get_large_doc_manager()` imports and constructs the document manager on first document/RAG use and reuses it afterward.

### Core Files
- `main_window.py` — UI handlers, document processing, Gemini-only feature orchestration, exact counting, and Q&A chat. Inherits from `LoadingOverlayMixin` and `QMainWindow`.
- `gemini_gateway.py` — replaceable boundary around direct Google Gen AI SDK calls, including timeout, cancellation, error mapping, model fallback, embeddings, and client cleanup. Milestone 2 replaces this transport/credential boundary without rewriting feature handlers.
- `gemini_fallback.py` — ordered generation model list and fallback classification.
- `gemini_ocr.py` — transcription-only image OCR adapter using `GeminiGateway`.
- `large_doc_manager.py` — lazy local Qdrant persistence, Gemini Embedding 2, chunking, retrieval, and complete-text storage.
- `ui_main_window.py` — PyQt6 UI definitions for the main window.
- `startup_helper.py` — lightweight startup state plus `LoadingOverlayMixin`; it does not initialize Qdrant.
- `lock_overlay.py` — full-screen overlay shown when the app is locked.
- `login_overlay.py` / `login_dialog.py` — login UI components.

### Document Processing Pipeline

`large_doc_manager.py` (`LargeDocumentManager`):
- Runs Qdrant embedded with no external server; storage is `%APPDATA%/AI Document Analyzer/vector_store/`.
- Uses `gemini-embedding-2` through `GeminiGateway` for document and query embeddings.
- Uses 1200-character chunks with 200-character overlap and a dependency-free fallback splitter for packaged builds.
- Builds document keys from MD5 of `filepath::size::mtime`; image keys also include `GEMINI_OCR_PIPELINE_VERSION`.
- Stores complete extracted text for deterministic exact-count execution.

`gemini_ocr.py`:
- Sends complete PNG/JPG/JPEG bytes through `GeminiGateway`.
- Returns transcription only; summarization remains a downstream step.
- Requires the user-configured Gemini key and internet access.
- Allows unchanged Gemini-OCR image indexes to be reused locally.

### Authentication & Licensing
- `auth.py` — `AuthState` singleton holds the access token in memory; the refresh token is persisted in the system keyring under service `"ai_document_analyzer"`.
- Backend API: `https://ssma.sa/console/api` (configurable through `API_BASE_URL` in `config.json`).
- `lock_manager.py` — polls a remote CSV every 60 seconds and encrypts the cached lock state locally with Fernet. A tampered state file defaults to locked.

### Gemini Service Boundary
- Gemini is the only supported AI provider; there is no Ollama or local inference path.
- Generation fallback order is `gemini-2.5-flash-lite` → `gemini-3.1-flash-lite` → `gemini-3.5-flash-lite`.
- Fallback advances only for model-not-found/unavailable/high-demand/server failures. Auth, quota, timeout, validation, and other client failures are mapped and returned without advancing.
- `gemini_gateway.py` owns the current direct SDK and user-key boundary. Do not bypass it when adding a Gemini request.
- Local Qdrant persistence and deterministic counting are separate from AI inference.

### Settings
- `settings_window.py` / `ui_settings_window.py` — dialog for the user-owned Gemini API key and language. Keep key ownership unchanged until Milestone 2.
- `config.json` — default config copied to `%APPDATA%/AI Document Analyzer/` on first run.
- `prompts.txt` / `PROMPTS_DOCUMENTATION.txt` — active packaged prompt reference and detailed prompt documentation.

## Key Patterns

### Threading Model
UI always runs on the main thread. Background operations use the `QThread` + `QObject` worker pattern:
- `InitializationWorker` initializes lightweight startup state only.
- Image OCR, document indexing, analysis, and Q&A run in workers defined in `main_window.py`.
- Success and error paths both terminate and clean up their worker thread.
- Gemini cancellation uses thread interruption checks in `GeminiGateway`.

### Optional and Lazy Imports
`main_window.py` wraps optional document readers such as PyPDF2 and python-docx in `try/except` blocks. `gemini_gateway.py` imports `google-genai` lazily and returns a stable SDK-missing error. `large_doc_manager.py` treats Qdrant as optional at import time and reports initialization failures when document/RAG functionality is first requested.

### Prompt Updates
`update_all_prompts.py` is a retired compatibility entry point. Edit OCR instructions in `gemini_ocr.py`; edit intent-classification, summary, and Q&A prompts in `main_window.py`; and synchronize both `PROMPTS_DOCUMENTATION.txt` and packaged `prompts.txt` manually.

### Language Support
English and Arabic are toggled through `apply_language()` in `MainWindow`. User-facing strings have English and Arabic variants in `main_window.py`.

### Lock System
CSV format: A1=`1` means locked (any other value means unlocked). A2 is the custom message shown in `LockOverlay`. Lock state is cached locally and encrypted; if decryption fails, the application stays locked. Offline/no-network wording in this subsystem refers to license or lock-state fallback, not offline AI support.

## File Structure Notes
- `%APPDATA%/AI Document Analyzer/` — user config, vector store, encrypted lock cache, app log, and possibly stale pre-migration OCR files.
- `assets/` — UI icons; `create_icon.py` regenerates the app icon.
- `dist/AI Document Analyzer/` — canonical one-folder output consumed by `installer.nsi`.
- `dist/AI Document Analyzer.exe` — alternate single-file output.

## Build Configuration
The canonical release input is `build_folder.bat` → `app_folder.spec` → `dist/AI Document Analyzer/` → `installer.nsi`.

Key concerns:
- Bundle `google-genai` for OCR, intent classification, summaries, Q&A, and embeddings.
- Bundle Qdrant, minimal LangChain text splitting, document readers, auth, keyring, and cryptography dependencies.
- Keep `sentence_transformers` and `transformers` exclusions as guards against optional transitive integrations in dirty developer environments; they do not indicate supported local ML.
- Retain `app.spec`, `AI Document Analyzer.spec`, and the single-file build scripts as alternate/diagnostic inputs until Milestone 3 consolidates packaging.
- Validate final package contents from a clean Python 3.11 environment during Milestone 1 Task 13.

## Migration History
Migrated from ChromaDB/FAISS to Qdrant, then from local embeddings/EasyOCR/Ollama to Gemini-only AI processing. `PYTHON_3.11_MIGRATION.md` and `QDRANT_MIGRATION.md` are historical migration records, not current setup instructions.

## Fix History
- [UAC Admin Elevation Fix](.claude/docs/fix-admin-elevation.md) — why the EXE required right-click → Run as Admin and how it was fixed with an embedded `asInvoker` manifest.
