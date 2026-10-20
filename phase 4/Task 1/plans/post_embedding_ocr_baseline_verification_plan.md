# Task 3 — Post-Embedding/OCR Build and Performance Baseline Plan

## Context

Phase 4, Milestone 1, Task 3 establishes a fresh, reproducible baseline after the Gemini Embedding 2 and Gemini Vision OCR migrations, but before Ollama and the remaining offline-AI surface are removed.

This task is evidence gathering, not cleanup. It must show:

- Which Python interpreter and exact installed packages were used.
- Whether the current requirements resolve and the installed environment is internally consistent.
- Whether the full automated test suite passes.
- Whether a fresh canonical one-folder build succeeds.
- Whether removed EasyOCR/local-embedding payloads are absent from that package.
- Whether the packaged Gemini OCR, summary, embedding/RAG, Q&A, exact-count, and Arabic workflows work.
- The fresh package size and reproducible startup measurements.

The result is a **pre-offline-removal baseline**, not final Milestone 1 acceptance. Task 13 remains the clean-environment and final acceptance gate.

## Deliverables

Create these two evidence files under `phase 4/Task 1/` during execution:

1. `pre_offline_removal_venv311_environment_snapshot.md`
   - Exact Python and pip information.
   - Exact output of `pip freeze --all`, including every installed distribution and its pinned version or original editable/direct-reference form.
   - Repository and environment metadata tying the snapshot to this baseline.

2. `post_embedding_ocr_baseline.md`
   - Exact commands, timestamps, exit codes, results, artifact inspection, live smoke-test evidence, measurements, defects, and limitations.
   - A link to the environment snapshot.

After every required check passes, update:

- `phase 4/Task 1/milestone1_tracker.md` — mark Task 3 complete and link the evidence report.
- `README_Windows_Deployment.md` — replace or append the concise latest one-folder measurement, qualified as a local pre-removal baseline.

Generated but normally git-ignored outputs:

- `build/app_folder/`
- `dist/AI Document Analyzer/`

No production source, test, requirements, spec, build script, installer, model-cache, AppData, or frozen Phase 2 snapshot file should be changed merely to complete this verification task.

---

## Scope and Guardrails

1. Work only from the active repository root:

   ```text
   F:\Asad\Talha Projects\ai-document-analyzer
   ```

2. Do not build, test, edit, or derive results from:

   ```text
   ai-document-analyzer_AfterPhase2Delivered/
   ```

3. Preserve all existing unrelated working-tree changes. Record Git status before and after execution. Do not stage, reset, restore, rename, or delete those changes.

4. Set `PYTHONDONTWRITEBYTECODE=1` and use Python's `-B` option where applicable so verification does not create source-tree bytecode.

5. Do not install, upgrade, downgrade, uninstall, or prune packages during baseline capture. The existing `.venv311` state is part of the evidence.

6. Before invoking `build_folder.bat`, verify that PyInstaller is already installed. The batch file can install PyInstaller when it is missing; that would mutate the environment after its package snapshot and invalidate the baseline.

7. The existing `.venv311` may contain obsolete EasyOCR/local-embedding packages. Preserve and record them exactly. A successful `pip check` does not make this a clean or minimal environment.

8. Do not delete or rename source or AppData model/cache folders. Old files outside the package are context, not proof that they were bundled.

9. Use only synthetic, non-sensitive fixtures for live Gemini tests.

10. Never record the Gemini API key, authentication tokens, refresh tokens, configuration contents, request headers, usernames, SIDs, IP addresses, or Wi-Fi SSIDs. Record only states such as `Gemini key configured: yes` and `Authenticated: yes`.

11. Do not build or modify the NSIS installer. Task 3 baselines the canonical one-folder artifact consumed by the installer; installer work belongs to Milestone 3.

12. If verification exposes a production defect, record the defect and leave Task 3 incomplete. Do not silently expand Task 3 into fixing application code.

13. Preserve raw results and outliers. Do not replace failed measurements with cleaner-looking numbers or classify a warning/exclusion-name match as packaged payload without checking its full path and context.

---

# Execution Plan

## Phase 0 — Establish the Execution Context

Run the baseline from Windows PowerShell 5.1 because the canonical build is a Windows batch/PyInstaller workflow.

Initialize paths without activating the environment implicitly:

```powershell
$Repo = 'F:\Asad\Talha Projects\ai-document-analyzer'
$Python = Join-Path $Repo '.venv311\Scripts\python.exe'
$Artifact = Join-Path $Repo 'dist\AI Document Analyzer'
$BuildEvidence = Join-Path $Repo 'build\app_folder'
$env:PYTHONDONTWRITEBYTECODE = '1'

if (-not (Test-Path -LiteralPath $Python)) {
    throw 'Required Python 3.11 environment is missing: .venv311'
}
```

Capture repository identity before any other verification:

```powershell
$TaskStartedUtc = (Get-Date).ToUniversalTime().ToString('o')
$Commit = git -C "$Repo" rev-parse HEAD
$Branch = git -C "$Repo" branch --show-current
$InitialGitStatus = @(git -C "$Repo" status --porcelain=v1 --untracked-files=all)

[pscustomobject]@{
    TaskStartedUtc = $TaskStartedUtc
    Commit = $Commit
    Branch = $Branch
}
$InitialGitStatus
```

Hash the active dependency/build inputs:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath `
    (Join-Path $Repo 'requirements.txt'), `
    (Join-Path $Repo 'app_folder.spec'), `
    (Join-Path $Repo 'build_folder.bat')
```

Record in the final report:

- UTC start time.
- Branch and full commit SHA.
- Exact initial porcelain Git status in a fenced block.
- Explicit statement that this dirty or clean tree is the tree being tested.
- SHA-256 values for `requirements.txt`, `app_folder.spec`, and `build_folder.bat`.

Existing untracked/moved planning documents are not test failures. Any new unexplained source change after execution is a stop condition.

---

## Phase 1 — Save the Exact Python and Installed-Package Snapshot

### 1.1 Snapshot file

Create:

