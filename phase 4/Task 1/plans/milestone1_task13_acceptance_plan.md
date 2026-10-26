# Phase 4 / Milestone 1 / Task 13 — Final Acceptance Plan

## Purpose

Task 13 is the final Milestone 1 gate. It proves from one clean Python 3.11 environment and one candidate commit that the active application, tests, dependencies, canonical one-folder package, and current documentation are Gemini-only. Local Qdrant remains supported, and offline license/lock network fallback is outside the removed offline-AI surface.

The existing development `.venv311` and pre-existing `dist/AI Document Analyzer/` are not acceptance evidence. The environment contains historical packages and the artifact predates the final source state.

## Deliverables

- `phase 4/Task 1/milestone1_task13_environment_snapshot.md`
- `phase 4/Task 1/milestone1_task13_acceptance.md`
- Updated tracker and current deployment guidance only after a complete pass.

Generated `build/` and `dist/` outputs remain ignored.

## Scope and exclusions

Scan active tracked source, UI, configuration, prompts, tests, requirements, all retained build inputs, installer input relationship, current/historical documentation, the backend subtree, generated tracked files, and the fresh package.

Deliberately exclude these frozen historical artifacts from active conclusions and record the exclusion:

- `ai-document-analyzer_AfterPhase2Delivered/`
- `ai-document-analyzer_AfterPhase2Delivered.zip`

Do not edit or execute the frozen snapshot. Do not remove local Qdrant or offline license/lock fallback.

## Pre-candidate remediation

Before the final run:

1. Remove tracked Python bytecode and ignore future `__pycache__`/`.pyc` files.
2. Mark superseded planning records clearly as historical.
3. Declare direct runtime dependencies, including `requests`.
4. Resolve stylesheet and icon resources through the PyInstaller-aware asset path.
5. Make `build_folder.bat` require CPython 3.11, PyInstaller 6.17.0, and required imports; it must not install packages silently.
6. Correct canonical cleanup to `build/app_folder/` and `dist/AI Document Analyzer/`.
7. Run the complete source regression suite and `git diff --check`.

No preflight run counts as final acceptance. Any source/input correction requires a fresh candidate and environment.

## Final execution

### 1. Freeze the candidate

Record branch, full commit, exact Git status, UTC start, and SHA-256 hashes for `requirements.txt`, `build_folder.bat`, `app_folder.spec`, `main.py`, `main_window.py`, `prompts.txt`, and `config.json`.

Create a disposable isolated checkout of that exact state. It must not inherit `.venv311`, `build/`, `dist/`, caches, or AppData. Set `PYTHONDONTWRITEBYTECODE=1` and use Python `-B` where applicable.

### 2. Create the clean environment

Create `.venv311` with CPython 3.11 and install only:

```text
.venv311\Scripts\python.exe -m pip install -r requirements.txt PyInstaller==6.17.0
```

Capture Python implementation/version/architecture/path, pip and PyInstaller versions, exact `pip freeze --all`, distribution count, and canonical-LF freeze SHA-256. Inspect evidence for credentials before publishing it.

Run and record:

```text
.venv311\Scripts\python.exe -B -m pip install --dry-run -r requirements.txt
.venv311\Scripts\python.exe -B -m pip install --dry-run --ignore-installed -r requirements.txt
.venv311\Scripts\python.exe -B -m pip check
```

Run positive imports for declared dependencies and active application modules. Require obsolete imports such as `ollama`, `easyocr`, `sentence_transformers`, `transformers`, `torch`, `torchvision`, `cv2`, `skimage`, `scipy`, `sklearn`, `imageio`, and `offline_bootstrap` to fail.

### 3. Classify residual scan results

Search for Ollama/offline bootstrap, removed controls and provider dispatch, EasyOCR/local embeddings, local model packages and model weights, and obsolete dependency/build entries.

Classify every hit as exactly one of:

- forbidden active behavior or payload;
- negative regression fixture;
- migration/cache-invalidation fixture;
- build exclusion guard;
- clearly marked historical evidence;
- harmless full-path module-name collision;
- unrelated license/lock network fallback.

Pass requires zero forbidden or unclassified hits, not zero raw text hits.

### 4. Run automated regressions

```text
.venv311\Scripts\python.exe -B -m unittest discover -s . -p "test_*.py" -v
```

