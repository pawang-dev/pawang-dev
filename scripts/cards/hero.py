"""Banner pembuka: headline besar, deskripsi singkat, dan maskot di atas pegunungan."""
import random

from common import BONE, ORANGE, SAGE, card_path, esc, split_accent
from cards._kit import T, logo_img, mascot_img, open_svg, sparkle, spotlight

NAME = "hero"
THEMED = True
W, H = 960, 330


def render(theme, ctx, attached=True):
    c, p = T(theme), ctx.p
    label = f'{p["name"]}{p["suffix"]}: {p["tagline"] or p["hero"]["line1"]}'
    o = [open_svg(W, H, label, c)]
    a = o.append
    sky2 = "#1B2B4F" if c["dark"] else "#FFEBD2"
    a(f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["bg"]}"/>'
      f'<stop offset="1" stop-color="{sky2}"/></linearGradient></defs>')
    a(f'<path d="{card_path(W, H, attached=attached)}" fill="url(#sky)"/>')
    if c["dark"]:
        rnd = random.Random(7)
        for _ in range(26):
            x, y, r = rnd.randint(24, 936), rnd.randint(14, 150), rnd.choice([1, 1, 1.4, 1.8])
            a(f'<circle class="tw" style="animation-delay:{rnd.random()*3:.1f}s" cx="{x}" cy="{y}" r="{r}" fill="{BONE}" opacity=".7"/>')
    a(f'<path d="M0 275L110 250L210 268L330 240L430 270L560 235L680 262L800 215L920 250L960 238V{H}H0Z" fill="{SAGE}" opacity="{.22 if c["dark"] else .35}"/>')
    a(f'<path d="M0 300L130 278L250 296L390 266L520 298L660 272L790 296L960 268V{H}H0Z" fill="{SAGE}" opacity="{.38 if c["dark"] else .6}"/>')
    a(spotlight(772, 160, 118, c))
    a(mascot_img(ctx, 772, 160, 0.98))
    a(sparkle(905, 70, 11, ORANGE) + sparkle(640, 60, 8, ORANGE, .8) + sparkle(890, 250, 7, ORANGE, 1.4))
    a(logo_img(ctx, 48, 26, 38, 36))
    a(f'<text x="96" y="52" class="b" style="font-size:22px">{esc(p["name"])}<tspan fill="{c["orange_txt"]}">{esc(p["suffix"])}</tspan></text>')
    h = p["hero"]
    a(f'<text x="48" y="122" class="b" style="font-size:46px;letter-spacing:-1px">{esc(h["line1"])}</text>')
    pre, acc, post = split_accent(h["line2"], h["accent"])
    a(f'<text x="48" y="174" class="b" style="font-size:46px;letter-spacing:-1px">{esc(pre)}'
      + (f'<tspan fill="{c["orange_txt"]}">{esc(acc)}</tspan>{esc(post)}' if acc else "") + '</text>')
    for i, line in enumerate(p["description"]):
        a(f'<text x="48" y="{212 + i*21}" class="m" style="font-size:14.5px">{esc(line)}</text>')
    chips = h["chips"] or [s["title"].replace(p["name"], "").strip() or s["title"] for s in p["services"]][:6]
    x = 48
    for chip in chips:
        w = len(chip) * 7.6 + 26
        a(f'<rect x="{x:.0f}" y="252" width="{w:.0f}" height="26" rx="13" fill="{c["panel"]}" stroke="{c["line"]}"/>')
        a(f'<text x="{x + w/2:.0f}" y="269" text-anchor="middle" style="font-size:12.5px;font-weight:600">{esc(chip)}</text>')
        x += w + 8
    a("</svg>")
    return "".join(o)
