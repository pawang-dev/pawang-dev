"""Potongan SVG yang dipakai bersama oleh kartu bergaya brand (hero, brand, sheet, typing)."""
from common import CREAM, MONO, NAVY, ORANGE, SANS, THEMES, card_path, esc


def T(theme):
    c = dict(THEMES[theme])
    dark = theme == "dark"
    c.update(dark=dark, panel2="#22345C" if dark else "#FFF0DC", spot=CREAM if dark else "#FFFFFF",
             on_card=NAVY, orange_txt=ORANGE if dark else "#C85A12", sage=THEMES["dark"]["accent"] if dark else "#6E9468")
    return c


def open_svg(w, h, label, c, extra_css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{esc(label)}"><style>'
        f"text{{font-family:{SANS};fill:{c['text']}}}"
        f".mono{{font-family:{MONO}}} .m{{fill:{c['muted']}}} .b{{font-weight:700}}"
        f".tw{{animation:tw 2.6s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}"
        "@keyframes tw{0%,100%{opacity:.25;transform:scale(.7)}50%{opacity:1;transform:scale(1.15)}}"
        f"{extra_css}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
        "</style>")


def frame(w, h, c, attached):
    return (f'<path d="{card_path(w, h, attached=attached)}" fill="{c["bg"]}"/>'
            f'<path transform="translate(.5 .5)" d="{card_path(w-1, h-1, attached=attached)}" fill="none" stroke="{c["line"]}"/>')


def sparkle(x, y, s, color, delay=0.0):
    return (f'<path class="tw" style="animation-delay:{delay}s" d="M{x} {y-s}Q{x} {y} {x+s} {y}'
            f'Q{x} {y} {x} {y+s}Q{x} {y} {x-s} {y}Q{x} {y} {x} {y-s}z" fill="{color}"/>')


def spotlight(cx, cy, r, c):
    """Lingkaran terang di belakang maskot (maskot bisa gelap, jadi butuh latar terang)."""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c["spot"]}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r+10}" fill="none" stroke="{ORANGE}" stroke-width="2.5" '
            f'stroke-dasharray="4 10" stroke-linecap="round" opacity=".9">'
            f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" '
            f'to="360 {cx} {cy}" dur="40s" repeatCount="indefinite"/></circle>')


def mascot_img(ctx, cx, cy, scale=1.0):
    w, h = 226 * scale, 257 * scale
    return (f'<image x="{cx - w/2:.1f}" y="{cy - h/2:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'preserveAspectRatio="xMidYMid meet" href="{ctx.mascot}"/>')


def logo_img(ctx, x, y, w, h):
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="{ctx.logo}"/>'


def icon(kind, x, y, c):
    col = c["orange_txt"]
    s = f'fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    box = f'<rect x="{x}" y="{y}" width="44" height="44" rx="12" fill="{ORANGE}" opacity=".16"/>'
    P = lambda d: f'<path d="{d}" {s}/>'  # noqa: E731
    g = {
        "web": f'<rect x="{x+10}" y="{y+12}" width="24" height="20" rx="3" {s}/>' + P(f"M{x+10} {y+19}H{x+34}"),
        "seo": f'<circle cx="{x+20}" cy="{y+20}" r="8" {s}/>' + P(f"M{x+26} {y+26}L{x+33} {y+33}"),
        "sheet": (f'<rect x="{x+11}" y="{y+11}" width="22" height="22" rx="3" {s}/>'
                  + P(f"M{x+18.3} {y+11}V{y+33}M{x+25.7} {y+11}V{y+33}M{x+11} {y+18.3}H{x+33}M{x+11} {y+25.7}H{x+33}")),
        "otomasi": (f'<circle cx="{x+22}" cy="{y+22}" r="5" {s}/>' + "".join(
            P(f"M{x+22+9*dx:.1f} {y+22+9*dy:.1f}L{x+22+12.5*dx:.1f} {y+22+12.5*dy:.1f}")
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, .7), (.7, -.7), (-.7, -.7)))),
        "rawat": (P(f"M{x+22} {y+10}L{x+33} {y+14}V{y+23}C{x+33} {y+29} {x+28} {y+33} {x+22} {y+35}"
                    f"C{x+16} {y+33} {x+11} {y+29} {x+11} {y+23}V{y+14}Z") + P(f"M{x+17} {y+23}L{x+21} {y+27}L{x+28} {y+19}")),
        "code": P(f"M{x+17} {y+15}L{x+9} {y+22}L{x+17} {y+29}M{x+27} {y+15}L{x+35} {y+22}L{x+27} {y+29}M{x+24.5} {y+12}L{x+19.5} {y+32}"),
        "design": P(f"M{x+12} {y+32}L{x+14} {y+24}L{x+30} {y+8}L{x+36} {y+14}L{x+20} {y+30}Z") + P(f"M{x+27} {y+11}L{x+33} {y+17}"),
        "chart": P(f"M{x+12} {y+33}V{y+22}M{x+22} {y+33}V{y+14}M{x+32} {y+33}V{y+19}"),
        "chat": P(f"M{x+11} {y+12}H{x+33}V{y+28}H{x+21}L{x+15} {y+34}V{y+28}H{x+11}Z"),
        "mail": f'<rect x="{x+10}" y="{y+13}" width="24" height="18" rx="3" {s}/>' + P(f"M{x+11} {y+15}L{x+22} {y+24}L{x+33} {y+15}"),
        "star": P(f"M{x+22} {y+10}L{x+25.5} {y+18.5}L{x+34} {y+19.2}L{x+27.5} {y+25}L{x+29.5} {y+33.5}L{x+22} {y+29}L{x+14.5} {y+33.5}L{x+16.5} {y+25}L{x+10} {y+19.2}L{x+18.5} {y+18.5}Z"),
    }[kind]
    return box + g
