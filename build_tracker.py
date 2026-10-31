#!/usr/bin/env python3
"""Build tracker.html from the frontmatter in runs/*/summary.md.

Usage (from the project root):
    python3 build_tracker.py

No dependencies. Re-run it whenever a run finishes or you change a status.
Each run folder needs a summary.md that starts with:

    ---
    company: ...
    role: ...
    date: YYYY-MM-DD
    fit_score: 60
    verdict: APPLY WITH PREP
    status: drafted
    ---
"""
import html
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
RUNS = ROOT / "runs"
OUT = ROOT / "tracker.html"
STATUSES = ["drafted", "applied", "interview", "offer", "rejected", "withdrawn"]
DOC_STEMS = [("fit", "Fit"), ("resume", "Resume"), ("coverletter", "Letter"), ("summary", "Summary")]


def parse_frontmatter(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data = {}
    for line in text[3:end].splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip().strip("\"'")
    return data


def collect():
    rows, skipped = [], []
    if not RUNS.is_dir():
        return rows, ["runs/ folder not found"]
    for folder in sorted(RUNS.iterdir()):
        if not folder.is_dir() or folder.name.startswith("_"):
            continue
        summary = folder / "summary.md"
        if not summary.exists():
            skipped.append(f"{folder.name}: no summary.md")
            continue
        fm = parse_frontmatter(summary)
        if not fm.get("company"):
            skipped.append(f"{folder.name}: summary.md has no frontmatter")
            continue
        try:
            score = int(float(fm.get("fit_score", "")))
        except ValueError:
            score = None
        docs = []
        for stem, label in DOC_STEMS:
            files = [f"runs/{folder.name}/{stem}.{ext}" for ext in ("md", "docx", "pdf")
                     if (folder / f"{stem}.{ext}").exists()]
            if files:
                docs.append({"label": label, "files": [{"ext": f.rsplit(".", 1)[1], "href": f} for f in files]})
        rows.append({
            "company": fm.get("company", ""),
            "role": fm.get("role", ""),
            "date": fm.get("date", ""),
            "score": score,
            "verdict": fm.get("verdict", ""),
            "status": (fm.get("status", "drafted") or "drafted").lower(),
            "folder": folder.name,
            "docs": docs,
        })
    return rows, skipped


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Application Tracker</title>
<style>
:root{--bg:#f7f7f5;--card:#fff;--text:#1c1c1a;--muted:#6b6b66;--line:#e4e4df;--accent:#2f5d9e}
@media(prefers-color-scheme:dark){:root{--bg:#161615;--card:#1f1f1d;--text:#ececea;--muted:#9a9a94;--line:#31312e;--accent:#7aa7e6}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
main{max-width:1100px;margin:0 auto;padding:32px 20px 64px}
h1{font-size:22px;margin:0 0 4px}
.sub{color:var(--muted);font-size:13px;margin-bottom:24px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin-bottom:20px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;cursor:pointer;text-align:left;color:inherit;font:inherit}
.tile .n{font-size:24px;font-weight:600;line-height:1.1}
.tile .l{font-size:12px;color:var(--muted);text-transform:capitalize}
.tile.on{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}
.bar{display:flex;gap:10px;margin-bottom:12px}
input{flex:1;padding:9px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--text);font:inherit}
.wrap{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow-x:auto}
table{width:100%;border-collapse:collapse}
th,td{text-align:left;padding:11px 14px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.03em;cursor:pointer;white-space:nowrap;user-select:none}
th.sorted::after{content:" \\2193"} th.sorted.asc::after{content:" \\2191"}
tr:last-child td{border-bottom:none}
.co{font-weight:600}.role{color:var(--muted);font-size:13px}
.badge{display:inline-block;padding:2px 9px;border-radius:99px;font-size:12px;font-weight:600;white-space:nowrap}
.s-drafted{background:#fdf0d5;color:#7a5200}.s-applied{background:#dbe8fb;color:#1d4a8a}
.s-interview{background:#e0f2e1;color:#1e6a2a}.s-offer{background:#c9f0d2;color:#0d5a22}
.s-rejected{background:#f6dcdc;color:#8a2323}.s-withdrawn{background:#e8e8e4;color:#555}
@media(prefers-color-scheme:dark){
.s-drafted{background:#4a3a14;color:#f1cd86}.s-applied{background:#1f3556;color:#a9c8f2}
.s-interview{background:#1e3d22;color:#a5dcaa}.s-offer{background:#17462a;color:#9be5b0}
.s-rejected{background:#4a2222;color:#f0aaaa}.s-withdrawn{background:#34342f;color:#bdbdb6}}
.score{font-weight:600}.hi{color:#1e8a3a}.mid{color:#b27300}.lo{color:#b03a3a}
.docs a{color:var(--accent);text-decoration:none;font-size:12.5px;margin-right:2px}
.docs a:hover{text-decoration:underline}.docs div{margin-bottom:2px;white-space:nowrap}
.empty{padding:36px;text-align:center;color:var(--muted)}
.skipped{margin-top:18px;font-size:12.5px;color:var(--muted)}
</style>
</head>
<body>
<main>
<h1>Application Tracker</h1>
<div class="sub">Generated __GENERATED__ &middot; re-run <code>python3 build_tracker.py</code> to refresh &middot; change a status in the run's <code>summary.md</code></div>
<div class="tiles" id="tiles"></div>
<div class="bar"><input id="q" type="search" placeholder="Search company or role"></div>
<div class="wrap"><table>
<thead><tr>
<th data-k="company">Company / role</th><th data-k="date">Date</th><th data-k="score">Score</th>
<th data-k="verdict">Verdict</th><th data-k="status">Status</th><th>Files</th>
</tr></thead>
<tbody id="rows"></tbody>
</table><div class="empty" id="empty" hidden>No applications match.</div></div>
<div class="skipped" id="skipped"></div>
</main>
<script>
const DATA = __DATA__;
const STATUSES = __STATUSES__;
const SKIPPED = __SKIPPED__;
let filter = "all", sortKey = "date", asc = false;
const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

function tiles() {
  const counts = {all: DATA.length};
  STATUSES.forEach(s => counts[s] = DATA.filter(d => d.status === s).length);
  const extra = [...new Set(DATA.map(d => d.status))].filter(s => !STATUSES.includes(s));
  extra.forEach(s => counts[s] = DATA.filter(d => d.status === s).length);
  $("tiles").innerHTML = ["all", ...STATUSES, ...extra]
    .filter(s => s === "all" || counts[s] > 0 || STATUSES.includes(s))
    .map(s => `<button class="tile ${filter === s ? "on" : ""}" data-s="${esc(s)}"><div class="n">${counts[s]}</div><div class="l">${esc(s)}</div></button>`).join("");
  document.querySelectorAll(".tile").forEach(t => t.onclick = () => { filter = t.dataset.s; render(); });
}

function render() {
  tiles();
  const q = $("q").value.toLowerCase();
  let rows = DATA.filter(d => (filter === "all" || d.status === filter) &&
    (d.company + " " + d.role).toLowerCase().includes(q));
  rows.sort((a, b) => {
    let x = a[sortKey], y = b[sortKey];
    if (x == null) x = -1; if (y == null) y = -1;
    const r = typeof x === "number" ? x - y : String(x).localeCompare(String(y));
    return asc ? r : -r;
  });
  document.querySelectorAll("th[data-k]").forEach(th => {
    th.classList.toggle("sorted", th.dataset.k === sortKey);
    th.classList.toggle("asc", th.dataset.k === sortKey && asc);
  });
  $("empty").hidden = rows.length > 0;
  $("rows").innerHTML = rows.map(d => {
    const sc = d.score == null ? "-" : d.score;
    const cls = d.score == null ? "" : d.score >= 75 ? "hi" : d.score >= 55 ? "mid" : "lo";
    const docs = d.docs.map(g => `<div>${esc(g.label)}: ` + g.files.map(f => `<a href="${esc(f.href)}">${esc(f.ext)}</a>`).join(" &middot; ") + `</div>`).join("");
    return `<tr><td><div class="co">${esc(d.company)}</div><div class="role">${esc(d.role)}</div></td>
      <td>${esc(d.date)}</td><td class="score ${cls}">${sc}</td><td>${esc(d.verdict)}</td>
      <td><span class="badge s-${esc(d.status)}">${esc(d.status)}</span></td><td class="docs">${docs}</td></tr>`;
  }).join("");
}

document.querySelectorAll("th[data-k]").forEach(th => th.onclick = () => {
  if (sortKey === th.dataset.k) asc = !asc; else { sortKey = th.dataset.k; asc = false; }
  render();
});
$("q").oninput = render;
$("skipped").innerHTML = SKIPPED.length ? "Skipped: " + SKIPPED.map(esc).join("; ") : "";
render();
</script>
</body>
</html>
"""


def main():
    rows, skipped = collect()

    def js(obj):
        return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")

    page = (PAGE.replace("__GENERATED__", html.escape(datetime.now().strftime("%Y-%m-%d %H:%M")))
            .replace("__DATA__", js(rows)).replace("__STATUSES__", js(STATUSES))
            .replace("__SKIPPED__", js(skipped)))
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT} ({len(rows)} applications, {len(skipped)} skipped)")
    for s in skipped:
        print(f"  skipped: {s}")


if __name__ == "__main__":
    main()