Record start/end UTC, duration, exit code, discovered count/modules, and pass/fail/error/skip totals. Explain intentional test-count changes. Any failure, error, or unexplained skip stops acceptance.

### 5. Build the canonical artifact

```text
cmd.exe /d /c "call build_folder.bat < nul"
```

Record the complete log and require a zero exit. The EXE, `Analysis-00.toc`, `COLLECT-00.toc`, `PYZ-00.toc`, `PYZ-00.pyz`, and `warn-app_folder.txt` must all exist and postdate build start. Read the complete warning file.

`installer.nsi` consumes this one-folder output, but NSIS compilation and installer behavior remain Milestone 3 work.

### 6. Inspect and measure the package

Inspect:

1. Physical `dist/AI Document Analyzer/` tree.
2. Complete Analysis/COLLECT/PYZ manifests.
3. Recursive `pyi-archive_viewer` output.
4. Complete warnings and build log.
5. Packaged text/config resources and source-to-package hashes.

Reject real Ollama, offline-bootstrap, EasyOCR, sentence-transformers/local-model, Transformers, Torch/torchvision, OpenCV, scikit-image, SciPy/sklearn/ImageIO, MiniLM/nomic, or model-weight payloads. Review full paths before classifying LangChain/Google names containing `transformers`.

Record exact package bytes, binary MiB, file/directory counts, EXE bytes, SHA-256, and UTC timestamp. Confirm packaged `prompts.txt` matches current source.

### 7. Packaged workflow matrix

Use the fresh EXE unelevated, launched from outside the artifact directory. Use unique synthetic fixtures outside the repository and record their SHA-256 values and independently known facts/counts.

Verify:

- Visible Ready without removed controls or local-model folders.
- Packaged stylesheet and application/login/tray icons.
- Lazy Qdrant startup and one-time first-use initialization.
- Fresh image OCR, indexing, and summary.
- Unchanged-image index reuse without claiming zero OCR calls absent provider telemetry.
- Fresh multi-chunk Gemini embeddings/RAG and summary.
- Semantic Q&A over separated facts.
- Deterministic `BASELINEQUARTZ` exact counting.
- Arabic summary/Q&A and readable RTL UI.
- Missing/invalid key and controlled network/timeout handling.
- Cancellation, stale-result suppression, worker cleanup, and no orphan process.

Use mocked regressions as evidence for quota/model-unavailable cases that should not be forced against a live key.

### 8. Startup measurements

Prefer a clean/new Windows account. Record OS/build, boot time, hardware/storage, power plan, Defender state, elevation, account/AppData state, auth/key-configured state, network state, observer method, candidate commit, and EXE hash without sensitive values.

After reboot, prove no earlier packaged launch occurred. Record one genuine first-after-reboot launch and five valid warm launches. Separately measure process start to `WaitForInputIdle` and process start to visible Ready. Visible Ready requires the loading overlay absent, the main window and Analyze control enabled, and Ready status visible.

Preserve every crash, timeout, outlier, and failed observation. Never describe `WaitForInputIdle` as fully ready. A crash, hang, abnormal exit, or leaked process fails the gate.

### 9. Reconcile

Re-run `pip freeze --all`, its hash, `pip check`, positive/negative imports, residual scans, package measurements, and EXE hash. Confirm no process remains, no candidate input changed, and `git diff --check` passes. Scan evidence for secrets and identifying account/network data.

## Stop and restart rule

A confirmed residual, dependency defect, candidate-file change, test failure, stale/missing build output, forbidden package payload, packaged workflow failure, startup failure, environment drift, or artifact drift ends the attempt as `FAIL` or `INCOMPLETE`.

After a fix, preserve the failed evidence, discard the acceptance checkout/environment/artifact, freeze a new candidate, and restart from the beginning. Syntax mistakes that launch nothing may be corrected in the ledger. External authentication/network/quota unavailability leaves the task incomplete and requires a new coherent run when restored.

## Completion

Write `PASS`, `FAIL`, or `INCOMPLETE` to the acceptance report. Only on `PASS`:

- Mark Task 13 complete in `milestone1_tracker.md` and link the evidence.
- Publish final package/startup measurements in `README_Windows_Deployment.md` while retaining Task 3 as history.
- Update `CLAUDE.md` so Task 13 is no longer outstanding.
- State that Milestone 1 passed and Milestone 2 may begin.
- Explicitly defer NSIS installer acceptance to Milestone 3.
