# AI Match Predictor - Backend Summary

## 1. What This Service Does

Backend for a **Bangladeshi VAS** (Value Added Service) offering AI-powered **cricket/football prediction, analytics, and entertainment** — NOT a betting product.

**Key Responsibilities:**
- ✅ Identity verification (Supabase Auth JWTs; social logins)
- ✅ Live match data ingestion from licensed sports-data API
- ✅ Win-probability model + RAG/LLM explanation layer
- ✅ Prediction game scoring, points, streaks, accuracy tracking
- ✅ Non-cash reward engine (badges, free premium days, giveaway entries)
- ✅ Subscriptions & paywall (bKash / telco billing)
- ✅ "Watch Live" legal deep-link targets (no video hosting)
- ✅ Realtime fan-out (live score + probability) over WebSocket

---

## 2. Core Business Rules (Authoritative - Contract Level)

| Rule | Detail |
|---|---|
| **Money** | Stored as integer **poisha** (1 BDT = 100 poisha). Never floats. |
| **Time** | Stored `timestamptz` UTC; presentation layer converts to `Asia/Dhaka`. |
| **No gambling** | No money staked to predict; no cash/cash-equivalent payout. Rewards are status/content only. |
| **Probability honesty** | Win probability is always a range/confidence, never "certainty". LLM narrates model output, never invents stats. |
| **Vendor key** | The sports-data API key lives server-side ONLY. Clients never call the vendor. |
| **Watch links** | Allowlist of licensed providers only. Deep-link out; never host/proxy streams. |

> ⚠️ **Changing any of these is a BREAKING change (§7)**

---

## 3. Domain Logic

### 3.1 Predictions (The AI) - Two Layers
1. **Quantitative Model** — Calibrated win probability from:
   - Recent form, venue, H2H records, batting depth, toss, pitch/weather
   - This is the **trusted number**
   
2. **RAG/LLM Layer** — Receives model numbers + retrieved history → produces:
   - Match previews
   - Chat explanations
   - **Prompt contract:** Model is a narrator of supplied stats, NEVER their source

### 3.2 Prediction Game
- Users submit **free daily predictions**:
  - Winner / Top scorer / Total runs / MOTM / First wicket
- On settlement: Predictions scored → points awarded → accuracy recomputed
- **Streaks** unlock non-cash surprise rewards (§3.3)
- **Premium tiers** get more predictions, advanced analytics, bigger multipliers

### 3.3 Reward Engine (Compliant "Surprise")
Rewards are:
- Badges
- Rank bumps
- **Free premium days**
- Content unlocks
- Sponsor-giveaway entries

> ⚠️ **NEVER cash, NEVER proportional to a stake**

### 3.4 Subscriptions & Paywall
- **Plans:** Daily 10 / Weekly 50 / Monthly 99·149·199·299 BDT
- **Billing:** bKash / telco carrier billing
- **Webhook** activates entitlement
- **Premium features** gated by active entitlement

### 3.5 Live Data + Realtime
Flow: Vendor feed → normalized → Postgres (source of truth) → Redis pub/sub → WebSocket fan-out

**Key:** Clients connect to us, not the vendor directly
- Win probability recomputed on each material event (wicket/over)
- Pushed on the same WebSocket channel

### 3.6 Watch Live
- `GET /matches/{id}/watch` returns ordered legal watch targets
- Empty list (no licensed target) is a **valid response**, NOT an error

---

## 4. API Surface (Contract v1.0.0)

### Response Envelope (Standard)
```json
{ "success": true, "data": {}, "error": null, "meta": {} }
```
**Every response carries header:** `X-API-Version: <CONTRACT_VERSION>`

### API Endpoints

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

---

## 5. Cross-Repo Contract Sync

### Source of Truth
- **`contracts/openapi.json`** — Generated from FastAPI on every build
- **`contracts/CONTRACT_VERSION`** — Semver string

### Version Bump Rules
- **MAJOR** = breaking (removed/renamed field/endpoint, changed type, changed business rule in §2)
- **MINOR** = additive, backward-compatible (new endpoint/optional field)
- **PATCH** = non-contract (docs, perf, internal)

### When You Change the API or Business Rule — MUST DO:
1. ✅ Update code + regenerate `contracts/openapi.json`
   - Verify locally with `make contract`
2. ✅ Bump `contracts/CONTRACT_VERSION` per rules above
3. ✅ Append entry to **`API_CHANGELOG.md`** (broadcast board) with:
   - New version
   - What changed
   - **Exact action each client must take**
4. ✅ Tag release `contract-vX.Y.Z` so clients can pin to it

### How Clients Pick It Up
- `aimp-web` and `aimp-app` pin a `CONTRACT_VERSION`
- Regenerate typed clients from `contracts/openapi.json`
- Their CI fails if spec drifts → forces deliberate upgrade + changelog read
- **MAJOR bump = coordination event:** Don't deploy until clients reconciled to new version

---

## 6. Technology Stack

- **Framework:** FastAPI (async), Pydantic v2
- **Database:** Postgres/Supabase
- **Cache:** Redis
- **Vector Store:** Chroma/FAISS → Pinecone
- **Auth:** Supabase JWT

---

## 7. Project Structure
```
/app
  /api        routers (auth, matches, predictions, chat, billing, users)
  /core       config, security (JWT verify), deps
  /models     pydantic + db models
  /services   prediction, rag, ingestion, billing, rewards
  /ml         model artifacts + inference
  /rag        index build + retrieval

/contracts
  openapi.json (generated)
  CONTRACT_VERSION

API_CHANGELOG.md
CLAUDE.md
```

---

## 8. Key Don'ts (Critical)
- ❌ Don't change §2 rules without MAJOR bump + changelog entry
- ❌ Don't expose vendor key or let LLM invent stats
- ❌ Don't add non-licensed source to `watch_providers`
- ❌ Don't return 404 when match has no watch target — return empty list
- ❌ Don't merge API change without updating `API_CHANGELOG.md`

---

## Status: ✅ Development Environment Ready
- ✅ Virtual environment created
- ✅ Dependencies installed (FastAPI, Uvicorn, Supabase, Redis, Pydantic v2)
- ✅ Environment configured with Supabase credentials
- ✅ Server running on http://localhost:8001
- ✅ API docs available at /docs
