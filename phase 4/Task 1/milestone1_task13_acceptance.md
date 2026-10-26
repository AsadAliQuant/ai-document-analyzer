# Phase 4 / Milestone 1 / Task 13 — Final Acceptance Evidence

## 1. Result

**Overall status: INCOMPLETE**

The clean environment, complete 73-test regression suite, canonical one-folder build, dependency/import reconciliation, package measurements, package residual inspection, packaged startup/resource smoke test, lazy-Qdrant startup check, missing-key validation, and five warm startup samples passed.

Task 13 remains open because the mandatory live packaged Gemini workflow matrix and a genuine first-after-reboot startup sample were not completed in this run. The isolated smoke profile intentionally had no Gemini key. This report does not promote the candidate as a release and does not authorize Milestone 2.

## 2. Scope and exclusions

The run covered the active repository, tests, requirements, retained build inputs, one-folder package, PyInstaller manifests/archive/warnings, packaged resources, and current/historical documentation.

The following frozen historical artifacts were deliberately excluded and were not edited, executed, or used as build guidance:

- `ai-document-analyzer_AfterPhase2Delivered/`
- `ai-document-analyzer_AfterPhase2Delivered.zip`

Local Qdrant persistence and unrelated license/lock offline-network fallback remain supported and are not offline-AI findings.

## 3. Candidate and clean environment

| Field | Value |
|---|---|
| Branch | `StartPhase4` |
| Base commit | `5d24a47adeb8f48879330644c9d15c423905ec38` |
| Candidate form | Base commit plus the documented uncommitted Task 13 remediation changes |
| Acceptance workspace | Disposable copy under `%TEMP%` |
| Python | CPython `3.11.9`, 64-bit |
| PyInstaller | `6.17.0` |
| Environment distributions | `71` |
| Environment freeze SHA-256 | `68772601de463e34b4a04a2e9b3d0aaa3be48c7f9763bf448a378a7fb46fdf0b` |

See [milestone1_task13_environment_snapshot.md](milestone1_task13_environment_snapshot.md) for dependency checks, exact input hashes, and reconciliation.

## 4. Pre-candidate remediation verified

- Removed all 47 tracked Python bytecode files from the working tree and added standard bytecode ignores. No tracked `.pyc` remains physically present.
- Declared the direct `requests` runtime dependency.
- Resolved packaged stylesheet and tray-icon paths through the PyInstaller-aware resource root.
- Added four source/frozen resource-path regression tests.
- Made the canonical batch build require CPython 3.11, PyInstaller 6.17.0, and successful runtime/application imports.
- Corrected canonical cleanup to `build/app_folder/` and `dist/AI Document Analyzer/`.
- Marked superseded planning/preference records as historical without deleting migration evidence.
- `git diff --check` reported only line-ending normalization notices and no whitespace errors.

## 5. Automated regressions

| Field | Result |
|---|---|
| Command | `.venv311\Scripts\python.exe -B -m unittest discover -s . -p "test_*.py" -v` |
| Start UTC | `2026-10-25T08:30:16.2440480Z` |
| Finish UTC | `2026-10-25T08:30:20.1508526Z` |
| unittest duration | `0.855 seconds` |
| Tests | `73` |
| Failures/errors/skips | `0 / 0 / 0` |
| Result | PASS |

The previous 69-test baseline increased by four intentionally added resource-path tests.

The passing suite supplies controlled evidence for behavior that should not be forced against a live account, including model fallback classification, quota/auth/network/timeout mapping, Gemini request timeouts, cancellation before/after calls and between embedding batches, stale-result suppression, worker/thread cleanup, exact counting, Arabic count output, OCR errors/cache behavior, and lazy document-manager initialization/retry.

## 6. Canonical build

| Field | Result |
|---|---|
| Build input | `build_folder.bat` → `app_folder.spec` |
| Start UTC | `2026-10-25T08:30:52.3040328Z` |
| Finish UTC | `2026-10-25T08:33:25.1232217Z` |
| Exit | `0` — PASS |
| Required outputs | EXE, Analysis/COLLECT/PYZ TOCs, PYZ archive, and warning file all present |

The build log included expected PyInstaller noise from optional/test-only integrations. The warning file was read completely. Relevant classifications include:

- Windows build reporting unavailable POSIX modules: harmless platform conditionals.
- `pytest`, Google SDK test helpers, mypy, IPython, rich/click CLI helpers, trio, aiohttp, optional proxy/compression packages, optional LangChain integrations, and Qdrant fastembed integrations: optional or test-only paths not used by the application.
- `transformers`: explicitly excluded optional integration; no Transformers distribution or payload was installed or packaged.
- `sentencepiece`: optional Google local-tokenizer path; not required by the cloud Gemini operations used here.
- `pycparser.lextab` / `pycparser.yacctab`: delayed CFFI parser tables; no clean import or packaged-launch failure was observed.

No warning identified a required application import missing from the clean import checks or packaged launch.

## 7. Package inspection and residual classification

Inspected layers:

1. Physical one-folder package tree.
2. Complete Analysis, COLLECT, and PYZ manifests.
3. Recursive PyInstaller archive listing.
4. Complete warning file and build output.
5. Packaged text/config/assets and source-to-package hashes.

### Forbidden payload results

Zero package files or recursive archive entries were found for:

- Ollama or offline bootstrap.
- EasyOCR.
- Torch or torchvision.
- OpenCV / `cv2`.
- scikit-image, SciPy package, scikit-learn, or ImageIO.
- MiniLM, Nomic, local model caches, or model-weight extensions (`.pt`, `.pth`, `.onnx`, `.safetensors`, `.ckpt`, model `.bin`).

Reviewed name collisions:

