# Phase 4 / Milestone 1 / Task 13 — Final Acceptance Evidence

## 1. Result

**Overall status: COMPLETE WITH DOCUMENTED LIMITATIONS**

The clean environment, complete 73-test regression suite, canonical one-folder build, dependency/import reconciliation, package measurements, package residual inspection, packaged startup/resource smoke test, lazy-Qdrant startup check, missing-key validation, and five warm startup samples passed.

A later installed-application session completed the live Gemini text, embedding, local-Qdrant, summary, semantic Q&A, exact-count, Arabic, image-OCR, invalid-key, controlled network-failure, index-reuse, responsiveness, and process-cleanup checks. Those results are recorded below. The installed artifact is not byte-for-byte the clean one-folder artifact documented in Sections 6–10, and a genuine first-after-reboot startup sample remains unavailable; these are retained as documented limitations rather than blockers. Task 13 is accepted complete and Milestone 2 may begin.

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

## 11. Later installed-application workflow session

On October 26–27, 2026, the NSIS-installed Windows application was exercised unelevated through Windows UI Automation using synthetic, non-sensitive fixtures and the already configured user state. No Gemini key, authentication token, request header, username, SID, or network identifier was recorded.

### Installed artifact identity

| Field | Result |
|---|---|
| Display name | `AI Document Analyzer (Testing Build)` |
| Version | `1.0.0-test` |
| Installed EXE bytes | `17,852,440` |
| Installed EXE SHA-256 | `8301D189CF9AFE61C2EF0C2D6F4DD8DB2E12F5E9A32B6881E193B12E82A85BE3` |
| Installed package | `227,921,353` bytes (`217.36 MiB`), 1,567 files, 249 directories |
| Setup EXE bytes | `66,760,700` |
| Setup EXE SHA-256 | `809FCA4DB9F9CC3AB7A5030339EC284262C5AA3AE11CAF7B2EB535E4C2379B4A` |

The installed package scan found no Ollama, EasyOCR, Torch/torchvision, OpenCV, scikit-image, SciPy package, scikit-learn, ImageIO, or model-weight payload. Reviewed Google/LangChain filename collisions were not local-AI packages. Installed hashes for `prompts.txt`, `config.json`, `styles.qss`, and both application images matched the current source resources.

### Synthetic fixtures

| Fixture | Bytes | SHA-256 |
|---|---:|---|
| `TASK13-20261026-ALPHA7.txt` | `4,242` | `5A3B2BF27F5A1EB548786ED8C3949B3F6CFDA811EF259F46E6EB8117E06AB679` |
| `TASK13-20261026-ALPHA7.png` | `18,054` | `C9C13A673277BF40BF395440586A30423E918945D8C9D3B4006737CFEAEE9636` |

### Live results

| Check | Observed result | Status |
|---|---|:---:|
| Fresh multi-chunk text indexing and summary | Completed in 8.3 seconds; status reached `Gemini - Done`; summary contained 966 characters; local Qdrant files changed at the workflow time. | PASS |
| Semantic Q&A | Correctly returned controlled facts `07:42` and `SILVER-MANGO-842`. | PASS |
| Deterministic exact count | Correctly returned 23 occurrences of `BASELINEQUARTZ`. | PASS |
| Arabic behavior | Arabic title, controls, status, and Q&A were readable; the Arabic answer returned the controlled time and phrase; accessibility text contained 130 Arabic characters. | PASS |
| Unchanged text reuse | Reanalysis completed in 5.3 seconds, consistent with local index reuse. | PASS |
| Fresh image OCR → indexing → summary | Completed in 10.5 seconds; summary contained controlled invoice code `AURORA-7319` and quantity `27`. | PASS |
| Unchanged image reuse | Reanalysis completed in 3.9 seconds, consistent with versioned index reuse. No zero-call provider claim is made without provider telemetry. | PASS |
| Invalid Gemini key | A fresh pasted-text workflow displayed `Processing Error` with `Gemini rejected the API key. Check the Gemini API key in Settings.` The synthetic invalid value was not displayed. After dismissal, status returned to Ready and the process remained responsive. Original configuration bytes were restored; the synthetic key was absent afterward. | PASS |
| Controlled Gemini network failure | The application was launched with a process-only refusing proxy while the unrelated backend host remained exempt. A fresh embedding request displayed `Gemini Embedding could not connect to the internet. Check the connection and try again.` No credential appeared, and the process remained responsive. | PASS |
| Close during active work | A fresh 250-section pasted-text analysis reached `Processing pasted text...`; normal window close exited within 15 seconds with no remaining application process. | PASS |
| Normal close after errors | Invalid-key and network-error dialogs were dismissed; normal close left zero application processes. | PASS |

Automated regressions remain the authoritative evidence for interruption checkpoints, stale-result suppression, worker/thread reference cleanup, timeout mapping, quota handling, and model-unavailability classification. The installed UI does not expose a dedicated Cancel command; closing during active processing supplied the safe live cleanup observation without logging out or destroying the saved authentication state.

### Artifact-coherence limitation

The installed application is not the clean one-folder artifact measured in Section 8:

- Clean one-folder EXE SHA-256: `8D59BCB2D3841BD3AF32E3BEDF5843F722F70B6C78C27F321D9C15C4FA5CC0D3`.
- Installed EXE SHA-256: `8301D189CF9AFE61C2EF0C2D6F4DD8DB2E12F5E9A32B6881E193B12E82A85BE3`.
- Clean one-folder size: `205,695,825` bytes; installed package size: `227,921,353` bytes.
- The clean environment resolved Qdrant `1.20.0`; the installed package contains `qdrant_client-1.16.2.dist-info` and additional packages such as `aiohttp`.

Consequently, these successful installed workflows cannot be substituted for live workflow evidence against the exact clean artifact under this plan's one-coherent-candidate requirement.

### Documented limitations

- The successful live workflow matrix was run against the installed testing build rather than the exact clean one-folder artifact.
- No genuine first packaged launch after a normal reboot was recorded.

These limitations remain explicit in the evidence but are accepted for closing Task 13. A reboot was not initiated automatically because it is disruptive and requires explicit approval.

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
- Installed negative-path configuration: original Gemini configuration restored; synthetic invalid key absent.
- Installed application processes remaining after live testing: zero.

## 13. Decision

Task 13 is **COMPLETE WITH DOCUMENTED LIMITATIONS**. Every completed clean-build gate passed, and the separately installed application passed the available live Gemini workflow and safe negative-path checks. The installed-binary mismatch and unavailable first-after-reboot sample remain recorded above and are accepted as non-blocking limitations.

Therefore:

- The milestone tracker is checked.
- Milestone 1 is complete, and Milestone 2 may begin.
- The observed installed-app results do not claim full NSIS install/upgrade/uninstall acceptance; those installer lifecycle gates remain deferred to Milestone 3.
