# Phase 4 Milestone 2 Task 7 Acceptance

**Completed:** 2026-11-17
**Scope:** Desktop transport/credential migration to the authenticated backend Gemini gateway

## Delivered

- Added `backend_api.py` as the shared desktop API base-URL resolver and authenticated `v1` JSON client.
- Added dispatch-time Bearer-token reads, pre-expiry refresh, a process-wide refresh lock, one replay only for `401 AUTH_REQUIRED`, UUID request IDs, bounded connect/read timeouts, cancellation checkpoints, and safe structured error metadata.
- Replaced direct Google Gen AI SDK transport in `GeminiGateway` with backend `/v1/gemini/generate`, `/v1/gemini/ocr`, and `/v1/gemini/embed` requests.
- Removed local Gemini-key gating and propagation from analysis, Q&A, OCR, document indexing, semantic retrieval, and all related workers.
- Preserved prompts, OCR validation/transcription behavior, local Qdrant persistence/search, deterministic counting, embedding batching/order/dimension validation, localized UI behavior, progress, cancellation, stale-session protection, and worker cleanup.
- Added finite numeric embedding-vector validation and backend/admin-managed service wording.

## Security assertions

- Active desktop AI requests contain no Gemini API key, model selector, or timeout override.
- The desktop reads the access token only when dispatching and sends it only in the Authorization header.
- Exceptions retain only safe backend metadata (`error_code`, `request_id`, retryability, retry delay); prompts, image base64, generated text, vectors, authorization values, and raw response bodies are not included.
- Desktop generation/OCR performs one backend request per logical AI call; model fallback remains server-owned.

## Verification

- Changed Python modules compiled successfully with Python 3.11.
- Focused Task 7 regression set: **61 tests passed**.
- Complete `unittest` discovery: **69 tests run; 66 passed; 3 pre-existing/unrelated failures**:
  - `test_gemini_fallback.GeminiFallbackTests.test_model_not_found_advances_to_next_model` expects the previously configured first model; `gemini_fallback.py` and its test were already modified before Task 7 and are not part of this transport migration.
  - Two `test_resource_paths` assertions differ only by Windows drive-letter case (`f:` versus `F:`); no resource-path implementation was changed by Task 7.
- `python -B -m pip check`: **passed** (`No broken requirements found`).
- Residual scans confirmed active desktop AI paths contain no Google SDK construction, keyed `GeminiGateway` construction, `gemini_key` worker payload, or AI request body fields for key/model/timeout.

## Live verification

Live generate/OCR/embed smoke calls were skipped. They require the already-running local backend, a valid signed-in desktop session, and an admin-configured staging key. No XAMPP service was started, stopped, or restarted.

## Deferred boundaries

- **Task 8:** remove the now-unreachable key settings UI, `GOOGLE_API_KEY` config/QSettings readers/writers, translations, and legacy plaintext cleanup.
- **Task 9:** remove `google-genai` dependency, hidden imports/build collection, and obsolete packaging checks.
- No GUI/browser run and no build/package artifact generation were performed for Task 7.
