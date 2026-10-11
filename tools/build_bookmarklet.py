#!/usr/bin/env python3
"""Inject tools/sync_bookmarklet.js into index.html as the Sync bookmark's href.

Strips // comments and indentation, fills in the app URL / player ids, then escapes for a
javascript: URL inside an HTML attribute (% -> %25 so the browser's URL-decoding can't mangle
it, & and " as HTML entities). Run after editing the bookmarklet source:

    python tools/build_bookmarklet.py

tools/serve_local.py imports bookmark_href() / inject() to build a local copy's bookmark on
the fly, so the committed index.html always keeps the published (GitHub Pages) one.
"""
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "sync_bookmarklet.js")
HTML = os.path.join(ROOT, "index.html")

# The published app comes from site.json: its address, and optionally a DUPR player it is
# pinned to (duprId numeric / duprCode short). Both empty = whoever is logged in to DUPR.
_site = json.load(io.open(os.path.join(ROOT, "site.json"), encoding="utf-8"))
PUBLISHED = {"app": _site["app"], "id": str(_site.get("duprId") or ""), "code": _site.get("duprCode") or ""}
ANCHOR = re.compile(r'(<a class="bm" id="syncBm" href=")[^"]*(")')


def _js_str(v):
    s = str(v)
    assert re.fullmatch(r"[A-Za-z0-9:/?=._\-]*", s), f"unexpected characters in bookmarklet value {s!r}"
    return s


def bookmark_href(app, id="", code=""):
    code_js = io.open(SRC, encoding="utf-8").read()
    for key, val in (("__APP__", app), ("__ID__", id), ("__CODE__", code)):
        code_js = code_js.replace(key, _js_str(val))
    lines = []
    for ln in code_js.splitlines():
        s = ln.strip()
        if not s or s.startswith("//"):
            continue
        lines.append(s)
    js = " ".join(lines)
    assert "//" not in re.sub(r"https?://", "", js), "inline // comment would swallow the rest"
    return "javascript:" + js.replace("%", "%25").replace("&", "&amp;").replace('"', "&quot;")


def inject(html, href):
    new, count = ANCHOR.subn(lambda m: m.group(1) + href + m.group(2), html)
    assert count == 1, f"expected one sync bookmark anchor, found {count}"
    return new


if __name__ == "__main__":
    href = bookmark_href(**PUBLISHED)
    html = io.open(HTML, encoding="utf-8").read()
    io.open(HTML, "w", encoding="utf-8", newline="").write(inject(html, href))
    print(f"Injected bookmarklet ({len(href)} chars) into index.html")
