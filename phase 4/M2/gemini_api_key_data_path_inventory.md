# Phase 4 / Milestone 2 / Task 1 — Gemini and API-key data-path inventory

**Audit state:** complete on 2026-11-09. This is the migration baseline for Tasks 2–9; it does not change runtime behavior.

## Scope and result

The audit covers the active desktop source, settings, tests, logs, dependencies, build inputs, PHP backend, and React admin console. The frozen `ai-document-analyzer_AfterPhase2Delivered/` snapshot, generated `dist/` and `build*/` output, `.venv311/`, backend `vendor/`, and admin-console `node_modules/` are not active source.

**Current result:** the desktop owns a plaintext user Gemini key and calls Google Gemini directly. The backend and admin console have no Gemini storage, gateway endpoints, or Gemini settings UI yet.

## Current end-to-end flow

```text
Desktop Settings UI
  -> %APPDATA%/AI Document Analyzer/config.json (plaintext GOOGLE_API_KEY)
  -> QSettings (duplicate plaintext GOOGLE_API_KEY)
  -> MainWindow._get_gemini_key()
  -> worker fields/parameter dictionaries
  -> GeminiGateway(api_key)
  -> google.genai.Client(api_key=...)
  -> Gemini generation / image OCR / embeddings

Authenticated PHP backend and React admin console
  -> currently handle users, licenses, and authentication only
  -> no Gemini key or Gemini request path exists
```

The key is not sent to the current backend. It remains in desktop memory while operations run and is sent from the desktop directly to Google through the Google Gen AI SDK.

## Desktop key ownership and persistence

| Classification | Evidence | Current behavior | Downstream owner |
|---|---|---|---|
| **replace, then remove** | `ui_settings_window.py:18-29` | The desktop displays a password-style Gemini key field and eye toggle. | Tasks 7–8 |
| **replace, then remove** | `settings_window.py:38-75` | Loads `GOOGLE_API_KEY` from `QSettings`, then from config; config wins and is copied into `QSettings`. Saving writes the raw value to both stores. Exceptions are silently ignored. | Tasks 7–8 |
| **remove** | `settings_window.py:107-124`; `config.json:2` | The default config is copied to `%APPDATA%/AI Document Analyzer/config.json`; the raw key therefore lives in a normal JSON file when entered. | Task 8 upgrade cleanup |
| **replace, then remove** | `main_window.py:2148-2184` | `_read_config()` can copy packaged/local config into AppData. `_get_gemini_key()` reads config first and falls back to `QSettings`. | Tasks 7–8 |
| **retain** | `config.json:3`; `main.py:35-64`; `auth.py` | `API_BASE_URL`, access-token memory state, and keyring-backed refresh tokens are the existing authenticated backend path and are not Gemini credentials. | Reuse in Tasks 2, 5, 7 |

No active desktop code reads Gemini credentials from an environment variable. Environment reads found in active Python code concern AppData paths and the unrelated lock encryption key.

## Gemini operations and in-memory key flow

| Operation | Key/data path | Gemini call | Gateway contract needed |
|---|---|---|---|
| Summary | `main_window.py:657-707` captures the key; `_AnalysisWorker` receives it at `:2260-2320`; `summarize_text_gemini()` calls `_generate_gemini_text()` at `:1769-1817`. | `GeminiGateway.generate_text()` | Authenticated generation operation with system instruction, prompt, optional JSON schema, timeout, fallback, and stable errors. |
| Q&A intent classification | `_send_question()` captures the key at `main_window.py:1220-1249`; `_QAWorker` passes it to `_classify_question_intent()` at `:2323-2379`; classification uses structured JSON generation at `:855-906`. | `GeminiGateway.generate_text()` | Same generation operation with response schema. Exact counting remains local after classification. |
| Semantic Q&A answer | `answer_question_gemini()` receives the key and builds document/history context at `main_window.py:2066-2146`. | `GeminiGateway.generate_text()` | Same generation operation; preserve English/Arabic prompts and conversation behavior. |
| Image OCR | `LargeDocProcessWorker` and `_AnalysisWorker` pass the key through `extract_text_from_file()` to `extract_text_from_image_ocr()` (`main_window.py:1729-1767`, `:2288-2297`, `:2387-2437`). `gemini_ocr.py:50-98` reads complete image bytes and creates a gateway. | `GeminiGateway.transcribe_image()` | Authenticated vision/OCR operation accepting supported image data and MIME type, preserving transcription-only prompt and blocked/no-text errors. |
| Document embeddings | `LargeDocProcessWorker` / `PastedTextProcessWorker` pass the key to `LargeDocumentManager.prepare_document()` (`main_window.py:2424-2474`; `large_doc_manager.py:237-361`). | `GeminiGateway.embed_contents()` via `GeminiEmbeddingClient` | Batch embedding operation using `gemini-embedding-2`, output dimension 768, current item/token limits, and stable errors. |
| Query embedding | Q&A passes the key to `retrieve_context()` (`main_window.py:2088-2107`; `large_doc_manager.py:390-443`). | `GeminiGateway.embed_contents()` via `GeminiEmbeddingClient.embed_query()` | Same embedding operation for one query. Qdrant search stays local. |
| Model fallback | `gemini_fallback.py:5-55` defines generation order and eligible fallback errors. `gemini_gateway.py:51-64` applies it. | Generation/OCR only | Server gateway must preserve ordered fallback and must not advance on auth, quota, validation, or timeout failures. |

