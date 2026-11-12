# Phase 4 / Milestone 2 / Task 2 — Secure Gemini gateway contract

**Contract version:** `v1`  
**Contract state:** approved implementation baseline on 2026-11-09  
**Scope:** backend key ownership, admin key management, authenticated Gemini operations, and the shared contract used by Tasks 3–12. This task defines behavior only; it does not change runtime code.

## 1. Security invariants and trust boundaries

1. The PHP backend is the only component allowed to decrypt the active Gemini key and attach it to a Google request.
2. The desktop, browser, standard users, API responses, logs, traces, audit records, analytics, and packaged files must never receive the stored raw key.
3. A submitted key may exist only in the incoming admin request and the backend's in-memory validation/encryption path. It must not be written to temporary files, session state, exception text, or normal application logs.
4. All routes require HTTPS outside local development and accept the existing Bearer access token. Refresh tokens are not accepted by Gemini routes.
5. `require_auth()` is the minimum authorization for Gemini operations. The authenticated user must be active and, where licensing is enforced by the existing deployment, have an active assigned license. License checks remain server-side.
6. `require_admin()` is required for every key-management route. Standard users may invoke approved Gemini operations but cannot read status, validate, create, update, rotate, or roll back a key.
7. Clients cannot select models, supply a Gemini key, override timeouts, or request arbitrary Google API methods.
8. Prompts and documents are transient request data. They are forwarded only to Gemini for the requested operation and are not persisted by this gateway.

A raw-key field is allowed only in an admin write request. If any future response schema appears to need it, the contract must be revised rather than returning it.

## 2. Versioning and common protocol

All new routes are rooted at `/api/v1`. Additive response fields are allowed within `v1`; removing or changing a field's meaning requires a new API version.

### Request headers

```http
Authorization: Bearer <access-token>
Content-Type: application/json
X-Request-ID: <optional client-generated UUID>
```

The backend accepts a valid `X-Request-ID` or creates one. It returns the identifier in both the `X-Request-ID` header and JSON. Duplicate request IDs do not make write operations idempotent.

### Successful operation envelope

```json
{
  "ok": true,
  "request_id": "7f1f2dc0-17bb-4fc7-86dc-63d061d6f604",
  "data": {},
  "meta": {
    "contract_version": "v1"
  }
}
```

`data` and operation-specific `meta` fields are defined below. HTTP `204` is not used, so the admin console and desktop can consistently parse JSON.

### Error envelope

```json
{
  "ok": false,
  "request_id": "7f1f2dc0-17bb-4fc7-86dc-63d061d6f604",
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests. Try again later.",
    "retryable": true,
    "retry_after_seconds": 30
  },
  "meta": {
    "contract_version": "v1"
  }
}
```

`error.code` is the stable machine interface. `message` is safe for display but may be localized or refined. No error response may include raw upstream text, stack traces, file paths, SQL, request bodies, authorization headers, prompts, image data, vectors, or key material.

## 3. Route and authorization matrix

| Method | Route | Authorization | Purpose |
|---|---|---|---|
| `GET` | `/api/v1/admin/gemini/key` | Admin | Return masked status and version metadata. |
| `POST` | `/api/v1/admin/gemini/key/validate` | Admin | Validate a submitted key without storing or activating it. |
| `PUT` | `/api/v1/admin/gemini/key` | Admin | Create the first active key or update it with optimistic version checking. |
| `POST` | `/api/v1/admin/gemini/key/rotate` | Admin | Validate and atomically activate a new key while retaining one rollback version. |
| `POST` | `/api/v1/admin/gemini/key/rollback` | Admin | Atomically restore the retained previous key. |
| `POST` | `/api/v1/gemini/generate` | Active authenticated user | Text or structured generation. |
| `POST` | `/api/v1/gemini/ocr` | Active authenticated user | PNG/JPEG transcription. |
| `POST` | `/api/v1/gemini/embed` | Active authenticated user | Document/query embeddings. |

Existing login, refresh, logout, and `/me` routes remain unchanged.

## 4. Admin key-management contract

### 4.1 Key metadata object

Every admin status/write response returns metadata only:

```json
{
  "configured": true,
  "state": "active",
  "masked_key": "AIza••••••••7xQp",
  "fingerprint": "sha256:9d1d02c8d7f1",
  "version": 4,
  "validated_at": "2026-11-09T12:30:00Z",
  "updated_at": "2026-11-09T12:30:01Z",
  "updated_by": {
    "id": 11,
    "email": "admin@example.com"
  },
  "rollback": {
    "available": true,
    "previous_version": 3,
    "expires_at": "2026-11-10T12:30:01Z"
  }
}
```