```text
phase 4/Task 1/pre_offline_removal_venv311_environment_snapshot.md
```

Begin it with this warning:

> This is a historical snapshot of the packages actually installed in `.venv311` for the Task 3 pre-offline-removal baseline. It is not `requirements.txt`, not an endorsed minimal dependency set, and not an application lock file. It may include obsolete EasyOCR/local-embedding packages from the development environment. Do not use it to reinstall or reproduce the application unless it is separately reviewed and validated.

This distinction is important: official pip behavior defines `pip freeze` as a report of what is installed, not a computed lockfile or dependency-solver result. `--all` is required on Python 3.11 to include bootstrap tools such as pip, setuptools, and wheel.

### 1.2 Capture Python, pip, and every installed distribution

Run this **before any potentially environment-changing command**:

```powershell
$CapturedUtc = (Get-Date).ToUniversalTime().ToString('o')

$PythonInfoJson = & $Python -B -c @'
import json
import platform
import struct
import sys

print(json.dumps({
    "implementation": platform.python_implementation(),
    "full_version": sys.version,
    "version_info": list(sys.version_info),
    "pointer_width_bits": struct.calcsize("P") * 8,
    "machine": platform.machine(),
    "platform": platform.platform(),
    "executable": sys.executable,
    "prefix": sys.prefix,
    "base_prefix": sys.base_prefix,
}, indent=2))
'@
$PythonInfoExit = $LASTEXITCODE

$PipVersionOutput = & $Python -B -m pip --version
$PipVersionExit = $LASTEXITCODE

$FreezeLines = @(& $Python -B -m pip freeze --all)
$FreezeExit = $LASTEXITCODE
if ($FreezeExit -ne 0) {
    throw "pip freeze --all failed with exit code $FreezeExit"
}

$FreezeText = ($FreezeLines -join "`n") + "`n"
$Sha = [System.Security.Cryptography.SHA256]::Create()
try {
    $FreezeSha256 = ([BitConverter]::ToString(
        $Sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($FreezeText))
    )).Replace('-', '').ToLowerInvariant()
} finally {
    $Sha.Dispose()
}

[pscustomobject]@{
    CapturedUtc = $CapturedUtc
    EnvironmentPath = (Get-Item -LiteralPath (Join-Path $Repo '.venv311')).FullName
    PythonInfoExit = $PythonInfoExit
    PipVersionExit = $PipVersionExit
    FreezeExit = $FreezeExit
    DistributionLines = $FreezeLines.Count
    CanonicalLfPayloadSha256 = $FreezeSha256
}
$PythonInfoJson
$PipVersionOutput
$FreezeLines
```

The package command must remain exactly:

```powershell
& $Python -B -m pip freeze --all
```

Do not replace it with:

- `pip list`
- `pip list --format=freeze`
- `pip freeze` without `--all`
- `pip-chill`
- A manually assembled list of top-level requirements

### 1.3 Snapshot Markdown structure

Write these sections in order:

1. **Purpose and warning**
2. **Capture metadata**
   - UTC timestamp and local timezone.
   - Absolute `.venv311` path.
   - `sys.executable`.
   - Python implementation and full `sys.version`.
   - `version_info`, machine, platform, and pointer width.
   - Exact `python -m pip --version` output.
   - Branch and full commit SHA.
   - Dirty/clean result.
   - `pip freeze --all` exit code, line count, and SHA-256.
3. **Exact repository state**
   - Raw `git status --porcelain=v1 --untracked-files=all` output.
4. **Exact installed-distribution snapshot**
   - Raw `$FreezeLines` output inside a four-backtick `text` fence.
5. **Interpretation and limitations**
   - The environment can be internally consistent while still containing obsolete packages.
   - Packages listed here are not necessarily active requirements.
   - Artifact inspection determines whether an obsolete payload entered the package.
   - Clean-environment validation remains Task 13.
6. **Post-execution drift check**
   - Initially marked pending, then completed in Phase 9.

Inside the raw package fence:

- Preserve the exact output order and text.
- Do not add bullets, comments, line numbers, labels, sorting, normalization, or manual pinning.
- Preserve editable, VCS, direct URL, and local `file:` lines exactly if any are emitted.
- Do not convert a direct reference into `package==version`.

### 1.4 Credential safety stop

Before saving or publishing the snapshot, inspect direct URL/VCS lines for embedded credentials.

- If no secret-bearing line exists, save the exact snapshot.
- If a line embeds a token, username/password, or secret-bearing URL, do not publish it and do not silently redact it, because redaction would make the snapshot inexact. Stop and request a secure disposition.
- Credential-free local paths and URLs remain exactly as emitted.

---

## Phase 2 — Verify Dependency Resolution, Consistency, and Imports

Do not run a real `pip install`. Use dry runs so the captured environment remains unchanged.

### 2.1 Verify current-environment resolution

```powershell
& $Python -B -m pip --disable-pip-version-check install --dry-run -r (Join-Path $Repo 'requirements.txt')
$CurrentEnvironmentResolutionExit = $LASTEXITCODE
```

Purpose: verify that the currently installed environment satisfies the active requirement ranges without changing it.

### 2.2 Verify a hypothetical fresh resolution

```powershell
& $Python -B -m pip --disable-pip-version-check install --dry-run --ignore-installed -r (Join-Path $Repo 'requirements.txt')
$FreshResolutionExit = $LASTEXITCODE
```

Purpose: ask pip whether the active ranges can resolve from the configured package index as a hypothetical fresh solve. Its `Would install` output is not the installed package snapshot and must not be described as a lock.

If package-index/network access prevents this check, record the limitation and leave Task 3 incomplete rather than replacing it with a mutating install.

### 2.3 Verify installed metadata consistency

```powershell
& $Python -B -m pip check
$PipCheckExit = $LASTEXITCODE
```

Interpretation: a zero exit proves that installed package metadata has no known broken requirements. It does not prove the environment is minimal, clean, or identical to `requirements.txt`.

### 2.4 Run the active-import smoke check

