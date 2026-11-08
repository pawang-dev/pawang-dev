#!/usr/bin/env python3
"""Generator SVG profil versi terminal hijau -> assets/svg/terminal_green.svg

Memakai data & fungsi dari build.py (token GH_TOKEN opsional).
Potret pixel diambil dari assets/data/portrait.json (dibuat oleh make_portrait.py).
"""
import json
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import MONTHS, ROOT, USERNAME, get_data, idn, level  # noqa: E402

MONO = "'JetBrains Mono','SF Mono','Menlo','Consolas','DejaVu Sans Mono',monospace"
W, H = 960, 690

BG = "#040905"
G = ["#0b2412", "#0f4a21", "#12782d", "#22c552", "#4dff7c"]   # level 0..4
TXT, DIM, MUTED = "#4dff7c", "#22a24c", "#4a7d58"
LINE = "#12361c"

# --- isi teks (ubah sesuai selera)
LAYANAN = "Web · SEO · Sheet · Otomasi · Rawat"
TAGLINE = "Digitalmu liar? Serahkan ke Pawang."
ROWS_INFO = [
    ("LAYANAN", LAYANAN),
    ("PAKET", "Jinak → Piawai → Sakti"),
    ("NILAI", "Tenang · Paham · Jinak"),
    ("UNTUK", "UMKM Indonesia"),
]
BUTTONS = ["WEBSITE", "KONSULTASI", "GITHUB"]


