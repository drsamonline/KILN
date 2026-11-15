"""The fleet index: every app in one file, installable, with one backup.

The apps are inlined rather than linked, so the index works from a USB stick as well
as from Pages, and the service worker has one URL to cache. Each app is a same-origin
srcdoc frame, which is what makes a fleet-wide backup possible at all: the index can
read every app's storage without a server.
"""
from __future__ import annotations

import html
import json
import tempfile
from pathlib import Path

from . import __version__
from . import catalog as cat
from . import compose, emit, spec as specmod

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "fleet"


def apps(catalog) -> list[dict]:
    """Every spec, built, with the namespace its storage lives under."""
    out = []
    for f in specmod.spec_paths(ROOT):
        s = specmod.load(f, catalog)
        with tempfile.TemporaryDirectory() as td:
            plan = compose.plan(s, catalog, tier="personal")
            emit.write(plan, td)
            html_text = (Path(td) / "index.html").read_text(encoding="utf-8")
        out.append({
            "id": s["id"],
            "name": s["name"],
            "pitch": s["pitch"],
            "category": s["category"],
            "namespace": s["storage"]["namespace"],
            "features": s["features"],
            "locked": "crypto" in s.get("features", []),
            "kb": round(len(html_text.encode("utf-8")) / 1024),
            "html": html_text,
            "spec": f.name,
        })
    return out


CSS = """
:root{--bg:#0f1116;--panel:#171a21;--panel2:#12151c;--line:#262b36;--ink:#e7ebf3;
  --muted:#98a2b3;--accent:#7c9cff;--ok:#4ade80;--bad:#ff6b6b;--r:12px}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.55 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);
  padding:12px 18px;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
header b{font-size:16px;letter-spacing:-.01em}
header .spacer{flex:1}
header a{color:var(--muted);text-decoration:none;font-size:13px}
header a:hover{color:var(--ink)}
main{display:grid;grid-template-columns:minmax(0,340px) minmax(0,1fr);gap:16px;
  padding:16px 18px 40px;max-width:1400px;margin:0 auto;align-items:start}
main>*{min-width:0}
@media (max-width:900px){main{grid-template-columns:1fr}}
.tools{display:flex;gap:8px;margin:0 0 10px;flex-wrap:wrap}
input[type=search]{width:100%;padding:9px 12px;border-radius:10px;border:1px solid var(--line);
  background:var(--panel);color:var(--ink);font-size:14px}
input[type=search]:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
button{font:inherit;font-size:13px;padding:7px 12px;border-radius:9px;cursor:pointer;
  border:1px solid var(--line);background:var(--panel);color:var(--ink)}
button.primary{background:var(--accent);border-color:var(--accent);color:#0b0e14;font-weight:600}
button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.list{display:flex;flex-direction:column;gap:8px}
.app{border:1px solid var(--line);border-radius:var(--r);background:var(--panel);
  padding:11px 12px;cursor:pointer;text-align:left}
.app:hover{border-color:var(--accent)}
.app.on{border-color:var(--accent);background:var(--panel2)}
.app h3{margin:0 0 2px;font-size:14px}
.app p{margin:0;color:var(--muted);font-size:12.5px}
.tag{font-size:11px;border:1px solid var(--line);border-radius:999px;padding:1px 7px;
  color:var(--muted);margin-left:6px;white-space:nowrap}
.frame{border:1px solid var(--line);border-radius:var(--r);overflow:hidden;background:var(--bg)}
.bar{display:flex;align-items:center;gap:8px;padding:8px 10px;background:var(--panel);
  border-bottom:1px solid var(--line);font-size:12.5px;color:var(--muted)}
.dot{width:9px;height:9px;border-radius:50%;background:var(--line);display:inline-block}
iframe{display:block;width:100%;height:min(74vh,760px);border:0;background:var(--bg)}
.hint{color:var(--muted);font-size:12.5px;margin:8px 0 0}
.note{margin:14px 0 0;padding:11px 13px;border:1px solid var(--line);border-radius:10px;
  background:var(--panel);color:var(--muted);font-size:12.5px}
.ok{color:var(--ok)} .bad{color:var(--bad)}
"""