```powershell
& $Python -B -c "import PyInstaller, PyQt6, PyPDF2, docx, google.genai, langchain_core, langchain_text_splitters, numpy, qdrant_client, portalocker, PIL, cryptography, keyring, ollama; print('active build/import smoke: OK')"
$ImportSmokeExit = $LASTEXITCODE
```

Ollama is expected here because this is the pre-removal baseline.

### 2.5 Verify PyInstaller without mutating the venv

```powershell
& $Python -B -c "import PyInstaller; print(PyInstaller.__version__)"
$PyInstallerPreflightExit = $LASTEXITCODE
```

If this fails, stop before invoking `build_folder.bat`. Its fallback installation step would alter the environment and invalidate the package snapshot.

For each Phase 2 command, record:

- Exact command.
- Start and finish UTC timestamps.
- Exit code.
- Relevant raw output or a lossless attached block.
- Interpretation and limitation.

All checks must exit zero for Task 3 to pass.

---

## Phase 3 — Run the Full Current Automated Test Suite

The repository uses standard-library `unittest` discovery and has no separate test-runner configuration.

Run from the active repository root:

```powershell
Push-Location $Repo
try {
    $TestStartedUtc = (Get-Date).ToUniversalTime().ToString('o')
    $TestTimer = [Diagnostics.Stopwatch]::StartNew()
    & $Python -B -m unittest discover -s . -p 'test_*.py' -v
    $TestExit = $LASTEXITCODE
    $TestTimer.Stop()
    $TestFinishedUtc = (Get-Date).ToUniversalTime().ToString('o')
} finally {
    Pop-Location
}

[pscustomobject]@{
    StartedUtc = $TestStartedUtc
    FinishedUtc = $TestFinishedUtc
    ExitCode = $TestExit
    ElapsedSeconds = [math]::Round($TestTimer.Elapsed.TotalSeconds, 3)
}
```

Expected current test-bearing modules:

- `test_document_processing_workers.py`
- `test_gemini_embeddings.py`
- `test_gemini_fallback.py`
- `test_gemini_generation.py`
- `test_gemini_ocr.py`

`test_mdls.py` is a manual Ollama model-list utility. Discovery may import it because of its filename, but it contains no `unittest` test cases and its live probe must not be run as part of this Gemini baseline.

Record:

- Actual discovered test count; do not hard-code the result.
- Module coverage.
- Start/finish time and elapsed duration.
- Passed, failed, errored, and skipped counts.
- Full failure tracebacks if any.
- That these tests are mocked/local and do not replace the packaged live Gemini smoke tests.

An unexplained test-count change, any failure, or any error leaves Task 3 incomplete.

---

## Phase 4 — Build the Fresh Canonical One-Folder Artifact

### 4.1 Use only the supported one-folder build

The canonical command is `build_folder.bat`, which builds `app_folder.spec` and outputs:

```text
dist/AI Document Analyzer/
```

Invoke the batch file without allowing its final `pause` to block automation:

```powershell
$BuildStartedUtc = (Get-Date).ToUniversalTime().ToString('o')
$StatusBeforeBuild = @(git -C "$Repo" status --porcelain=v1 --untracked-files=all)

Push-Location $Repo
try {
    cmd.exe /d /c "call build_folder.bat < nul"
    $BuildExit = $LASTEXITCODE
} finally {
    Pop-Location
}

$BuildFinishedUtc = (Get-Date).ToUniversalTime().ToString('o')
$StatusAfterBuild = @(git -C "$Repo" status --porcelain=v1 --untracked-files=all)

[pscustomobject]@{
    StartedUtc = $BuildStartedUtc
    FinishedUtc = $BuildFinishedUtc
    ExitCode = $BuildExit
}
```

Preserve the build console output and warnings for the report.

Do not use:

- `build_exe.bat`
- `build_complete.bat`
- `build_debug.bat`
- `app.spec`
- `AI Document Analyzer.spec`
- An ad hoc PyInstaller command with different options

PyInstaller's documented one-folder shape consists of `Analysis`, `PYZ`, `EXE`, and `COLLECT`; `app_folder.spec` follows that shape. The command-line `--clean` and `--noconfirm` options remain effective when building from a spec.

### 4.2 Prove the output is fresh

Require these files:

```text
dist/AI Document Analyzer/AI Document Analyzer.exe
build/app_folder/PYZ-00.toc
build/app_folder/COLLECT-00.toc
build/app_folder/Analysis-00.toc
build/app_folder/warn-app_folder.txt
build/app_folder/PYZ-00.pyz
```

Check existence, size, and timestamp:

```powershell
$RequiredBuildEvidence = @(
    (Join-Path $Artifact 'AI Document Analyzer.exe'),
    (Join-Path $BuildEvidence 'PYZ-00.toc'),
    (Join-Path $BuildEvidence 'COLLECT-00.toc'),
    (Join-Path $BuildEvidence 'Analysis-00.toc'),
    (Join-Path $BuildEvidence 'warn-app_folder.txt'),
    (Join-Path $BuildEvidence 'PYZ-00.pyz')
)

$RequiredBuildEvidence | ForEach-Object {
    if (-not (Test-Path -LiteralPath $_)) {
        throw "Missing fresh build evidence: $_"
    }
    Get-Item -LiteralPath $_ | Select-Object FullName, Length, LastWriteTimeUtc
}
```

Every output timestamp must postdate `$BuildStartedUtc`. Otherwise reject the artifact as stale and leave Task 3 incomplete.

Record that `installer.nsi` consumes `dist\AI Document Analyzer\*`, but do not build or edit the installer.

---

## Phase 5 — Measure and Inspect the One-Folder Package

### 5.1 Record exact size and file count

Count recursive regular files only, report exact bytes first, and derive binary MiB second:

