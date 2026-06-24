# AI Match Predictor — Backend (FastAPI)

> Repo: `aimp-backend` · Pairs with `CLAUDE.md` in this repo.
> **This repo is the single source of truth for the API contract and all business rules.**
> Frontend (`aimp-web`) and app (`aimp-app`) are downstream consumers. If logic or the API
> changes here, the contract version bumps and the change is broadcast via `API_CHANGELOG.md`
> (see §7). Read that section before changing any endpoint or rule.

## 1. What this service does

Backend for a Bangladeshi VAS: an AI-powered cricket/football **prediction, analytics, and
entertainment** product. It is **not** a betting product — no real-money wagering, no cash
payouts on outcomes. Revenue is subscriptions, distributed via bKash/telco.

Responsibilities owned here:
- Identity (verify Supabase Auth JWTs; social logins)
- Live match **data** ingestion from a licensed sports-data API
- Win-probability model + RAG/LLM explanation layer
- Prediction **game** scoring, points, streaks, accuracy
- Non-cash reward engine (badges, free premium days, giveaway entries)
- Subscriptions & paywall (bKash / telco billing)
- "Watch Live" legal deep-link targets (no video hosting)
- Realtime fan-out (live score + probability) over WebSocket

## 2. Core business rules (authoritative)

| Rule | Detail |
|---|---|
| Money | Stored as integer **poisha** (1 BDT = 100 poisha). Never floats. |
| Time | Stored `timestamptz` UTC; presentation layer converts to `Asia/Dhaka`. |
| No gambling | No money staked to predict; no cash/cash-equivalent payout on a winning prediction. Rewards are status/content only. |
| Probability honesty | Win probability is always a range/confidence, never "certainty". LLM never invents the number — it narrates the model's output. |
| Vendor key | The sports-data API key lives server-side only. Clients never call the vendor. |
| Watch links | Allowlist of licensed providers only. We deep-link out; we never host/proxy streams. |

These rules are contract-level. Changing any of them is a **breaking** change (§7).

## 3. Domain logic

### 3.1 Predictions (the AI)
Two separate layers:
1. **Quantitative model** — calibrated win probability from structured features (recent form,
   venue, H2H, batting depth, toss, pitch/weather). This is the trusted number.
2. **RAG/LLM layer** — receives the model's numbers + retrieved history and produces the match
   preview and chat explanations. Prompt contract: *the model is a narrator of supplied stats,
   never their source.* An eval set guards against hallucination regressions.

### 3.2 Prediction game
- User submits free daily predictions (winner / top scorer / total runs / MOTM / first wicket).
- On settlement, each prediction is scored → points awarded → accuracy recomputed.
- Streaks of correct predictions unlock **non-cash** surprise rewards (§3.3).
- Premium tiers get more daily predictions, advanced analytics, bigger reward multipliers (status, not cash).

### 3.3 Reward engine (compliant "surprise")
Rewards are: badges, rank bumps, **free premium days**, content unlocks, sponsor-giveaway entries.
Never cash, never proportional to a stake. This is the engagement loop, kept legal.

### 3.4 Subscriptions & paywall
- Plans: daily 10 / weekly 50 / monthly 99·149·199·299 BDT (poisha internally).
- Billing via bKash / telco carrier billing; webhook activates entitlement.
- Premium features (advanced analytics, more predictions) gated by active entitlement.

### 3.5 Live data + realtime
- One ingestion worker per live match pulls/subscribes to the vendor feed → normalizes →
  Postgres (source of truth) → Redis pub/sub → WebSocket fan-out. Clients connect to us, not the vendor.
- Win probability recomputed on each material event (wicket/over) and pushed on the same channel.

### 3.6 Watch Live
- `GET /matches/{id}/watch` returns ordered legal watch targets from `live_links` + `watch_providers`.
- Empty list (no licensed target) is a valid response, not an error.

## 4. API surface (contract v1.0.0)

