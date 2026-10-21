# PBStats

A personal, installable web app (PWA) for your DUPR pickleball history: filter every match by
year / type / level / event / partner, see subset performance (win %, points won %, a normalized
margin and a custom **Value** score), watch your rating and form over time, and find out who you
play best and worst with and against, measured against what the ratings expected.

> **Origin:** this started on 2026-10-11 as a copy of
> [kyeill/pickleball](https://github.com/kyeill/pickleball) (Kyle Yost's DUPR tracker), taken with
> a fresh history and without its data. It adds local running for any DUPR account, the
> Opponents & Partners tab, the expected-results model, close-game, form and streak analysis,
> and fixes for DUPR's 2FA login and late-entered matches.
> The win-probability curve comes from
> [DaRubberDuckieee/pickleball-dupr-predictor](https://github.com/DaRubberDuckieee/pickleball-dupr-predictor).

---

## Run it locally

```
python tools/serve_local.py --code Z49MRW      # your short DUPR id; then open http://localhost:8000
```

Needs Python 3 only. Your matches and edits are kept in `local/data/`, which git ignores, so
they never get committed or pushed. The `data/` files in the repo are empty starters.

## Syncing your DUPR data

Sync whenever you've played. It runs in your own browser while you're logged in to DUPR, so
**no DUPR password, 2FA code or token is stored anywhere**.

**One time, computer:** open the app → **🔄 Sync from DUPR** card (bottom of the page) → drag the
**🔄 Sync to Pickleball** button to your bookmarks bar.

**One time, phone:** you need a *second* bookmark just for syncing (your normal bookmark of the
app stays). In the same card tap **📌 Open bookmark helper**. That's the app at its own address
(`?bm=1`), so Chrome's ☆ makes a new bookmark there rather than editing your existing one. Tap
**📋 Copy bookmark code**, bookmark the helper page (⋮ → ☆), then **Edit** it: name it **PB Sync**
and replace its address with the code.

**Each sync:**

1. Log in at <https://dashboard.dupr.com> as usual, including DUPR's 2FA prompt.
2. Run the bookmark there (on a phone: type **PB Sync** in the address bar and tap the
   bookmark suggestion). A panel on the DUPR page shows progress, then the app opens in the same
   tab. Tap **Save**. The first time on a device it asks for your GitHub token. On Android, sync from
   **Chrome**: Edge doesn't run bookmarks like this (viewing in Edge is fine).

The data travels in the part of the address after `#`, which browsers never send to a server.

The bookmark works out who is logged in and refuses to run if that isn't the DUPR id you gave.
If it can't work out who is logged in, put your numeric DUPR id in `local/config.json` as `"id"`
and reload the page to get a fresh bookmark. If DUPR returns fewer matches than you already have,
nothing is saved. Pop-up blocked? Allow pop-ups for dashboard.dupr.com.

DUPR's API only answers requests made from dashboard.dupr.com with your login cookie, which is
why the sync is a bookmark that runs there and hands the data to the app.

---

## What's in the app

- **Overview:** subset KPIs (incl. *Beat expectations*: share of matches where your rating rose),
  Performance by Event, rating by event, and the event's matches.
- **Analysis:** rating over time, rolling 20-match **Form**, Performance by Date and by Matchup
  Strength, **Close Games & Deciders**, **Streaks & Bounce-back**, and the full Match Log.
- **Opponents & Partners** (desktop): the **Partner / Opponent Index** (expected vs actual
  results), ranked lists with DUPR change per match, and pattern tables: you vs your partner's
  rating, balanced vs lopsided opponents, repeat meetings.

**Sample size:** anyone or anything with fewer than 4 matches is shown separately and greyed as
low reliability, with no signal (game tables use 10 games).

## Cleaning up (events, types, partners)

**Filters → ⚙ Clean up data:**

- **Rename** an event (tidy DUPR's long names). Give two events the same name to **merge** them.
- Set each event's **Type** (Tournament / League) and **Level**.
- **Hide** one-off partners (or events) from the dropdowns. Their matches still count.
- **📅** (only on events with matches entered in DUPR late): move every match to the event's last
  date. Use it only for a league typed in long after it was played; leave it off for a normal
  weekly league.

Running locally, **Save** writes `local/data/overrides.json`. These edits survive every sync.

## Hosting on GitHub Pages (optional)

The committed app is set up for <https://colin-oconnor13.github.io/PBStats/>: its Sync bookmark
opens that address, and *Save to GitHub* commits to this repo using a fine-grained token
(Contents: Read and write on this repo only, stored only in your browser). Pages on a free
account needs a public repo, and the synced `data/data.json` would then be public too.

---

## Files

| Path | What it is |
|---|---|
| `index.html` | The whole app (shell + logic). Static, no build. |
| `data/data.json`, `data/overrides.json` | Empty starters for a hosted copy. Locally, `local/data/` is used. |
| `tools/serve_local.py` | Local server: serves the app, builds your bookmark, saves to `local/data/`. |
| `tools/sync_bookmarklet.js` | Readable source of the 🔄 Sync bookmark (runs on dashboard.dupr.com). |
| `tools/build_bookmarklet.py` | Writes `sync.js` from that source and puts a short loader bookmark for it in `index.html`. Run after editing it or `site.json`. |
| `sync.js` | Generated: the sync code the bookmark loads on dashboard.dupr.com. Don't edit by hand. |
| `manifest.webmanifest`, `sw.js`, `icons/` | PWA install + offline. |

## Metric definitions

- **Value** = `Win% + 25·Pts% + 50·(oppDUPR − teamDUPR)`. The last term is strength of schedule
  (positive = tougher opponents).
- **Points won %**: pooled (your points ÷ all points played).
- **Margin**: average per-game point margin, each game rescaled to 11 points (15 if the winning
  score is 15 or more) so 11–9 and 15–12 compare fairly.
- **Matchup strength / edge (Δ)**: (your DUPR + partner's) / 2 − opponents' average DUPR.
- **Expected win %**: `1 / (1 + 10^(−Δ / S))`, the predictor repo's DUPR curve, with S fitted to
  your own matches. Δ uses everyone's DUPR going into the match.
- **Wins vs expected**: actual wins − expected wins.
- **Signal**: an evidence score z built from two surprises, each divided by what chance alone
  gives: wins vs expected, and margin vs expected (spread measured across all your matches).
  They're added and scaled by √(2 + 2ρ), ρ being how closely the two track each other in your
  matches (about 0.85), so shared evidence isn't counted twice. **Strong** when |z| clears a
  cutoff that allows for how many rows the table tests (two-sided 5% shared across them; about
  3.3 for 45 people, never below 2), **Some** at |z| ≥ 2, **Leaning** at 1–2 (direction only),
  otherwise **Could be luck**. An arrow shows the direction.
- **DUPR Δ / match**: DUPR's own rating change, which already accounts for the opponents.