```powershell
$ArtifactFiles = @(Get-ChildItem -LiteralPath $Artifact -Recurse -Force -File)
$ArtifactDirectories = @(Get-ChildItem -LiteralPath $Artifact -Recurse -Force -Directory)
$ArtifactBytes = [long](($ArtifactFiles | Measure-Object -Property Length -Sum).Sum)
$ExePath = Join-Path $Artifact 'AI Document Analyzer.exe'

[pscustomobject]@{
    Artifact = $Artifact
    Files = $ArtifactFiles.Count
    Directories = $ArtifactDirectories.Count
    Bytes = $ArtifactBytes
    MiB = [math]::Round($ArtifactBytes / 1MB, 2)
    ExeLastWriteUtc = (Get-Item -LiteralPath $ExePath).LastWriteTimeUtc.ToString('o')
}

Get-FileHash -Algorithm SHA256 -LiteralPath $ExePath
```

Record:

- Exact bytes.
- Binary MiB (`bytes / 1MB`).
- File and directory counts.
- EXE SHA-256 and timestamp.
- The exact measurement command.

Keep the older 217.41 MiB / 1,576-file result only as a separately labeled prior local observation. Never reuse it as the new Task 3 measurement.

### 5.2 Search for removed OCR/local-embedding payloads

Use a case-insensitive candidate pattern:

```powershell
$PayloadPattern = '(?i)easyocr|sentence[_-]transformers|transformers|torch|torchvision|cv2|opencv|skimage|scipy|sklearn|imageio|offline_bootstrap|all[-_]?minilm|models--sentence|pytorch_model|model\.bin|\.(pt|pth|onnx|safetensors|ckpt)$'
```

Inspect four distinct layers.

#### Layer A — Physical artifact tree

```powershell
$PhysicalCandidates = $ArtifactFiles | ForEach-Object {
    $Relative = $_.FullName.Substring($Artifact.Length + 1)
    if ($Relative -match $PayloadPattern) { $Relative }
}
$PhysicalCandidates
```

#### Layer B — Collected external files

Search `build/app_folder/COLLECT-00.toc`.

#### Layer C — Embedded Python modules

Search `build/app_folder/PYZ-00.toc` and recursively list the executable archive:

```powershell
$ArchiveViewer = Join-Path $Repo '.venv311\Scripts\pyi-archive_viewer.exe'
$ArchiveListing = @(& $ArchiveViewer -l -r -b (Join-Path $Artifact 'AI Document Analyzer.exe'))
$ArchiveExit = $LASTEXITCODE
$ArchiveCandidates = @($ArchiveListing | Where-Object { $_ -match $PayloadPattern })
$ArchiveCandidates

[pscustomobject]@{
    ArchiveViewerExit = $ArchiveExit
    CandidateLines = $ArchiveCandidates.Count
}
```

PyInstaller documents `pyi-archive_viewer` as the inspection tool for executables/PYZ archives; `-l` logs contents, `-r` recurses, and `-b` emits a concise filename list.

#### Layer D — Analysis and warnings

Search and then read the full contents of:

- `build/app_folder/Analysis-00.toc`
- `build/app_folder/warn-app_folder.txt`

```powershell
$ManifestPaths = @(
    (Join-Path $BuildEvidence 'PYZ-00.toc'),
    (Join-Path $BuildEvidence 'COLLECT-00.toc'),
    (Join-Path $BuildEvidence 'Analysis-00.toc'),
    (Join-Path $BuildEvidence 'warn-app_folder.txt')
)

$ManifestCandidates = Select-String -LiteralPath $ManifestPaths -Pattern $PayloadPattern
$ManifestCandidates
```

### 5.3 Classify every candidate

Do not require a zero-match search. Require **zero unclassified forbidden payloads**.

Record every candidate in a table containing:

| Layer | Exact entry | Classification | Rationale | Pass/fail effect |
|---|---|---|---|---|

Use these classifications:

- `forbidden payload`
- `expected name collision`
- `exclusion-only entry`
- `warning-only entry`
- `expected dependency`

Forbidden packaged payloads include actual EasyOCR, `sentence_transformers`, Hugging Face `transformers`, Torch/torchvision, OpenCV, scikit-image, SciPy, scikit-learn, ImageIO, `offline_bootstrap`, old OCR/local-embedding model cache names, and model weight files.

Known classifications:

- `langchain_text_splitters/sentence_transformers.py` is an expected LangChain helper, not the removed `sentence-transformers` distribution.
- `google.genai._transformers`, Google SDK transformer test/data paths, and `langchain_core.documents.transformers` can be expected name collisions; classify by full module path.
- Names appearing only in `Analysis-00.toc`'s exclusion list are configured exclusions, not bundled payloads.
- A warning that an optional/excluded package is missing is not evidence it was bundled.
- A real path/module in the physical tree, `COLLECT-00.toc`, `PYZ-00.toc`, or archive listing is substantive and requires classification.
- Qdrant, NumPy, LangChain core/text splitters, and `google.genai` are expected.
- Ollama is expected in this pre-removal baseline; removing it belongs to later tasks.

Read the entire warning file and identify any missing module that could affect an active workflow.

### 5.4 Keep package and cache boundaries explicit

Read-only inventory may note whether these exist:

```text
models/
%APPDATA%/AI Document Analyzer/models/
%APPDATA%/AI Document Analyzer/vector_store/
```

Do not delete, rename, or count them as package payloads. The inspection boundary is the fresh `dist/AI Document Analyzer/` artifact and its PyInstaller manifests/archive.

---

## Phase 6 — Capture the Performance-Test Environment

Before measuring startup, capture enough context to make results comparable:

```powershell
Get-CimInstance Win32_OperatingSystem |
    Select-Object Caption, Version, BuildNumber, OSArchitecture, LastBootUpTime

Get-CimInstance Win32_Processor |
    Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed

Get-CimInstance Win32_ComputerSystem |
    Select-Object Manufacturer, Model, TotalPhysicalMemory

Get-Partition -DriveLetter 'F' | Get-Disk |
    Select-Object FriendlyName, BusType, MediaType, Size, HealthStatus

Get-Volume -DriveLetter 'F' |
    Select-Object DriveLetter, FileSystemType, Size, SizeRemaining, HealthStatus

powercfg.exe /getactivescheme

Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue |
    Select-Object BatteryStatus, EstimatedChargeRemaining

Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct -ErrorAction SilentlyContinue |
    Select-Object displayName, productState

Get-MpComputerStatus -ErrorAction SilentlyContinue |
    Select-Object AMServiceEnabled, AntivirusEnabled, RealTimeProtectionEnabled, BehaviorMonitorEnabled, AntivirusSignatureLastUpdated

$Principal = New-Object Security.Principal.WindowsPrincipal(
    [Security.Principal.WindowsIdentity]::GetCurrent()
)

[pscustomobject]@{
    Elevated = $Principal.IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator
    )
    PythonEnvironment = (Get-Item -LiteralPath (Join-Path $Repo '.venv311')).FullName
    Artifact = $Artifact
}
```

