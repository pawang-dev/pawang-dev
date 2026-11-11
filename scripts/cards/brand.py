"""Kartu brand: layanan, paket, dan nilai."""
from common import ORANGE, SAGE, NAVY, esc, split_accent
from cards._kit import T, frame, icon, logo_img, mascot_img, open_svg, sparkle

NAME = "brand"
THEMED = True
W, H = 960, 568


def render(theme, ctx, attached=True):
    c, p, S = T(theme), ctx.p, ctx.S
    o = [open_svg(W, H, f'{p["name"]}{p["suffix"]}: {S["plans"]}', c)]
    a = o.append
    a(frame(W, H, c, attached))
    a(logo_img(ctx, 32, 20, 46, 44))
    a(f'<text x="90" y="50" class="b" style="font-size:26px">{esc(p["name"])}<tspan fill="{c["orange_txt"]}">{esc(p["suffix"])}</tspan></text>')
    if p["tagline"]:
        pre, acc, post = split_accent(p["tagline"], p["tagline_accent"])
        a(f'<text x="928" y="48" text-anchor="end" class="b" style="font-size:15px">{esc(pre)}'
          + (f'<tspan fill="{c["orange_txt"]}">{esc(acc)}</tspan>{esc(post)}' if acc else "") + '</text>')
    a(f'<line x1="32" y1="76" x2="928" y2="76" stroke="{c["line"]}"/>')
    # kartu maskot
    a(f'<rect x="32" y="92" width="240" height="446" rx="16" fill="{c["spot"]}" stroke="{c["card_line"]}"/>')
    a(mascot_img(ctx, 152, 228))
    a(sparkle(236, 120, 9, ORANGE) + sparkle(222, 148, 6, ORANGE, 1))
    m = p["mascot"]
    if m["name"]:
        a(f'<text x="152" y="378" text-anchor="middle" class="b" style="font-size:20px;fill:{NAVY}">{esc(m["name"])}</text>')
    if m["caption"]:
        a(f'<text x="152" y="398" text-anchor="middle" style="font-size:12px;fill:#5B6784">{esc(m["caption"])}</text>')
    if p["values"]:
        a('<line x1="52" y1="414" x2="252" y2="414" stroke="#E6D6BB"/>')
        a(f'<text x="52" y="436" class="b" style="font-size:11px;letter-spacing:1.5px;fill:#5B6784">{esc(S["brand_values"])}</text>')
        for i, v in enumerate(p["values"]):
            yy = 462 + i * 24
            a(f'<circle cx="58" cy="{yy-4}" r="5" fill="{SAGE}"/>')
            a(f'<text x="72" y="{yy}" class="b" style="font-size:14px;fill:{NAVY}">{esc(v["name"])}</text>')
            a(f'<text x="136" y="{yy}" style="font-size:12px;fill:#5B6784">{esc(v["desc"])}</text>')
    # layanan
    for i, s in enumerate(p["services"]):
        x, y = 296 + (i % 2) * 324, 92 + (i // 2) * 154
        a(f'<rect x="{x}" y="{y}" width="308" height="138" rx="14" fill="{c["panel"]}" stroke="{c["line"]}"/>')
        a(icon(s["icon"], x + 16, y + 16, c))
        a(f'<text x="{x+72}" y="{y+44}" class="b" style="font-size:17px">{esc(s["title"])}</text>')
        for j, line in enumerate(s["promise"]):
            a(f'<text x="{x+18}" y="{y+84+j*20}" class="b" style="font-size:13.5px;fill:{c["orange_txt"]}">{esc(line)}</text>')
        if s["detail"]:
            a(f'<text x="{x+18}" y="{y+126}" class="m" style="font-size:12px">{esc(s["detail"])}</text>')
    # paket
    if p["packages"]:
        k = len(p["services"])
        x, y = 296 + (k % 2) * 324, 92 + (k // 2) * 154
        a(f'<rect x="{x}" y="{y}" width="308" height="138" rx="14" fill="{c["panel"]}" stroke="{c["line"]}"/>')
        a(f'<text x="{x+18}" y="{y+34}" class="b" style="font-size:17px">{esc(S["plans"])}</text>')
        styles = ((SAGE, NAVY, None), (ORANGE, NAVY, None), ("none", c["text"], c["text"]))
        for i, pk in enumerate(p["packages"]):
            fill, tc, stroke = styles[i]
            cx = x + 18 + i * 96
            st = f' stroke="{stroke}" stroke-width="1.5"' if stroke else ""
            a(f'<rect x="{cx}" y="{y+50}" width="86" height="30" rx="15" fill="{fill}"{st}/>')
            a(f'<text x="{cx+43}" y="{y+70}" text-anchor="middle" class="b" style="font-size:13px;fill:{tc}">{esc(pk["name"])}</text>')
            if pk["desc"]:
                a(f'<text x="{cx+43}" y="{y+100}" text-anchor="middle" class="m" style="font-size:12px">{esc(pk["desc"])}</text>')
        a(f'<text x="{x+18}" y="{y+126}" class="m" style="font-size:12px">{esc(S["plans_note"].format(n=len(p["packages"])))}</text>')
    a("</svg>")
    return "".join(o)
