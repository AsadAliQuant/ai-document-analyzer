# Task 3 — Post-Embedding/OCR Build and Performance Baseline

## 1. Status and Purpose

**Overall status: COMPLETE — startup correction and fresh post-reboot sampling passed**

This is the pre-offline-removal baseline for Phase 4, Milestone 1, Task 3. It is not final Milestone 1 acceptance.

The original artifact exposed intermittent startup crashes while the startup worker imported Qdrant/NumPy. That failure is retained below. The authorized correction removed Qdrant/NumPy from startup and made `LargeDocumentManager` initialization lazy, locked, reusable, and retryable on first RAG use. A fresh canonical package was then built and revalidated.

All correction-segment checks that do not require another reboot now pass: 41/41 tests, dependency/import checks, unchanged 140-distribution environment, package freshness/content inspection, launch, fresh multi-chunk indexing, Gemini summary and semantic Q&A, deterministic exact count, manually confirmed fresh/cached image behavior, and Arabic summary/Q&A/RTL. Fresh post-correction reboot sampling passed without a process crash, so the Task 3 tracker and deployment README were updated with the accepted baseline.

The earlier exact-count defect and pre-correction startup failures remain in Sections 13–15 as historical evidence; they must not be confused with the current artifact.

## 2. Repository Identity

| Field | Value |
|---|---|
| Active repository root | `F:\Asad\Talha Projects\ai-document-analyzer` |
| Branch | `StartPhase4` |
| Full commit SHA | `5d7a7c0333af622746bcdf103a94d10233007682` |
| Original Task 3 start UTC | `2026-10-18T12:34:37.3582786Z` |
| Corrected-build verification segment | `2026-10-18T17:04:43.910Z` through `2026-10-18T17:37:14.8789713Z` |
| Frozen Phase 2 snapshot used | No |
| Package/environment mutation performed | No |

The original baseline began from this seven-entry dirty tree:

```text
 D "phase 4/Task 1/gemini_vision_ocr_implementation_plan.md"
 D "phase 4/Task 1/task1_tracker.md"
?? "phase 4/Task 1/milestone1_tracker.md"
?? "phase 4/Task 1/milestone2_tracker.md"
?? "phase 4/Task 1/milestone3_tracker.md"
?? "phase 4/Task 1/plans/gemini_vision_ocr_implementation_plan.md"
?? "phase 4/Task 1/plans/post_embedding_ocr_baseline_verification_plan.md"
```

After the separately authorized exact-count correction and evidence capture, the reconciliation state was:

```text
 M main_window.py
 D "phase 4/Task 1/gemini_vision_ocr_implementation_plan.md"
 D "phase 4/Task 1/task1_tracker.md"
?? "phase 4/Task 1/milestone1_tracker.md"
?? "phase 4/Task 1/milestone2_tracker.md"
?? "phase 4/Task 1/milestone3_tracker.md"
?? "phase 4/Task 1/plans/gemini_vision_ocr_implementation_plan.md"
?? "phase 4/Task 1/plans/post_embedding_ocr_baseline_verification_plan.md"
?? "phase 4/Task 1/post_embedding_ocr_baseline.md"
?? "phase 4/Task 1/pre_offline_removal_venv311_environment_snapshot.md"
?? test_question_counting.py
```

The intended additions are the evidence files and `test_question_counting.py`; `main_window.py` contains the user-authorized exact-count correction. Existing moved/untracked planning and tracker files were preserved. No unexplained source-tree change was introduced.

### Active input hashes

| Input | SHA-256 |
|---|---|
| `requirements.txt` | `154D2F392EAFACEA8BF20726939D8871E81B2A690AD6950DF6702BE7C997F629` |
| `app_folder.spec` | `CA1A7D084F0EA2BEEDEBB4791DAF4A0B338198EB6A40CC7424C3A729C274F1DE` |
| `build_folder.bat` | `439F85CC8E394DA4E16BBBFBF5A7383B748E1710B10216C2C87968D783FB4A4B` |

## 3. Execution Environment

| Field | Observed value |
|---|---|
| OS | Microsoft Windows 10 Pro, version/build `10.0.19045`, 64-bit |
| Boot time during corrected-build verification | `2026-10-18 13:46:55` local |
| Startup-sampling reboot | `2026-10-19T15:48:54.5000000+05:00` local (`2026-10-19T10:48:54.5000000Z`) |
| CPU | Intel Core i7-4790 @ 3.60 GHz, 4 cores / 8 logical processors |
| RAM | `34,260,258,816` bytes installed (about 31.9 GiB) |
| Storage | SPCC Solid State Disk, SATA, healthy, `512,110,190,592` bytes physical disk |
| `F:` volume | NTFS, healthy, `197,535,985,664` bytes total, `37,752,958,976` bytes free at final context capture |
| Power | Desktop/no battery; Balanced power plan |
| Antivirus | Windows Defender; antivirus, real-time protection, and behavior monitoring enabled |
| Elevation | Unelevated |
| Account/AppData | Existing developer account and retained AppData config/vector-store/model/cache/log state; secret-bearing contents were not recorded |
| Network | Internet connected; no network identifiers recorded |
| Authentication at packaged launch | Authenticated through existing stored state |
| Gemini key configured | Yes; value not read or recorded |
| Machine idle state | Not controlled; the user was performing other work during startup sampling |
| Artifact | `F:\Asad\Talha Projects\ai-document-analyzer\dist\AI Document Analyzer` |
| EXE timestamp UTC | `2026-10-18T17:11:43.1032346Z` |
| EXE SHA-256 | `48754E6B95E2BC933B2FC471AF34C46513854762EDC3BE1D7E2BB2E65FFDF909` |

No antivirus feature was disabled. No source/AppData model or vector-store directory was deleted or renamed.

## 4. Installed-Environment Snapshot