Record manually:

- AC/battery state and active power plan.
- Whether the machine was otherwise idle.
- Storage type and free space for drive `F:`.
- Antivirus product and real-time protection state; do not disable antivirus for the benchmark.
- Existing developer account versus clean account; do not record identity.
- Unelevated/elevated launch state.
- Existing/clean AppData state, including presence of config, vector store, logs, and old model directories without reading secrets.
- Authentication at launch: signed in/out and silent login observed/not observed.
- Gemini key configured: yes/no.
- Network connected: yes/no and connection type, without network identifiers.
- Artifact SHA/timestamp, commit, dirty state, display state, and any visible Windows Update/antivirus scan activity.

Use the current AppData/profile as-is and describe it accurately. Do not delete caches to manufacture a clean-account result.

---

## Phase 7 — Measure Startup with Two Separate Endpoints

### 7.1 Definitions

Measure both:

1. **Process start → `WaitForInputIdle`**
   - Automated and comparable with the previous local metric.
   - Does not prove background initialization is complete.

2. **Process start → visible Ready**
   - First video frame where the loading overlay is gone, controls are enabled, and the status visibly reads `Ready` or the Arabic equivalent.
   - Captures the user-observable application-ready state.

Never call `WaitForInputIdle` “fully ready.”

### 7.2 Sampling protocol

1. Complete the fresh build and package inspection first.
2. Save all evidence, then restart Windows normally.
3. After logging back into the same account, do not launch the packaged app before the cold sample.
4. Confirm `LastBootUpTime` reflects the restart.
5. Start screen recording at a known frame rate.
6. Record one first-after-reboot sample.
7. Let the app reach visible Ready, then close it normally.
8. Record at least three consecutive warm launches under the same conditions.
9. Retain every raw value and outlier.
10. Report the cold sample separately; calculate medians only across valid warm samples.

If the execution cannot survive/resume after reboot, a human must perform and record this checkpoint. Do not relabel a normal first launch as cold.

### 7.3 First-after-reboot command

```powershell
$Exe = Join-Path $Artifact 'AI Document Analyzer.exe'
$Label = 'cold-after-reboot-1'
$LaunchUtc = (Get-Date).ToUniversalTime().ToString('o')
$Timer = [Diagnostics.Stopwatch]::StartNew()
$Process = Start-Process -FilePath $Exe -WorkingDirectory $Artifact -PassThru
$IdleError = ''

try {
    $IdleReached = $Process.WaitForInputIdle(120000)
} catch {
    $IdleReached = $false
    $IdleError = $_.Exception.Message
}

$Timer.Stop()
$ColdInputIdle = [pscustomobject]@{
    Label = $Label
    LaunchUtc = $LaunchUtc
    ProcessId = $Process.Id
    InputIdleReached = $IdleReached
    ElapsedSeconds = [math]::Round($Timer.Elapsed.TotalSeconds, 3)
    Error = $IdleError
}

$ColdInputIdle | Format-List
Write-Host 'After visible Ready is recorded, close the app normally.'
$Process.WaitForExit()
```

### 7.4 Warm-run command and median

```powershell
function Measure-AidaInputIdle {
    param([Parameter(Mandatory=$true)][string]$Label)

    $LaunchUtc = (Get-Date).ToUniversalTime().ToString('o')
    $Timer = [Diagnostics.Stopwatch]::StartNew()
    $Process = Start-Process -FilePath $Exe -WorkingDirectory $Artifact -PassThru
    $IdleError = ''

    try {
        $IdleReached = $Process.WaitForInputIdle(120000)
    } catch {
        $IdleReached = $false
        $IdleError = $_.Exception.Message
    }

    $Timer.Stop()
    $Record = [pscustomobject]@{
        Label = $Label
        LaunchUtc = $LaunchUtc
        ProcessId = $Process.Id
        InputIdleReached = $IdleReached
        ElapsedSeconds = [math]::Round($Timer.Elapsed.TotalSeconds, 3)
        Error = $IdleError
    }

    Write-Host "$Label measured. Keep recording until visible Ready, then close the app normally."
    $Process.WaitForExit()
    $Record
}

$WarmInputIdle = @(
    Measure-AidaInputIdle -Label 'warm-1'
    Measure-AidaInputIdle -Label 'warm-2'
    Measure-AidaInputIdle -Label 'warm-3'
)

$WarmInputIdle | Format-Table -AutoSize

$SortedWarm = @($WarmInputIdle.ElapsedSeconds | Sort-Object)
$Middle = [int][math]::Floor($SortedWarm.Count / 2)
if (($SortedWarm.Count % 2) -eq 1) {
    $WarmInputIdleMedian = $SortedWarm[$Middle]
} else {
    $WarmInputIdleMedian = (
        $SortedWarm[$Middle - 1] + $SortedWarm[$Middle]
    ) / 2
}

[pscustomobject]@{
    WarmRuns = $SortedWarm.Count
    MedianSeconds = [math]::Round($WarmInputIdleMedian, 3)
}
```

If a run times out, crashes, or is disturbed:

- Preserve it as a failed/raw row.
- Add replacement runs until at least three valid warm samples exist.
- Do not delete or hide the failed row.

### 7.5 Visible-Ready measurement

For the same launches:

