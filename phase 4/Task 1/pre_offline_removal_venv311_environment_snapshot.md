# Task 3 Pre-Offline-Removal `.venv311` Environment Snapshot

## Purpose and Warning

> This is a historical snapshot of the packages actually installed in `.venv311` for the Task 3 pre-offline-removal baseline. It is not `requirements.txt`, not an endorsed minimal dependency set, and not an application lock file. It may include obsolete EasyOCR/local-embedding packages from the development environment. Do not use it to reinstall or reproduce the application unless it is separately reviewed and validated.

This file records what was installed before Task 3 verification. As documented by pip, `pip freeze` reports the installed environment; it is not a computed lockfile or dependency-solver result. The capture uses `--all` so Python 3.11 bootstrap tools such as pip and setuptools are included.

## Capture Metadata

| Field | Value |
|---|---|
| Capture UTC | `2026-10-18T12:34:57.8903546Z` |
| Capture local time | `2026-10-18T17:34:57.8968840+05:00` |
| Local time zone | `Pakistan Standard Time` |
| Environment path | `F:\Asad\Talha Projects\ai-document-analyzer\.venv311` |
| `sys.executable` | `F:\Asad\Talha Projects\ai-document-analyzer\.venv311\Scripts\python.exe` |
| Python implementation | `CPython` |
| Full Python version | `3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)]` |
| `version_info` | `[3, 11, 9, "final", 0]` |
| Machine | `AMD64` |
| Platform | `Windows-10-10.0.19045-SP0` |
| Pointer width | `64` bits |
| `sys.prefix` | `F:\Asad\Talha Projects\ai-document-analyzer\.venv311` |
| `sys.base_prefix` | `C:\Users\Asad\AppData\Local\Python\pythoncore-3.11-64` |
| Exact pip version output | `pip 24.0 from F:\Asad\Talha Projects\ai-document-analyzer\.venv311\Lib\site-packages\pip (python 3.11)` |
| Branch | `StartPhase4` |
| Commit | `5d7a7c0333af622746bcdf103a94d10233007682` |
| Repository state | Dirty (`7` porcelain entries) |
| `pip freeze --all` exit code | `0` |
| Distribution lines | `140` |
| Canonical LF payload SHA-256 | `e999ac9f193d5b46ef1cf431674da5278385f10f137ae3cd4aedfd31fdfb565f` |
| Credential-safety inspection | No credential-bearing direct URL/VCS line detected |

The exact package command was:

```powershell
& $Python -B -m pip freeze --all
```

The Python metadata capture was retried after the first inline PowerShell/Python quoting attempt failed with `NameError: name 'implementation' is not defined`. That failed attempt did not modify the environment. The successful metadata command exited `0` at `2026-10-18T12:35:16.7980904Z`.

## Exact Repository State

This dirty working tree is the tree being tested. The output below is the exact initial output from `git status --porcelain=v1 --untracked-files=all`:

````text
 D "phase 4/Task 1/gemini_vision_ocr_implementation_plan.md"
 D "phase 4/Task 1/task1_tracker.md"
?? "phase 4/Task 1/milestone1_tracker.md"
?? "phase 4/Task 1/milestone2_tracker.md"
?? "phase 4/Task 1/milestone3_tracker.md"
?? "phase 4/Task 1/plans/gemini_vision_ocr_implementation_plan.md"
?? "phase 4/Task 1/plans/post_embedding_ocr_baseline_verification_plan.md"
````

## Exact Installed-Distribution Snapshot

