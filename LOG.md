# Change log — PBStats

Newest first. Repo `colin-oconnor13/PBStats`.

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