Rules:

- `state` is `missing`, `active`, or `invalid`. Revoked/unauthorized responses from Gemini mark the active version `invalid`; quota/network/service failures do not.
- `masked_key` reveals at most the first four and last four characters. If the key is too short, it is entirely masked. It is display-only and cannot reconstruct the key.
- `fingerprint` is the first 12 hexadecimal characters of an HMAC-SHA-256 computed with a deployment-managed fingerprint secret. It is not a plain hash and is used only to distinguish versions safely.
- `version` is a monotonically increasing integer. It never goes backward, including after rollback.
- Timestamps are UTC ISO 8601. `updated_by` is safe actor metadata, never a token.
- When no key exists, nullable fields are `null`, `configured` is `false`, and `state` is `missing`.

### 4.2 Inspect status

`GET /api/v1/admin/gemini/key`

Returns `200` with the key metadata object. It must not decrypt the key merely to display status.

### 4.3 Validate without storing

`POST /api/v1/admin/gemini/key/validate`

```json
{
  "api_key": "<new-key>"
}
```

The backend performs a minimal server-to-Gemini validation request using the first generation model. It does not activate, encrypt for storage, or retain the submitted key. A valid key returns `200`:

```json
{
  "ok": true,
  "request_id": "...",
  "data": {
    "valid": true,
    "fingerprint": "sha256:9d1d02c8d7f1",
    "validated_at": "2026-11-09T12:30:00Z"
  },
  "meta": { "contract_version": "v1" }
}
```

An invalid/revoked key returns `422 KEY_INVALID`; quota, timeout, network, and provider failures retain their distinct stable codes because they do not prove invalidity.

### 4.4 Create or update

`PUT /api/v1/admin/gemini/key`

```json
{
  "api_key": "<new-key>",
  "expected_version": 3,
  "validate": true
}
```

- `expected_version` is `null` only when creating the first key. Updating an existing key requires the current version.
- `validate` must be `true` in production. Local automated tests may inject a validation adapter; they must not weaken the production route.
- Validation succeeds before encryption and database mutation.
- The encrypted value and metadata are committed atomically. Failure leaves the old active version untouched.
- A version mismatch returns `409 KEY_VERSION_CONFLICT` with current masked metadata, never either key.
- Success returns `200` for update or `201` for initial creation with the metadata object.

### 4.5 Rotate

`POST /api/v1/admin/gemini/key/rotate`

```json
{
  "api_key": "<replacement-key>",
  "expected_version": 4
}
```

Rotation validates the replacement, encrypts it, moves the current encrypted value into the single rollback slot, and activates the new value in one database transaction. New requests resolve the new version immediately after commit; already-started requests may finish with the version they resolved.

One previous encrypted version is retained for **24 hours**. A later successful rotation replaces the prior rollback slot. The retained value is excluded from normal status reads and is automatically purged after expiry.

Success returns `200` with current metadata plus:

```json
{
  "rotated_from_version": 4
}
```

### 4.6 Roll back

`POST /api/v1/admin/gemini/key/rollback`

```json
{
  "expected_version": 5,
  "rollback_to_version": 4
}
```

Rollback is allowed only when the requested retained version exists and has not expired. It is atomic and creates a new monotonically increasing active version; it does not reset the active version to `4`. Success returns `200` with metadata and `restored_from_version: 4`. Missing/expired history returns `409 KEY_ROLLBACK_UNAVAILABLE`; stale active version returns `409 KEY_VERSION_CONFLICT`.

## 5. Gemini operation contracts

### 5.1 Generate

`POST /api/v1/gemini/generate`

```json
{
  "prompt": "Analyze the supplied document context.",
  "system_instruction": "Return only information supported by the document.",
  "response_schema": null
}
```

- `prompt` is required and non-empty.
- `system_instruction` is optional.
- `response_schema` is optional and must be a JSON Schema object. When present, the backend requests `application/json` and passes the schema using Gemini's structured-output configuration. The client must not duplicate the schema in the prompt merely for transport.
- Temperature and model are server-owned. This route preserves existing feature prompts rather than rewriting them.

Success:

```json
{
  "ok": true,
  "request_id": "...",
  "data": {
    "text": "Generated response"
  },
  "meta": {
    "contract_version": "v1",
    "model": "gemini-2.5-flash-lite",
    "key_version": 5,
    "usage": {
      "input_tokens": 120,
      "output_tokens": 45,
      "total_tokens": 165
    }
  }
}
```

Usage values may be `null` when Gemini does not supply them. They are informational and must not contain content.

