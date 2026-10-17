# Short Summary

| ✅ | Task No. | What to do | Expected benefit | Notes |
|:---:|---:|---|---|---|
|  | 1 | Remove `torch`, `transformers`, `sentence-transformers`, EasyOCR, Ollama, SciPy, scikit-learn, and unnecessary LangChain packages | Largest EXE reduction: **~2.2 GB → 100–150 MB** | |
| ✅ | 2 | Replace local embeddings with **Gemini Embedding**, **NVIDIA free embedding**, or **Cloudflare Workers AI** | No bundled embedding model; faster startup | Replaced local embeddings with the **Gemini Embedding 2** model. |
| ✅ | 3 | Replace EasyOCR with **Gemini Vision OCR** | Removes ~150–300 MB of OCR/ML dependencies | Implemented with ordered `gemini-2.5-flash-lite` → `gemini-3.1-flash-lite` → `gemini-3.5-flash-lite` fallback for unavailable models, versioned image caching, localized errors, worker cleanup, and mocked tests. Clean packaged-build validation is tracked separately below. |
|  | 4 | Remove offline model bootstrap, validation, downloads, and Ollama startup checks | Startup could drop from **60–120s → 3–5s** | |
|  | 5 | Keep local Qdrant, but initialize it **only when a document needs RAG** | Preserves RAG with little size/startup impact | |
|  | 6 | Remove unused hidden imports, model folders, and ML data files from the PyInstaller spec | Prevents deleted libraries/models from remaining in the build | |
|  | 7 | Build with PyInstaller **one-folder (`onedir`)**, then package it with Inno Setup/NSIS | Faster launch because files are not extracted on every run | |
|  | 8 | Lazy-load Gemini, Qdrant, OCR, and document-processing modules after the UI appears | Main window opens faster | |
|  | 9 | Store config, cache, logs, and Qdrant data under `%APPDATA%` | No admin rights; fewer startup permission problems | |
| ✅ | 10 | Clean-build and measure EXE size/startup time after each major removal | Confirms which optimization provides the real improvement | Local validation complete on October 16, 2026: 33 tests passed; requirements resolve; `pip check` passed; latest one-folder build after the Gemini SDK consolidation is 217.41 MiB across 1,576 files with 7.79 s first-run input-idle startup; the earlier single-file build was 105.48 MiB with 10.91/5.70/6.51 s startup and now requires a rebuild for an updated figure. Removed OCR/ML payloads were absent. Clean-environment and clean-account acceptance remain release checks. Live API checks confirmed Gemini 2.5 and 3.5 Flash-Lite work while Gemini 3.1 returns 503 high demand; live OCR succeeds through the configured chain. |