- `t0`: terminal/frame timestamp when `Start-Process` is issued.
- `tReady`: first frame where the overlay is gone, controls are enabled, and Ready is visible.
- Record `tReady - t0` for the cold sample and every warm sample.
- Calculate the warm median separately from the `WaitForInputIdle` median.
- If login, licensing, or lock overlays prevent Ready from being visible, mark the visible-Ready measurement incomplete rather than redefining the endpoint as “window appeared.”

Record limitations such as video frame resolution, screen-recording overhead, scheduler noise, network/silent authentication work, and the semantic weakness of `WaitForInputIdle`.

---

## Phase 8 — Run Packaged Gemini Workflow Smoke Tests

### 8.1 Create unique, synthetic fixtures outside the repository

Create a unique `%TEMP%` directory so a previous document key cannot mask a fresh OCR/embedding call.

```powershell
$RunId = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$FixtureRoot = Join-Path ([IO.Path]::GetTempPath()) "AIDA-Task3-$RunId"
[void](New-Item -ItemType Directory -Path $FixtureRoot)
$Utf8NoBom = New-Object Text.UTF8Encoding($false)

$Filler = ((1..40 | ForEach-Object {
    "Neutral chunk boundary sentence $_ describes routine baseline validation without changing the stated facts."
}) -join ' ')

$Markers = ((1..7 | ForEach-Object { 'BASELINEQUARTZ' }) -join ' ')

$EnglishText = @(
    "Task 3 synthetic multi-chunk fixture $RunId.",
    'Project Cedar has launch code ORBIT-731.',
    $Filler,
    'The review owner is Lina Haddad.',
    $Filler,
    'The retention period is 47 days.',
    'The controlled marker occurs exactly seven times on the next line.',
    $Markers
) -join "`r`n`r`n"

$EnglishPath = Join-Path $FixtureRoot "task3-multichunk-$RunId.txt"
[IO.File]::WriteAllText($EnglishPath, $EnglishText, $Utf8NoBom)

$ArabicFiller = ((1..35 | ForEach-Object {
    "هذه جملة محايدة رقم $_ لاختبار تقسيم المستند واسترجاع المعلومات من عدة مقاطع."
}) -join ' ')

$ArabicText = @(
    "مستند عربي اصطناعي لاختبار المهمة الثالثة $RunId.",
    'اسم المشروع هو مشروع النور.',
    $ArabicFiller,
    'رمز الموافقة هو قمر-٧٢.',
    $ArabicFiller,
    'مدة الاحتفاظ بالسجلات هي تسعة عشر يوماً.'
) -join "`r`n`r`n"

$ArabicPath = Join-Path $FixtureRoot "task3-arabic-$RunId.txt"
[IO.File]::WriteAllText($ArabicPath, $ArabicText, $Utf8NoBom)

Add-Type -AssemblyName System.Drawing
$ImagePath = Join-Path $FixtureRoot "task3-ocr-$RunId.png"
$Bitmap = New-Object Drawing.Bitmap 1600, 900
$Graphics = [Drawing.Graphics]::FromImage($Bitmap)
$EnglishFont = New-Object Drawing.Font 'Arial', 32
$ArabicFont = New-Object Drawing.Font 'Arial', 34
$RtlFormat = New-Object Drawing.StringFormat
$RtlFormat.FormatFlags = [Drawing.StringFormatFlags]::DirectionRightToLeft

try {
    $Graphics.Clear([Drawing.Color]::White)
    $Graphics.DrawString("TASK 3 OCR $RunId", $EnglishFont, [Drawing.Brushes]::Black, 80, 100)
    $Graphics.DrawString('Project Falcon approval code: SKY-482', $EnglishFont, [Drawing.Brushes]::Black, 80, 210)
    $Graphics.DrawString('The orchid count is three: ORCHID ORCHID ORCHID', $EnglishFont, [Drawing.Brushes]::Black, 80, 320)
    $Graphics.DrawString('رمز الموافقة العربي هو قمر-٧٢', $ArabicFont, [Drawing.Brushes]::Black, 1450, 470, $RtlFormat)
    $Bitmap.Save($ImagePath, [Drawing.Imaging.ImageFormat]::Png)
} finally {
    $RtlFormat.Dispose()
    $ArabicFont.Dispose()
    $EnglishFont.Dispose()
    $Graphics.Dispose()
    $Bitmap.Dispose()
}

[pscustomobject]@{
    FixtureRoot = $FixtureRoot
    EnglishCharacters = $EnglishText.Length
    EnglishMarkerCount = [regex]::Matches($EnglishText, '\bBASELINEQUARTZ\b').Count
    ArabicCharacters = $ArabicText.Length
}

Get-FileHash -Algorithm SHA256 -LiteralPath $EnglishPath, $ArabicPath, $ImagePath
```

Visually inspect the PNG before using it. If Arabic glyphs are malformed, replace it with a synthetic, manually verified image and record that fixture's hash.

Record fixture commands, non-sensitive descriptions, hashes, and expected facts. Do not copy API keys or personal documents into fixtures or evidence.

### 8.2 Use only the freshly packaged executable

Run:

```text
dist/AI Document Analyzer/AI Document Analyzer.exe
```

Do not substitute `python main.py` for these smoke tests.

Use the Settings UI to confirm a Gemini key is configured, but record only yes/no. Use an authenticated test account and active internet connection.

### 8.3 Smoke matrix

| ID | Workflow | Action | Required result/evidence |
|---|---|---|---|
| P1 | Packaged launch | Launch unelevated, authenticate normally, and select Online/Gemini. | Fresh artifact reaches visible Ready; record auth/key state without values. |
| P2 | Fresh OCR + indexing | Analyze the unique PNG for the first time. | Gemini image extraction/indexing runs; summary reflects `SKY-482`, three ORCHIDs, and usable image text; UI stays responsive and loading clears. |
| P3 | Cached image reuse | Re-analyze the exact same unchanged image path. | Existing image index is reused and summary succeeds. Record only what UI/cache evidence proves; if no provider telemetry exists, do not claim independently verified zero OCR calls. |
| P4 | Fresh embedding/RAG | Analyze the unique multi-chunk English TXT. | More than one chunk is stored and a Gemini summary completes, exercising fresh Gemini Embedding 2 indexing rather than an old cache. |
| P5 | Semantic Q&A | Ask `For how many days must the records be retained?` and `Who owns the review?`. | Answers identify 47 days and Lina Haddad from distinct parts of the fixture. |
| P6 | Exact counting | Ask `How many times does the word BASELINEQUARTZ appear in the document?`. | Exact-count path returns 7, matching the independently generated count. |
| P7 | Arabic | Switch UI to Arabic, analyze the Arabic TXT, then ask `ما رمز الموافقة؟` and `كم مدة الاحتفاظ بالسجلات؟`. | Summary is usable; answers include قمر-٧٢ and 19 days; RTL UI is readable; indicators clear and UI remains responsive. |

