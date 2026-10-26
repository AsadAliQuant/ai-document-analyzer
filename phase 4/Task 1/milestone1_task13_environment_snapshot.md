# Milestone 1 Task 13 — Clean Environment Snapshot

## Status

**Captured and reconciled.** This is the disposable Python 3.11 environment used for the current Task 13 candidate. It contains no copied development environment, build output, frozen Phase 2 snapshot, or local AppData state.

## Candidate identity

| Field | Value |
|---|---|
| Branch | `StartPhase4` |
| Base commit | `5d24a47adeb8f48879330644c9d15c423905ec38` |
| Acceptance workspace | Disposable copy under `%TEMP%` |
| Frozen Phase 2 snapshot used | No — both the directory and ZIP were excluded |
| Python bytecode writes | Disabled for validation commands with `-B` |

The acceptance candidate includes the documented uncommitted Task 13 remediation changes. The source-to-isolated-copy hashes below remained stable after testing and building.

## Runtime and tooling

| Field | Observed value |
|---|---|
| OS | Windows 10 Pro, build `19045`, 64-bit |
| Python | CPython `3.11.9`, 64-bit AMD64 |
| pip | `24.0` |
| PyInstaller | `6.17.0` |
| Installed distribution lines | `71` |
| Canonical-LF `pip freeze --all` SHA-256 | `68772601de463e34b4a04a2e9b3d0aaa3be48c7f9763bf448a378a7fb46fdf0b` |

The environment was created with only the reviewed runtime requirements and `PyInstaller==6.17.0`.

Selected resolved versions:

- `PyQt6==6.11.0`
- `google-genai==2.33.0`
- `langchain-core==1.7.0`
- `langchain-text-splitters==1.1.3`
- `numpy==2.4.6`
- `qdrant-client==1.20.0`
- `requests==2.34.2`
- `PyInstaller==6.17.0`

The full freeze output was inspected during the run. It is summarized by the line count and hash rather than copied here to avoid publishing machine-local environment paths.

## Dependency and import checks

| Check | Result |
|---|---|
| Installed-state resolver dry run | Exit `0` |
| Clean-resolution dry run with `--ignore-installed` | Exit `0` |
| `python -B -m pip check` | `No broken requirements found.` |
| Positive runtime/application imports | PASS |
| Negative obsolete-import scan | PASS; no obsolete imports found |

Positive imports covered the declared runtime stack plus `auth`, Gemini fallback/gateway/OCR, the lazy document manager, startup helper, main window, and application entrypoint.

The following obsolete imports were required to be absent and were absent:

`ollama`, `easyocr`, `sentence_transformers`, `transformers`, `torch`, `torchvision`, `cv2`, `skimage`, `scipy`, `sklearn`, `imageio`, and `offline_bootstrap`.

## Candidate input hashes

| Input | SHA-256 |
|---|---|
| `requirements.txt` | `2676D4F5CB10B231C9C6DA60CC24034F5F6EFD1ABEF2521C9CDDA971FC7B1A82` |
| `build_folder.bat` | `88A584C18603A9F86A16D809A8E12003486C3C08BA6F3212D8EBDAC8E241D771` |
| `app_folder.spec` | `A58011108D81723E4DFDBA31DC00C2DAAA1C6EF0500F24E28F1D895038C96453` |
| `main.py` | `609D8B6651FFA10092D6E38671584B6BE8936BB2A7339D830E966F957EEFCE9A` |
| `main_window.py` | `AE53C4574D42459B26A5C47B6C96839FE709F127C7FF2A14326A19DA4E7691BB` |
| `prompts.txt` | `78AA495F1DFB860F79C6F4A2AD105D15854D66DC2D5A33C8390A8E47FC40122E` |
| `config.json` | `22412F9589F7C602522A01BFE2F40D730B5AD232CC529C834F2CA66E52CD8D33` |

The same hashes were obtained after the clean build. The environment was also recaptured after packaging: the freeze still contained 71 lines with the same canonical-LF SHA-256, `pip check` still passed, positive imports still passed, and the obsolete-import list remained empty.

## Secret handling

No Gemini key, authentication token, refresh token, request header, username, SID, IP address, or Wi-Fi identifier is recorded in this evidence. Only configuration state is reported where necessary.