Structured-generation example:

```json
{
  "prompt": "Classify the question intent.",
  "response_schema": {
    "type": "object",
    "properties": {
      "operation": { "type": "string" },
      "target": { "type": "string" },
      "unit": { "type": "string" }
    },
    "required": ["operation", "target", "unit"]
  }
}
```

The returned `data.text` is the JSON text produced by Gemini so the Task 7 adapter can preserve the current desktop gateway interface.

### 5.2 OCR

`POST /api/v1/gemini/ocr`

```json
{
  "mime_type": "image/png",
  "image_base64": "<base64-encoded-image>",
  "prompt": "Transcribe all visible text in this image..."
}
```

- Supported MIME types are exactly `image/png` and `image/jpeg` in `v1`.
- The backend strictly decodes base64, verifies PNG/JPEG magic bytes match `mime_type`, and rejects empty or malformed data before Gemini is called.
- `prompt` is required so the current transcription-only prompt remains feature-owned during Task 7. It is subject to the normal prompt limit.
- The backend sets temperature to `0`. The response must be transcription only.

Success returns `data.text`, `meta.model`, `meta.key_version`, and token usage in the same shape as generation. Safety-blocked content returns `OCR_BLOCKED`; a successful response with no text returns `OCR_NO_TEXT`.

### 5.3 Embed

`POST /api/v1/gemini/embed`

```json
{
  "contents": [
    "title: example.pdf | text: First document chunk",
    "title: example.pdf | text: Second document chunk"
  ],
  "output_dimension": 768
}
```

- `contents` is required, ordered, and contains 1–32 non-empty strings.
- `output_dimension` must be `768`; it is explicit to detect incompatible clients but cannot select arbitrary dimensions.
- The server uses `gemini-embedding-2` with no generation-model fallback.
- The server preserves input order and requires exactly one 768-value finite numeric vector per input.

Success:

```json
{
  "ok": true,
  "request_id": "...",
  "data": {
    "vectors": [
      [0.0123, -0.0456],
      [0.0789, 0.0101]
    ]
  },
  "meta": {
    "contract_version": "v1",
    "model": "gemini-embedding-2",
    "key_version": 5,
    "dimension": 768,
    "item_count": 2,
    "usage": {
      "input_tokens": 42,
      "output_tokens": 0,
      "total_tokens": 42
    }
  }
}
```

The shortened vectors above are documentation placeholders. A real response must contain 768 values per vector. Vectors are returned to the authenticated desktop for local Qdrant indexing/search but are never logged or audited.

## 6. Models, fallback, timeout, retry, and cancellation

### Generation and OCR model order

1. `gemini-2.5-flash-lite`
2. `gemini-3.1-flash-lite`
3. `gemini-3.5-flash-lite`

The server advances only for:

- model not found or unsupported for the operation (`404`);
- server/provider failures (`5xx`);
- explicit model unavailable, service unavailable, temporary unavailable, or high-demand responses.

It must not advance for invalid/revoked key, permission, quota/rate limit, invalid input/image/schema, content blocking, timeout, cancellation, conflict, or any other `4xx` response. Each model is attempted at most once. There is no general automatic retry in `v1`; model fallback is the only retry-like behavior.

Embeddings always use `gemini-embedding-2` and do not try generation models.

### Timeout

Each upstream attempt has a hard **60-second** timeout. The complete endpoint also has a server execution deadline sufficient for validation plus the bounded fallback sequence. A timeout ends the operation immediately and does not advance to another model.

### Cancellation

- Before each upstream call, the backend checks whether the client connection is already gone and aborts when the hosting environment exposes that state.
- A disconnect after an upstream call starts is best-effort cancellation; PHP/shared hosting may not be able to terminate the provider request immediately.
- Timed-out or cancelled work is never retried or failed over.
- If a response can still be sent, cancellation uses `499 REQUEST_CANCELLED`. Otherwise only the safe audit outcome is recorded.

## 7. Validation and payload limits

Limits are checked before decrypting the active key or calling Gemini.

| Limit | `v1` value |
|---|---:|
| Maximum JSON request body | 12 MiB |
| `prompt` | 256,000 Unicode characters |
| `system_instruction` | 32,000 Unicode characters |
| Serialized `response_schema` | 32 KiB |
| JSON Schema nesting depth | 12 |
| Decoded OCR image | 8 MiB |
| OCR base64 field | constrained by 12 MiB body limit |
| Supported OCR MIME types | `image/png`, `image/jpeg` |
| Embedding items | 32 |
| Estimated embedding input | 24,000 tokens per request |
| One embedding content string | 64,000 Unicode characters |
| Successful generated/OCR text returned | 2 MiB UTF-8 |
| Upstream timeout per attempt | 60 seconds |