For each row record:

- UTC timestamp.
- Artifact SHA-256.
- Fixture alias and SHA-256.
- Fresh/cached precondition.
- Exact user action or question.
- Expected result.
- Observed result.
- Pass/fail.
- Error dialog/status text if applicable.
- Responsiveness and worker/loading cleanup observation.
- Provider-attribution limitation.

The current UI does not expose which configured fallback model handled a successful request. Record the successful model as `unknown from UI` unless separate provider-side evidence identifies it. Do not infer Gemini 2.5, 3.1, or 3.5 Flash-Lite from a successful request alone.

Live tests consume quota. Mocked automated tests do not replace these live tests, and live tests do not replace deterministic automated coverage.

---

## Phase 9 — Prove the Python Environment Did Not Drift

After tests, build, inspection, smoke tests, and measurements, recapture the package list:

```powershell
$FreezeLinesAfter = @(& $Python -B -m pip freeze --all)
$FreezeAfterExit = $LASTEXITCODE

$FreezeTextAfter = ($FreezeLinesAfter -join "`n") + "`n"
$ShaAfter = [System.Security.Cryptography.SHA256]::Create()
try {
    $FreezeSha256After = ([BitConverter]::ToString(
        $ShaAfter.ComputeHash([Text.Encoding]::UTF8.GetBytes($FreezeTextAfter))
    )).Replace('-', '').ToLowerInvariant()
} finally {
    $ShaAfter.Dispose()
}

$EnvironmentDrift = @(
    Compare-Object -ReferenceObject $FreezeLines -DifferenceObject $FreezeLinesAfter
)

[pscustomobject]@{
    ExitCode = $FreezeAfterExit
    DistributionLines = $FreezeLinesAfter.Count
    CanonicalLfPayloadSha256 = $FreezeSha256After
    DriftRows = $EnvironmentDrift.Count
}
$EnvironmentDrift
```

If the exit code is zero, both hashes match, and `DriftRows` is zero:

- Complete the snapshot's post-execution drift section.
- State that the snapshot represents the unchanged environment used throughout Task 3.

If the environment changed:

- Add a second, clearly labeled, fully raw post-execution snapshot.
- Document every difference.
- Leave Task 3 incomplete.
- Do not silently select either state as the definitive baseline.

---

## Phase 10 — Write the Baseline Evidence Report

Create:

```text
phase 4/Task 1/post_embedding_ocr_baseline.md
```

Use this structure:

### 1. Status and Purpose

- Overall status: `PASS`, `INCOMPLETE`, or `FAIL`.
- State that this is a pre-offline-removal baseline, not final Milestone 1 acceptance.

### 2. Repository Identity

- Branch and full commit SHA.
- Exact initial and final dirty status.
- Start/end UTC timestamps.
- Active-root confirmation.
- Hashes of requirements/build inputs.

### 3. Execution Environment

- OS/build and architecture.
- CPU/RAM/storage.
- Power/AC state.
- Antivirus state.
- Existing/clean account and AppData state.
- Elevated/unelevated state.
- Network/auth/key-configured state without secret values.
- Artifact path, timestamp, and hash.

### 4. Installed-Environment Snapshot

- Link to `pre_offline_removal_venv311_environment_snapshot.md`.
- Exact capture command.
- Python version and pip version summary.
- Package-line count and snapshot SHA-256.
- Pre/post equality result.
- Dirty-environment qualification.

### 5. Dependency and Import Verification

Table containing both resolver dry runs, `pip check`, import smoke, and PyInstaller preflight, with exact commands, times, exits, and concise raw results.

### 6. Automated Tests

- Exact discovery command.
- Actual test/module count.
- Duration and exit code.
- Passed/failed/error/skipped counts.
- Explain that `test_mdls.py` is manual.

### 7. Canonical Build

- Exact batch command.
- Start/end time and exit.
- Active spec and output.
- Freshness checks.
- Build warnings.
- Explicit installer out-of-scope note.

### 8. Artifact Size

- Exact bytes and binary MiB.
- File/directory count.
- EXE SHA and timestamp.
- Separately labeled comparison with old local observations.

### 9. Artifact Inspection

- Physical tree, `COLLECT`, `PYZ`, archive, Analysis, and warning results.
- Candidate-classification table.
- Cache-boundary explanation.

### 10. Live Packaged Smoke Matrix

- P1-P7 results.
- Fixture hashes and fresh/cached state.
- Provider/fallback attribution caveat.
- No credentials or private content.

### 11. Startup Baseline

Separate tables for:

- First-after-reboot `WaitForInputIdle`.
- Warm `WaitForInputIdle` raw rows and median.
- First-after-reboot visible Ready.
- Warm visible-Ready raw rows and median.

Include endpoint definitions and measurement method.

### 12. Limitations

At minimum:

- Dirty `.venv311` despite possible `pip check` success.
- Existing AppData/account state.
- One machine and one cold sample.
- Antivirus/network/auth variability.
- Screen-recording overhead and frame selection.
- `WaitForInputIdle` can precede actual application readiness.
- Successful fallback model is not visible in the UI.
- Live Gemini results can vary.
- Source/AppData caches were deliberately left untouched.
- Clean-environment/final acceptance remains Task 13.

### 13. Defects and Stop Conditions Encountered

