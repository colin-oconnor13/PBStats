# Notes for Claude (PBStats)

Personal DUPR tracker PWA for Colin OConnor (short DUPR id `Z49MRW`). Repo
**colin-oconnor13/PBStats**; started 2026-10-11 as a fresh-history copy of
[kyeill/pickleball](https://github.com/kyeill/pickleball). Static site, no build. Normally run
locally with `python tools/serve_local.py` (data in git-ignored `local/data/`); the committed
`data/` files are empty seeds. Displayed app name is "Dink Data" (tagline "your DUPR history, analysed"); the logo is a
lime pickleball whose holes form a rising trend line (`favicon.svg`, header SVG, `icons/`).
See README for the user-facing story; see LOG.md for change history.

**`site.json` is the only per-copy setting** (whose copy, where data goes, the Sync bookmark's
app URL and optional pinned DUPR player). `storage: "github"` (this repo) commits synced data to
`repo`; `storage: "browser"` (the shared copy) keeps each visitor's data in localStorage
`pb-data-v1`, shows a welcome card when empty, and swaps the GitHub save UI for Export / Import /
Delete. Code is meant to stay identical across copies: port changes by copying everything except
`site.json`, `data/`, README/CLAUDE/LOG. Run `python tools/build_bookmarklet.py` after editing
`site.json` (it reads app / duprId / duprCode from there).

## Architecture
- `index.html` — the whole app. Async IIFE: fetches `./data/data.json` then
  `./data/overrides.json`, merges committed overrides with `localStorage` (local wins), renders.
  **Six tabs** (`tab-<name>`, toggled in `render()`; internal id `analysis` is labelled "Trends"):
  *Overview* (grouped KPI **clusters** with tooltips + `SPARK` sparklines, the real rating line,
  `renderLatest` last day's games, Highlights teasers), *Trends* (recent rating changes, Form,
  goal, Performance by Event + Event Matches, by Date, Matchup Strength, `renderBuckets` opponent
  bands, Close Games, Streaks), *Opponents & Partners* (`renderIndex` expected-vs-actual from
  `MODEL`; `renderPeople` ranked lists with a `pplRecent` 60-day toggle + last-played; `renderChem`
  partner margin with/without; Standouts; predictor), *Matches* (the Match Log), *Highlights*
  (`renderHighlights`: upset index + notable results), *Guide*. `MODEL` is a logistic win curve
  fitted to the user's matches; <`PPL_MIN`=4 matches go to low-reliability lists; desktop tables
  become cards on phones. Collapsible sticky-when-collapsed filter bar (Year/Type/Level/Event/Partner). Charts
  use a real date x-axis; zoom is 3M/6M/1Y + All + years. Matchup + event tables share a
  "DUPR actual / DUPR now" basis toggle (global `basis`). Clean-up panel edits events
  (rename/merge-by-name, Type, Level, hide, 🏆-highlight), hides one-off partners, and saves
  overrides to the repo via the GitHub Contents API (token in localStorage `gh-token`).
  Standard sans throughout (Archivo for headings; no monospace). SW `sw.js` (network-first,
  cache bumped on shell changes). Logo: lime pickleball whose holes form a rising trend line (header SVG + `favicon.svg` + `icons/`).
- **Sync** — `tools/sync_bookmarklet.js` runs on dashboard.dupr.com (login cookie works there),
  shows a progress panel on that page, fetches profile + paged history + every other player's
  current rating (6 parallel), trims to the fields `duprToData` reads, gzips, and opens the app in
  the same tab at `?sync=1#pb=<z|j><base64url>` (no pop-up: phones pause background tabs). The
  app's `decodePb()` reads it, strips it from the URL, and `handle()` builds data.json, refuses
  fewer matches, skips unchanged, **asks before saving** (crafted links), prompts for a gh-token
  inline if missing, commits via `ghPutJSON()` and stashes `pb-fresh` in sessionStorage. Old
  pop-up bookmarks still postMessage after `pb-ready` (origins checked) into the same `handle()`.
  After editing the bookmarklet source run `python tools/build_bookmarklet.py`: it writes `sync.js`
  (the source with site.json values filled in) and puts a ~300-char **loader** bookmark in index.html
  that adds `<site>/sync.js` to the DUPR page (the full 9 KB inline code got truncated at ~2,000
  chars when pasted into Chrome-for-Android bookmarks). `serve_local.py` still inlines the full code.
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
