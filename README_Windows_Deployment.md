# AI Document Analyzer — Windows Deployment

## Overview

AI Document Analyzer is a PyQt6 desktop application for document summarization, RAG-powered Q&A, and exact counting. It supports Google Gemini and optional Ollama generation models.

## Requirements

### Development

- Windows 10 or 11 (64-bit)
- Python 3.11
- The `.venv311` virtual environment
- Dependencies from `requirements.txt`
- PyInstaller for packaged builds
- NSIS only when creating the installer

### End users

- No Python installation for packaged builds
- A Gemini API key and internet connection for document embeddings
- A Gemini API key and internet connection for new PNG/JPG/JPEG OCR
- Ollama installed and running only when using Ollama for final summary/Q&A generation

## Privacy and online processing

- The full uploaded image is sent to Gemini 2.5 Flash-Lite for OCR. If that model is unavailable, the app tries Gemini 3.1 Flash-Lite and then Gemini 3.5 Flash-Lite.
- Extracted chunks are sent to Gemini Embedding 2 to create vectors.
- Qdrant and its vector/index files remain local under `%APPDATA%/AI Document Analyzer/vector_store/`.
- Gemini quota or billing rules may apply.
- Selecting Ollama keeps final text generation local, but new image OCR and all new document embeddings still depend on Gemini.
- Scanned-PDF OCR is not supported in this release.

Unchanged Gemini-processed images reuse their local index and do not require another OCR request. Old EasyOCR caches are left untouched and can be deleted manually from `%APPDATA%/AI Document Analyzer/models/easyocr/` if desired.

## Supported inputs

- PDF (text-based)
- DOCX
- TXT
- PNG, JPG, JPEG
- Pasted text

## Source setup

```bat
py -3.11 -m venv .venv311
.venv311\Scripts\python.exe -m pip install -r requirements.txt
.venv311\Scripts\python.exe main.py
```

Add the Gemini API key through the application's Settings dialog.

## Build commands

```bat
REM Recommended single-file build with import checks
build_exe.bat

REM One-folder build for faster packaging iteration
build_folder.bat

REM Single-file build driven by app.spec
build_complete.bat

REM Console-enabled diagnostic build
build_debug.bat
```

Build from a clean Python 3.11 environment. Do not reuse an environment merely because removed OCR/ML packages remain installed there.

## Clean-build acceptance checks

1. Install the updated requirements.
2. Run `python -m pip check`.
3. Run all unit tests.
4. Build and test the one-folder artifact.
5. Build and test the single-file artifact.
6. Confirm the output does not contain EasyOCR, Torch, torchvision, OpenCV, scikit-image, SciPy, scikit-learn, old OCR weights, or `offline_bootstrap`.
7. Test English, Arabic, mixed-language, table, blank, damaged, missing-key, invalid-key, offline, quota, and model-unavailable image cases.
8. Test PDF, DOCX, TXT, pasted text, Gemini summaries, Ollama summaries, Q&A, and exact counting.
9. Measure artifact size and cold-start time on a clean Windows account before publishing claims.

## Output

- Single-file: `dist\AI Document Analyzer.exe`
- One-folder: `dist\AI Document Analyzer\`
- Installer output depends on `installer.nsi`

## Latest local measurements

Measured on Windows 10 on October 20, 2026 from the existing `.venv311` environment:

- Current canonical one-folder package: 217.41 MiB (`227,968,502` bytes) across 1,576 files and 252 directories. EXE SHA-256: `4ABB0562A605DF0A3E097BD60D579E447AE12F1658BC6B820501B77F6C89EFC5`.
- Qdrant/NumPy are excluded from startup and initialized lazily on first document/RAG use.
- Genuine first packaged launch after reboot: `WaitForInputIdle` 10.636 seconds and visible Ready 11.050 seconds. Visible Ready means the loading overlay is absent, the main window and Analyze control are enabled, and `Status: Ready` is visible.
- Five accepted warm launches: `WaitForInputIdle` median 5.420 seconds and visible-Ready median 5.472 seconds. All five reached Ready and exited normally.
- Package inspection found no EasyOCR, Hugging Face Transformers, sentence-transformers, Torch, torchvision, OpenCV, scikit-image, SciPy, scikit-learn, ImageIO, `offline_bootstrap`, or local model-weight payloads. Google Gen AI and LangChain modules containing `transformers` in their filenames are expected helper-name collisions.
- Earlier single-file measurement before the SDK consolidation: 105.48 MiB, with 10.91 seconds on the first run and 5.70/6.51 seconds on subsequent runs. Rebuild before relying on this historical single-file figure.

These are local development-machine measurements, not clean-account or end-user benchmarks. Repeat the acceptance checks on a clean Windows account before publishing performance claims.

## Troubleshooting

- **Gemini key missing or rejected:** update the key in Settings.
- **Image OCR cannot connect or times out:** check internet access and retry.
- **Quota reached:** wait for quota reset or inspect Google API billing/quota.
- **OCR models unavailable:** verify access to at least one configured model: Gemini 2.5, 3.1, or 3.5 Flash-Lite.
- **No readable image text:** try a clearer PNG/JPG/JPEG.
- **Ollama unavailable:** install/start Ollama and select a chat model.
- **File extraction error:** verify that the document is readable and not password protected.

Application data and logs are stored under `%APPDATA%/AI Document Analyzer/`.
