# Notes for Claude (PBStats)

Personal DUPR tracker PWA for Colin OConnor (short DUPR id `Z49MRW`). Repo
**colin-oconnor13/PBStats**; started 2026-10-11 as a fresh-history copy of
[kyeill/pickleball](https://github.com/kyeill/pickleball). Static site, no build. Normally run
locally with `python tools/serve_local.py` (data in git-ignored `local/data/`); the committed
`data/` files are empty seeds. Displayed app name is "Pickleball".
See README for the user-facing story; see LOG.md for change history.

## Architecture
- `index.html` — the whole app. Async IIFE: fetches `./data/data.json` then
  `./data/overrides.json`, merges committed overrides with `localStorage` (local wins), renders.
  **Three tabs** — *Overview* (KPIs, Performance by Event, per-event rating chart, event-scoped
  match list), *Analysis* (overall rating chart, Performance by Matchup Strength, full Match
  Log) and *Opponents & Partners* (`renderIndex`: expected-vs-actual index from `MODEL`, a
  logistic win curve fitted to the user's matches; `renderPeople`: per-opponent or per-partner
  `agg`, ranked; <`PPL_MIN`=4 matches go to a separate low-reliability list; desktop only). Collapsible sticky-when-collapsed filter bar (Year/Type/Level/Event/Partner). Charts
  use a real date x-axis; zoom is All + years only. Matchup + event tables share a
  "DUPR actual / DUPR now" basis toggle (global `basis`). Clean-up panel edits events
  (rename/merge-by-name, Type, Level, hide, 🏆-highlight), hides one-off partners, and saves
  overrides to the repo via the GitHub Contents API (token in localStorage `gh-token`).
  Standard sans throughout (Archivo for headings; no monospace). SW `sw.js` (network-first,
  cache bumped on shell changes). Lime pickleball logo (header SVG + `favicon.svg` + `icons/`).
- **Sync** (replaced the GitHub Action, 2026-09-16) — `tools/sync_bookmarklet.js` runs on
  dashboard.dupr.com (login cookie works there), opens the app with `?sync=1` (local server or Pages), fetches profile +
  paged history + every opponent's current rating (6 parallel), and `postMessage`s the raw data
  after the app sends `pb-ready` (origins checked both ways). The app's `duprToData()` (a verified
  port of the old Python transform) builds data.json, refuses to save if it has fewer matches,
  skips the commit if unchanged, then commits via `ghPutJSON()` (Contents API, gh-token) and
  stashes it in sessionStorage `pb-fresh` (used while `syncedAt` is newer than Pages' copy).
  After editing the bookmarklet source run `python tools/build_bookmarklet.py` (escapes % & ").
  data.json: `{player:{id,name,currentDoubles(number)}, generated, syncedAt, matches:[...]}`.
- `data/overrides.json` — durable user edits:
  `{meta:{events:{<rawEventStr>:{name,type,level,hidden}}, partnersHidden:[]}, tags:{}}`.
  Edited in-browser, saved to the repo (Save to GitHub) or exported/committed.

## DUPR API facts (api.dupr.com, `dupr_at` cookie JWT; CORS-locked to dashboard.dupr.com)
- **Changed ~2026-09-07:** host moved `api.dupr.gg` → **`api.dupr.com`**; auth moved from
  `Authorization: Bearer` to the **`dupr_at` cookie** (httpOnly JWT). Old tokens 401'd. Nothing in
  localStorage/sessionStorage/`document.cookie`/IndexedDB holds it, and Chrome's "Copy as cURL"
  omits the Cookie header — read it from DevTools → Application → Cookies, or from the request's
  Headers panel. The dashboard also sends `X-Dupr-Client-Capabilities: totp,webauthn`.
  Unauthenticated calls return `401 "Please provide a valid API key."`
- **Token lifetime:** JWT `exp` is only an upper bound — DUPR **revokes on logout**, so a token
  can 401 while `exp` still shows weeks left. The profile GET is the real liveness check.
  Tokens are NOT a password. `POST /auth/v1.0/login` `{email,password}` exists (unused).
- Match history: dashboard uses `POST /player/v1.0/{id}/history` with
  `{filters:{eventFormat:null},limit,offset,sort:{order:"DESC",parameter:"MATCH_DATE"}}`;
  the bookmarklet falls back to legacy `POST /match/v1.0/history` `{limit,offset}` on 404/405.
  Page size 25. Per-match scores, winner, players, and each team's
  `preMatchDoubleRating`+`matchDoubleRatingImpact` per player (rating curve reconstructed from these).
- `GET /player/v1.0/{id}` — profile incl. current doubles rating (comes back as a **string** →
  coerce to number).
- A `rating-history` endpoint exists (seen in dashboard traffic; exact path/method unverified) —
  could replace the reconstructed rating curve.
- **Copied tokens do NOT work off-browser** (tested exhaustively from GitHub Actions: cookie
  at / at+rt ignored, Bearer → "Invalid token", same on api.dupr.gg) — hence the in-browser sync.

## Metrics (inherited from the original app)
`Value = Win%(0-100) + 25·Pts%(0-1) + 50·(oppDUPR − teamDUPR)` — last term is strength of
schedule; `VALUE_K=50`; it follows the then/now toggle. Pts% pooled. Norm margin = avg per-game
margin rescaled to 11 (target 15 if winner score ≥15 else 11). Matchup bands on
(you+partner)/2 − opp avg DUPR, cutoffs ±0.10 / ±0.25. Only two event types: Tournament / League
(legacy Ladder/Other coerce to League).

## Refresh history
The original app tried a copied token, then a daily GitHub Action; both stopped working when
DUPR moved to the httpOnly cookie (2026-09), hence the in-browser bookmark. DUPR's 2FA prompt
only affects logging in at dashboard.dupr.com; the bookmark uses the session afterwards. Claude
never handles the user's DUPR token, password or 2FA code.