### Direct SDK boundary

`gemini_gateway.py:16-38` is the only active creator of `google.genai.Client`. It strips and validates the key, lazily imports `google.genai`, applies a 60-second HTTP timeout, and gives the key to the SDK constructor. `gemini_gateway.py:66-109` owns generation, image, and embedding SDK calls; `:118-137` maps exceptions to key-free user messages.

The service boundary is suitable for Task 7's transport swap: preserve feature handlers, prompts, worker lifecycle, cancellation checks, local Qdrant, and deterministic counting while replacing direct SDK transport with authenticated backend calls.

## Logs and error surfaces

- `main.py:10-25` redirects stdout/stderr and crashes to `%APPDATA%/AI Document Analyzer/app.log` in packaged mode.
- `auth.py:56-69` writes login response headers/body to `auth_debug.log`; this path does not currently receive the Gemini key.
- Active Gemini code does not intentionally print or log the raw key. Worker errors and `_safe_request_error()` return mapped messages rather than request credentials.
- `main_window.py:906` prints classification exception text. Current mapped gateway exceptions are safe, but Task 2/5 must require backend and desktop error redaction because upstream exception text must never contain secrets.
- PHP `src/util.php:2-7` appends exception messages and supplied metadata to `storage/logs/error.log`; future key-management/gateway code must never pass request bodies, raw keys, authorization headers, or raw upstream responses to this logger.
- PHP `public/index.php:75-80` currently returns/logs exception messages. The Task 2 contract must require stable key-free responses for all new Gemini routes.

## Tests, dependencies, builds, and documentation

| Classification | Evidence | Finding | Downstream owner |
|---|---|---|---|
| **adapt** | `test_gemini_generation.py`, `test_gemini_ocr.py`, `test_gemini_embeddings.py`, `test_gemini_fallback.py` | Tests directly construct/fake `GeminiGateway` and SDK clients. Preserve feature/fallback/error assertions while replacing transport tests. | Tasks 7, 9, 11 |
| **adapt** | `test_document_processing_workers.py`, `test_lazy_document_manager.py`, `test_ollama_removal.py` | Fixtures and assertions pass keys through workers or expect missing-key Settings messages. | Tasks 7–8, 11 |
| **remove after migration** | `requirements.txt:4` | Desktop directly depends on `google-genai`. | Task 9 only after no SDK imports remain |
| **remove after migration** | `app_folder.spec:19,46-47`; `app.spec:19,64-65`; `AI Document Analyzer.spec:11-12,25` | Canonical and alternate specs collect or hide-import Google Gen AI modules. | Task 9 |
| **remove after migration** | `build_folder.bat:40`; `build_exe.bat:56-57`; `build_debug.bat:45,47-48` | Build validation/CLI inputs explicitly import or collect Google Gen AI. | Task 9 |
| **adapt** | `CLAUDE.md`, `README_Windows_Deployment.md`, `LARGE_DOC_GUIDE.md`, `PROMPTS_DOCUMENTATION.txt`, `prompts.txt` | Current guidance describes a user key and/or direct Gemini behavior. Prompt text itself must remain behaviorally stable when moved behind the gateway. | Tasks 7–9, 12 |
| **historical/generated** | `ai-document-analyzer_AfterPhase2Delivered/`, `dist/`, `build*/`, `.venv311/` | May contain old keys/dependencies or warnings but is not an active source path. Never edit generated packages as source; inspect final packages in Task 11. | Task 11 inspection |