Embedding token estimation initially preserves the desktop rule `max(1, (character_count + 2) // 3)`. Task 5 may replace estimation with an exact provider-supported counter only if it does not permit more than Gemini accepts. Over-limit input returns `413 PAYLOAD_TOO_LARGE` for body/image/returned-text size and `422 VALIDATION_FAILED` for field/count/schema/token constraints.

## 8. Usage controls

Rate policy is keyed by authenticated user ID and, when present, active license ID. IP address may be an additional abuse signal but must not replace identity limits.

Initial configurable ceilings:

| Operation | Per identity | Daily ceiling | Concurrent per user |
|---|---:|---:|---:|
| Generate | 30 requests/minute | 500 requests/day | 2 |
| OCR | 10 requests/minute | 100 requests/day | 1 |
| Embed | 60 requests/minute | 5,000 items/day | 2 |

The deployment also enforces a configurable global concurrency ceiling, initially `10`. Administrators do not bypass gateway usage limits. Key-management validation has a separate limit of 5 attempts per admin per 15 minutes.

Task 10 may tune values without changing route or error shapes. Exceeding a time bucket returns `429 RATE_LIMITED` with `Retry-After` and `retry_after_seconds`. Exceeding concurrency returns `429 CONCURRENCY_LIMITED`. Usage counters must be updated server-side and must not trust client token/item claims.

## 9. Stable errors

| HTTP | Code | Retryable | Meaning |
|---:|---|:---:|---|
| 400 | `INVALID_JSON` | No | Body is not valid JSON. |
| 401 | `AUTH_REQUIRED` | No | Bearer token is missing/invalid/expired. |
| 403 | `ACCOUNT_INACTIVE` | No | User is disabled. |
| 403 | `ADMIN_REQUIRED` | No | Admin route called by a standard user. |
| 403 | `LICENSE_REQUIRED` | No | Required active license is absent. |
| 404 | `NOT_FOUND` | No | Route does not exist. |
| 409 | `KEY_VERSION_CONFLICT` | No | Optimistic version is stale. |
| 409 | `KEY_ROLLBACK_UNAVAILABLE` | No | Previous version is missing or expired. |
| 413 | `PAYLOAD_TOO_LARGE` | No | Body, decoded image, or response exceeds a hard limit. |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | No | OCR MIME type is unsupported. |
| 422 | `VALIDATION_FAILED` | No | Request fields/schema/counts are invalid. |
| 422 | `INVALID_IMAGE` | No | Image bytes are empty, malformed, or mismatch MIME. |
| 422 | `OCR_BLOCKED` | No | Gemini blocked OCR output. |
| 422 | `OCR_NO_TEXT` | No | Gemini returned no transcription. |
| 422 | `KEY_INVALID` | No | Submitted/active key is rejected or revoked. |
| 429 | `RATE_LIMITED` | Yes | Identity/time-bucket ceiling exceeded. |
| 429 | `CONCURRENCY_LIMITED` | Yes | Concurrent-operation ceiling exceeded. |
| 429 | `GEMINI_QUOTA_EXHAUSTED` | Yes | Central Gemini quota is exhausted. |
| 499 | `REQUEST_CANCELLED` | No | Client cancelled/disconnected when a reply remains possible. |
| 500 | `INTERNAL_ERROR` | Yes | Safe generic internal failure. |
| 503 | `GEMINI_KEY_NOT_CONFIGURED` | No | No active admin-managed key exists. |
| 503 | `GEMINI_MODEL_UNAVAILABLE` | Yes | All eligible fallback models are unavailable. |
| 503 | `GEMINI_NETWORK_ERROR` | Yes | Backend cannot reach Gemini. |
| 503 | `GEMINI_SERVICE_ERROR` | Yes | Provider failed without a safer category. |
| 504 | `GEMINI_TIMEOUT` | Yes | Upstream exceeded the deadline. |

Example safe failure:

```json
{
  "ok": false,
  "request_id": "...",
  "error": {
    "code": "GEMINI_KEY_NOT_CONFIGURED",
    "message": "AI service is not configured. Contact an administrator.",
    "retryable": false
  },
  "meta": { "contract_version": "v1" }
}
```

The backend may internally classify provider details, but public responses and `log_error()` calls must use the stable code and sanitized metadata—not exception messages or raw upstream responses.

## 10. Audit and observability contract

Audit writes are append-only and must not block a safe API response if the audit sink is temporarily unavailable; such failure is reported through a separate sanitized operational alert.