Include exact reproduction/evidence and which later checks were stopped or invalidated.

### 14. Completion Checklist and Conclusion

One row per Task 3 requirement and a final status.

### 15. Exact Command Log

Every executed command in order, with exit code and timestamp. Exclude key-bearing configuration and provider request headers.

---

# Pass, Failure, and Stop Rules

## Task 3 passes only if all conditions are true

- The exact environment snapshot exists and includes Python details plus raw `pip freeze --all` output.
- The package snapshot has no embedded credential and matches the post-run recapture.
- Current and hypothetical-fresh resolver dry runs exit zero.
- `pip check`, import smoke, and PyInstaller preflight exit zero.
- Full test discovery exits zero with the expected scope or a legitimate, explained count change.
- `build_folder.bat` exits zero.
- All required output/manifests are fresh and postdate build start.
- Fresh bytes/file counts and EXE hash are recorded.
- No unclassified forbidden OCR/local-embedding payload appears in package layers.
- Build warnings contain no unresolved active-path defect.
- Packaged live smoke tests P1-P7 all pass.
- One genuine first-after-reboot startup sample is recorded.
- At least three valid warm startup samples exist.
- `WaitForInputIdle` and visible Ready are measured separately with raw values and warm medians.
- Environment/hardware/power/AV/account/AppData/auth/commit/artifact context is recorded.
- No secret or unrelated source change was introduced.

## Stop and leave Task 3 incomplete if any condition occurs

- `.venv311` or Python 3.11 is missing.
- PyInstaller is missing and the build script would install it.
- `pip freeze --all` fails.
- A direct URL line contains credentials that cannot safely be committed exactly.
- The package set drifts during execution.
- Resolver, `pip check`, imports, tests, or build fail.
- Artifact/manifests are stale or missing.
- A forbidden payload is present or a suspicious package match cannot be classified.
- A build warning indicates an active workflow may be missing.
- The packaged app crashes or fails OCR, summary, RAG, Q&A, exact count, Arabic, responsiveness, or worker/loading cleanup.
- A valid key, authentication, quota, or network is unavailable for live smoke tests.
- No genuine reboot sample can be obtained.
- Fewer than three valid warm measurements are available.
- Visible Ready cannot be observed with the defined endpoint.
- Any unexplained source-tree change appears.

Even on failure:

- Save the exact safe package snapshot.
- Save the evidence report as `INCOMPLETE` or `FAIL`.
- Include exact reproduction details and limitations.
- Do not modify production code under this task.

---

## Conditional Tracker and README Updates

Only when every required check is green:

1. Update `phase 4/Task 1/milestone1_tracker.md`:
   - Mark Task 3 complete.
   - Link `post_embedding_ocr_baseline.md`.
   - Note that the exact `.venv311` snapshot is linked from the report.
   - Preserve Task 13 as the final clean acceptance gate.

2. Update `README_Windows_Deployment.md`:
   - Replace or append the stale one-folder measurement.
   - Include exact bytes/MiB and file count.
   - Include first-after-reboot and warm startup values/median.
   - Keep `WaitForInputIdle` and visible Ready distinct.
   - Qualify machine/date/account/AppData and dirty-venv conditions.
   - Link the detailed baseline report.

If any required check is missing or failed, do not mark the tracker complete and do not publish the numbers as the latest accepted baseline. The incomplete report remains the evidence record.

---

# Final Reconciliation

Before declaring Task 3 complete:

1. Confirm the pre/post `pip freeze --all` arrays and SHA-256 values match.
2. Re-run `git status --porcelain=v1 --untracked-files=all` and compare it with the initial status plus only intended evidence/planning/documentation changes.
3. Confirm artifact and manifest timestamps postdate build start.
4. Recompute bytes/file count and ensure they exactly match the report.
5. Re-run candidate searches and ensure every match is classified.
6. Confirm every report table includes commands, timestamps, exit codes, raw evidence, and limitations.
7. Confirm the package snapshot's raw fence exactly matches the captured output, including editable/direct/local lines.
8. Search the two new Markdown files for likely Gemini keys (for example, a long token beginning with `AIza`) and credential-bearing URLs. If detected, stop publication and handle securely rather than silently weakening snapshot exactness.
9. Validate links among the tracker, report, snapshot, and README.
10. Run `git diff --check` for tracked edits and inspect untracked Markdown for malformed fences or placeholders.
11. Confirm no claim describes `.venv311` as clean merely because `pip check` passed.
12. Confirm the report does not claim installer acceptance or final Milestone 1 acceptance.
13. Mark Task 3 complete only after this reconciliation passes.

---

# Critical Files

## Files created by Task 3 execution

- `phase 4/Task 1/pre_offline_removal_venv311_environment_snapshot.md`
- `phase 4/Task 1/post_embedding_ocr_baseline.md`

## Files edited only on a complete pass

- `phase 4/Task 1/milestone1_tracker.md`
- `README_Windows_Deployment.md`

## Build and dependency inputs

- `requirements.txt`
- `build_folder.bat`
- `app_folder.spec`
- `installer.nsi` (read only, to verify it consumes the folder output)

## Runtime paths reviewed for smoke-test expectations

- `main.py`
- `main_window.py`
- `startup_helper.py`
- `large_doc_manager.py`
- `gemini_ocr.py`
- `gemini_fallback.py`

## Automated test inputs

- `test_document_processing_workers.py`
- `test_gemini_embeddings.py`
- `test_gemini_fallback.py`
- `test_gemini_generation.py`
- `test_gemini_ocr.py`

## Generated evidence inspected

- `dist/AI Document Analyzer/`
- `build/app_folder/PYZ-00.toc`
- `build/app_folder/COLLECT-00.toc`
- `build/app_folder/Analysis-00.toc`
- `build/app_folder/warn-app_folder.txt`
- `build/app_folder/PYZ-00.pyz`

## Explicitly untouched

- `ai-document-analyzer_AfterPhase2Delivered/`
- Source and AppData model caches
- Existing vector stores
- Production source/tests/requirements/specs/build scripts
- NSIS installer behavior
