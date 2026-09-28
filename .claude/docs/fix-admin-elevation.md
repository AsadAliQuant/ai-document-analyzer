# Fix: App Required Admin to Run (UAC Elevation)

**Chat reference:** Claude Code session — branch `AfterPhase2Completed`, 2026-05-31

## Problem

Users had to right-click the distributed `.exe` and choose "Run as Administrator" to launch the app. Normal double-click either failed or triggered a UAC elevation prompt.

## Root Cause

**Windows Installer Detection heuristic** — when a PyInstaller `--onefile` executable has no embedded UAC manifest, Windows analyzes the binary (a self-extracting archive) and may auto-elevate it, treating it like an installer.

The `app.spec` and `app_folder.spec` EXE() calls had no `manifest` parameter, so PyInstaller was not embedding any privilege declaration → Windows fired its heuristic.

**What was NOT the cause:**
- Local model downloads → go to `%APPDATA%`, user-writable, no admin needed
- Qdrant vector store → same, `%APPDATA%`
- Keyring → Windows Credential Manager, user-level
- The NSIS installer requiring admin → correct behavior for the installer itself, unrelated to running the already-installed exe

## Fix Applied

### 1. Created `manifest.xml` (project root)

Embeds `asInvoker` execution level — explicitly tells Windows this is not an installer and should run as the current user.

```xml
<requestedExecutionLevel level="asInvoker" uiAccess="false"/>
```

Declares support for Windows 8.1, 10, and 11 via `supportedOS` GUIDs.

### 2. Updated `app.spec` and `app_folder.spec`

Added to the `EXE()` call in both spec files:

```python
uac_admin=False,
uac_uiaccess=False,
manifest='manifest.xml',
```

## Result

After rebuilding with `build_exe.bat`, the EXE has the manifest baked in. Users can double-click it directly — no UAC prompt, no right-click required. Works on Windows 10 and 11.

## Files Changed

| File | Change |
|------|--------|
| `manifest.xml` | Created — asInvoker UAC manifest |
| `app.spec` | Added `uac_admin`, `uac_uiaccess`, `manifest` to EXE() |
| `app_folder.spec` | Same additions |
