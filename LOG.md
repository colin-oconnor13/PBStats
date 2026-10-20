# Change log — PBStats

Newest first. Repo `colin-oconnor13/PBStats`.

## 2026-10-20 — hide owner-only pieces when viewing another player
- When a scouted player is being viewed (`VIEW` set → `VIEWING_OTHER`, root `data-viewing="other"`),
  the pieces that are "you"-centric or need your full career history are hidden (CSS), since we
  only hold the scouted player's capped recent history: the **matchup predictor**, **rating goal**,
  the Overview **teasers**, and the whole **Highlights** tab (button + panel). `renderHighlights`
  is also skipped in that mode. Everything that recomputes from the viewed player's matches
  (KPIs, rating line, Trends, the people lists, Standouts, chemistry) still shows. SW rj-v76.

## 2026-10-20 — page-level 60-day filter (Opponents + Matches)
- Replaced the per-person "recent" toggle with a **page-level Last-60-days report filter**
  (`recent60` / `inRecent60`) shown at the top of the **Opponents & Partners** page and the
  **Matches** tab, synced between the two (`.recentT` toggles). It limits the *matches* feeding
  those pages (`recentList`), so opponent/partner stats and the match log reflect only recent
  play. Overview, Trends and Highlights are untouched — Highlights keeps its own window. SW rj-v75.

## 2026-10-20 — Highlights: recent/lifetime, peak-low, clickable
- **Recent · 60 days / All-time toggle** on Highlights (`hlWindow`): the upset index and notable
  results recompute over the chosen window (from `M`, independent of the top filters).
- **Your rating, all-time** card: peak and lowest DUPR with their dates, plus current.
- **Notable results and the Overview teasers are clickable** — `goToMatch(matchId)` switches to
  Matches, un-collapses the log, scrolls to that match (now tagged `data-mid`) and flashes it.
