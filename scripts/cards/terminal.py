"""Kartu terminal hijau: heatmap hijau, panel identitas, potret pixel maskot."""
from common import card_path, esc, idn, safe_stem
from cards.neofetch import level

NAME = "terminal"
THEMED = False          # satu file saja (tema gelap)
FILE = "terminal_green.svg"
W, H = 960, 690
MONO = "'JetBrains Mono','SF Mono','Menlo','Consolas','DejaVu Sans Mono',monospace"
BG = "#040905"
G = ["#0b2412", "#0f4a21", "#12782d", "#22c552", "#4dff7c"]
TXT, DIM, MUTED = "#4dff7c", "#22a24c", "#4a7d58"
LINE = "#12361c"


def render(ctx, attached=True):
    p, S, data = ctx.p, ctx.S, ctx.data
    user = p["username"]
    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
      f'aria-label="{esc(p["name"] + p["suffix"])}: terminal">')
    a(f"""<defs>
<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.4" fill="#000" opacity=".28"/></pattern>
<radialGradient id="vig" cx="50%" cy="45%" r="75%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".55"/></radialGradient>
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
    a(f'<path d="{card_path(W, H, attached=attached)}" fill="{BG}"/>')
    a('<text x="28" y="27" class="m">●</text><text x="46" y="27" class="m">●</text><text x="64" y="27" class="m">●</text>')
    a(f'<text x="100" y="27" class="d">{esc(user)}/README.md</text>')
    if p["badge"]:
        a(f'<text x="{W-28}" y="27" text-anchor="end" class="m">{esc(p["badge"])}</text>')
    a(f'<line x1="0" y1="42" x2="{W}" y2="42" stroke="{LINE}"/>')

    # heatmap
    weeks = data["weeks"]
    mx = max([n for w in weeks for _, n, _ in w] + [1])
    gx, gy, cell, gap = 56, 124, 13, 3
    step = cell + gap
    a(f'<g filter="url(#glow)"><text x="{gx}" y="82" style="font-size:17px" class="b">{esc(S["contrib_year"].format(n=idn(data["total"])))}'
      + (f' <tspan class="m" style="font-size:12px;font-weight:400">{esc(S["sample"])}</tspan>' if data["sample"] else '') + '</text></g>')
    a(f'<rect x="{W-176}" y="62" width="120" height="28" rx="4" fill="none" stroke="{DIM}"/>')
    a(f'<text x="{W-116}" y="81" text-anchor="middle" class="d">{esc(S["year_btn"])}</text>')
    last = -1
    for i, wk in enumerate(weeks):
        m = int(wk[0][0][5:7]) - 1
        if m != last and i < len(weeks) - 2:
            a(f'<text x="{gx+i*step}" y="{gy-10}" class="m" style="font-size:11px">{esc(S["months"][m])}</text>')
            last = m
    a('<g filter="url(#glow)">')
    for i, wk in enumerate(weeks):
        for (_, n, wd) in wk:
            a(f'<rect class="cell" style="animation-delay:{i*0.015:.2f}s" x="{gx+i*step}" y="{gy+wd*step}" '
              f'width="{cell}" height="{cell}" rx="2" fill="{G[level(n, mx)]}"/>')
    a('</g>')
    a(f'<text x="{gx}" y="{gy+7*step+18}" class="m" style="font-size:11px">› github activity heatmap :: contribution stream online</text>')
    a(f'<line x1="30" y1="272" x2="{W-30}" y2="272" stroke="{LINE}"/>')

    # panel kiri
    PX, PY, PW, PH = 40, 296, 540, 350
    a(f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="6" fill="#06110a" stroke="{LINE}"/>')
    status = f'// {S["brand_identity"]}   STATUS: <tspan class="d">ONLINE</tspan>'
    if p["mode"]:
        status += f'   MODE: <tspan class="d">{esc(p["mode"].upper())}</tspan>'
    a(f'<text x="{PX+24}" y="{PY+30}" class="m" style="font-size:11px">{status}</text>')
    name, suffix = p["name"].upper(), p["suffix"].upper()
    size = 64 if len(name) <= 9 else max(34, int(430 / (len(name) * 0.66)))
    sfx = f'<tspan class="d" style="font-size:{max(16, size * 28 // 64)}px">{esc(suffix)}</tspan>' if suffix else ""
    a(f'<g filter="url(#glow)"><text x="{PX+24}" y="{PY+92}" class="b" style="font-size:{size}px;letter-spacing:2px">{esc(name)}{sfx}</text></g>')
    if p["tagline"]:
        a(f'<text x="{PX+24}" y="{PY+126}" class="b" style="font-size:15px">{esc(p["tagline"][:56])}</text>')
    y = PY + 160
    rows = [r for r in p["info"] if r["terminal"]][:5]
    for r in rows:
        a(f'<text x="{PX+24}" y="{y}" class="d">&gt; {esc(r["label"].upper())}</text><text x="{PX+130}" y="{y}">{esc(r["value"][:46])}</text>')
        y += 22
    y += 6
    stats = [(S["repo"], data["repos"]), (S["stars"], data["stars"]), (S["commits"], data["commits"]), (S["followers"], data["followers"])]
    for i, (k, v) in enumerate(stats):
        bx = PX + 24 + i * 122
        a(f'<rect x="{bx}" y="{y-14}" width="112" height="42" rx="4" fill="none" stroke="{LINE}"/>')
        a(f'<text x="{bx+10}" y="{y+2}" class="m" style="font-size:10px">{esc(k.upper())}</text>')
        a(f'<text x="{bx+10}" y="{y+21}" class="b" style="font-size:16px">{idn(v)}</text>')
    a(f'<text x="{PX+24}" y="{PY+PH-22}" class="d">~ $ <tspan class="cur">█</tspan></text>')

    # panel kanan (potret)
    QX, QY, QW, QH = 610, 296, 310, 350
    a(f'<rect x="{QX}" y="{QY}" width="{QW}" height="{QH}" rx="6" fill="#06110a" stroke="{LINE}"/>')
    for (cx, cy, dx, dy) in ((QX, QY, 1, 1), (QX+QW, QY, -1, 1), (QX, QY+QH, 1, -1), (QX+QW, QY+QH, -1, -1)):
        a(f'<path d="M{cx} {cy+dy*14}V{cy}H{cx+dx*14}" fill="none" stroke="{TXT}" stroke-width="2"/>')
    pct_vals = [0, 20, 40, 60, 80, 100, 100]
    n = len(pct_vals)
    keys = ";".join(f"{i/n:.4f}" for i in range(n)) + ";1"
    dur = "7s"
    for i in range(n):
        vals = ";".join("1" if j == i else "0" for j in range(n)) + ";" + ("1" if i == n - 1 else "0")
        a(f'<text x="{QX+22}" y="{QY+30}" class="b" opacity="0">PRINTING {pct_vals[i]}%'
          f'<animate attributeName="opacity" values="{vals}" keyTimes="{keys}" calcMode="discrete" dur="{dur}" repeatCount="indefinite"/></text>')
    pj = ctx.portrait
    if pj:
        cols, prow, grid = pj["cols"], pj["rows"], pj["grid"]
        c = min(4.9, 290 / max(prow, 1), 280 / max(cols, 1))
        ox, oy = QX + (QW - cols * c) / 2, QY + 44
        full = prow * c
        hs = ";".join(f"{full*pc/100:.1f}" for pc in pct_vals) + f";{full:.1f}"
        a(f'<clipPath id="pc"><rect x="{ox-2}" y="{oy-2}" width="{cols*c+4}" height="0">'
          f'<animate attributeName="height" values="{hs}" keyTimes="{keys}" calcMode="discrete" dur="{dur}" repeatCount="indefinite"/></rect></clipPath>')
        a('<g clip-path="url(#pc)" filter="url(#glow)">')
        for r in range(prow):
            for cc in range(cols):
                lv = grid[r][cc]
                if lv:
                    a(f'<rect x="{ox+cc*c:.1f}" y="{oy+r*c:.1f}" width="{c-0.7:.1f}" height="{c-0.7:.1f}" fill="{G[lv]}"/>')
        a('</g>')
    else:                                           # tanpa potret: inisial besar bergaya terminal
        a(f'<g filter="url(#glow)"><text x="{QX+QW/2}" y="{QY+230}" text-anchor="middle" class="b" '
          f'style="font-size:170px;fill:{TXT}">{esc((p["name"][:1] or "?").upper())}</text></g>')
    stem = safe_stem(p["mascot"]["name"])
    a(f'<text x="{QX+22}" y="{QY+QH-16}" class="m" style="font-size:11px">› {stem}.svg  line 42 / 86</text>')
    a(f'<text x="{QX+QW-22}" y="{QY+30}" text-anchor="end" class="m" style="font-size:11px">@{esc(user)}</text>')

    a(f'<path d="{card_path(W, H, attached=attached)}" fill="url(#scan)" pointer-events="none"/>')
    a(f'<path d="{card_path(W, H, attached=attached)}" fill="url(#vig)" pointer-events="none"/>')
    a(f'<path transform="translate(.5 .5)" d="{card_path(W-1, H-1, attached=attached)}" fill="none" stroke="{DIM}" stroke-opacity=".6"/>')
    a('</svg>')
    return "\n".join(o)
