// "🔄 Sync to Pickleball" bookmarklet — readable source.
// Runs on dashboard.dupr.com, where your login cookie already works, so no DUPR
// token is ever copied or stored. It fetches your history right there (with a small
// progress panel, so the page stays in front — phones pause background tabs), trims
// it to the fields the app uses, gzips it, and opens the app in the same tab with the
// data after "#pb=". A #fragment never leaves the browser. The app asks before saving.
//
// After editing, run:  python tools/build_bookmarklet.py   (injects it into index.html)
// __APP__ / __ID__ / __CODE__ are filled in by the build (tools/serve_local.py fills them for a
// local copy). ID '' means "whoever is logged in", checked against CODE (the short DUPR id).
// No inline comments below a code line, and no double slash outside https: (the build joins lines).
(async () => {
  const APP = '__APP__';
  const CODE = '__CODE__', API = 'https://api.dupr.com';
  let ID = '__ID__';
  if (!/(^|\.)dupr\.com$/.test(location.hostname)) {
    alert('Open dashboard.dupr.com (logged in), then run this bookmark there.');
    return;
  }
  if (document.getElementById('pb-sync-panel')) return;
  const box = document.createElement('div');
  box.id = 'pb-sync-panel';
  box.style.cssText = 'position:fixed;left:12px;right:12px;top:12px;z-index:2147483647;max-width:420px;margin:0 auto;'
    + 'background:#14201a;color:#eef3ef;border:1px solid #35B79E;border-radius:14px;padding:16px 18px;'
    + 'font:15px/1.5 system-ui,sans-serif;box-shadow:0 10px 30px rgba(0,0,0,.4)';
  box.innerHTML = '<b style="font-size:16px">🔄 Sync to Pickleball</b><div id="pb-sync-msg" style="margin-top:6px">Starting…</div>';
  document.body.appendChild(box);
  const say = t => { box.querySelector('#pb-sync-msg').textContent = t; };
  const fail = t => {
    say(t);
    const b = document.createElement('button');
    b.textContent = 'Close';
    b.style.cssText = 'margin-top:10px;padding:7px 14px;border-radius:8px;border:1px solid #35B79E;background:none;color:#35B79E;font:inherit;font-weight:600';
    b.onclick = () => box.remove();
    box.appendChild(b);
  };

  const H = { 'Accept': 'application/json', 'Content-Type': 'application/json',
              'X-Dupr-Client-Capabilities': 'totp,webauthn' };
  const call = async (method, path, body) => {
    const r = await fetch(API + path, { method, headers: H, credentials: 'include',
                                        body: body ? JSON.stringify(body) : undefined });
    if (!r.ok) {
      const t = await r.text().catch(() => '');
      const err = new Error(method + ' ' + path + ' returned ' + r.status + ' ' + t.slice(0, 120));
      err.status = r.status;
      throw err;
    }
    return r.json();
  };

  try {
    say('Reading your DUPR profile…');
    if (!ID) {
      let me;
      try { const r = await call('GET', '/user/v1.0/profile'); me = r.result || r; }
      catch (e) { if (e.status === 401 || e.status === 403) throw e;
        throw new Error('Could not look up the logged-in player (' + e.message + '). Put your numeric DUPR id in local/config.json as "id".'); }
      if (CODE && me.duprId && String(me.duprId).toUpperCase() !== CODE.toUpperCase())
        throw new Error('Logged in to DUPR as ' + me.duprId + ', but this copy is set up for ' + CODE + '.');
      if (!me.id) throw new Error('DUPR profile had no id (keys: ' + Object.keys(me).join(', ') + '). Put your numeric DUPR id in local/config.json as "id".');
      ID = me.id;
    }
    ID = Number(ID);
    const prof = (await call('GET', '/player/v1.0/' + ID)).result;
    if (CODE && prof.duprId && String(prof.duprId).toUpperCase() !== CODE.toUpperCase())
      throw new Error('Player ' + ID + ' is ' + prof.duprId + ', not ' + CODE + '.');

    const hits = [];
    let off = 0, total = null, legacy = false, size = 25;
    for (;;) {
      let r = null;
      if (!legacy) {
        try {
          r = await call('POST', '/player/v1.0/' + ID + '/history',
            { filters: { eventFormat: null }, limit: size, offset: off,
              sort: { order: 'DESC', parameter: 'MATCH_DATE' } });
        } catch (e) {
          if (e.status === 400 && off === 0 && size > 10) { size = 10; continue; }
          if (e.status === 404 || e.status === 405) legacy = true; else throw e;
        }
      }
      if (legacy) r = await call('POST', '/match/v1.0/history', { limit: size, offset: off });
      const res = r.result !== undefined ? r.result : r;
      const page = Array.isArray(res) ? res : (res && res.hits);
      if (!Array.isArray(page)) throw new Error('Unexpected match-history response (keys: ' + Object.keys(res || {}).join(', ') + ')');
      if (res && res.total != null) total = res.total;
      hits.push(...page);
      off += size;
      say('Matches: ' + hits.length + (total != null ? ' of ' + total : ''));
      if (page.length < size || (total != null && off >= total)) break;
    }

    const ids = [...new Set(hits.flatMap(m => (m.teams || []).flatMap(t => [t.player1, t.player2]))
      .filter(p => p && p.id !== ID).map(p => p.id))];
    const n = ids.length, now = {};
    let done = 0;
    const worker = async () => {
      while (ids.length) {
        const pid = ids.pop();
        try {
          const r = (await call('GET', '/player/v1.0/' + pid)).result;
          now[pid] = r && r.ratings ? r.ratings.doubles : null;
        } catch (e) {
          if (e.status === 401 || e.status === 403) throw e;
          now[pid] = null;
        }
        done++;
        say('Current ratings: ' + done + ' of ' + n);
      }
    };
    await Promise.all([1, 2, 3, 4, 5, 6].map(worker));

    say('Packing ' + hits.length + ' matches…');
    const K = ['preMatchDoubleRatingPlayer1', 'preMatchDoubleRatingPlayer2', 'matchDoubleRatingImpactPlayer1', 'matchDoubleRatingImpactPlayer2'];
    const P = p => p && { id: p.id, fullName: p.fullName, postMatchRating: { doubles: (p.postMatchRating || {}).doubles } };
    const T = t => {
      const o = { player1: P(t.player1), player2: P(t.player2), winner: t.winner };
      for (let i = 1; i <= 5; i++) if (t['game' + i] != null) o['game' + i] = t['game' + i];
      const b = t.preMatchRatingAndImpact;
      if (b) { o.preMatchRatingAndImpact = {}; K.forEach(k => { if (b[k] != null) o.preMatchRatingAndImpact[k] = b[k]; }); }
      return o;
    };
    const slim = hits.map(m => ({ matchId: m.matchId, eventDate: m.eventDate, league: m.league, venue: m.venue,
      eventFormat: m.eventFormat, confirmed: m.confirmed, teams: (m.teams || []).map(T) }));
    const json = JSON.stringify({ v: 2, profile: { id: prof.id, fullName: prof.fullName, doubles: prof.ratings && prof.ratings.doubles },
      hits: slim, now });
    let bytes = new TextEncoder().encode(json), tag = 'j';
    if (window.CompressionStream) {
      bytes = new Uint8Array(await new Response(new Blob([bytes]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer());
      tag = 'z';
    }
    let bin = '';
    for (let i = 0; i < bytes.length; i += 32768) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 32768));
    const b64 = btoa(bin).split('+').join('-').split('/').join('_').replace(/=+$/, '');
    say('Opening the app…');
    location.href = APP + '#pb=' + tag + b64;
  } catch (e) {
    if (e.status === 401 || e.status === 403) fail('DUPR says you are not logged in. Log in at dashboard.dupr.com (2FA too), then run the bookmark again.');
    else fail('Sync failed: ' + e.message);
  }
})();
