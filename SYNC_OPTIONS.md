# How do we improve DUPR sync on mobile?

**The ask:** a static web app (GitHub Pages, no backend) shows a user's DUPR pickleball match
history and derived stats. Getting the data in **works on desktop and Chrome-for-Android today**,
but the **mobile setup is the adoption blocker**. We want options to make the **mobile** experience
better. This document states the hard constraint, what mobile users hit today, every option
considered (with why each does or doesn't help mobile), and the open questions.

---

## The hard constraint (why this is tricky at all)

DUPR's data API (`api.dupr.com`) only answers requests from a page on `dashboard.dupr.com`
carrying the user's httpOnly login cookie (same-origin policy hides that cookie from every other
site). Therefore:

- A page on `*.github.io` **cannot** call DUPR's API with the user's login.
- The data must come from **code running on `dashboard.dupr.com`** (a bookmarklet or a browser
  extension), **a server** (not bound by browser rules), or a **login-free source**.

This is a security boundary, not a setting. In particular, a "Sync" button in the app **cannot**
open `dashboard.dupr.com` and run the sync itself: a page may `window.open()` that tab but cannot
run code in it or read from it (cross-origin isolation). Only an extension can.

---

## What a mobile user hits today (the thing to fix)

Method = a `javascript:` **bookmarklet** that runs on `dashboard.dupr.com`, fetches the history,
and hands it to the app via a URL `#fragment`. It works, but on a phone:

1. **Install is painful.** You can't drag a bookmark to a toolbar on mobile. The workaround:
   copy a ~9 KB code string → bookmark any page → edit it → rename it → paste the code over its
   URL. **Pasting the long code is where most people give up.**
2. **Running it is non-obvious.** You type the bookmark's name in the address bar and tap the
   suggestion — not something a user guesses.
3. **Browser gaps.** Chrome Android: OK. **Edge Android: does NOT run javascript bookmarks**
   (confirmed). iPhone Safari: untested.

Goal: cut or remove the copy-paste install, make "sync now" obvious, and cover more mobile
browsers.

---

## Options, judged by mobile impact

### Option A — Make the bookmarklet setup easy (keeps mobile coverage)
Guided, one-screen-at-a-time setup: detect the browser (warn + "open in Chrome" on Edge Android;
show Safari steps on iPhone); have the setup page **name its own bookmark** so the rename step
disappears; show where "Edit bookmark" is; end with a live test. Add a **Sync now** button that
opens `dashboard.dupr.com` with the one reminder needed.
- **Mobile impact:** still one copy-paste, but far fewer failure points; **only option that keeps
  Chrome-Android working with no server and no credentials.**
- **Can't be removed:** a page cannot install a bookmark or run code in another tab, so some
  manual step remains on mobile.

### Option B — Browser extension / userscript (great on desktop, weak on mobile)
An extension may run code on `dashboard.dupr.com`: tap Sync → DUPR opens → extension syncs →
data returns. No code to copy.
- **Mobile impact:** **Chrome for Android supports no extensions at all** — so it does NOT fix
  the main mobile case. Helps desktop (Chrome/Edge/Firefox) and **Firefox Android**. iPhone would
  need an App Store app (large effort).

### Option C — Server-side "pass-through" login (removes mobile setup, but risky; feasibility unconfirmed)
User types DUPR email/password (+2FA) into the app; a server (e.g. Cloudflare Worker) logs in to
DUPR and relays the data.
- **Mobile impact:** **best possible — no bookmark, no copy-paste, every mobile browser.**
- **But:**
  - **Requires a server.**
  - **May not work:** a predecessor found DUPR rejected copied tokens from a server context;
    server-side login may be blocked/session-bound. **Unconfirmed** — a probe that would capture
    the user's password + 2FA was declined as unsafe credential handling, so feasibility is open.
  - **Passkey/WebAuthn 2FA can't pass through** (works only on DUPR's origin); TOTP/SMS/email can.
  - **Trust/phishing shape:** users type their DUPR password + 2FA into a non-DUPR site. For a
    shared/among-friends app this is a real adoption and safety problem even if nothing is stored.
  - **Ops + ToS risk:** running a credential relay invites abuse (password-guessing) and is the
    kind of automation platform terms usually prohibit.
  - DUPR auth endpoints (mapped from public dashboard JS, for feasibility reasoning only — no
    login performed): `POST /auth/v1.0/login {email,password}` → on 2FA, HTTP **428** with
    `challengeToken` + methods (`urn:dupr:second-factor:{email,sms,totp,webauthn,recovery}`);
    `POST /auth/v1.0/2fa/verify {challengeToken, code, method}`; header
    `X-DUPR-Client-Capabilities: totp,webauthn`.

### Option D — Login-free public source: pickleball.com (no mobile setup, but data too thin)
`pickleball.com/players/<slug>/rating-history` is public; players are findable by DUPR ID via
`/players?search=<DUPRID>` (exact, solves name duplicates).
- **Mobile impact:** no bookmark, no login — type a name/ID. But **checked against the real
  user: their page showed 0 matches** (site favors tournament/event play, not the league/ladder
  that is most of a rec player's record; DUPR had 211). Ratings are often masked when logged out;
  only ~10 matches render per page; no per-match "rating at the time" for others. **Also needs a
  server** and scrapes a third party. **Too thin to be a primary source for rec players.**

---

## Mobile option matrix

| Option | Server | Removes phone copy-paste | Chrome Android | Credentials leave DUPR | Data completeness |
|---|---|---|---|---|---|
| A. Easier bookmarklet | No | Reduced, not removed | **Yes** | No | Full |
| B. Extension/userscript | No | Yes | **No** | No | Full |
| C. Server login relay | **Yes** | **Yes** | Yes (if DUPR allows) | **Yes (to your server)** | Full minus passkey; **unconfirmed** |
| D. pickleball.com | **Yes** | Yes | Yes | No | **Poor for rec players** |

## How to frame the decision (mobile-first)

- **Baseline that actually covers mobile today:** Option A — the only no-server, no-credential
  path that works on Chrome Android. Biggest, safest win for the stated problem.
- **Desktop/Firefox-Android bonus:** add Option B on top (does not help Chrome Android).
- **Only way to truly remove mobile setup** is Option C, but it is unconfirmed and carries
  trust/ops/ToS cost — least-bad only for a single-user, self-hosted, self-trusted setup, not a
  shared app.
- **D** is not viable as a primary source given the data gaps.

**Open questions for the next step:**
1. Is there a lower-friction mobile install for a `javascript:` bookmark than copy-paste (e.g. a
   browser that imports bookmarks, a share-sheet target, a QR/deep-link path)?
2. Does DUPR accept a login performed outside a browser? (Needed to judge Option C — must be
   tested without a tool that stores/transmits the password beyond DUPR.)
3. Is Firefox-for-Android adoption high enough among target users to make Option B worthwhile?
