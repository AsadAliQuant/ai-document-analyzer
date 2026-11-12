# Phase 4 / Milestone 2 / Task 4 — Acceptance

**Accepted locally:** 2026-11-12  
**Active backend:** `C:\xampp\htdocs\server-php-auth`

## Delivered

- `GET /api/v1/admin/gemini/key` — metadata-only masked status.
- `POST /api/v1/admin/gemini/key/validate` — submitted-key validation without storage.
- `PUT /api/v1/admin/gemini/key` — validate then optimistic create/update.
- `POST /api/v1/admin/gemini/key/rotate` — validate then atomic rotation with 24-hour rollback retention.
- `POST /api/v1/admin/gemini/key/rollback` — atomic restore as a new monotonically increasing version.
- Stable `v1` success/error envelopes and `X-Request-ID` parity.
- Admin-only access with stable unauthenticated, inactive-account, and non-admin errors.
- Strict JSON/object parsing and generic sanitized internal failures.
- Minimal Gemini REST validation using `gemini-2.5-flash-lite` and the `x-goog-api-key` header.
- Append-only secret-free key-management audits.
- Five key-validation attempts per admin per 15 minutes.
- Rerunnable Task 4 migration and fresh-install schema parity.
- Task 3 active-key decryption alias corrected (`auth_tag AS tag`).

## Verification completed

- PHP syntax lint passed for every Task 4 PHP file.
- `tests/GeminiKeyApiTest.php` passed.
- `tests/GeminiKeyServiceTest.php` passed with the local isolated database configuration, including create/update, optimistic conflict, rotation, rollback, operation-scoped decryption, expiry cleanup, and plaintext-at-rest checks.
- Local database migrations applied successfully and all three `gemini_key_*` tables confirmed.
- All five unauthenticated routes returned `401 AUTH_REQUIRED` before processing submitted keys.
- A standard user received `403 ADMIN_REQUIRED`.
- An admin status request returned `200`, `configured: false`, `state: missing`, and no decryption.
- A supplied UUID was returned identically in the `X-Request-ID` header and JSON body.
- Malformed JSON returned `400 INVALID_JSON`; an unknown `v1` route returned `404 NOT_FOUND`.
- A deliberately invalid submitted key returned `422 KEY_INVALID` and generated a secret-free `gemini.key.validation_failed` audit record.
- The sixth validation attempt inside the window returned `429 RATE_LIMITED` with `Retry-After` and `retry_after_seconds`.
- Temporary audit/rate-limit rows and key-store test data were cleared after verification; local status is back to an unconfigured key.
- `git diff --check` reported no whitespace errors.

## Boundaries retained

- Desktop key transport, UI, persistence, and Google SDK usage are unchanged until Tasks 7–9.
- General server-side generate/OCR/embed operations remain Task 5.
- The React admin settings panel remains Task 6.
- Broad operational usage controls remain Task 10; only the key-validation-specific limit was implemented here.
- No production deployment or production Gemini key configuration was performed.
