# Phase 4 / Milestone 1 / Task 5 — Gemini-Only Feature Dispatch Plan

## Objective

Consolidate document summarization, Q&A, OCR, and embedding requests behind one Gemini-only application path. Keep feature logic independent of the current user-entered API key and Google SDK transport so Milestone 2 can replace that boundary with the admin-managed backend gateway without rewriting those features.

Task 5 establishes the seam and behavior. Ollama package/code removal belongs to Task 6, offline selector/UI removal to Task 7, and final regression coverage to Task 11. Keep the transitional UI from silently routing a selection labeled Offline to Gemini: reject that selection with a clear message until Task 7 removes it.

## Current State and Constraints

- `main_window.py` reads the source/model selectors and branches to Ollama or Gemini in `analyze_document`, `_send_question`, `_classify_question_intent`, `_AnalysisWorker`, `_QAWorker`, and `_RefreshWorker`.
- Gemini text generation already uses `gemini_fallback.py` and a 60-second SDK timeout. `gemini_ocr.py` uses the same fallback list with its own client and timeout. `GeminiEmbeddingClient` in `large_doc_manager.py` creates a separate SDK client and has no explicit timeout.
- Feature-specific prompts, JSON parsing/rendering, image transcription and cache versioning, text chunking, Gemini Embedding 2, local Qdrant storage, semantic retrieval, exact-count handling, localized behavior, and worker lifecycle must retain their current behavior.
- Keep user Gemini API-key ownership in Settings for Milestone 1. Do not add the backend gateway or change credential ownership in this task.
- Do not delete Ollama modules, dependencies, model assets, configuration, or offline UI here; those are assigned to Tasks 6–9. Remove Ollama from active feature dispatch so all supported processing is Gemini-only.

## Implementation Changes

### 1. Add a replaceable Gemini request boundary

- Add a small internal `GeminiGateway` interface/module, initialized per operation with the current API key supplied by the application. The feature layer receives the gateway rather than constructing `google.genai.Client` directly or passing keys through summarization/Q&A/OCR feature logic.
- Give the boundary operations for text generation, image generation/transcription, and text embeddings. Keep prompts, response schemas, OCR validation, chunking, and retrieval in their existing feature modules/classes.
- Implement the first adapter with `google-genai`. Keep SDK types and client creation inside this adapter so Milestone 2 can replace the adapter with backend requests without changing feature algorithms or UI handlers.
- Keep credentials operation-scoped; never store them in a module global, log them, or include them in errors. Close SDK clients in `finally` blocks.

### 2. Normalize request policy and feature dispatch

- Centralize the 60-second request timeout and safe error classification in the gateway. Preserve stable OCR user-facing categories and map generation/embedding failures to actionable application errors without exposing credentials or raw request data.
- Preserve the ordered Flash-Lite fallback for generation and OCR, advancing only for model-unavailable/service-unavailable errors. Do not fall back from Gemini Embedding 2 to a generation model; embeddings remain on the configured embedding model and dimension.
- Route summary, intent classification, Q&A, OCR, document indexing, and semantic retrieval through the Gemini boundary. Remove provider selection from worker/request parameters where it only chooses Ollama versus Gemini; retain only model or operation options that still affect Gemini behavior.
- Require a valid Gemini configuration/key at the operation boundary. Until Task 7 removes the selector, reject the legacy Offline selection rather than silently running Gemini under an Offline label.
- Preserve exact-count deterministic handling and its Gemini intent-classification fallback, English/Arabic prompts and rendering, RAG context selection, image OCR cache invalidation, and local Qdrant persistence.

### 3. Make cancellation and cleanup consistent

- Pass the existing operation/session cancellation state to workers and the gateway. Check cancellation before a request, between fallback attempts and embedding batches, and immediately after a request returns. A synchronous request already in flight may finish until the configured timeout; discard its result if the operation/session was cancelled.
- Keep generation, document processing, and Q&A work off the UI thread. Ensure success, failure, timeout, and cancellation all close clients, quit threads, clear worker references, stop loading/typing indicators, and ignore stale session results.
- Keep the existing session-ID guards. Do not use `QThread.terminate()` or create a new global background-worker framework.

## Internal Interface and Data Flow

- `GeminiGateway(api_key, cancellation_token)` is the only layer that knows about `google-genai`, SDK request configuration, timeout, fallback eligibility, and provider error translation.
- Feature callers use typed operations equivalent to `generate_text(prompt, system_instruction, response_schema)`, `transcribe_image(image_bytes, mime_type, prompt)`, and `embed_contents(contents, output_dimension, task_kind)`. The exact Python names may follow existing style, but feature modules must not import or instantiate the Google SDK client.
- UI thread validates the selected input and captures the existing key; the worker invokes the feature logic with a gateway/factory. Data flow remains UI → worker → feature operation → Gemini gateway → result/error signal → UI.
- Keep this boundary internal to the application. No external API, persisted configuration schema, or user credential workflow changes in Task 5.

## Test Plan and Acceptance Criteria

Use mocked SDK/adapters only; no live Gemini calls are required for Task 5. Update focused tests and run the existing relevant suites after implementation.

- **Dispatch:** summary, OCR, embedding/indexing, intent classification, and Q&A all select Gemini; no active handler or worker can call an Ollama method. A legacy Offline selector value is rejected clearly and never reaches a local provider call.
- **Gateway:** SDK construction uses the captured key without logging it; client closes after success/error; all request types use the shared timeout; unavailable generation/OCR models follow the ordered fallback; quota/auth/validation errors do not trigger inappropriate fallback; embeddings retain Gemini Embedding 2 and the expected vector dimension.
- **Cancellation and workers:** cancellation before a request prevents the call; cancellation after an in-flight response discards its result; cancellation between batches/fallbacks stops subsequent calls; success, exceptions, and timeouts clear worker/thread references and UI busy state; stale session signals remain ignored.
- **Behavior preservation:** existing OCR transcription/cache tests, embedding/index/Qdrant tests, summary JSON parsing/rendering, exact-count tests, English/Arabic behavior, RAG semantic Q&A, and document worker cleanup continue to pass.
- **Architecture scan:** active feature code outside the Google SDK adapter contains no direct `genai.Client` construction and no provider branch that selects between Ollama and Gemini. Ollama definitions may remain temporarily for Task 6, but are unreachable from the supported application flow.
- Task 5 is complete when the feature paths use the new seam, acceptance checks pass, and the Milestone 2 credential/transport replacement can be implemented by swapping the gateway adapter without editing feature prompts or RAG/OCR algorithms.

## Assumptions and Explicit Non-Goals

- The existing Flash-Lite fallback order and Gemini Embedding 2 model/dimension are authoritative and remain unchanged.
- Network calls are synchronous inside existing worker threads. Cancellation is cooperative and bounded by the shared request timeout, not an attempt to forcibly abort an SDK call.
- UI strings/model-selector cleanup, broad Ollama deletion, dependency/build cleanup, documentation rewrite, final acceptance, and admin-gateway implementation remain owned by later tasks.
- No data migration is required. Existing Qdrant stores and OCR cache-key versioning remain intact.