- The **Recent · 60d toggle moved onto the Opponent/Partner Index** card header (it already
  filtered both the Index and the ranked lists; now it's prominent there). SW rj-v74.

## 2026-10-20 — layout rebuild, phase 3: Highlights tab
- New **Highlights** tab (6th): **upset index** (upset wins = won as rating underdog by `diffPre`;
  given up = lost as favorite; net; biggest upset) and **notable results** (biggest upset win,
  toughest loss on paper, biggest win, closest call) — `renderHighlights`.
- Overview gains a **Worth a look** teaser strip (biggest upset, biggest win, current streak via
  `streakNow`) with a button to the Highlights tab (`goTab`).
- Guide tab list and CLAUDE.md updated to the six-tab structure. SW rj-v73.

## 2026-10-20 — layout rebuild, phase 2: new analytics
- **Opponent strength buckets** ("Who you struggle with") on Trends: win % + avg margin against
  opponents grouped by their actual DUPR (<3.0 … >4.5), by `oppThen` (`renderBuckets`).
- **Opponents & Partners: Recent · 60d toggle** (`pplRecent`/`recentOk`) filtering the Index and
  ranked lists by last-played; the ranked list now shows the date **and** relative "3d ago"
  (`lastPlayedTxt`).
- **Partner chemistry** card (`renderChem`): your average per-11 margin *with* each partner vs
  your overall baseline, as diverging bars (4+ matches). SW rj-v72.

## 2026-10-19 — layout rebuild, phase 1: tabs + Overview
Approved via mocks. **Tabs:** Overview / Trends (was Analysis) / Opponents & Partners / Matches /
Guide. The **Match Log moved to its own Matches tab**; **Performance by Event + Event Matches
moved to Trends**.
- **Overview redesigned:** grouped KPI **clusters** (Rating / Results / Context) with hover
  tooltips and **sparklines** (`SPARK`, filter-independent chronological buckets; `sparkSvg`); the
  real **Rating Over Time** line (moved from Analysis, with event markers) replaces the misleading
  one-dot-per-event chart (`drawEvents` dropped); and **Latest matches** (`renderLatest`) showing
  the most recent day you played. SW rj-v71.

## 2026-10-19 — rating goal tracker + Standouts
- **Rating goal** card on Analysis: enter a target DUPR and it estimates how many matches (and
  wins) to get there from your recent win rate and per-win/per-loss rating change. Handles
  "already there" and "not on current pace" (with the win rate you'd need). Rough, filter-independent.
- **Standouts** card on Opponents & Partners: best / toughest partner and favourite opponent /
  nemesis by wins-vs-expected (4+ matches), at a glance (`renderStandouts`, reuses `expStats`).
  Follows the filters. SW rj-v70.

## 2026-10-19 — sortable Event table + player search
- **Performance by Event** headers are clickable to sort (Event / M / Win% / Pts% / Margin /
  Value / DUPR / Change), with a ▲/▼ arrow; re-click toggles direction (`evSort`). Default stays
  newest-event-first.
- **Player search** box on Opponents & Partners filters the Index and the ranked lists by name
  (`pplQuery` / `matchName`), live as you type — helps with 45+ rows and the small-sample list.
  SW rj-v69.

## 2026-10-19 — matchup predictor
- New card at the top of Opponents & Partners: enter your partner and two opponents (pick a
  player from your history or type a rating) and it shows your expected win % and margin, using
  `MODEL` (the win curve fitted to your matches). "You" defaults to your current DUPR. Independent
  of the filters; players come from your own match history. SW rj-v68.

## 2026-10-19 — clarity cleanup (from AI review)
- **Rating changes now shown as DUPR deltas** (`+0.388`, `+0.011`) instead of `+388 pts` — ends
  the clash with "Pts Won" (rally points). `ptsTxt` reformatted; affects every Change / DUPR-change
  cell, the Form hover and Recent-rating-change tiles.
- **Name casing**: `nameCase()` title-cases all-lowercase DUPR names ("clark janssen" → "Clark
  Janssen") in the viewing bar and scout messages, without mangling cased ones ("OConnor").
- **Beat-expectations tile** relabelled **Rating rose** with an unambiguous sub ("20 of 123 losses
  too") so the % and the loss note no longer read as the same measure.
- **Recent rating changes** gains a caption: Per event/date/match = typical swing; per win/loss =
  average signed change.
- **Match log** now reads "vs <opponents> … with <partner> (rating)" instead of a bare bracket.
- **Close Games**: the "Deciding game 3" row is hidden when there are no best-of-3 deciders.
- **Guide**: notes Value can exceed 100, and ties "Rating rose" to "beat expectations". SW rj-v67.

## 2026-10-19 — DUPR page link in the viewing bar
- The 👁 Viewing bar now shows a **DUPR page ↗** link to the current player's DUPR profile
  (`dashboard.dupr.com/dashboard/player/<id>`), for your own view and any scouted player. Only
  rendered when the id is numeric. (The bar appears once you've pulled in another player.) SW rj-v66.

## 2026-10-19 — clear viewed players from Clean up
- Clean up data now has a **Viewed players** section (shown when any other players are cached)
  with a **Clear all viewed players** button (two-tap confirm). It empties the on-device
  `pb-scouts` IndexedDB store and the `pb-view` key, leaving your own matches untouched — the
  one-click version of the earlier dev-tools-only clear. Works in both GitHub and browser modes.
  SW rj-v65.

## 2026-10-19 — cap scouted players at 150 recent games
- "Me + my 14 most recent people" now caps each scouted player's history to their **150 most
  recent matches** (`SCOUT_CAP`); `getHist` takes a `cap` and stops paging once reached (history
  is newest-first, so the cap keeps the latest). Your own sync is unaffected. Shrinks the sync
  time and the URL payload. SW rj-v64.

## 2026-10-19 — desktop tables wrap instead of scrolling
- `thead th` now wraps (`white-space:normal`, bottom-aligned) so long headers like "Wins vs
  expected" / "Margin vs expected" stack to two lines instead of forcing the Opponents & Partners
  grids to scroll sideways.
- `.evname` and `.evtd` wrap too (were `nowrap` + ellipsis), so event names — e.g. the long
  Moorhead address row, and the event-label line under each date on Analysis → Performance by
  Date — show in full rather than being clipped or widening the column. Mobile (cards) unchanged.
  SW rj-v63.

## 2026-10-11 — "How to read this" guide tab
- New 4th tab (**How to read this** / **Guide** on mobile): a static, data-free explainer so it
  works even before a first sync. Covers the three views, filters, every metric (DUPR, Win %,
  Points won %, Margin, Value, DUPR change, Beat expectations, Avg Opp), the expected-vs-actual
  idea (Wins/Margin vs expected), the Strong/Some/Could-be-luck signal and 4-match/10-game
  small-sample rule, the charts, and viewing other players. Plain language, `.gdef` glossary
  grid that stacks on phones. SW rj-v62.

## 2026-10-11 — plainer wording for non-technical users
- Removed jargon from visible text: "Subset performance" → "Your performance"; "DUPR changes —
  fixed recent windows" → "Recent rating changes — your most recent matches…"; the `Δ` symbol in
  column headers → "DUPR change"; "Exp Win% / Wins vs exp / Margin vs exp" → "Expected…"; the
  "Could be luck" signal (was "Noise") with plain tooltips; and the Partner-Index model note is
  now plain English (no formula or "pb predictor" reference). Tooltips reworded throughout.
- Browser-storage copies now show no "GitHub" wording anywhere visible: the view-bar note and the
  scouted-player message are mode-aware (`BROWSER`), and all other GitHub strings are on
  GitHub-mode-only code paths (confirmed by render scan: 0 visible GitHub text nodes).

## 2026-10-11 — easier mobile sync
- **Sync now** button (header, sync card, and the stale banner): opens dashboard.dupr.com in a
  new tab, copies the keyword "PB Sync", and shows a tip reminding you to type it in the address
  bar and tap the bookmark. Turns "remember to go to DUPR first" into one tap.
- **Visual setup cards**: the phone bookmark setup is now 3 numbered steps (copy code / bookmark
  page / paste + rename) instead of a text paragraph — the copy-paste step was the #1 failure.
- **Chart presets**: Rating Over Time gains rolling-window pills 3M / 6M / 1Y alongside All and
  per-year (`Z.months`); phones default to 3M. SW rj-v61.

## 2026-10-11 — view other players ("scouting")
- **From a player's DUPR page** (`dashboard.dupr.com/dashboard/player/<id>`) the bookmark asks
  "Sync <name> (view only)" or "Sync my own matches". **On your own sync** it offers
  "Me + my 14 most recent people" (partners and opponents, newest first; `RECENT` in the
  bookmark), reusing your sync's current-ratings lookups instead of fetching theirs.
- Other players are stored **only in this browser** (IndexedDB `pb-scouts`, keyed by DUPR id) and
  are never saved to GitHub or mixed with your data. A **👁 Viewing** bar switches the whole app
  to any of them (`pb-view`) and removes them; own syncs always compare against your own data
  (`OWN`). Payload over 1.5M chars drops the largest extras and says so. Tested end-to-end in
  real time (headless Chrome, fake DUPR API): single player, recent 14, switch, remove. SW rj-v60.

## 2026-10-11 — site.json: one codebase, personal or shared
- New `site.json` holds everything copy-specific: `storage` ("github" | "browser"), `repo`,
  the Sync bookmark's `app` URL and optional `duprId` / `duprCode`. `build_bookmarklet.py` reads
  it; the app reads it on load. This copy is unchanged ("github", pinned to Z49MRW).
- **Browser storage mode** (for a shareable copy): synced data goes to localStorage `pb-data-v1`
  and is preferred over `data/data.json`; a welcome card appears when there are no matches; the
  Clean up panel offers Export my data / Import data / Delete my data instead of GitHub saving.
  Bookmark with no pinned player syncs whoever is logged in. Tested end-to-end (fake DUPR API →
  save → reload shows 204 matches) and the github mode re-checked. SW rj-v59 (caches site.json).

## 2026-10-11 — phone-friendly sync bookmark
- The bookmark no longer opens a pop-up (phones pause the background DUPR tab, and you can't
  drag a bookmark there). It now fetches on dashboard.dupr.com with an on-page progress panel,
  trims the history to the fields `duprToData` uses, gzips it (CompressionStream) and opens the
  app **in the same tab** at `…?sync=1#pb=<z|j><base64url>` (~19.5 KB for 204 matches). The app
  decodes it, removes it from the address bar and history, and **asks before saving** (anyone
  can craft such a link; a different player than the one on file gets a warning). With no
  GitHub token in that browser it asks for one inline (Connect & save). Old pop-up bookmarks
  still work through the postMessage path; both share one `handle()`.
- Sync card: **📋 Copy bookmark code** + phone steps (bookmark any page, paste the code as its
  address, run it by typing its name in the address bar on dashboard.dupr.com).
- Tested end-to-end in headless Chrome with the real bookmark against a fake DUPR API built from
  synced data: identical matches after the round trip (bar fixture rounding). SW rj-v57.

## 2026-10-11 — full app on phones
- Phones (≤620px) now get everything: all three tabs (the third is labelled "People"), every
  chart and table. Table rows become cards: the name across the top, the numbers in a 4-column
  grid (3 under 380px), each labelled from its column header. `labelTables()` copies header text
  into `data-l` after each render, so new tables work on phones without extra CSS. The old
  phone-only "Analysis minus `mob-hide`" view is gone. SW rj-v56.

## 2026-10-11 — fresh start
Started from [kyeill/pickleball](https://github.com/kyeill/pickleball) at `ba02a40`, with a new
history and without its match data (committed `data/` files are empty starters). Changes made on
top of it before this first commit:

- **Local running for any DUPR account.** `tools/serve_local.py` serves the app on localhost, keeps
  data in the git-ignored `local/data/`, and builds a Sync bookmark for the local copy that works
  out who is logged in to DUPR and checks it against the short DUPR id. DUPR's 2FA prompt only
  affects logging in; the bookmark uses the session afterwards. The bookmark's app URL, numeric id
  and short id are build-time values (`tools/build_bookmarklet.py`).
- **Pre-match ratings for partners and opponents.** `duprToData` stores `ratingPre` for every
  other player (their team's `preMatchRatingAndImpact`, or post − impact), so expected results
  aren't tilted by the match's own outcome. Older data falls back to post-match per player.
- **Opponents & Partners tab** (desktop): Partner / Opponent Index (`MODEL`: logistic win curve
  `1/(1+10^(−Δ/S))` from the pb predictor with S fitted to the user's matches; expected margin a
  linear fit on Δ), ranked people lists with DUPR change per match and beat-expectations rate,
  and pattern tables (you vs partner rating, balanced vs lopsided opponents, repeat meetings).
  4+ matches ranked; 1–3 shown separately as low reliability, with no signal.
- **Analysis tab:** rolling 20-match Form chart, Close Games & Deciders, Streaks & Bounce-back
  (entry order = playing order). Overview gets a *Beat expectations* tile.
- **Late-entered matches:** moving an event onto its last date is now opt-in per event
  (Clean up → 📅, `meta.events[raw].collapse`). It used to be automatic, which piled a whole
  weekly league onto its final night.
- **Sort by DUPR now** on the people lists.