### Required event names

- `gemini.key.validation_succeeded`
- `gemini.key.validation_failed`
- `gemini.key.created`
- `gemini.key.updated`
- `gemini.key.rotated`
- `gemini.key.rollback_succeeded`
- `gemini.key.rollback_failed`
- `gemini.request.succeeded`
- `gemini.request.failed`
- `gemini.request.rate_limited`
- `gemini.request.cancelled`

### Allowed fields

- event name and UTC timestamp;
- request ID;
- actor/user ID and, for admin actions, actor email;
- license ID when used for authorization/rate limiting;
- operation (`generate`, `ocr`, `embed`, or key-management action);
- key version and non-secret fingerprint;
- selected model, fallback attempt count, result/error code;
- latency, input/output token counts when provided, embedding item count, and image byte count;
- source IP only under the deployment's retention/privacy policy.

### Forbidden fields

Raw or masked key input, encryption secrets/nonces/tags, Bearer/refresh tokens, authorization headers, complete request/response bodies, prompts/system instructions/schema values, document or conversation content, image/base64 data, transcriptions/generated text, embedding vectors, raw Google responses/errors, stack traces, and SQL connection data.

Operational logs follow the same forbidden-field rules. Secret-bearing request objects must never be passed as logger metadata.

## 11. Storage, encryption, and rotation requirements for Task 3

- Encrypt the active and retained rollback values at rest with an authenticated cipher using a deployment-managed encryption secret that is separate from the database and repository.
- Store ciphertext, nonce/IV, authentication tag as required by the chosen construction, key version, masked display value, HMAC fingerprint, state, timestamps, and actor IDs. Never store the plaintext key.
- Decrypt only in the operation-scoped backend service immediately before creating the server-to-Gemini request. Do not cache plaintext globally or in PHP sessions.
- Ensure status reads use metadata without decryption.
- Rotation, rollback, and optimistic version checks occur in database transactions with row locking or an equivalent atomic compare-and-swap.
- Backups may contain encrypted rows but never the deployment encryption secret. Audit exports contain no ciphertext or key material.
- Redact secret-like values before any exception reaches the existing top-level PHP handler. New Gemini routes must always emit the stable error envelope even while legacy routes retain their current response format.

## 12. Migration, compatibility, and deployment-copy behavior

1. Tasks 2–6 add backend/admin capabilities without removing or changing the current desktop key path.
2. Tasks 3–5 deploy database/storage and gateway routes first. An admin configures and validates the centralized key before desktop migration.
3. Task 6 adds the admin UI using the existing authenticated `api.ts` request/refresh pattern. The browser sends a newly entered key once and receives only masked metadata.
4. Task 7 replaces `GeminiGateway` transport with these authenticated routes while preserving feature prompts, progress, cancellation, localization, exact counting, local Qdrant, and response/error behavior.
5. Task 8 removes desktop key UI/persistence and performs one-time deletion of legacy `GOOGLE_API_KEY` values only after Task 7 is verified.
6. Task 9 removes the desktop Google SDK dependency only after the residual import scan is clean.
7. Backend/admin production deployment precedes the migrated desktop release. If the desktop release must be rolled back, roll back to the last compatible desktop while the new backend routes remain available; do not expose or copy the centralized key to restore compatibility.

`C:\xampp\htdocs\server-php-auth` is the sole editable development source for backend/admin implementation. Its `production/` directory is a deployment snapshot, not a second implementation. Build/copy deployable `public/`, `src/`, dependencies, migrations, and production configuration templates from the active source using the documented deployment process. Never patch active source and `production/` independently. Production secrets are provisioned directly in the deployment environment and are never copied into this desktop repository.

## 13. Task 2 acceptance checklist

- [x] Roles and authorization boundaries are defined.
- [x] Admin status, validate, create/update, rotate, and rollback routes are defined.
- [x] Generate, OCR, and embedding request/response schemas are defined.
- [x] Models, fallback eligibility, timeouts, retry, and cancellation are fixed to the Milestone 1 baseline.
- [x] Payload, image, schema, embedding, and output limits are explicit.
- [x] Per-user/license rate and concurrency controls have stable behavior.
- [x] Stable machine-readable errors and redaction requirements are defined.
- [x] Key encryption metadata, atomic rotation, optimistic concurrency, retention, and rollback are defined.
- [x] Safe audit events and forbidden fields are defined.
- [x] Migration order and active-source/deployment-copy behavior are defined.
- [x] Every response and audit path explicitly forbids returning the raw key.

Tasks 3–12 must implement this contract or record and approve a contract revision before diverging.
