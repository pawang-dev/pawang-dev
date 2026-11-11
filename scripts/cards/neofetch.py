"""Kartu neofetch: foto/maskot di kiri, info di kanan, heatmap kontribusi di bawah."""
from common import THEMES, card_path, esc, idn

NAME = "neofetch"
THEMED = True
W, H = 960, 624
MONO = "'JetBrains Mono','SF Mono','Menlo','Consolas','DejaVu Sans Mono',monospace"


def level(n, mx):
    if n <= 0:
        return 0
    r = n / mx
    return 1 if r <= .25 else 2 if r <= .5 else 3 if r <= .75 else 4


def render(theme, ctx, attached=True):
    c, p, S, data = THEMES[theme], ctx.p, ctx.S, ctx.data
    user, domain = p["username"], p["domain"]
    where = domain or "github"
    o = []
    a = o.append
    label = f'{p["name"]}{p["suffix"]}: {p["tagline"]}'.strip(": ")
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(label)}">')
    a(f"""<style>
text{{font-family:{MONO};font-size:14px;fill:{c['text']}}}
.k{{fill:{c['key']};font-weight:700}}
.m{{fill:{c['muted']}}}
.h{{font-size:15px;font-weight:700}}
.s{{font-size:12px;fill:{c['muted']}}}
.cur{{animation:blink 1.1s steps(1) infinite}}
.tw{{animation:tw 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
.cell{{animation:pop .5s ease-out both}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes tw{{0%,100%{{opacity:.25;transform:scale(.7)}}50%{{opacity:1;transform:scale(1.15)}}}}
@keyframes pop{{from{{opacity:0}}to{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{.cur,.tw,.cell{{animation:none}}}}
</style>""")
    a(f'<path d="{card_path(W, H, attached=attached)}" fill="{c["bg"]}"/>')
    a(f'<path transform="translate(.5 .5)" d="{card_path(W-1, H-1, attached=attached)}" fill="none" stroke="{c["line"]}"/>')
    # title bar
    a(f'<path d="M0 14a14 14 0 0 1 14-14h{W-28}a14 14 0 0 1 14 14v34H0z" fill="{c["panel"]}"/>')
    a(f'<line x1="0" y1="48" x2="{W}" y2="48" stroke="{c["line"]}"/>')
    for i, col in enumerate((c["orange"], c["accent"], c["muted"])):
        a(f'<circle cx="{26+i*20}" cy="24" r="6" fill="{col}"/>')
    a(f'<image x="100" y="11" width="28" height="27" preserveAspectRatio="xMidYMid meet" href="{ctx.logo}"/>')
    title = f"{user} — {domain} — zsh" if domain else f"{user} — zsh"
    a(f'<text x="138" y="29" class="m">{esc(title)}</text>')
    if p["badge"]:
        a(f'<text x="{W-24}" y="29" text-anchor="end" class="s">{esc(p["badge"])}</text>')

    # kartu maskot
    a(f'<rect x="30" y="70" width="270" height="302" rx="16" fill="{c["card"]}" stroke="{c["card_line"]}"/>')
    a(f'<image x="52" y="80" width="226" height="257" preserveAspectRatio="xMidYMid meet" href="{ctx.mascot}"/>')
    if p["mascot"]["name"]:
        a(f'<text x="165" y="361" text-anchor="middle" style="fill:#14213D;font-weight:700">{esc(p["mascot"]["name"])}</text>')
    for (x, y, d) in ((262, 100, 0), (252, 126, 0.8)):
        a(f'<path class="tw" style="animation-delay:{d}s" d="M{x} {y-8}Q{x} {y} {x+8} {y}'
          f'Q{x} {y} {x} {y+8}Q{x} {y} {x-8} {y}Q{x} {y} {x} {y-8}z" fill="{c["orange"]}"/>')

    # panel info
    X, VX = 340, 440
    a(f'<text x="{X}" y="92" class="h"><tspan class="k">{esc(user)}</tspan>@{esc(where)}</text>')
    a(f'<line x1="{X}" y1="104" x2="{W-30}" y2="104" stroke="{c["line"]}"/>')
    y = 130
    for r in p["info"]:
        a(f'<text x="{X}" y="{y}" class="k">{esc(r["label"])}</text>')
        a(f'<text x="{VX}" y="{y}">{esc(r["value"])}</text>')
        y += 23
    y += 10
    a(f'<text x="{X}" y="{y}" class="h">{esc(S["github_stats"])}</text>')
    a(f'<line x1="{X+118}" y1="{y-5}" x2="{W-30}" y2="{y-5}" stroke="{c["line"]}"/>')
    y += 26
    stats = [(S["repo"], data["repos"]), (S["stars"], data["stars"]), (S["commits"], data["commits"]), (S["followers"], data["followers"])]
    for i, (k, v) in enumerate(stats):
        sx, sy = X + (i % 2) * 280, y + (i // 2) * 23
        a(f'<text x="{sx}" y="{sy}" class="k">{esc(k)}</text>')
        a(f'<text x="{sx+100}" y="{sy}">{idn(v)}</text>')
    prompt = p["prompt"]
    a(f'<text x="{X}" y="{y+45}"><tspan class="k">~ $</tspan> {esc(prompt)}'
      f'<tspan class="cur" style="fill:{c["orange"]}"> █</tspan></text>')

    # heatmap
    weeks = data["weeks"]
    mx = max([n for w in weeks for _, n, _ in w] + [1])
    a(f'<line x1="30" y1="398" x2="{W-30}" y2="398" stroke="{c["line"]}"/>')
    a(f'<text x="30" y="428" class="h">{esc(S["contrib_year"].format(n=idn(data["total"])))}'
      + (f' <tspan class="s">{esc(S["sample"])}</tspan>' if data["sample"] else '') + '</text>')
    cell, gap = 13, 3
    step = cell + gap
    gx, gy = 30, 466
    last = -1
    for i, wk in enumerate(weeks):
        m = int(wk[0][0][5:7]) - 1
        if m != last and i < len(weeks) - 2:
            a(f'<text x="{gx+i*step}" y="{gy-10}" class="s">{esc(S["months"][m])}</text>')
            last = m
    opac = {1: .3, 2: .55, 3: .8, 4: 1}
    for i, wk in enumerate(weeks):
        for (_, n, wd) in wk:
            lv = level(n, mx)
            x, yy = gx + i * step, gy + wd * step
            delay = f"animation-delay:{i*0.015:.2f}s"
            fill = c["cell0"] if lv == 0 else c["orange"]
            fo = "" if lv == 0 else f' fill-opacity="{opac[lv]}"'
            a(f'<rect class="cell" style="{delay}" x="{x}" y="{yy}" width="{cell}" height="{cell}" rx="3" fill="{fill}"{fo}/>')
    ly = gy + 7 * step + 12
    a(f'<text x="30" y="{ly+10}" class="s">github.com/{esc(user)}</text>')
    lx = W - 30 - (5 * step) - 108
    a(f'<text x="{lx}" y="{ly+10}" class="s">{esc(S["less"])}</text>')
    for i in range(5):
        fill = c["cell0"] if i == 0 else c["orange"]
        fo = "" if i == 0 else f' fill-opacity="{opac[i]}"'
        a(f'<rect x="{lx+56+i*step}" y="{ly}" width="{cell}" height="{cell}" rx="3" fill="{fill}"{fo}/>')
    a(f'<text x="{lx+56+5*step+4}" y="{ly+10}" class="s">{esc(S["more"])}</text>')
    a("</svg>")
    return "\n".join(o)