- `langchain_text_splitters.sentence_transformers` is a text-splitter helper module, not the `sentence-transformers` distribution or a local embedding model.
- Google Gen AI and LangChain files containing `transformers` are data/request transformation helpers, not Hugging Face Transformers.
- NumPy's `libscipy_openblas...dll` is NumPy's bundled BLAS runtime, not the SciPy Python package.
- Qdrant conversion metadata mentions optional ecosystem types; no local inference backend or model payload is present.
- Build-spec exclusions for `sentence_transformers` and `transformers` are defensive guards, not packaged features.

No forbidden or unclassified package residual survived inspection.

### Resource integrity

Source and packaged hashes matched for:

- `styles.qss`
- `config.json`
- `prompts.txt`
- `assets/app-icon-logo.jpeg`
- `assets/logo.png`

`prompts.txt` matched exactly with SHA-256 `78AA495F1DFB860F79C6F4A2AD105D15854D66DC2D5A33C8390A8E47FC40122E`.

## 8. Fresh package measurements

| Metric | Result |
|---|---|
| Exact package bytes | `205,695,825` |
| Binary MiB | `196.17 MiB` |
| Files | `1,609` |
| Directories | `274` |
| EXE bytes | `18,057,437` |
| EXE SHA-256 | `8D59BCB2D3841BD3AF32E3BEDF5843F722F70B6C78C27F321D9C15C4FA5CC0D3` |
| EXE timestamp UTC | `2026-10-25T08:33:21.3590470Z` |

Reconciliation reproduced the same values and EXE hash.

## 9. Packaged startup and UI smoke test

The fresh EXE was launched unelevated from an external temporary working directory with isolated `APPDATA` and `LOCALAPPDATA`.

Passed observations:

- Process reached a responsive `AI Document Analyzer` main window.
- Accessibility inspection found enabled `Analyze Document` and visible `Status: Ready`.
- The stylesheet loaded; the UI was not an unstyled fallback.
- Main-window and Settings icons rendered from packaged assets.
- Settings displayed only the Gemini API key and language controls; no provider, model, Ollama, or offline-AI controls appeared.
- Main UI exposed upload/paste, summary, Q&A, and settings controls without removed provider/model selectors.
- No `vector_store`, local-model, Ollama, or offline-model directory was created during startup.
- Startup process-module inspection showed neither NumPy native libraries nor a Qdrant-named module loaded, supporting lazy document-manager startup.
- Missing-key packaged flow displayed `Missing GOOGLE_API_KEY. Add it in Settings.` and returned to a responsive Ready state.
- The smoke process was terminated and no packaged process remained.

The isolated profile had `Gemini key configured: no`. No secret value was read or recorded.

A Windows `0x8001010d` faulthandler line appeared in the application log during UI Automation interaction, but the process remained responsive and continued to pass UI actions and five normal close/relaunch cycles. It is retained as an observation rather than hidden; no crash or abnormal exit occurred in the measured launches.

## 10. Startup measurements

Environment:

- Windows 10 Pro build `19045`.
- Intel Core i7-4790, 8 logical processors.
- 31.9 GiB visible RAM.
- SSD system storage, NTFS.
- Balanced power plan.
- Unelevated launch using an existing developer account and isolated application data.
- Internet connected; no network identifiers recorded.

Five warm packaged launches were measured. Visible Ready required `Status: Ready` and an enabled Analyze control.

| Run | WaitForInputIdle | Visible Ready | Responding | Exit |
|---:|---:|---:|:---:|:---:|
| 1 | 5.491 s | 5.771 s | Yes | 0 |
| 2 | 5.079 s | 5.208 s | Yes | 0 |
| 3 | 5.139 s | 5.262 s | Yes | 0 |
| 4 | 4.477 s | 4.601 s | Yes | 0 |
| 5 | 4.176 s | 4.302 s | Yes | 0 |
| **Median** | **5.079 s** | **5.208 s** |  |  |

These are warm existing-account measurements, not the mandatory first-after-reboot measurement. No genuine cold sample was claimed.

## 11. Mandatory acceptance items still open

The following required rows were not completed and prevent a PASS:

- Fresh packaged image OCR → indexing → summary using a synthetic image.
- Unchanged-image index reuse.
- Fresh multi-chunk Gemini Embedding 2 indexing and local Qdrant initialization/reuse.
- Live packaged summary and semantic Q&A over controlled separated facts.
- Live packaged deterministic `BASELINEQUARTZ` exact-count flow.
- Live packaged Arabic summary/Q&A and RTL review.
- Live invalid-key and controlled network/timeout packaged checks.
- Live packaged cancellation/cleanup observation.
- A genuine first packaged launch after a normal reboot, with proof that no earlier post-reboot launch occurred.

Mocked regressions for quota/model-unavailable/cancellation/network mappings passed, but they do not replace the plan's live safe-path workflow rows.

## 12. Reconciliation

- Freeze recapture: 71 lines, exact SHA-256 match.
- `pip check`: PASS.
- Positive imports: PASS.
- Obsolete imports: none.
- Candidate input hashes: unchanged after build.
- Package measurements and EXE hash: unchanged.
- Physical tracked bytecode present: zero.
- Packaged processes remaining: zero.
- Source/package prompt and resource hashes: matched.
- Secret-bearing values: not included in this report.

## 13. Decision

Task 13 is **INCOMPLETE**, not failed: the completed gates passed, but live Gemini credentials/workflows and post-reboot timing were not available in this coherent run.

Therefore:

- The milestone tracker remains unchecked.
- Current deployment guidance is not changed to claim final acceptance.
- Milestone 2 must not begin based on this report.
- NSIS compilation and installer install/upgrade/uninstall acceptance remain deferred to Milestone 3.