````text
aiohappyeyeballs==2.6.1
aiohttp==3.13.2
aiosignal==1.4.0
altgraph==0.17.5
annotated-types==0.7.0
anyio==4.12.0
attrs==25.4.0
backports.tarfile==1.2.0
cachetools==6.2.4
certifi==2025.11.12
cffi==2.0.0
charset-normalizer==3.4.4
colorama==0.4.6
cryptography==46.0.3
dataclasses-json==0.6.7
distro==1.9.0
easyocr==1.7.2
filelock==3.20.1
frozenlist==1.8.0
fsspec==2025.12.0
google-ai-generativelanguage==0.6.15
google-api-core==2.28.1
google-api-python-client==2.187.0
google-auth==2.62.0
google-auth-httplib2==0.3.0
google-genai==2.31.0
google-generativeai==0.8.6
googleapis-common-protos==1.72.0
greenlet==3.3.0
grpcio==1.76.0
grpcio-status==1.71.2
h11==0.16.0
h2==4.3.0
hpack==4.1.0
httpcore==1.0.9
httplib2==0.31.0
httpx==0.28.1
httpx-sse==0.4.3
huggingface-hub==0.36.0
hyperframe==6.1.0
idna==3.11
ImageIO==2.37.2
importlib_metadata==8.7.1
jaraco.classes==3.4.0
jaraco.context==6.0.1
jaraco.functools==4.4.0
Jinja2==3.1.6
joblib==1.5.3
jsonpatch==1.33
jsonpointer==3.0.0
keyring==25.7.0
langchain==1.2.0
langchain-classic==1.0.0
langchain-community==0.4.1
langchain-core==1.2.5
langchain-huggingface==1.2.0
langchain-qdrant==1.1.0
langchain-text-splitters==1.1.0
langgraph==1.0.5
langgraph-checkpoint==3.0.1
langgraph-prebuilt==1.0.5
langgraph-sdk==0.3.1
langsmith==0.5.0
lazy_loader==0.4
lxml==6.0.2
MarkupSafe==3.0.3
marshmallow==3.26.2
more-itertools==10.8.0
mpmath==1.3.0
multidict==6.7.0
mypy_extensions==1.1.0
networkx==3.6.1
ninja==1.13.0
numpy==1.26.4
ollama==0.6.1
opencv-python-headless==4.11.0.86
orjson==3.11.5
ormsgpack==1.12.1
packaging==25.0
pefile==2024.8.26
pillow==12.0.0
pip==24.0
portalocker==3.2.0
propcache==0.4.1
proto-plus==1.27.0
protobuf==5.29.5
pyasn1==0.6.1
pyasn1_modules==0.4.2
pyclipper==1.4.0
pycparser==2.23
pydantic==2.12.5
pydantic-settings==2.12.0
pydantic_core==2.41.5
pyinstaller==6.17.0
pyinstaller-hooks-contrib==2025.10
pyparsing==3.3.0
PyPDF2==3.0.1
PyQt6==6.10.1
PyQt6-Qt6==6.10.1
PyQt6_sip==13.10.3
python-bidi==0.6.7
python-docx==1.2.0
python-dotenv==1.2.1
pywin32==311
pywin32-ctypes==0.2.3
PyYAML==6.0.3
qdrant-client==1.16.2
regex==2025.11.3
requests==2.32.5
requests-toolbelt==1.0.0
rsa==4.9.1
safetensors==0.7.0
scikit-image==0.26.0
scikit-learn==1.8.0
scipy==1.11.4
sentence-transformers==5.2.0
setuptools==65.5.0
shapely==2.1.2
sniffio==1.3.1
SQLAlchemy==2.0.45
sympy==1.14.0
tenacity==9.1.2
threadpoolctl==3.6.0
tifffile==2025.12.20
tokenizers==0.22.1
torch==2.9.1
torchvision==0.24.1
tqdm==4.67.1
transformers==4.57.3
typing-inspect==0.9.0
typing-inspection==0.4.2
typing_extensions==4.15.0
uritemplate==4.2.0
urllib3==2.6.2
uuid_utils==0.12.0
websockets==16.1.1
xxhash==3.6.0
yarl==1.22.0
zipp==3.23.0
zstandard==0.25.0
````

## Interpretation and Limitations

- This environment can be internally consistent while still containing obsolete packages.
- Packages listed here are not necessarily active application requirements.
- In particular, the snapshot includes historical EasyOCR and local-embedding/ML packages; their presence in `.venv311` does not show that they entered the packaged artifact.
- Artifact-tree, manifest, and archive inspection determine whether an obsolete payload entered the package.
- Clean-environment validation and final Milestone 1 acceptance remain Task 13.

## Post-Execution Drift Check

Two post-execution recaptures were made: one after the initial run exposed the P6 exact-count defect, and a later one after the separately authorized fix, complete test rerun, fresh corrected build, artifact inspection, and packaged P1-P7 verification.

| Field | Initial stopped-run recapture | Latest corrected-build recapture |
|---|---|---|
| Command | `& $Python -B -m pip freeze --all` | `& $Python -B -m pip freeze --all` |
| Started/captured UTC | `2026-10-18T12:55:49.7334356Z` | `2026-10-18T17:36:24.7624543Z` |
| Finished UTC | `2026-10-18T12:55:51.2283748Z` | Result returned at `2026-10-18T17:36:24.814Z` |
| Exit code | `0` | `0` |
| Distribution lines | `140` | `140` |
| Canonical LF payload SHA-256 | `e999ac9f193d5b46ef1cf431674da5278385f10f137ae3cd4aedfd31fdfb565f` | `e999ac9f193d5b46ef1cf431674da5278385f10f137ae3cd4aedfd31fdfb565f` |
| Match with pre-execution snapshot | **Yes** | **Yes** |
| Drift rows | `0` | `0` (identical exact-output line count and canonical payload hash) |

A third reconciliation at `2026-10-19T12:02:12.7862097Z`, after the original post-reboot startup attempts, again returned exit `0`, 140 lines, and canonical LF SHA-256 `e999ac9f193d5b46ef1cf431674da5278385f10f137ae3cd4aedfd31fdfb565f`.

After the separately authorized lazy-startup correction, a further recapture at `2026-10-20T06:20:11.4591015Z` returned exit `0`, 140 lines, and the same canonical hash. The latest reconciliation at `2026-10-20T08:47:15.7301348Z` again reported CPython `3.11.9`, 140 lines, and the exact same hash. The snapshot therefore represents the unchanged Python environment used throughout both the original and correction verification segments. No package installation, upgrade, downgrade, uninstall, or prune occurred. Fresh post-correction reboot sampling and final reconciliation were completed on `2026-10-20`. The final recapture at `2026-10-20T09:21:44.5823036Z` again returned CPython `3.11.9`, 140 distribution lines, and the same canonical LF SHA-256. Task 3 is complete with no environment drift.