See [pre_offline_removal_venv311_environment_snapshot.md](pre_offline_removal_venv311_environment_snapshot.md).

| Field | Value |
|---|---|
| Exact package command | `& $Python -B -m pip freeze --all` |
| Python | CPython `3.11.9`, 64-bit |
| pip | `24.0` from `.venv311` |
| Distribution lines | `140` |
| Canonical LF snapshot SHA-256 | `e999ac9f193d5b46ef1cf431674da5278385f10f137ae3cd4aedfd31fdfb565f` |
| Credential-bearing direct reference detected | No |
| Latest recapture UTC | `2026-10-18T17:36:24.7624543Z` |
| Latest recapture | Exit `0`; 140 lines; exact SHA match |
| Environment drift | None observed |

The `.venv311` environment is non-minimal and still contains historical EasyOCR, sentence-transformers, Transformers, Torch, torchvision, OpenCV, scikit-image, SciPy, scikit-learn, and ImageIO packages. `pip check` success does not make it clean. Package/manifests determine what entered the artifact; Task 13 remains the clean-environment gate.

## 5. Dependency and Import Verification

No installation or package-changing command was run.

| Check | Exact command | Original exact execution (UTC) | Exit | Result |
|---|---|---|---:|---|
| Current environment resolution | `& $Python -B -m pip --disable-pip-version-check install --dry-run -r (Join-Path $Repo 'requirements.txt')` | `12:35:57.5333774`–`12:35:59.6869607` | 0 | Active requirements satisfied; no install performed. |
| Hypothetical fresh resolution | `& $Python -B -m pip --disable-pip-version-check install --dry-run --ignore-installed -r (Join-Path $Repo 'requirements.txt')` | `12:35:59.7071487`–`12:36:29.0638932` | 0 | Resolver emitted a `Would install ...` plan; this is not a lock or installed snapshot. |
| Installed metadata | `& $Python -B -m pip check` | `12:36:29.0658767`–`12:36:31.4689885` | 0 | `No broken requirements found.` |
| Active imports | `& $Python -B -c "import PyInstaller, PyQt6, PyPDF2, docx, google.genai, langchain_core, langchain_text_splitters, numpy, qdrant_client, portalocker, PIL, cryptography, keyring, ollama; print('active build/import smoke: OK')"` | `12:36:31.4709862`–`12:36:43.6345718` | 0 | `active build/import smoke: OK` |
| PyInstaller preflight | `& $Python -B -c "import PyInstaller; print(PyInstaller.__version__)"` | `12:36:43.6501981`–`12:36:43.9481385` | 0 | `6.17.0` |

All five checks were also rerun after the exact-count change, beginning at `2026-10-18T17:05:51.365Z` and completing by `17:07:42.713Z`. The current and hypothetical-fresh dry runs both completed, `pip check` again printed `No broken requirements found.`, imports printed `active build/import smoke: OK`, and PyInstaller reported `6.17.0`. The fresh resolver selected newer allowed versions only in its hypothetical plan; the installed environment did not change.

The first metadata command in the original segment had a PowerShell/Python quoting error (`NameError: name 'implementation' is not defined`). Its corrected read-only replacement passed and did not mutate the environment.

## 6. Automated Tests

Command:

```powershell
& $Python -B -m unittest discover -s . -p 'test_*.py' -v
```

| Field | Corrected-build result |
|---|---|
| Last reconfirmation start | `2026-10-18T17:04:43.916Z` |
| Tool result returned | `2026-10-18T17:05:13.567Z` |
| unittest reported elapsed | `13.053` seconds |
| Exit code | `0` |
| Discovered tests | `37` |
| Passed / failed / errors / skipped | `37 / 0 / 0 / 0` |

The four newly added exact-count regressions also passed independently (`4/4`), then passed in two full-suite runs. The first full post-fix run reported `37` tests in `52.191` seconds; the final reconfirmation above reported `37` in `13.053` seconds.

Covered modules:

- `test_document_processing_workers.py`
- `test_gemini_embeddings.py`
- `test_gemini_fallback.py`
- `test_gemini_generation.py`
- `test_gemini_ocr.py`
- `test_question_counting.py`

`test_mdls.py` remains a manual Ollama utility and contributes no discovered `unittest` cases. Mocked/local tests do not replace packaged live Gemini verification.

## 7. Canonical Build

The corrected package was rebuilt using the supported batch file by absolute path so the child `cmd.exe` used the intended script:

```powershell
cmd.exe /d /c "call \"F:\Asad\Talha Projects\ai-document-analyzer\build_folder.bat\" < nul"
```

