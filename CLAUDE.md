# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Document Analyzer is a PyQt6-based Windows desktop application for AI-powered document analysis. It supports both offline (Ollama) and online (Google Gemini) AI models, with OCR capabilities for image processing and RAG (Retrieval-Augmented Generation) for large documents.

## Development Environment

- **Python**: 3.11 — use `.venv311` virtual environment
- **Activate venv**: `.venv311\Scripts\activate`
- **Reference snapshot**: `ai-document-analyzer_AfterPhase2Delivered/` is a frozen backup of the Phase 2 deliverable. The active code lives in the project root, not this folder.

## Development Commands

```bash
# Run the application
python main.py

# Install dependencies
pip install -r requirements.txt

# List installed Ollama models (sanity check)
python test_mdls.py

# Batch-update all AI prompts in main_window.py
python update_all_prompts.py

# Build EXE with pre-flight checks — verifies venv + RAG imports first (RECOMMENDED)
build_exe.bat

# Build standalone EXE with NSIS installer (for client distribution)
build_complete.bat

# Build EXE without installer, no pre-checks (legacy)
build_debug.bat

# Build as folder (faster iteration, not single-file)
build_folder.bat

# Clear Qdrant vector store
clear_vector_store.bat
```

## Architecture

### Startup Flow
`main.py` sets required env flags (`KMP_DUPLICATE_LIB_OK`, `TOKENIZERS_PARALLELISM`, etc.) **before** any ML imports, then:
1. Loads `config.json` from `%APPDATA%/AI Document Analyzer/` (falls back to local `config.json`)
2. Attempts silent sign-in via stored refresh token (`auth.py`)
3. Creates `MainWindow`, shows `LoginOverlay` if not signed in

### Core Files
- `main_window.py` (~130KB) — all UI handlers, document processing, AI dispatch, Q&A chat. Inherits from `LoadingOverlayMixin` (in `startup_helper.py`) and `QMainWindow`.
- `ui_main_window.py` — PyQt6 UI definitions for the main window
- `startup_helper.py` — `InitializationWorker` (QThread worker for heavy startup) + `LoadingOverlayMixin` (animated overlay mixin for QMainWindow)
- `lock_overlay.py` — Full-screen overlay shown when the app is locked
- `login_overlay.py` / `login_dialog.py` — Login UI components

### Document Processing Pipeline
`large_doc_manager.py` (`LargeDocumentManager`):
- Runs Qdrant embedded (no server); storage at `%APPDATA%/AI Document Analyzer/vector_store/`
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- Chunking: 1200 chars, 200 char overlap; has a dependency-free fallback splitter for packaged builds
- Document keys: MD5 of `filepath::size::mtime` — re-processes only on file change

### Authentication & Licensing
- `auth.py` — `AuthState` singleton holds access token in memory; refresh token persisted in system keyring (`keyring` library, service `"ai_document_analyzer"`)
- Backend API: `https://ssma.sa/ai_api` (configurable via `API_BASE_URL` in `config.json`)
- `lock_manager.py` — `LockManager` polls a remote CSV every 60s; encrypts lock state locally with Fernet (key derived from hardcoded secret, overridable via `AI_DOC_LOCK_KEY` env var). Tampered state file defaults to LOCKED.

### AI Backends
- **Online (Gemini)**: `google-generativeai` package. Models: `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.5-flash-lite`, `gemini-flash-latest`, `gemini-flash-lite-latest`
- **Offline (Ollama)**: `ollama` Python client; requires local Ollama daemon running

### Offline Model Bootstrap
`offline_bootstrap.py` — copies bundled models from `./models/` to the user's app data dir on first run. Runtime downloads are gated by `AIDA_RUNTIME_PREFETCH=1` env var (always `0` in packaged builds).

### Settings
- `settings_window.py` / `ui_settings_window.py` — dialog for Gemini API key and language
- `config.json` — default config, copied to `%APPDATA%/AI Document Analyzer/` on first run
- `prompts.txt` / `PROMPTS_DOCUMENTATION.txt` — summarization prompt templates

## Key Patterns

### Threading Model
UI always on main thread. Background operations use `QThread` + `QObject` worker pattern:
- `InitializationWorker` (in `startup_helper.py`) — Qdrant init, offline model bootstrap
- Analysis workers and Q&A workers defined inline in `main_window.py`

### Optional Imports
`main_window.py` wraps all heavy optional dependencies in `try/except` blocks (`PyPDF2`, `python-docx`, `google.generativeai`, `ollama`, `PIL`). Never assume these are available without checking the module-level guard variable (e.g., `_ocr_available`).

### Prompt Updates
`update_all_prompts.py` is a one-shot script that does string replacement directly into `main_window.py`. Run it when you need to bulk-update prompt text across both Ollama and Gemini, English and Arabic variants.

### Language Support
English and Arabic toggled via `apply_language()` in `MainWindow`. All user-facing strings have both `_en` and `_ar` variants in `main_window.py`.

### Lock System
CSV format: A1=`1` means locked (any other value = unlocked). A2=custom message shown in `LockOverlay`. Lock state is cached locally encrypted; if decryption fails (tampered file), app stays locked.

## File Structure Notes
- `%APPDATA%/AI Document Analyzer/` — user config, vector store, offline state, `cache.txt` (encrypted lock state), app log
- `models/` — cached HuggingFace and EasyOCR models for bundling
- `assets/` — UI icons; `create_icon.py` regenerates the app icon
- `dist/` — built executable output
- `app.spec` — PyInstaller single-file build config; `app_folder.spec` — folder build variant

## Build Configuration
`app.spec` targets a single-file Windows EXE. Key concerns:
- All ML models and EasyOCR weights must be bundled as data files
- Extensive `hiddenimports` for LangChain, Qdrant, transformers, sentence-transformers
- `AIDA_RUNTIME_PREFETCH` forced to `"0"` in packaged builds via `main.py`

## Migration History
Migrated from ChromaDB/FAISS to Qdrant for Python 3.11+ compatibility. See `PYTHON_3.11_MIGRATION.md` and `QDRANT_MIGRATION.md` for details.

## Fix History
- [UAC Admin Elevation Fix](.claude/docs/fix-admin-elevation.md) — why the EXE required right-click → Run as Admin and how it was fixed (embedded `asInvoker` manifest via `manifest.xml` + `app.spec`)
