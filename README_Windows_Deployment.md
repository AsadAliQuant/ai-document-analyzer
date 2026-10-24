# AI Document Analyzer — Windows Deployment

## Overview

AI Document Analyzer is a PyQt6 desktop application for Gemini-powered document summarization, RAG Q&A, exact counting, image transcription, and semantic embeddings. Gemini is the only supported AI provider. Qdrant stores document indexes locally; it is not a local AI model or offline inference provider.

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
- A Gemini API key entered through the application's Settings dialog
- Internet access and available Gemini quota for OCR, embeddings, summaries, question classification, and semantic Q&A

Exact-count calculations run locally against stored document text after Gemini classifies the question.

## Privacy and online processing

The application sends the following content to Google Gemini:

- The complete PNG/JPG/JPEG image bytes for OCR.
- Extracted document chunks for Gemini Embedding 2 indexing.
- Selected document context for summary generation.
- The current question, retrieved document passages, and applicable conversation history for semantic Q&A.
- The question text for count-versus-semantic intent classification.

Gemini generation requests automatically try `gemini-2.5-flash-lite`, then `gemini-3.1-flash-lite`, then `gemini-3.5-flash-lite` when the current model is unavailable. Authentication, quota, validation, and other client errors do not advance to another model. Gemini quota or billing rules may apply.

The following data remains local:

- Source files are read from the user's computer.
- Extracted text, ordered chunks, vectors, embedding metadata, and Qdrant files are stored under `%APPDATA%/AI Document Analyzer/vector_store/`.
- Exact-count calculations read the complete stored text locally after Gemini classifies the question.
- Unchanged Gemini-processed images can reuse their versioned local index, avoiding another OCR upload.

Local persistence does not make AI processing offline. Scanned-PDF OCR is not supported in this release. Upgraded installations may retain obsolete EasyOCR data under `%APPDATA%/AI Document Analyzer/models/easyocr/`; the application no longer loads or recreates those weights, so they may be deleted manually.

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

Before testing an AI workflow, add the Gemini API key through Settings and confirm that the computer has internet access.

## Build commands

```bat
REM Canonical one-folder build used as the NSIS installer input
build_folder.bat

REM Alternate single-file build with Gemini/Qdrant import checks
build_exe.bat

REM Alternate single-file build driven by app.spec
build_complete.bat

REM Console-enabled diagnostic single-file build
build_debug.bat
```

The canonical release path is:

```text
build_folder.bat
    → app_folder.spec
    → dist\AI Document Analyzer\
    → installer.nsi
    → AI_Document_Analyzer_Setup.exe
```

Run NSIS against `installer.nsi` only after creating the one-folder output. The retained single-file scripts do not create the NSIS installer. Build from a clean Python 3.11 environment; do not rely on a development environment merely because obsolete OCR or local-ML packages remain installed there.

## Release acceptance checklist (Task 13)

The following checks describe the later final acceptance gate; their presence here is not evidence that the clean build has already passed:

1. Install the current requirements in a clean Python 3.11 environment.
2. Run `python -m pip check` and the complete unit-test suite.
3. Build and test the canonical one-folder artifact.
4. Inspect the package for Ollama, offline bootstrap/model payloads, EasyOCR, Torch, torchvision, OpenCV, scikit-image, SciPy, scikit-learn, and obsolete OCR weights.
5. Test Gemini summary, Q&A, OCR, embeddings/RAG, exact counting, English/Arabic behavior, missing or invalid keys, no-network/timeout handling, quota, model availability, cancellation, and worker cleanup.
6. Measure artifact size and cold-start time on a clean Windows account before publishing performance claims.

Final clean-build execution, package inspection, smoke testing, and updated measurements belong to Milestone 1 Task 13.

## Output

- Canonical one-folder package and NSIS input: `dist\AI Document Analyzer\`
- NSIS installer: `AI_Document_Analyzer_Setup.exe` after compiling `installer.nsi`
- Alternate single-file package: `dist\AI Document Analyzer.exe`

## Task 3 pre-removal baseline

The following measurements were recorded on Windows 10 on October 20, 2026 as the Task 3 baseline, before the later offline-provider removal work. They must not be treated as final post-removal package measurements:

- One-folder package: 217.41 MiB (`227,968,502` bytes) across 1,576 files and 252 directories. EXE SHA-256: `4ABB0562A605DF0A3E097BD60D579E447AE12F1658BC6B820501B77F6C89EFC5`.
- Qdrant/NumPy were excluded from startup and initialized lazily on first document/RAG use.
- Genuine first packaged launch after reboot: `WaitForInputIdle` 10.636 seconds and visible Ready 11.050 seconds. Visible Ready meant the loading overlay was absent, the main window and Analyze control were enabled, and `Status: Ready` was visible.
- Five accepted warm launches: `WaitForInputIdle` median 5.420 seconds and visible-Ready median 5.472 seconds. All five reached Ready and exited normally.
- That package inspection found no EasyOCR, Hugging Face Transformers, sentence-transformers, Torch, torchvision, OpenCV, scikit-image, SciPy, scikit-learn, ImageIO, `offline_bootstrap`, or local model-weight payloads. Google Gen AI and LangChain modules containing `transformers` in their filenames were expected helper-name collisions.
- An earlier single-file measurement before SDK consolidation was 105.48 MiB, with 10.91 seconds on the first run and 5.70/6.51 seconds on subsequent runs.

These are historical development-machine measurements. Task 13 must rebuild and repeat the measurements before current performance claims are published.

## Troubleshooting

- **Gemini key missing:** add the Gemini API key in Settings, then retry.
- **Gemini key rejected:** verify the key in Google AI Studio and replace it in Settings.
- **Network failure or timeout:** internet access is required for OCR, indexing, summaries, question classification, and semantic Q&A. Check the connection and retry.
- **Quota reached:** wait for quota reset or inspect the Google API billing/quota configuration.
- **Generation models unavailable:** confirm the account can access at least one configured Flash-Lite model. The app tries Gemini 2.5, 3.1, and 3.5 Flash-Lite only for model-availability/server failures.
- **Embedding or indexing failed:** verify the key, network, and Gemini Embedding 2 access, then process the document again.
- **Qdrant initialization or storage failed:** verify that `%APPDATA%/AI Document Analyzer/` is writable and has sufficient disk space, then restart the application.
- **File extraction failed:** verify that the document is supported, readable, and not password protected.
- **No readable image text:** use an undamaged PNG/JPG/JPEG with clearer visible text.

Application data and logs are stored under `%APPDATA%/AI Document Analyzer/`.