| Field | Result |
|---|---|
| Started UTC | `2026-10-18T17:08:13.2876610Z` |
| Finished UTC | `2026-10-18T17:12:20.8910757Z` |
| Exit code | `0` |
| Python | `3.11.9` |
| PyInstaller | `6.17.0` |
| Spec | `app_folder.spec` |
| Output | `dist\AI Document Analyzer\` |
| Hidden imports | `1021` |
| Result | `BUILD SUCCESSFUL` |

All required outputs existed and postdated the build start. The initial freshness script incorrectly parsed the UTC comparison and displayed `AllFresh: False`; a corrected `DateTimeOffset` comparison established the following per-file results:

| Evidence | Bytes | Last write UTC | Fresh |
|---|---:|---:|---|
| `dist/AI Document Analyzer/AI Document Analyzer.exe` | 17,889,142 | `2026-10-18T17:11:43.1032346Z` | Yes |
| `build/app_folder/PYZ-00.toc` | 446,899 | `2026-10-18T17:11:23.0632103Z` | Yes |
| `build/app_folder/COLLECT-00.toc` | 311,727 | `2026-10-18T17:12:20.3760459Z` | Yes |
| `build/app_folder/Analysis-00.toc` | 1,076,661 | `2026-10-18T17:11:20.8429300Z` | Yes |
| `build/app_folder/warn-app_folder.txt` | 51,134 | `2026-10-18T17:11:20.1556226Z` | Yes |
| `build/app_folder/PYZ-00.pyz` | 17,574,177 | `2026-10-18T17:11:22.9922246Z` | Yes |

Build notices included the Google Gen AI test-submodule collection warning because `pytest` is absent, missing hidden import `tzdata`, NumPy `array_api` experimental warnings, and many platform-specific/optional/test entries. The full warning file was reviewed. No warning was identified as an unresolved dependency for the exercised Gemini generation, OCR, Gemini Embedding 2/Qdrant, document reading, authentication, or keyring workflows.

`installer.nsi` consumes `dist\AI Document Analyzer\*`. It was read only; the installer was not built or modified.

## 8. Artifact Size

The artifact was measured by recursively enumerating regular files and directories, summing file `Length`, and dividing exact bytes by `1MB` (1,048,576 bytes).

| Metric | Fresh corrected-build result |
|---|---:|
| Exact bytes | `227,967,668` |
| Binary MiB | `217.41` |
| Files | `1,576` |
| Directories | `252` |
| EXE bytes | `17,889,142` |
| EXE SHA-256 | `48754E6B95E2BC933B2FC471AF34C46513854762EDC3BE1D7E2BB2E65FFDF909` |
| EXE timestamp UTC | `2026-10-18T17:11:43.1032346Z` |
| Final recomputation UTC | `2026-10-18T17:36:30.5207996Z` |

The earlier local observation was 217.41 MiB / 1,576 files. The pre-lazy corrected build happened to match those rounded/count values, but its exact bytes, EXE size, hash, and timestamps were independently captured. The accepted current lazy-startup artifact is documented separately in Section 13A and is now published in the deployment README after successful startup acceptance.

## 9. Artifact Inspection

Candidate pattern:

```text
(?i)easyocr|sentence[_-]transformers|transformers|torch|torchvision|cv2|opencv|skimage|scipy|sklearn|imageio|offline_bootstrap|all[-_]?minilm|models--sentence|pytorch_model|model\.bin|\.(pt|pth|onnx|safetensors|ckpt)$
```

| Layer | Raw result | Classification result |
|---|---:|---|
| Physical artifact tree | 16 candidates | All expected Google SDK/LangChain name collisions |
| `COLLECT-00.toc`, `PYZ-00.toc`, `Analysis-00.toc`, warning file | 131 matching lines | Expected collisions, configured exclusions, or optional warning-only references |
| Executable recursive archive | 4 candidates; viewer exit `0` | The same four expected modules |
| Unclassified forbidden payloads | 0 | Pass |

### Candidate classification

| Layer | Exact entry/group | Classification | Rationale | Effect |
|---|---|---|---|---|
| Physical / COLLECT | `google/genai/_base_transformers.py`, `google/genai/_transformers.py` | expected name collision | Google Gen AI SDK transformation helpers, not Hugging Face Transformers | Pass |
| Physical / COLLECT | `google/genai/tests/transformers/` (12 files) | expected name collision | Google SDK test/data paths, not the forbidden distribution or weights | Pass |
| Physical / COLLECT / archive | `langchain_core/documents/transformers.py` | expected name collision | LangChain document-transformer helper | Pass |
| Physical / COLLECT / archive | `langchain_text_splitters/sentence_transformers.py` | expected name collision | Optional LangChain helper, not the `sentence-transformers` distribution | Pass |
| Analysis exclusion list | `easyocr`, `sentence_transformers`, `transformers`, `torch`, `torchvision`, `cv2`, `skimage`, `scipy`, `sklearn`, `imageio` | exclusion-only entry | Names appear in configured PyInstaller excludes | Pass |
| Warning file | excluded/missing `transformers` and `sentence_transformers` imports | warning-only entry | Optional integrations are absent/excluded and not packaged | Pass |

No physical, collected, PYZ, or executable-archive payload was found for actual EasyOCR, sentence-transformers, Hugging Face Transformers, Torch/torchvision, OpenCV, scikit-image, SciPy, scikit-learn, ImageIO, `offline_bootstrap`, historical local embedding model cache names, or model-weight extensions.

Repository/AppData model folders and the AppData vector store are outside the package boundary. They were neither changed nor counted.

## 10. Live Packaged Smoke Matrix

Only this corrected executable was used:

```text
F:\Asad\Talha Projects\ai-document-analyzer\dist\AI Document Analyzer\AI Document Analyzer.exe
```

Artifact SHA-256 for every row: `48754E6B95E2BC933B2FC471AF34C46513854762EDC3BE1D7E2BB2E65FFDF909`.

Synthetic fixture run ID: `20261018T171605Z`.

| Alias | Description | SHA-256 |
|---|---|---|
| English TXT | 8,976 characters, multi-chunk facts, independently generated 7 markers | `46693FB2873A01374A8961C046F7550CB6A3D6638329ADF6B75EB4F78EB3F8F9` |
| Arabic TXT | 5,609 characters with project/code/19-day facts | `BC52F3E32CEC0ABDB9999079C5C21AAB0A467418BB102A7013294E766B268A1E` |
| OCR PNG | English code/count plus readable Arabic line | `FD4E7CD4B288304A05D781EB6A615CE88DDCE1F0871A1210A19181028E3EE854` |

The unique fixture directory was `%TEMP%\AIDA-Task3-20261018T171605Z`. The PNG was visually inspected before use; `SKY-482`, three `ORCHID` tokens, and the Arabic line were readable. No private or credential-bearing content was used.

| ID | UTC evidence | Action/precondition | Observed result | Result |
|---|---|---|---|---|
| P1 | Launch `17:17:17.7349963`; Ready `17:17:30.8359056` | Launch corrected package unelevated with retained authenticated state and configured Gemini key | `WaitForInputIdle` succeeded in `10.636s`; visible `Status: Ready`, overlay cleared, process responsive | **PASS** as smoke only; not an accepted startup sample |
| P2 | `17:22:48.5911776`–`17:22:56.8642122` | Analyze unique PNG for the first time | 393-character summary included `SKY-482`, ORCHID, and three; status Done; controls re-enabled | **PASS** |
| P3 | `17:23:13.9791269`–`17:23:17.8136052` | Re-analyze exact unchanged PNG | Completed in `3.83s`; 548-character summary included `SKY-482`/ORCHID; controls re-enabled | **PASS**; UI cannot independently prove zero provider OCR calls |
| P4 | `17:17:52.8621354`–`17:17:59.1332437` | Analyze unique 8,976-character English fixture | Fresh indexing/RAG and 653-character summary completed; included `ORBIT-731`, Lina Haddad, and 47 days | **PASS** |
| P5a | `17:19:20.6588995`–`17:19:28.0568546` | Ask `For how many days must the records be retained?` | `47 days`; controls re-enabled | **PASS** |
| P5b | `17:19:28.1198700`–`17:19:34.3604642` | Ask `Who owns the review?` | `Lina Haddad`; controls re-enabled | **PASS** |
| P6 | `17:19:34.4034620`–`17:19:36.4937419` | Ask `How many times does the word BASELINEQUARTZ appear in the document?` | `The word/phrase "BASELINEQUARTZ" appears 7 times in the document.`; controls re-enabled | **PASS** |
| P7 summary | `17:33:40.3768065`–`17:33:48.6778737` | Switch to Arabic and analyze unique Arabic fixture | Status `الحالة: متصل - Gemini - تم`; usable 464-character Arabic summary included project and retention facts | **PASS** |
| P7a | `17:34:11.0238923`–`17:34:17.3534322` | Ask `ما رمز الموافقة؟` | `رمز الموافقة هو قمر-٧٢.`; controls re-enabled | **PASS** |
| P7b | `17:34:17.4104549`–`17:34:27.4831608` | Ask `كم مدة الاحتفاظ بالسجلات؟` | `مدة الاحتفاظ بالسجلات هي تسعة عشر يوماً.`; controls re-enabled | **PASS** |
| P7 RTL visual | PrintWindow capture at `17:35:51.6196249` | Inspect packaged Arabic UI directly | Readable Arabic, right-aligned input/summary, coherent RTL Q&A, indicators cleared, controls enabled | **PASS** |

The Arabic summary did not repeat the approval code, but it was usable and the required Q&A independently returned the exact approval code and retention period. The process remained alive and responsive throughout; loading/typing indicators cleared and operation controls re-enabled. It closed normally at `2026-10-18T17:37:14.8789713Z`.

The successful fallback model remains **unknown from UI**. No request is attributed to Gemini 2.5, 3.1, or 3.5 Flash-Lite without provider-side evidence.

## 11. Startup Baseline

### Endpoint definitions and method

- `WaitForInputIdle`: process start to the Windows GUI input-idle signal. It may precede actual readiness and is not described as “fully ready.”
- Visible Ready: loading overlay absent, main window and Analyze control enabled, and `Status: Ready` visibly exposed through Windows UI Automation.
- UI Automation polled the visible-Ready conditions approximately every 100 ms. The cold run and first warm run were also recorded at 30 frames per second with FFmpeg/GDI desktop capture. Video frames were visually inspected, but the recorder captured the user's foreground work rather than the app because foreground activation was not reliable; acceptance therefore rests on the three explicit UI Automation conditions rather than the unrelated desktop frame.
- Every attempt below is retained. Failed attempts were not included in the warm medians.

### Earlier non-benchmark observation

The corrected packaged app reached `WaitForInputIdle` in `10.636` seconds and visible Ready in approximately `13.101` seconds during P1 on the pre-reboot verification boot. It remains a smoke observation and is not included in the accepted startup samples.

### Genuine first-after-reboot sample

The user restarted Windows. The changed boot time was verified as `2026-10-19T15:48:54.5000000+05:00`, the corrected EXE still predated that reboot, and zero packaged-app processes were running before the measured launch.

| Label | Launch UTC | `WaitForInputIdle` | Visible Ready | Ready evidence | Exit |
|---|---|---:|---:|---|---|
| cold-after-reboot-1 | `2026-10-19T11:38:16.0190563Z` | `28.966s` | `31.185s` at `11:38:47.2052949Z` | `Status: Ready`; window and Analyze enabled; loading text absent | Normal, code `0` |

### Warm raw attempts

| Label | Launch UTC | `WaitForInputIdle` | Visible Ready | Outcome |
|---|---|---:|---:|---|
| warm-1 | `2026-10-19T11:39:22.5849596Z` | `26.038s` | `27.466s` | Valid; normal exit `0` |
| warm-2 | `2026-10-19T11:39:55.4014072Z` | `5.335s` | Not reached | **CRASH**; exit `0xC000041D` |
| warm-3 | `2026-10-19T11:40:18.8184612Z` | `19.306s` | Not reached | **CRASH**; exit `0xC000041D` |
| warm-4 | `2026-10-19T11:42:31.4894820Z` | `22.583s` | Not reached | **CRASH**; exit `0xC000041D` |
| warm-5 | `2026-10-19T11:51:50.8360697Z` | `6.622s` | `7.610s` | Valid; normal exit `0` |
| warm-6 | `2026-10-19T11:52:11.9597406Z` | `5.280s` | Not reached | **CRASH**; exit `0xC000041D` |
| warm-7 | `2026-10-19T11:53:24.2807281Z` | `15.175s` | `16.230s` | Valid; normal exit `0` |
| warm-8 | `2026-10-19T11:53:54.0283748Z` | `6.228s` | Not reached | **CRASH**; exit `0xC000041D` |
| warm-9 | `2026-10-19T12:00:06.1417357Z` | `6.575s` | `7.556s` | Valid; normal exit `0` |

| Warm metric | Valid raw samples | Median |
|---|---|---:|
| `WaitForInputIdle` | `26.038, 6.622, 15.175, 6.575s` | `10.898s` |
| Visible Ready | `27.466, 7.610, 16.230, 7.556s` | `11.920s` |

There are four valid warm samples, exceeding the required minimum of three. The first three valid-run medians would be `6.622s` input-idle and `7.610s` visible Ready, but the report uses all four valid samples and retains every failed attempt.

### Post-sampling reconciliation

At `2026-10-19T12:02:12.7862097Z`, the artifact still measured `227,967,668` bytes, 1,576 files, and 252 directories; the EXE remained `17,889,142` bytes with SHA-256 `48754E6B95E2BC933B2FC471AF34C46513854762EDC3BE1D7E2BB2E65FFDF909`. The package snapshot remained 140 lines with canonical LF SHA-256 `e999ac9f193d5b46ef1cf431674da5278385f10f137ae3cd4aedfd31fdfb565f`. No packaged process remained running.

## 12. Limitations

- `.venv311` is non-minimal and includes historical EasyOCR/local-embedding packages despite `pip check` passing.
- Existing account/AppData config, vector-store, model, cache, and log state were deliberately retained.
- Tests and build ran on one Windows 10 machine.
- The user was performing other work, so machine-idle conditions were not controlled; scheduler and disk-cache noise are visible in the wide valid-run spread.
- Only one genuine first-after-reboot sample exists.
- The 30-fps recorder added overhead to the cold and warm-1 launches, and its desktop frames captured foreground work rather than the packaged window. Visible Ready was therefore determined by three independently queried UI Automation states at approximately 100 ms polling resolution, not by selecting a video frame.
- `WaitForInputIdle` can precede application readiness and, on every failed attempt, occurred before the eventual startup crash.
- Antivirus, network, silent authentication, and provider latency can vary; Defender remained enabled.
- The successful Gemini fallback model is not visible in the UI.
- Live Gemini output can vary.
- UI evidence supports unchanged-image cache reuse but cannot independently establish that the provider received zero OCR calls.
- Source/AppData caches were deliberately left untouched; fixture uniqueness established fresh OCR and English document keys.
- Clean-environment validation and final Milestone 1 acceptance remain Task 13.
- This report does not claim NSIS installer acceptance or final Milestone 1 acceptance.

## 13. Defects and Stop Conditions Encountered

### Historical P6 defect — fixed by separate user authorization

The first package returned `Number of lines in the document: 8` for both:

- `How many times does the word BASELINEQUARTZ appear in the document?`
- `How many times does 'BASELINEQUARTZ' appear in the document?`

Expected: `7`.

Cause: the former `_detect_structural_count()` used a naive `"line" in question` substring check. `BASELINEQUARTZ` contains the letters `line`, so the question was routed to structural line counting.

After the baseline stopped, the user explicitly authorized only the correction and tests. The implemented architecture now uses Gemini schema-constrained structured intent to interpret the question, deterministic Python over complete document text to perform exact counting, and safe semantic-Q&A fallback for invalid intent. Four regression tests were added. Targeted tests passed `4/4`; full discovery passed `37/37`; the fresh corrected package returned `7` in P6.

### Post-reboot warm-start crash — unresolved

The genuine cold launch passed, and warm-1, warm-5, warm-7, and warm-9 reached visible Ready and closed normally. Warm-2, warm-3, warm-4, warm-6, and warm-8 instead returned from `WaitForInputIdle` and then crashed before any ready window could be observed. Each process exited with signed code `-1073740771` (`0xC000041D`).

Windows Application Error event 1000 records paired `0xC0000005` access-violation and `0xC000041D` fatal-unhandled-callback events in the packaged `_internal\python311.dll`. The packaged `app.log` captured native fatal exceptions during these runs, including access violations while the `InitializationWorker` background thread imported `large_doc_manager`, Qdrant, and NumPy. The log also recorded `0x8001010D` COM reentrancy errors. This evidence localizes the failure to startup/background initialization but does not yet prove a single root cause.

The crash reproduced both with and without screen recording, so it was not classified as an FFmpeg-only disturbance. At that historical stopping point, Task 3 correctly remained incomplete despite four valid warm values. A separately authorized lazy-startup correction and fresh artifact verification were subsequently completed; see Sections 13A–13B.

### Non-product execution issues retained as raw evidence

- The original Python metadata inline command had a quoting error; its corrected read-only form passed.
- The original relative batch invocation was not found by the child `cmd.exe`; the supported batch file then succeeded by absolute path.
- The first corrected-build freshness summary said `AllFresh: False` due to PowerShell UTC parsing; the per-file `DateTimeOffset` rerun proved all six outputs fresh.
- The first P5/P6 UI selector expected a lower screen position and found no question field; UI inspection established its current bounds, and the corrected selector passed.
- One UI-inspection command had a missing closing brace; it was corrected without changing the app.
- The native file picker did not expose the needed `ValuePattern`; the path was set with Win32 `WM_SETTEXT` and Open invoked with `BM_CLICK`.
- Foreground screen capture initially captured another application; direct Win32 `PrintWindow` captured the packaged Arabic window for visual review.
- The first two post-reboot measurement tool calls were rejected by the host permission UI before execution; no app launch occurred and the genuine cold opportunity was preserved.
- A replacement warm-9 command initially had a PowerShell parenthesis syntax error and did not launch the app; the corrected command produced a valid sample.
- Startup video frame extraction confirmed that the recorder captured the user's foreground desktop rather than the app; UI Automation remained the acceptance endpoint.

## 13A. Authorized Lazy-Startup Correction and Current Artifact

The pre-correction failures consistently placed the first `large_doc_manager`/Qdrant/NumPy import in `InitializationWorker`'s QThread. The evidence did not prove that `LargeDocumentManager.__init__` had been reached. The minimum correction therefore:

- removed the document-manager import and construction from startup;
- left startup initialization lightweight;
- imported and constructed `LargeDocumentManager` on first validated RAG use;
- guarded construction with a per-window `threading.Lock`;
- published the instance only after successful construction;
- reused injected/existing managers and allowed retry after failed construction;
- preserved local Qdrant, Gemini Embedding 2, OCR, summary, Q&A, exact counting, Arabic behavior, and worker cleanup.

Focused lazy-manager/worker/counting coverage passed `12/12`. Full `.venv311` discovery passed `41/41` with no failures, errors, or skips (`2026-10-20T06:14:18.2044365Z`–`06:15:19.5875111Z`; unittest elapsed `52.358s`). Both resolver dry runs, `pip check`, active imports, and PyInstaller 6.17.0 preflight then passed without package mutation.

The fresh canonical `build_folder.bat` run completed successfully from `2026-10-20T06:20:51.8061903Z` through `06:30:32.9142733Z`. All required build outputs were fresh. Current package identity:

| Field | Current value |
|---|---:|
| EXE SHA-256 | `4ABB0562A605DF0A3E097BD60D579E447AE12F1658BC6B820501B77F6C89EFC5` |
| Exact package bytes | `227,968,502` |
| Binary MiB | `217.41` |
| Files / directories | `1,576 / 252` |
| EXE bytes | `17,889,976` |
| EXE timestamp UTC | `2026-10-20T06:24:15.6421472Z` |

Package inspection again found only 16 physical and four archive name collisions belonging to Google Gen AI/LangChain helpers. No actual EasyOCR, Hugging Face Transformers, sentence-transformers, Torch/torchvision, OpenCV, scikit-image, SciPy, scikit-learn, ImageIO, local model weights, or `offline_bootstrap` payload was packaged. Manifest-only exclusions and warning-only optional imports remain non-payload matches.

### Current-artifact non-reboot smoke evidence

| ID | Evidence | Current result |
|---|---|---|
| P1 | Packaged launches repeatedly reached visible Ready and exited normally. Valid English run launched `2026-10-20T07:24:32.4029657Z`; input-idle `6.786s`, then visible Ready `0.317s` later. | **PASS as smoke; not post-reboot acceptance** |
| P2 | User manually analyzed a new synthetic image and observed a new document-key folder under `%APPDATA%\AI Document Analyzer\vector_store`. The folder contained the persisted local Qdrant/index artifacts. | **PASS, user-observed** |
| P3 | User repeatedly analyzed the exact same unchanged image. No new document-key folder was created; the existing index was reused and only a new summary was generated. Provider telemetry was unavailable, so zero provider OCR calls is not independently claimed. | **PASS with telemetry limitation** |
| P4 | Fresh 5,509-character fixture `20261020T072431Z`, SHA-256 `538CB29FD8D51050D5962A0E91BFB0F754EE09A534D02F64556D2440C46D1E9B`, created seven independent markers and crossed multiple chunks. Summary length `713` included AURORA-846, Mara Saleem, 53 days, and seven markers. | **PASS** |
| P5 | Q&A returned `53 days.` and `Mara Saleem.` from separate fixture facts. | **PASS** |
| P6 | Required exact-count path returned `The word/phrase "BASELINEQUARTZ" appears 7 times in the document.` | **PASS** |
| P7 | User screenshot on `2026-10-20` shows packaged Arabic UI, readable/right-aligned Arabic summary, cleared indicators, enabled controls, answer `رمز الموافقة هو قمر-٧٢.`, and answer `مدة الاحتفاظ بالسجلات هي تسعة عشر يوماً.` | **PASS, user-supplied visual evidence** |

Authentication was present and a Gemini key was configured; values were neither read nor recorded. Only synthetic content was used.

### UI Automation observer diagnosis

After the lazy correction, controlled experiments isolated logged `0x8001010D` lines to external Windows UI Automation interrogation:

- A no-UIA control reached a window, remained alive for 30 seconds, exited normally with code 0, appended no fatal line, and produced no Windows Application Error event.
- UIA-observed runs reached visible Ready, remained responsive, and exited normally with code 0, but appended one `0x8001010D` line and produced no event 1000.

This observer-triggered COM callback line is therefore distinguished from the original process-terminating `0xC000041D`/`0xC0000005` startup failures. It is retained as a measurement limitation; the subsequently completed post-reboot stability sampling is recorded in Section 13B.

At `2026-10-20T08:47:15.7301348Z`, reconciliation again showed CPython 3.11.9, 140 distributions, exact canonical LF freeze SHA-256 `e999ac9f193d5b46ef1cf431674da5278385f10f137ae3cd4aedfd31fdfb565f`, unchanged current EXE/package identity, and `git diff --check` exit 0. The user then closed the packaged process and restarted Windows manually.

## 13B. Fresh Post-Correction Startup Acceptance

The new Windows boot was verified before any packaged-app launch:

| Field | Value |
|---|---|
| Boot local / UTC | `2026-10-20T14:07:09.5000000+05:00` / `2026-10-20T09:07:09.5000000Z` |
| Verification UTC | `2026-10-20T09:18:14.6650390Z` |
| Packaged processes before launch | `0` |
| EXE timestamp UTC | `2026-10-20T06:24:15.6421472Z` (predates reboot) |
| EXE SHA-256 | `4ABB0562A605DF0A3E097BD60D579E447AE12F1658BC6B820501B77F6C89EFC5` |

The cold sample was therefore the genuine first packaged-application launch after this reboot. Visible Ready required all four defined conditions: loading overlay absent, main window enabled, Analyze enabled, and visible `Status: Ready`.

| Label | Launch UTC | `WaitForInputIdle` | Visible Ready | Outcome |
|---|---|---:|---:|---|
| cold-post-correction-1 | `2026-10-20T09:19:05.2167886Z` | `10.636s` | `11.050s` at `09:19:16.2707520Z` | Ready; normal exit `0` |
| warm-post-correction-1 | `09:19:33.4023867Z` | `6.350s` | `6.519s` | Ready; normal exit `0` |
| warm-post-correction-2 | `09:19:45.3198139Z` | `5.418s` | `5.466s` | Ready; normal exit `0` |
| warm-post-correction-3 | `09:19:56.1210268Z` | `5.545s` | `5.604s` | Ready; normal exit `0` |
| warm-post-correction-4 | `09:20:07.1630113Z` | `5.071s` | `5.115s` | Ready; normal exit `0` |
| warm-post-correction-5 | `09:20:17.6195061Z` | `5.420s` | `5.472s` | Ready; normal exit `0` |

| Warm metric | Five valid raw samples | Median |
|---|---|---:|
| `WaitForInputIdle` | `6.350, 5.418, 5.545, 5.071, 5.420s` | `5.420s` |
| Visible Ready | `6.519, 5.466, 5.604, 5.115, 5.472s` | `5.472s` |

All five warm attempts passed, remained responsive through the hold period, and closed normally. No replacement sample was needed. The UIA-observed samples each appended the already isolated observer-associated `0x8001010D` callback line, but none terminated, none returned a nonzero exit code, and all reached Ready. A post-reboot no-UIA control launched at `09:20:44.5827416Z`, returned input-idle in `4.900s`, remained alive and responsive after 30 seconds with a main window, exited normally with code `0`, and appended zero fatal lines. This confirms the distinction from the old process-terminating Qdrant/NumPy startup defect.

Final reconciliation at `2026-10-20T09:21:44.5823036Z` found no running packaged process and confirmed:

- CPython `3.11.9`;
- 140 distributions and the expected canonical environment SHA-256;
- current EXE SHA-256 `4ABB0562A605DF0A3E097BD60D579E447AE12F1658BC6B820501B77F6C89EFC5`;
- `227,968,502` package bytes, 1,576 files, 252 directories, and 17,889,976-byte EXE;
- `git diff --check` exit `0`;
- no package installation or source/AppData cache deletion.

## 14. Completion Checklist and Conclusion

| Requirement | Result |
|---|---|
| Exact safe environment snapshot | PASS |
| Pre/post package snapshot equality | PASS |
| Current resolver dry run | PASS |
| Hypothetical fresh resolver dry run | PASS |
| `pip check` | PASS |
| Active imports | PASS |
| PyInstaller preflight | PASS |
| Full automated test discovery | PASS — 41/41 |
| Canonical one-folder build | PASS |
| Fresh required build evidence | PASS |
| Fresh bytes/count/hash recorded | PASS |
| Zero unclassified forbidden payloads | PASS |
| No unresolved active-path warning | PASS based on full warning review and exercised active paths |
| P1 packaged launch | PASS |
| P2 fresh OCR/indexing | PASS |
| P3 unchanged-image reuse | PASS with provider-telemetry limitation |
| P4 fresh embedding/RAG + summary | PASS |
| P5 semantic Q&A | PASS |
| P6 exact counting | PASS after authorized fix and fresh rebuild |
| P7 Arabic summary/Q&A/RTL | PASS |
| Genuine first-after-reboot sample | PASS — current cold input-idle `10.636s`; visible Ready `11.050s` |
| At least three valid warm samples | PASS — five current valid samples retained |
| Separate visible-Ready measurements and warm median | PASS — input-idle median `5.420s`; visible-Ready median `5.472s` |
| Packaged startup stability | **PASS — cold plus 5/5 warm launches reached Ready and exited normally; no-UIA control stayed alive and clean** |
| Environment/context recorded | PASS |
| No secret/unexplained source change | PASS |
| Tracker/README updated | PASS after all mandatory gates passed |

**Conclusion: COMPLETE.** The current lazy-startup artifact passed every mandatory Task 3 gate. Historical failures remain documented, but they belong to the superseded pre-correction artifact. Task 3 is complete; Task 4 has not begun.

## 15. Command and Action Log

This condensed log preserves all material verification actions in execution order. Secret-bearing settings, request headers, identities, and configuration contents are excluded. The exact commands for dependency checks, tests, canonical build, package measurement, and candidate inspection are reproduced in their corresponding sections; UI Automation/Win32 actions are summarized here because their raw scripts contain implementation detail rather than additional acceptance data.

| # | UTC | Command/action | Result |
|---:|---:|---|---|
| 1 | `12:34:37` | Capture repository root, branch, commit, porcelain status, and dependency/build-input hashes | PASS |
| 2 | `12:34:57` | Capture Python/pip metadata and `python -B -m pip freeze --all`; first inline metadata attempt had quoting error | Freeze PASS; metadata retried |
| 3 | `12:35:16` | Corrected Python metadata capture | PASS |
| 4 | `12:35:57` | Current-environment resolver dry run | PASS |
| 5 | `12:35:59` | Hypothetical-fresh resolver dry run | PASS |
| 6 | `12:36:29` | `python -B -m pip check` | PASS |
| 7 | `12:36:31` | Active import smoke | PASS |
| 8 | `12:36:43` | PyInstaller version preflight | PASS — 6.17.0 |
| 9 | `12:37:05` | Full unittest discovery before defect discovery | PASS — 33/33 |
| 10 | `12:37:33` | Relative `cmd.exe /d /c "call build_folder.bat < nul"` | Did not find script; no build ran |
| 11 | `12:37:45` | Supported batch file invoked by absolute path | PASS |
| 12 | `12:41`–`12:56` | Initial freshness, artifact size/hash, package inspection, machine context, fixtures, packaged P1/P4/P5/P6 | P6 exposed exact-count defect; execution stopped and recorded |
| 13 | `16:54`–`16:55` | Implement user-authorized Gemini structured-intent routing plus deterministic counting and create four regression tests | Completed |
| 14 | `16:55:21` | Run `test_question_counting.py` | PASS — 4/4 |
| 15 | `16:55:41` | Run full unittest discovery | PASS — 37/37 |
| 16 | `17:04:43` | Recapture boot/repository/process state and reconfirm full unittest discovery | PASS — 37/37 |
| 17 | `17:05:51` | Rerun both resolver dry runs, `pip check`, import smoke, and PyInstaller preflight | PASS; no environment mutation |
| 18 | `17:08:13` | Fresh `build_folder.bat` corrected-package build | PASS at `17:12:20`; 1021 hidden imports |
| 19 | `17:15` | Freshness, size/hash, archive/manifests/warnings, Git/input-hash reconciliation | PASS after correcting UTC comparison |
| 20 | `17:16:05` | Create and hash unique synthetic English, Arabic, and OCR fixtures | PASS; PNG visually readable |
| 21 | `17:17:17` | Launch corrected package and observe input-idle/visible Ready | P1 PASS; explicitly non-benchmark |
| 22 | `17:17:52` | Analyze unique English fixture | P4 PASS |
| 23 | `17:19:20` | Retention semantic Q&A | P5a PASS |
| 24 | `17:19:28` | Review-owner semantic Q&A | P5b PASS |
| 25 | `17:19:34` | Required exact-count question | P6 PASS — 7 |
| 26 | `17:22:30` | Select unique OCR PNG through native dialog | PASS |
| 27 | `17:22:48` | Fresh OCR/index/summary | P2 PASS |
| 28 | `17:23:13` | Re-analyze unchanged image | P3 PASS; provider call not independently observable |
| 29 | `17:24:08` | Switch packaged UI to Arabic | PASS |
| 30 | `17:33:40` | Analyze unique Arabic fixture | P7 summary PASS |
| 31 | `17:34:11` | Arabic approval-code Q&A | P7a PASS |
| 32 | `17:34:17` | Arabic retention Q&A | P7b PASS |
| 33 | `17:34`–`17:35` | Capture and visually inspect Arabic UI; final capture used Win32 `PrintWindow` | RTL/readability PASS |
| 34 | `17:36:24` | Recapture `pip freeze --all` and canonical hash | PASS; exact match, 140 lines |
| 35 | `17:36:30` | Recompute artifact bytes/count/hash and payload candidates | PASS; values unchanged |
| 36 | `17:36:36` | Recapture branch/commit/porcelain status | PASS; only known changes |
| 37 | `17:36:50` | Recapture hardware/power/Defender/elevation context | PASS |
| 38 | `17:37:14` | Close packaged app normally | PASS |
| 39 | `2026-10-19 11:05` | Verify user-performed reboot, unchanged corrected EXE, and zero running packaged processes | PASS; cold opportunity valid |
| 40 | `11:38:16` | Record genuine first-after-reboot launch with 30-fps desktop recorder plus 100-ms UI Automation checks | PASS — input-idle `28.966s`, visible Ready `31.185s`, normal exit `0` |
| 41 | `11:39:22` | warm-1 | PASS — `26.038s` / `27.466s`, normal exit `0` |
| 42 | `11:39:55`–`11:40:18` | warm-2 and warm-3 | **CRASH** before Ready; both `0xC000041D` |
| 43 | `11:42:31` | warm-4 without screen recorder | **CRASH** before Ready; `0xC000041D` |
| 44 | `11:51:50` | warm-5 | PASS — `6.622s` / `7.610s`, normal exit `0` |
| 45 | `11:52:11` | warm-6 | **CRASH** before Ready; `0xC000041D` |
| 46 | `11:53:24` | warm-7 | PASS — `15.175s` / `16.230s`, normal exit `0` |
| 47 | `11:53:54` | warm-8 | **CRASH** before Ready; `0xC000041D` |
| 48 | `12:00:06` | warm-9 replacement after one non-launching PowerShell syntax error | PASS — `6.575s` / `7.556s`, normal exit `0` |
| 49 | `12:01`–`12:02` | Extract/inspect recorder frames, capture Windows crash events, calculate medians, and reconcile artifact/environment/Git state | Crashes confirmed; artifact and 140-line environment snapshot unchanged |

| 50 | `2026-10-20 06:14`–`06:30` | Run 41-test correction suite, dependency/import checks, environment recapture, and fresh canonical lazy-startup build | PASS; artifact SHA `4ABB0562...EFC5` |
| 51 | `2026-10-20 07:24` | Run fresh English multi-chunk summary, semantic Q&A, and exact count against current artifact | PASS |
| 52 | `2026-10-20` | User manually confirms new-image Qdrant folder creation and unchanged-image index reuse | P2/P3 PASS with provider-telemetry limitation |
| 53 | `2026-10-20` | User supplies packaged Arabic summary/Q&A/RTL screenshot | P7 PASS |
| 54 | `2026-10-20 09:18` | Verify user-performed reboot, changed boot time, unchanged EXE, and zero running packaged processes | PASS; genuine cold opportunity valid |
| 55 | `09:19:05` | Record genuine first-after-reboot cold sample | PASS — input-idle `10.636s`, Ready `11.050s`, exit `0` |
| 56 | `09:19:33`–`09:20:23` | Record five warm post-correction samples | PASS — 5/5 Ready and exit `0`; medians `5.420s` / `5.472s` |
| 57 | `09:20:44` | Run no-UIA post-reboot control for 30 seconds | PASS — alive/responsive, exit `0`, zero appended fatal lines |
| 58 | `09:21:44` | Final environment/artifact/process/Git reconciliation | PASS; no drift and no process left running |

No package install, upgrade, downgrade, uninstall, or prune command was executed. No restart was initiated automatically.