All responses use the standard envelope:
```json
{ "success": true, "data": {}, "error": null, "meta": {} }
```
Every response carries header `X-API-Version: <CONTRACT_VERSION>`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/matches` | List matches (filter by league/status/date) |
| GET | `/matches/{id}` | Match detail |
| GET | `/matches/{id}/prediction` | Win prob + key factors + expected score |
| GET | `/matches/{id}/preview` | AI-generated preview (RAG) |
| GET | `/matches/{id}/watch` | Legal watch targets (deep-link) |
| WS | `/ws/matches/{id}` | Realtime score + probability stream |
| POST | `/predictions` | Submit a game prediction |
| GET | `/leaderboard` | Ranked users |
| GET | `/me` | Profile |
| GET | `/me/points` | Points / streak |
| GET | `/me/accuracy` | Accuracy stats |
| POST | `/chat` | AI chat Q&A (RAG) |
| GET | `/subscriptions/plans` | Plans + pricing |
| POST | `/subscriptions` | Start a subscription (bKash) |
| POST | `/webhooks/bkash` | Billing callback (server-to-server) |

## 5. Stack & layout
- FastAPI (async), Pydantic v2, Postgres/Supabase, Redis, vector store (Chroma/FAISS→Pinecone).
```
/app
  /api        routers (auth, matches, predictions, chat, billing, users)
  /core       config, security (JWT verify), deps
  /models     pydantic + db models
  /services   prediction, rag, ingestion, billing, rewards
  /ml         model artifacts + inference
  /rag        index build + retrieval
/contracts    openapi.json (generated), CONTRACT_VERSION
API_CHANGELOG.md
```

## 6. Local dev
```bash
uv venv && source .venv/bin/activate   # or python -m venv
uv pip install -r requirements.txt
cp .env.example .env                   # Supabase, Redis, vendor key, bKash creds
uvicorn app.main:app --reload
# OpenAPI: http://localhost:8000/openapi.json  ·  Docs: /docs
```

## 7. Cross-repo contract sync — READ BEFORE CHANGING THE API

This is how `aimp-web` and `aimp-app` "simultaneously know" about backend changes.

### Source of truth
- `contracts/openapi.json` — generated from FastAPI on every build.
- `contracts/CONTRACT_VERSION` — semver string. Bump rules:
  - **MAJOR** = breaking (removed/renamed field or endpoint, changed type, changed business rule in §2).
  - **MINOR** = additive, backward-compatible (new endpoint/optional field).
  - **PATCH** = non-contract (docs, perf, internal).

### When you change the API or a business rule, you MUST:
1. Update code + regenerate `contracts/openapi.json` (CI does this; verify locally with `make contract`).
2. Bump `contracts/CONTRACT_VERSION` per the rules above.
3. Append an entry to **`API_CHANGELOG.md`** (the broadcast board) using the template there:
   the new version, what changed, **and the exact action each client must take**.
4. Tag the release `contract-vX.Y.Z` so clients can pin to it.

### How clients pick it up
- `aimp-web` and `aimp-app` pin a `CONTRACT_VERSION` and regenerate their typed clients from
  `contracts/openapi.json` (raw URL or CI artifact). Their CI fails if the spec drifts from the
  pin, forcing a deliberate upgrade + changelog read.
- A **MAJOR** bump is a coordination event: do not deploy backend to prod until both clients have
  a branch reconciled to the new version, OR ship behind a version-gated route and support N-1.

### For Claude Code agents
When an agent edits this repo and touches the API/rules, it follows steps 1–4 above and writes the
client action into `API_CHANGELOG.md`. Agents working in `aimp-web` / `aimp-app` are instructed
(in their READMEs) to read `API_CHANGELOG.md` first and apply the listed action. The changelog is
the contract between the repos.

## 8. Don'ts
- Don't change §2 rules without a MAJOR bump + changelog entry.
- Don't expose the vendor key or let the LLM invent stats.
- Don't add a non-licensed source to `watch_providers`.
- Don't return 404 when a match simply has no watch target — return an empty list.
- Don't merge an API change without updating `API_CHANGELOG.md`.