def index_html(catalog, built: list[dict]) -> str:
    cards = []
    for a in built:
        tags = (f'<span class="tag">locked</span>' if a["locked"] else "") + \
               f'<span class="tag">{html.escape(a["category"])}</span>'
        cards.append(
            f'<button class="app" data-id="{html.escape(a["id"])}" '
            f'data-ns="{html.escape(a["namespace"])}">'
            f'<h3>{html.escape(a["name"])}{tags}</h3>'
            f'<p>{html.escape(a["pitch"])}</p></button>')
    payload = json.dumps({
        "version": __version__,
        "apps": [{"id": a["id"], "name": a["name"], "ns": a["namespace"],
                  "kb": a["kb"], "locked": a["locked"], "html": a["html"]}
                 for a in built],
    }, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>KILN fleet — {len(built)} apps</title>
<meta name="description" content="Every KILN app in one file. Offline, installable, one backup for all of them.">
<meta name="theme-color" content="#0f1116">
<link rel="manifest" href="manifest.webmanifest">
<style>{CSS}</style></head>
<body>
<header>
  <b>KILN fleet</b>
  <span class="hint" id="count">{len(built)} apps</span>
  <span class="spacer"></span>
  <a href="../index.html">Home</a>
  <a href="../studio.html">Studio</a>
  <a href="https://github.com/drsamonline/KILN">GitHub</a>
</header>
<main>
  <section>
    <div class="tools">
      <input id="q" type="search" placeholder="Search {len(built)} apps" autocomplete="off">
    </div>
    <div class="tools">
      <button id="backup" class="primary">Back up all data</button>
      <button id="restore">Restore</button>
      <input id="file" type="file" accept=".json" hidden>
    </div>
    <p class="hint" id="status" aria-live="polite">Nothing backed up yet.</p>
    <div class="list" id="list">{''.join(cards)}</div>
  </section>
  <section>
    <div class="frame">
      <div class="bar"><i class="dot"></i><i class="dot"></i><i class="dot"></i>
        <span id="addr">pick an app</span></div>
      <iframe id="view" title="the app you picked"
              sandbox="allow-scripts allow-forms allow-modals allow-same-origin"></iframe>
    </div>
    <p class="note">Every app here is one HTML file, running inside this page. Your data stays
    in this browser. <b>Back up all data</b> reads the storage of every app at once and writes
    one JSON file; <b>Restore</b> puts it back. Nothing leaves the device.</p>
  </section>
</main>
<script>
const DATA = {payload};

function el(id) {{ return document.getElementById(id); }}

function pick(id) {{
  const a = DATA.apps.find((x) => x.id === id);
  if (!a) return;
  el("view").srcdoc = a.html;
  el("addr").textContent = a.id + " · " + a.kb + " KB · " + (a.locked ? "locked" : "offline");
  document.querySelectorAll(".app").forEach((b) => b.classList.toggle("on", b.dataset.id === id));
  pick.current = a;
}}

/* one backup for the whole fleet: read each app's own storage key */
function backup() {{
  const out = {{kiln: DATA.version, exported: new Date().toISOString(), apps: {{}}}};
  let n = 0;
  DATA.apps.forEach((a) => {{
    const key = "kiln:" + a.ns;
    const v = localStorage.getItem(key);
    if (v !== null) {{ out.apps[a.id] = {{namespace: a.ns, value: v}}; n += 1; }}
  }});
  const blob = new Blob([JSON.stringify(out, null, 2)], {{type: "application/json"}});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "kiln-fleet-backup.json";
  link.click();
  URL.revokeObjectURL(url);
  el("status").innerHTML = '<span class="ok">Backed up ' + n + " of " + DATA.apps.length +
    " apps that hold data.</span>";
}}

function restore(file) {{
  const fr = new FileReader();
  fr.onload = () => {{
    try {{
      const doc = JSON.parse(fr.result);
      if (!doc || !doc.apps) throw new Error("not a fleet backup");
      let n = 0;
      Object.keys(doc.apps).forEach((id) => {{
        const entry = doc.apps[id];
        if (!entry || typeof entry.value !== "string") return;
        localStorage.setItem("kiln:" + entry.namespace, entry.value);
        n += 1;
      }});
      el("status").innerHTML = '<span class="ok">Restored ' + n +
        " apps. Open one to see its data.</span>";
      if (pick.current) pick(pick.current.id);
    }} catch (e) {{
      el("status").innerHTML = '<span class="bad">' + e.message + "</span>";
    }}
  }};
  fr.readAsText(file);
}}

document.querySelectorAll(".app").forEach((b) => {{
  b.onclick = () => pick(b.dataset.id);
}});
el("q").oninput = () => {{
  const q = el("q").value.trim().toLowerCase();
  let shown = 0;
  document.querySelectorAll(".app").forEach((b) => {{
    const a = DATA.apps.find((x) => x.id === b.dataset.id);
    const hay = (a.name + " " + a.id + " " + (a.locked ? "locked" : "")).toLowerCase();
    const ok = !q || hay.indexOf(q) >= 0;
    b.hidden = !ok;
    if (ok) shown += 1;
  }});
  el("count").textContent = shown === DATA.apps.length ? DATA.apps.length + " apps"
    : shown + " of " + DATA.apps.length;
}};
el("backup").onclick = backup;
el("restore").onclick = () => el("file").click();
el("file").onchange = (e) => {{ if (e.target.files[0]) restore(e.target.files[0]); }};
pick(DATA.apps[0].id);

if ("serviceWorker" in navigator && location.protocol.startsWith("http")) {{
  navigator.serviceWorker.register("sw.js").catch(() => {{}});
}}
</script>
</body></html>
"""


MANIFEST = {
    "name": "KILN fleet",
    "short_name": "KILN",
    "description": "Every KILN app in one file. Offline, installable, one backup for all.",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "background_color": "#0f1116",
    "theme_color": "#0f1116",
    "icons": [{
        "src": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA1MTIgNTEyIj48cmVjdCB3aWR0aD0iNTEyIiBoZWlnaHQ9IjUxMiIgcng9Ijk2IiBmaWxsPSIjMGYxMTE2Ii8+PHBhdGggZD0iTTEzMCAxMjBoNzB2MTIybDEwMi0xMjJoODZMjc4IDI0MGw5MiAxNTJoLTg2bC02MC0xMDQtMzAgMzR2NzBoLTcwVjEyMHoiIGZpbGw9IiM3YzljZmYiLz48L3N2Zz4=",
        "sizes": "512x512",
        "type": "image/svg+xml",
        "purpose": "any maskable",
    }],
}


SW = """/* the fleet index is one file, so the cache is one entry plus the shell */
const CACHE = "kiln-fleet-%(version)s";
const SHELL = ["./", "./index.html", "./manifest.webmanifest"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(
    keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request).then((res) => {
    const copy = res.clone();
    caches.open(CACHE).then((c) => c.put(e.request, copy));
    return res;
  }).catch(() => caches.match("./index.html"))));
});
"""


def build(catalog) -> dict[str, str]:
    built = apps(catalog)
    return {
        "index.html": index_html(catalog, built),
        "manifest.webmanifest": json.dumps(MANIFEST, indent=2) + "\n",
        "sw.js": SW % {"version": __version__},
    }


def write(catalog, out: Path | None = None) -> list[Path]:
    target = Path(out) if out else OUT
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for name, text in build(catalog).items():
        p = target / name
        p.write_text(text, encoding="utf-8")
        written.append(p)
    return written
