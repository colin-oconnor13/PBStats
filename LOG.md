# Change log — PBStats

Newest first. Repo `colin-oconnor13/PBStats`.

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