def render(data):
    o, a = [], None
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'role="img" aria-label="Profil GitHub Pawang.dev versi terminal hijau">')
    a(f"""<defs>
<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.4" fill="#000" opacity=".28"/></pattern>
<radialGradient id="vig" cx="50%" cy="45%" r="75%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".55"/></radialGradient>
<clipPath id="reveal"><rect id="rv" x="0" y="0" width="{W}" height="0"/></clipPath>
</defs>
<style>
text{{font-family:{MONO};font-size:13px;fill:{TXT}}}
.d{{fill:{DIM}}} .m{{fill:{MUTED}}} .b{{font-weight:700}}
.cur{{animation:blink 1s steps(1) infinite}}
.cell{{animation:pop .5s ease-out both}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes pop{{from{{opacity:0}}to{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{.cur,.cell{{animation:none}}}}
</style>""")
    a(f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>')
    # title bar
    a(f'<text x="28" y="27" class="m">●</text><text x="46" y="27" class="m">●</text><text x="64" y="27" class="m">●</text>')
    a(f'<text x="100" y="27" class="d">{USERNAME}/README.md</text>')
    a(f'<text x="{W-28}" y="27" text-anchor="end" class="m">tty1 · jinak</text>')
    a(f'<line x1="0" y1="42" x2="{W}" y2="42" stroke="{LINE}"/>')

    # ---- heatmap
    weeks = data["weeks"]
    mx = max([n for w in weeks for _, n, _ in w] + [1])
    gx, gy, cell, gap = 56, 124, 13, 3
    step = cell + gap
    a(f'<g filter="url(#glow)"><text x="{gx}" y="82" style="font-size:17px" class="b">{idn(data["total"])} kontribusi dalam setahun terakhir'
      + (' <tspan class="m" style="font-size:12px;font-weight:400">(data contoh)</tspan>' if data["sample"] else '')
      + '</text></g>')
    a(f'<rect x="{W-176}" y="62" width="120" height="28" rx="4" fill="none" stroke="{DIM}"/>')
    a(f'<text x="{W-116}" y="81" text-anchor="middle" class="d">Setahun ▾</text>')
    last = -1
    for i, wk in enumerate(weeks):
        m = int(wk[0][0][5:7]) - 1
        if m != last and i < len(weeks) - 2:
            a(f'<text x="{gx+i*step}" y="{gy-10}" class="m" style="font-size:11px">{MONTHS[m]}</text>')
            last = m
    a('<g filter="url(#glow)">')
    for i, wk in enumerate(weeks):
        for (_, n, wd) in wk:
            lv = level(n, mx)
            a(f'<rect class="cell" style="animation-delay:{i*0.015:.2f}s" x="{gx+i*step}" y="{gy+wd*step}" '
              f'width="{cell}" height="{cell}" rx="2" fill="{G[lv]}"/>')
    a('</g>')
    a(f'<text x="{gx}" y="{gy+7*step+18}" class="m" style="font-size:11px">› github activity heatmap :: contribution stream online</text>')
    a(f'<line x1="30" y1="272" x2="{W-30}" y2="272" stroke="{LINE}"/>')

    # ---- panel kiri
    PX, PY, PW, PH = 40, 296, 540, 350
    a(f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="6" fill="#06110a" stroke="{LINE}"/>')
    a(f'<text x="{PX+24}" y="{PY+30}" class="m" style="font-size:11px">// BRAND IDENTITY   STATUS: <tspan class="d">ONLINE</tspan>   MODE: <tspan class="d">JINAK</tspan></text>')
    a(f'<g filter="url(#glow)"><text x="{PX+24}" y="{PY+92}" class="b" style="font-size:64px;letter-spacing:2px">PAWANG<tspan class="d" style="font-size:28px">.DEV</tspan></text></g>')
    a(f'<text x="{PX+24}" y="{PY+126}" class="b" style="font-size:15px">{escape(TAGLINE)}</text>')
    y = PY + 160
    for k, v in ROWS_INFO:
        a(f'<text x="{PX+24}" y="{y}" class="d">&gt; {k}</text><text x="{PX+130}" y="{y}">{escape(v)}</text>')
        y += 22
    # statistik
    y += 6
    stats = [("REPO", data["repos"]), ("BINTANG", data["stars"]), ("KOMIT", data["commits"]), ("PENGIKUT", data["followers"])]
    for i, (k, v) in enumerate(stats):
        bx = PX + 24 + i * 122
        a(f'<rect x="{bx}" y="{y-14}" width="112" height="42" rx="4" fill="none" stroke="{LINE}"/>')
        a(f'<text x="{bx+10}" y="{y+2}" class="m" style="font-size:10px">{k}</text>')
        a(f'<text x="{bx+10}" y="{y+21}" class="b" style="font-size:16px">{idn(v)}</text>')
    # tombol
    by = PY + PH - 54
    bx = PX + 24
    for label in BUTTONS:
        w = 11 * len(label) + 34
        a(f'<g filter="url(#glow)"><rect x="{bx}" y="{by}" width="{w}" height="30" rx="3" fill="{TXT}"/></g>')
        a(f'<text x="{bx+w/2}" y="{by+20}" text-anchor="middle" class="b" style="fill:{BG};font-size:12px;letter-spacing:1px">{label}</text>')
        bx += w + 14
    a(f'<text x="{PX+PW-24}" y="{by+20}" text-anchor="end" class="d">~ $ <tspan class="cur">█</tspan></text>')

    # ---- panel kanan (potret)
    QX, QY, QW, QH = 610, 296, 310, 350
    a(f'<rect x="{QX}" y="{QY}" width="{QW}" height="{QH}" rx="6" fill="#06110a" stroke="{LINE}"/>')
    for (cx, cy, dx, dy) in ((QX, QY, 1, 1), (QX+QW, QY, -1, 1), (QX, QY+QH, 1, -1), (QX+QW, QY+QH, -1, -1)):
        a(f'<path d="M{cx+dx*0} {cy+dy*14}V{cy}H{cx+dx*14}" fill="none" stroke="{TXT}" stroke-width="2"/>')
    pct_vals = [0, 20, 40, 60, 80, 100, 100]
    n = len(pct_vals)
    keys = ";".join(f"{i/n:.4f}" for i in range(n)) + ";1"
    dur = "7s"
    for i in range(n):
        vals = ";".join("1" if j == i else "0" for j in range(n)) + ";" + ("1" if i == n - 1 else "0")
        a(f'<text x="{QX+22}" y="{QY+30}" class="b" opacity="0">PRINTING {pct_vals[i]}%'
          f'<animate attributeName="opacity" values="{vals}" keyTimes="{keys}" calcMode="discrete" dur="{dur}" repeatCount="indefinite"/></text>')
    # potret pixel
    pj = json.loads((ROOT / "assets" / "data" / "portrait.json").read_text())
    cols, rows, grid = pj["cols"], pj["rows"], pj["grid"]
    c = 4.9
    ox = QX + (QW - cols * c) / 2
    oy = QY + 44
    full = rows * c
    hs = ";".join(f"{full*p/100:.1f}" for p in pct_vals) + f";{full:.1f}"
    a(f'<clipPath id="pc"><rect x="{ox-2}" y="{oy-2}" width="{cols*c+4}" height="0">'
      f'<animate attributeName="height" values="{hs}" keyTimes="{keys}" calcMode="discrete" dur="{dur}" repeatCount="indefinite"/></rect></clipPath>')
    a('<g clip-path="url(#pc)" filter="url(#glow)">')
    for r in range(rows):
        for cc in range(cols):
            lv = grid[r][cc]
            if lv:
                a(f'<rect x="{ox+cc*c:.1f}" y="{oy+r*c:.1f}" width="{c-0.7:.1f}" height="{c-0.7:.1f}" fill="{G[lv]}"/>')
    a('</g>')
    a(f'<text x="{QX+22}" y="{QY+QH-16}" class="m" style="font-size:11px">› dev.svg  line 42 / 86</text>')
    a(f'<text x="{QX+QW-22}" y="{QY+30}" text-anchor="end" class="m" style="font-size:11px">@{USERNAME}</text>')

    # scanline + vignette
    a(f'<rect width="{W}" height="{H}" rx="14" fill="url(#scan)" pointer-events="none"/>')
    a(f'<rect width="{W}" height="{H}" rx="14" fill="url(#vig)" pointer-events="none"/>')
    a(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="{DIM}" stroke-opacity=".6"/>')
    a('</svg>')
    return "\n".join(o)


def main():
    data = get_data()
    out = ROOT / "assets" / "svg" / "terminal_green.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(data), encoding="utf-8")
    print("tulis", out.relative_to(ROOT), f"({out.stat().st_size // 1024} KB)", "[data contoh]" if data["sample"] else "[data live]")


if __name__ == "__main__":
    main()
