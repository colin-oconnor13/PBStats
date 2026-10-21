#!/usr/bin/env python3
"""Run the Dink Data app locally for your own DUPR account.

    python tools/serve_local.py            # then open http://localhost:8000
    python tools/serve_local.py --port 8123

- Serves the repo, but /data/* comes from local/data/ (git-ignored), so your matches never
  mix with the committed data/ files and nothing is pushed to GitHub.
- The app's saves (sync + Clean up -> Save) PUT to /local-api/data/<file>.json, written here.
- index.html is served with a Sync bookmark built for this copy: it opens this server and
  uses the player in local/config.json ({"code": "<short DUPR id>", "id": "<numeric id or ''>"}).

DUPR login (including its 2FA prompt) happens only in your browser on dashboard.dupr.com;
this server never sees a DUPR password, code or cookie.
"""
import argparse, http.server, io, json, os, sys, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_bookmarklet as bb  # noqa: E402

ROOT = bb.ROOT
LOCAL = os.path.join(ROOT, "local")
DATA = os.path.join(LOCAL, "data")
CONFIG = os.path.join(LOCAL, "config.json")
WRITABLE = {"data.json", "overrides.json"}


def ensure_local(code):
    os.makedirs(DATA, exist_ok=True)
    if not os.path.exists(CONFIG):
        write_json(CONFIG, {"code": code or "", "id": ""})
    cfg = json.load(io.open(CONFIG, encoding="utf-8"))
    if code and cfg.get("code") != code:
        cfg["code"] = code
        write_json(CONFIG, cfg)
    seeds = {
        "data.json": {"player": {"id": cfg.get("code") or "", "name": "", "currentDoubles": None},
                      "generated": None, "syncedAt": "", "matches": []},
        "overrides.json": {"meta": {"events": {}, "partnersHidden": []}, "tags": {}},
    }
    for name, seed in seeds.items():
        if not os.path.exists(os.path.join(DATA, name)):
            write_json(os.path.join(DATA, name), seed)
    return cfg


def write_json(path, obj):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


class Handler(http.server.SimpleHTTPRequestHandler):
    port = 8000

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _path(self):
        return urllib.parse.urlsplit(self.path).path

    def translate_path(self, path):
        p = urllib.parse.unquote(urllib.parse.urlsplit(path).path)
        if p.startswith("/data/"):
            name = os.path.basename(p)
            return os.path.join(DATA, name)
        if p.startswith("/local/"):  # never serve config or data straight from local/
            return os.path.join(ROOT, "__nope__")
        return super().translate_path(path)

    def do_GET(self):
        if self._path() in ("/", "/index.html"):
            cfg = ensure_local(None)  # re-read so edits to local/config.json apply on reload
            app = f"http://localhost:{self.port}/?sync=1"
            href = bb.bookmark_href(app, str(cfg.get("id") or ""), cfg.get("code") or "")
            html = bb.inject(io.open(bb.HTML, encoding="utf-8").read(), href).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return
        super().do_GET()

    def do_PUT(self):
        p = self._path()
        name = p[len("/local-api/data/"):] if p.startswith("/local-api/data/") else ""
        origin = self.headers.get("Origin", "")
        if origin not in (f"http://localhost:{self.port}", f"http://127.0.0.1:{self.port}"):
            return self._reply(403, "Saves are only accepted from this app.")
        if name not in WRITABLE:
            return self._reply(404, "Unknown file.")
        try:
            n = int(self.headers.get("Content-Length", "0"))
            obj = json.loads(self.rfile.read(n).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return self._reply(400, "Body is not JSON.")
        if name == "data.json" and not (isinstance(obj, dict) and isinstance(obj.get("matches"), list)):
            return self._reply(400, "data.json needs a matches list.")
        write_json(os.path.join(DATA, name), obj)
        self.log_message("saved local/data/%s", name)
        self._reply(200, "ok")

    def _reply(self, code, text):
        body = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--code", help="your short DUPR id (saved to local/config.json)")
    a = ap.parse_args()
    cfg = ensure_local(a.code)
    Handler.port = a.port
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    who = cfg.get("code") or "(whoever is logged in to DUPR)"
    print(f"Dink Data (local) for DUPR {who}: http://localhost:{a.port}/   Ctrl+C to stop")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
