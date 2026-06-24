# API Changelog

> **Read before upgrading.** Each entry describes what changed in the backend and what action the frontend/app **must take** to remain compatible.

## [2.0.0] — 2026-06-24

### Version Type
- **MAJOR (breaking)** — authentication is now required on endpoints that were previously public.

### What Changed
- 🔒 **Every endpoint now requires a Bearer token, except `/auth/*`.**
  Previously-public routes (`GET /matches`, `GET /matches/{id}`,
  `GET /matches/{id}/prediction`, `GET /matches/{id}/preview`,
  `GET /matches/{id}/watch`, `GET /subscriptions/plans`) now return **401**
  without a valid `Authorization: Bearer <token>` header.
- 🔒 `POST /webhooks/bkash` and `WS /ws/matches/{id}` are now behind the same
  guard. **Why:** these are server-to-server / handshake routes that cannot send
  a user JWT — integrators must supply a service token (webhook) or a
  query-param token (WebSocket) once those auth paths are wired up.
- ✉️ Email verification flow added (additive): `POST /auth/verify-email` now
  takes `{ "email", "verification_code" }`, plus new `POST /auth/resend-verification`.
- `X-API-Version` header is now `2.0.0`.

### Endpoints Added/Changed/Removed
- **Changed (now auth-required):** `GET /matches`, `GET /matches/{id}`,
  `GET /matches/{id}/prediction`, `GET /matches/{id}/preview`,
  `GET /matches/{id}/watch`, `GET /subscriptions/plans`, `POST /webhooks/bkash`,
  `WS /ws/matches/{id}`.
- **Changed (request body):** `POST /auth/verify-email` → body `{ email, verification_code }`.
- **Added:** `POST /auth/resend-verification`.

### Client Action Required
1. **Send `Authorization: Bearer <token>` on every request except `/auth/*`.**
   Audit all calls — any unauthenticated call to `/matches*` or
   `/subscriptions/plans` will now fail with 401.
2. Regenerate the typed client from `contracts/openapi.json` and re-pin to
   `CONTRACT_VERSION: 2.0.0`.
3. Update the email-verification call to send `{ email, verification_code }`;
   wire a "resend code" action to `POST /auth/resend-verification`.
4. For realtime: pass the auth token to `/ws/matches/{id}` (query param) so the
   handshake is accepted.

### Migration Note
This is a coordination event (§7): do not deploy backend to prod until
`aimp-web` and `aimp-app` have branches reconciled to 2.0.0, or ship behind a
version-gated route supporting N-1.

---

## [1.0.0] — 2026-06-24

### Released
Initial release of AI Match Predictor backend.

### What Changed
- ✅ Initial API surface with 15 core endpoints
- ✅ Response envelope standard: `{ "success": true, "data": {}, "error": null, "meta": {} }`
- ✅ All responses include `X-API-Version: 1.0.0` header
- ✅ Supabase authentication integration
- ✅ WebSocket support for realtime match updates
- ✅ Standard prediction game flow

### Endpoints Added
- `GET /matches` — List matches
- `GET /matches/{id}` — Match detail
- `GET /matches/{id}/prediction` — Win probability + factors
- `GET /matches/{id}/preview` — AI-generated preview
- `GET /matches/{id}/watch` — Legal watch targets
- `WS /ws/matches/{id}` — Realtime score + probability
- `POST /predictions` — Submit prediction
- `GET /leaderboard` — User rankings
- `GET /me` — User profile
- `GET /me/points` — Points/streak stats
- `GET /me/accuracy` — Accuracy metrics
- `POST /chat` — AI chat Q&A
- `GET /subscriptions/plans` — Available plans
- `POST /subscriptions` — Start subscription
- `POST /webhooks/bkash` — bKash billing callback

### Client Action Required
1. ✅ Generate typed client from `contracts/openapi.json`
2. ✅ Pin to `CONTRACT_VERSION: 1.0.0`
3. ✅ Implement authentication with Supabase JWT
4. ✅ Test WebSocket connection to `/ws/matches/{id}`
5. ✅ Handle standard response envelope in all requests

---

## Template for Future Changes

```markdown
## [X.Y.Z] — YYYY-MM-DD

### Version Type
- MAJOR (breaking)
- MINOR (additive)
- PATCH (non-contract)

### What Changed
- Brief description of changes
- Explain the "why" behind breaking changes

### Endpoints Added/Changed/Removed
- Specific endpoint changes with before/after

### Client Action Required
1. Exact step-by-step actions the frontend/app must take
2. Be explicit (e.g., "update TypeScript type X from Y to Z")
3. Include any new environment variables or config needed
```

---

## Versioning Rules

| Type | Rule | Example |
|---|---|---|
| **MAJOR** | Breaking change (removed/renamed field/endpoint, changed type, changed business rule in §2) | 1.0.0 → 2.0.0 |
| **MINOR** | Additive, backward-compatible (new endpoint/optional field) | 1.0.0 → 1.1.0 |
| **PATCH** | Non-contract (docs, perf, internal) | 1.0.0 → 1.0.1 |

---

## When to Update This File

You **MUST** update this file whenever:
1. ✅ An endpoint is added, removed, or renamed
2. ✅ A request/response field is added, removed, or changed type
3. ✅ A core business rule (§2 of CLAUDE.md) is changed
4. ✅ A breaking change requires client-side action

You do **NOT** need to update for:
- Internal refactoring
- Performance improvements
- Bug fixes that don't change the contract
- Documentation updates

---

## Release Checklist

Before merging any API change:
- [ ] Update code
- [ ] Regenerate `contracts/openapi.json` (`make contract`)
- [ ] Bump `contracts/CONTRACT_VERSION`
- [ ] Add entry to this file with client actions
- [ ] Tag release as `contract-vX.Y.Z`
- [ ] Notify `aimp-web` and `aimp-app` maintainers
