# EXE Size and Startup Optimization Summary

## Short Summary

| Priority | What to do | Expected benefit |
|---:|---|---|
| 1 | Remove `torch`, `transformers`, `sentence-transformers`, EasyOCR, Ollama, SciPy, scikit-learn, and unnecessary LangChain packages | Largest EXE reduction: **~2.2 GB → 100–150 MB** |
| 2 | Replace local embeddings with **Gemini Embedding**, **NVIDIA free embedding**, or **Cloudflare Workers AI** | No bundled embedding model; faster startup |
| 3 | Replace EasyOCR with **Gemini Vision OCR** | Removes ~150–300 MB of OCR/ML dependencies |
| 4 | Remove offline model bootstrap, validation, downloads, and Ollama startup checks | Startup could drop from **60–120s → 3–5s** |
| 5 | Keep local Qdrant, but initialize it **only when a document needs RAG** | Preserves RAG with little size/startup impact |
| 6 | Remove unused hidden imports, model folders, and ML data files from the PyInstaller spec | Prevents deleted libraries/models from remaining in the build |
| 7 | Build with PyInstaller **one-folder (`onedir`)**, then package it with Inno Setup/NSIS | Faster launch because files are not extracted on every run |
| 8 | Lazy-load Gemini, Qdrant, OCR, and document-processing modules after the UI appears | Main window opens faster |
| 9 | Store config, cache, logs, and Qdrant data under `%APPDATA%` | No admin rights; fewer startup permission problems |
| 10 | Clean-build and measure EXE size/startup time after each major removal | Confirms which optimization provides the real improvement |

## Estimated Speed, Disk-Size, and Memory Benefits

| Priority | What to do | Main benefit | Estimated startup-speed gain | Estimated disk-size / RAM saving |
|---:|---|---|---|---|
| 1 | Remove Torch, Transformers, Sentence-Transformers, EasyOCR, Ollama, SciPy, scikit-learn, and unnecessary LangChain packages | Biggest overall improvement | **30–90 seconds faster** | **1.5–2.1 GB disk**, **500 MB–1.5 GB RAM** |
| 2 | Use Gemini, NVIDIA, or Cloudflare embeddings instead of local embeddings | Removes local embedding-model loading | **5–30 seconds faster** | **300 MB–1 GB disk**, **300 MB–1 GB RAM** |
| 3 | Replace EasyOCR with Gemini Vision | Removes the local OCR model and processing stack | **5–20 seconds faster** | **150–500 MB disk**, **200–700 MB RAM** |
| 4 | Remove offline-model bootstrap, validation, downloads, and Ollama checks | Eliminates the main startup wait | **20–60 seconds faster** | **Small disk saving**, **50–300 MB temporary RAM** |
| 5 | Keep Qdrant, but initialize it only when RAG is first used | Keeps RAG without delaying launch | **0.5–3 seconds faster** | **No disk saving**, **50–200 MB startup RAM deferred** |
| 6 | Remove unused hidden imports, model folders, and ML data from PyInstaller specs | Prevents removed dependencies from entering the build | **1–10 seconds faster** | **100 MB–2 GB disk**, depending on bundled files |
| 7 | Use PyInstaller `onedir`, packaged with Inno Setup or NSIS | Avoids extracting a large one-file EXE at every launch | **5–30 seconds faster** | Installer may be **5–15% smaller**; installed size is usually similar |
| 8 | Lazy-load Gemini, Qdrant, OCR, and document-processing modules after showing the UI | Makes the window appear quickly | **2–10 seconds faster** | **No disk saving**, **50–300 MB startup RAM deferred** |
| 9 | Store configuration, logs, cache, and Qdrant data in `%APPDATA%` | Avoids permission checks and admin-related delays | **0–2 seconds faster** | No meaningful disk or RAM reduction |
| 10 | Clean-build and measure after each major removal | Identifies remaining bottlenecks and accidentally bundled files | No direct gain | No direct saving |
| **Overall target** | Apply points 1–9 together | Lightweight online-first application | **60–120 seconds → approximately 3–5 seconds** | **2–3 GB → approximately 100–150 MB**; estimates overlap and must not be added together |

> **Note:** These are rough estimates based on the current Phase 4 plan. Several rows overlap, so their savings should not be added together. Actual results must be measured using clean builds on a typical user's PC.