## Backend audit — `C:\xampp\htdocs\server-php-auth`

### Existing reusable patterns

- `public/index.php:1-73` is the active route table and requires controllers/repositories manually.
- `src/auth.php:6-53` extracts Bearer tokens, validates JWTs, reloads active users, and provides `require_admin()`.
- `src/controllers/AdminController.php:7-80` demonstrates admin-only controller methods.
- `src/db.php` / repository classes provide the existing PDO access pattern.
- `src/util.php:10-29` provides JSON request/response helpers.
- `config.php`, `config.prod.php`, and `production/config.php` contain deployment configuration; no Gemini key setting exists.
- `schema.sql` contains users and refresh tokens only; additional license/password-reset tables are managed elsewhere. No Gemini credential or audit table exists.

### Missing Gemini surfaces

Targeted source scans found no Gemini API key, Google Gen AI client, Gemini endpoint, Gemini repository/service, Gemini database table, or Gemini admin component. The only Google-related backend code is Google sign-in token verification in `AuthController.php`, which is unrelated to Gemini.

Task 2 must therefore define new contracts before implementation: admin key-management endpoints, authenticated generation/OCR/embedding gateway endpoints, request limits, stable errors, usage controls, audit events, rotation behavior, and the strict rule that no response returns the raw key.

The repository also has a `production/` deployment copy. Implementation tasks must define the deployment/synchronization method rather than accidentally changing only one copy.

## Admin-console audit

- `admin_console_shadcn/apps/web/src/lib/api.ts:95-148` is the shared authenticated API client with one refresh-and-retry cycle; new admin key-management calls must use this client.
- `App.tsx:361-366` defines sidebar pages and `App.tsx:1408-1443` renders pages by state; Task 6 should add an admin-only Settings page here.
- `App.tsx:1451-1470` already separates standard-user and admin views.
- No Gemini settings component or API method exists.
- `src/lib/firebase.ts` contains a Firebase browser configuration `apiKey`. It is not a Gemini credential and is excluded from Milestone 2 Gemini-key migration.

## Security findings and constraints

1. The current raw Gemini key is duplicated in plaintext AppData JSON and `QSettings`, visible in the desktop UI, copied into multiple worker objects/dictionaries, and delivered directly to the Google SDK.
2. Task 3 must store only an encrypted server-side value using a deployment-managed encryption secret; current PHP config files are not an acceptable raw-key store.
3. Standard users may call approved Gemini gateway operations after authentication, but only admins may create, inspect masked status, validate, update, or rotate the server key.
4. Neither desktop nor browser may fetch the stored raw key. Admin responses may contain masked metadata/status only.
5. Do not remove the current desktop key path in Tasks 2–6. Task 7 first migrates all operations; Task 8 then removes UI/persistence and deletes legacy local keys during upgrade.
6. Existing backend configuration includes sensitive deployment values. This audit intentionally does not reproduce them; future logging, docs, and tests must use placeholders.

## Downstream task map

- **Task 2:** define contracts for `generate`, `ocr`, and `embed`, admin key management, authorization, limits, fallback, cancellation/timeouts, stable errors, redaction, rotation, audit, and deployment-copy behavior.
- **Tasks 3–4:** implement encrypted storage/service and admin-only management endpoints using existing PDO, JWT, and `require_admin()` patterns.
- **Task 5:** implement server-to-Gemini transport for every operation listed above; preserve current models, prompts, dimensions, limits, and error semantics.
- **Task 6:** add masked Gemini settings to the existing admin-only React application through `api.ts` and sidebar/page-state conventions.
- **Task 7:** replace `GeminiGateway`'s direct SDK/user-key transport with the authenticated backend without rewriting feature logic.
- **Task 8:** remove desktop key UI, config/QSettings reads and writes, worker key fields, key-specific messages, and legacy plaintext values.
- **Task 9:** remove `google-genai` and all desktop build collection/import rules only after a residual import scan is clean.
- **Tasks 10–12:** add usage safeguards, verify no secret reaches clients/logs/packages, and deploy backend/storage/admin before the desktop release.

## Completion check

Task 1 is complete because summary, Q&A, OCR, embeddings, fallback, configuration, `QSettings`, files, environment values, logs, tests, build inputs, backend endpoints, and admin-console extension points have been inventoried and assigned to downstream tasks.
