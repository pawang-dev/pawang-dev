"""Kartu "data berantakan jadi dashboard": sel liar di kiri, dashboard rapi (data asli) di kanan."""
import random

from common import MONO, ORANGE, SAGE, esc, idn
from cards._kit import T, frame, mascot_img, open_svg, spotlight

NAME = "sheet"
THEMED = True
W, H = 960, 420


def monthly(data):
    sums = {}
    for wk in data["weeks"]:
        for d, n, _ in wk:
            sums[d[:7]] = sums.get(d[:7], 0) + n
    return [(int(k[5:7]) - 1, sums[k]) for k in sorted(sums)[-12:]]


def render(theme, ctx, attached=True):
    c, p, S, data = T(theme), ctx.p, ctx.S, ctx.data
    sh = p["sheet"]
    css = (".wob{animation:wob 3.2s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}"
           "@keyframes wob{0%{transform:translate(0,0) rotate(-3deg)}100%{transform:translate(3px,-4px) rotate(3deg)}}"
           ".flow{stroke-dasharray:6 8;animation:flow 1.1s linear infinite}"
           "@keyframes flow{to{stroke-dashoffset:-28}}"
           ".bar{transform-box:fill-box;transform-origin:50% 100%;animation:grow 1s cubic-bezier(.2,.8,.2,1) both}"
           "@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}")
    o = [open_svg(W, H, f'{sh["labels"][0]} → {sh["labels"][1]}', c, css)]
    a = o.append
    a(frame(W, H, c, attached))
    w0, w1 = len(sh["labels"][0]) * 8.2 + 32, len(sh["labels"][1]) * 8.2 + 32
    a(f'<rect x="32" y="22" width="{w0:.0f}" height="28" rx="14" fill="{ORANGE}" opacity=".18"/>')
    a(f'<text x="{32 + w0/2:.0f}" y="41" text-anchor="middle" class="b" style="font-size:12.5px;letter-spacing:1px;fill:{c["orange_txt"]}">{esc(sh["labels"][0])}</text>')
    a(f'<rect x="608" y="22" width="{w1:.0f}" height="28" rx="14" fill="{SAGE}" opacity="{.28 if c["dark"] else .4}"/>')
    a(f'<text x="{608 + w1/2:.0f}" y="41" text-anchor="middle" class="b" style="font-size:12.5px;letter-spacing:1px;fill:{c["sage"]}">{esc(sh["labels"][1])}</text>')
    rnd = random.Random(11)
    for i, v in enumerate(sh["messy"]):
        col, row = i % 3, i // 3
        x, y = 36 + col * 104 + rnd.randint(-5, 5), 86 + row * 64 + rnd.randint(-6, 6)
        rot = rnd.randint(-13, 13)
        bad = v.startswith("#") or v in ("???", "dup?")
        a(f'<g transform="translate({x} {y}) rotate({rot})"><g class="wob" style="animation-delay:{rnd.random()*2:.1f}s">'
          f'<rect width="96" height="32" rx="6" fill="{c["panel"]}" stroke="{ORANGE if bad else c["line"]}" stroke-width="{1.6 if bad else 1}"/>'
          f'<text x="48" y="21" text-anchor="middle" style="font-family:{MONO};font-size:11px;fill:{c["orange_txt"] if bad else c["text"]}">{esc(v)}</text></g></g>')
    a(f'<path class="flow" d="M352 200H394" fill="none" stroke="{ORANGE}" stroke-width="3" stroke-linecap="round"/>')
    a(f'<path d="M392 192L402 200L392 208" fill="none" stroke="{ORANGE}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    a(spotlight(480, 196, 74, c))
    a(mascot_img(ctx, 480, 196, 0.6))
    if p["mascot"]["name"]:
        a(f'<text x="480" y="298" text-anchor="middle" class="b" style="font-size:14px">{esc(p["mascot"]["name"])}</text>')
    a(f'<path class="flow" d="M566 200H600" fill="none" stroke="{SAGE}" stroke-width="3" stroke-linecap="round"/>')
    a(f'<path d="M598 192L608 200L598 208" fill="none" stroke="{SAGE}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    dx, dy, dw, dh = 616, 70, 312, 284
    a(f'<rect x="{dx}" y="{dy}" width="{dw}" height="{dh}" rx="14" fill="{c["panel"]}" stroke="{c["line"]}"/>')
    for i, col in enumerate((ORANGE, SAGE, c["muted"])):
        a(f'<circle cx="{dx+20+i*16}" cy="{dy+20}" r="4.5" fill="{col}"/>')
    a(f'<text x="{dx+dw-16}" y="{dy+24}" text-anchor="end" class="m mono" style="font-size:11px">dashboard.{esc((p["name"] or "app").lower().replace(" ", ""))}</text>')
    kp = ((S["kpi_contrib"], idn(data["total"])), (S["kpi_repo"], idn(data["repos"])), (S["kpi_commits"], idn(data["commits"])))
    for i, (k, v) in enumerate(kp):
        x = dx + 16 + i * 98
        a(f'<rect x="{x}" y="{dy+40}" width="90" height="56" rx="10" fill="{c["panel2"]}"/>')
        a(f'<text x="{x+12}" y="{dy+60}" class="m" style="font-size:11px">{esc(k)}</text>')
        a(f'<text x="{x+12}" y="{dy+84}" class="b" style="font-size:20px">{v}</text>')
    series = monthly(data)
    top = max([n for _, n in series] + [1])
    base_y, max_h = dy + dh - 34, 112
    for i, (m, n) in enumerate(series):
        h = max(4, n / top * max_h)
        x = dx + 16 + i * 24.5
        a(f'<rect class="bar" style="animation-delay:{i*0.07:.2f}s" x="{x:.1f}" y="{base_y-h:.1f}" width="17" height="{h:.1f}" rx="4" '
          f'fill="{ORANGE if i == len(series) - 1 else SAGE}"/>')
        a(f'<text x="{x+8.5:.1f}" y="{base_y+16}" text-anchor="middle" class="m" style="font-size:10px">{esc(S["months"][m][0])}</text>')
    a(f'<text x="480" y="394" text-anchor="middle" class="b" style="font-size:15px">{esc(sh["caption"])} '
      f'<tspan fill="{c["orange_txt"]}">{esc(sh["accent"])}</tspan></text>')
    a("</svg>")
    return "".join(o)
