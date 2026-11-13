"""Komponen bersama: kartu judul berbingkai + tile krem yang menempel rapat di bawahnya.

Dipakai oleh connect, featured, portfolio, articles, dan activity. Tile tidak bergantung tema (selalu krem),
sedangkan kartu judul punya versi dark dan light.
"""
import base64
import math

from common import CARD_R, CREAM, NAVY, ORANGE, SANS, THEMES, esc

INK, SUB, TILE_LINE = NAVY, "#5B6784", "#E6D6BB"
ORANGE_TXT = {"dark": ORANGE, "light": "#C85A12"}
R = CARD_R


def uri(data: bytes, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(data).decode()


def T(x, y, s, size, weight, fill, extra=""):
    return f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="{size}" font-weight="{weight}" fill="{fill}" {extra}>{esc(s)}</text>'


def tpath(w, h, bl=False, br=False):
    """Tile persegi; hanya sudut bawah yang membulat (di ujung baris terakhir)."""
    return (f"M0 0H{w}" + (f"V{h-R}A{R} {R} 0 0 1 {w-R} {h}" if br else f"V{h}")
            + (f"H{R}A{R} {R} 0 0 1 0 {h-R}" if bl else "H0") + "Z")


def arrow(x, y):
    return (f'<g transform="translate({x} {y})"><path d="M0 11L10 1M2 1H10V9" fill="none" stroke="{ORANGE}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round"/><animateTransform attributeName="transform" type="translate" '
            f'additive="sum" values="0 0;2 -2;0 0" dur="1.8s" repeatCount="indefinite"/></g>')


def wrap_tile(w, h, body, label, divr=True, divb=True, bl=False, br=False, defs=""):
    div = (f'<rect x="{w-1}" y="0" width="1" height="{h}" fill="{TILE_LINE}"/>' if divr else "") + \
          (f'<rect x="0" y="{h-1}" width="{w}" height="1" fill="{TILE_LINE}"/>' if divb else "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
            f'{defs}<path d="{tpath(w, h, bl, br)}" fill="{CREAM}"/>{div}{body}</svg>')


def pct(n):
    """Lebar persen per tile; dibulatkan ke bawah supaya jumlahnya tidak melebihi 100% (hindari baris pecah)."""
    v = math.floor(100 / n * 1000) / 1000
    return f"{int(v)}%" if v == int(v) else f"{v}%"


# ---------------------------------------------------------------- ikon (garis, 44x44)
def icon(kind, x, y, col):
    s = f'fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'

    def P(d):
        return f'<path d="{d}" {s}/>'
    return {
        "star": P(f"M{x+22} {y+10}L{x+25.5} {y+18.5}L{x+34} {y+19.2}L{x+27.5} {y+25}L{x+29.5} {y+33.5}L{x+22} {y+29}"
                  f"L{x+14.5} {y+33.5}L{x+16.5} {y+25}L{x+10} {y+19.2}L{x+18.5} {y+18.5}Z"),
        "web": f'<rect x="{x+10}" y="{y+12}" width="24" height="20" rx="3" {s}/>' + P(f"M{x+10} {y+19}H{x+34}"),
        "doc": f'<rect x="{x+13}" y="{y+10}" width="18" height="24" rx="3" {s}/>' + P(f"M{x+17} {y+18}H{x+27}M{x+17} {y+23}H{x+27}M{x+17} {y+28}H{x+23}"),
        "chart": P(f"M{x+12} {y+33}V{y+22}M{x+22} {y+33}V{y+14}M{x+32} {y+33}V{y+19}"),
        "link": P(f"M{x+19} {y+25}L{x+25} {y+19}M{x+16} {y+22}L{x+13} {y+25}A4.2 4.2 0 0 0 {x+19} {y+31}L{x+22} {y+28}"
                  f"M{x+28} {y+22}L{x+31} {y+19}A4.2 4.2 0 0 0 {x+25} {y+13}L{x+22} {y+16}"),
    }[kind]


def repo_icon(x, y, col=ORANGE):
    """Ikon buku repositori 20x20 (garis)."""
    return (f'<path d="M{x+3} {y+16.5}V{y+3.5}A1.5 1.5 0 0 1 {x+4.5} {y+2}H{x+17}V{y+14}H{x+5}A2 2 0 0 0 {x+3} {y+16}A2 2 0 0 0 {x+5} {y+18}H{x+17}" '
            f'fill="none" stroke="{col}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')


def star_mini(x, y, col):
    """Bintang kecil 12px, titik tengah kiri-atas di (x, y)."""
    pts = [(6, 0.5), (7.6, 4.2), (11.6, 4.5), (8.5, 7.1), (9.5, 11), (6, 8.9), (2.5, 11), (3.5, 7.1), (0.4, 4.5), (4.4, 4.2)]
    return f'<polygon points="{" ".join(f"{x+a:.1f},{y+b:.1f}" for a, b in pts)}" fill="{col}"/>'


def fork_mini(x, y, col):
    s = f'fill="none" stroke="{col}" stroke-width="1.5" stroke-linecap="round"'
    return (f'<circle cx="{x+2.5}" cy="{y+2}" r="1.8" {s}/><circle cx="{x+9.5}" cy="{y+2}" r="1.8" {s}/><circle cx="{x+6}" cy="{y+10}" r="1.8" {s}/>'
            f'<path d="M{x+2.5} {y+3.8}V{y+5.5}Q{x+2.5} {y+6.8} {x+4} {y+6.8}H{x+8}Q{x+9.5} {y+6.8} {x+9.5} {y+5.5}V{y+3.8}M{x+6} {y+6.8}V{y+8.2}" {s}/>')


# ------------------------------------------------------------------ kartu judul
def header_svg(theme, title, subtitle, ic=None, mascot=None, accent_dot=True, h=96):
    """Kartu judul (sudut atas membulat, bawah rata). ic = nama ikon di lingkaran kanan, mascot = data URI (utama: connect)."""
    c = THEMES[theme]
    spot = CREAM if theme == "dark" else "#FFFFFF"
    W = 960
    d = f"M0 {R}A{R} {R} 0 0 1 {R} 0H{W-R}A{R} {R} 0 0 1 {W} {R}V{h}H0Z"
    mid = h / 2
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{esc(title)}">',
           '<style>@keyframes tw{0%,100%{opacity:.25;transform:scale(.7)}50%{opacity:1;transform:scale(1.15)}}'
           '.tw{animation:tw 2.6s ease-in-out infinite;transform-box:fill-box;transform-origin:center}'
           '@media (prefers-reduced-motion:reduce){.tw{animation:none}}</style>',
           f'<path d="{d}" fill="{c["bg"]}"/>',
           f'<path transform="translate(.5 .5)" d="M0 {R}A{R} {R} 0 0 1 {R} 0H{W-R-1}A{R} {R} 0 0 1 {W-1} {R}V{h-1}H0Z" fill="none" stroke="{c["line"]}"/>']
    ty = 52 if subtitle else mid + 10
    dot = f'<tspan fill="{ORANGE_TXT[theme]}">.</tspan>' if accent_dot else ""
    out.append(f'<text x="40" y="{ty}" font-family="{SANS}" font-size="28" font-weight="800" fill="{c["text"]}" letter-spacing="-.5">{esc(title)}{dot}</text>')
    if subtitle:
        out.append(f'<text x="40" y="76" font-family="{SANS}" font-size="13.5" fill="{c["muted"]}">{esc(subtitle)}</text>')
    cx = 884
    out.append(f'<circle cx="{cx}" cy="{mid}" r="30" fill="{spot}"/><circle cx="{cx}" cy="{mid}" r="38" fill="none" stroke="{ORANGE}" '
               f'stroke-width="2.2" stroke-dasharray="4 9" stroke-linecap="round" opacity=".9"/>')
    if mascot:
        out.append(f'<image x="{cx-24}" y="{mid-27}" width="48" height="54" preserveAspectRatio="xMidYMid meet" href="{mascot}"/>'
                   f'<path class="tw" d="M{cx+38} {mid-34}Q{cx+38} {mid-26} {cx+46} {mid-26}Q{cx+38} {mid-26} {cx+38} {mid-18}Q{cx+38} {mid-26} {cx+30} {mid-26}Q{cx+38} {mid-26} {cx+38} {mid-34}z" fill="{ORANGE}"/>')
    elif ic:
        out.append(icon(ic, cx - 22, mid - 22, "#C85A12"))
    out.append("</svg>")
    return "".join(out)


# ------------------------------------------------------------------ HTML README
def picture(dirname, base, alt):
    return ("<picture>\n"
            f'  <source media="(prefers-color-scheme: dark)" srcset="assets/svg/{dirname}/{base}_dark.svg">\n'
            f'  <source media="(prefers-color-scheme: light)" srcset="assets/svg/{dirname}/{base}_light.svg">\n'
            f'  <img alt="{esc(alt)}" src="assets/svg/{dirname}/{base}_dark.svg" width="100%" align="top">\n</picture>')


def tile_img(dirname, fname, width, url, alt):
    img = f'<img src="assets/svg/{dirname}/{fname}" width="{width}" align="top" alt="{esc(alt)}">'
    return f'<a href="{esc(url)}">{img}</a>' if url else img


def assemble(dirname, base, header_alt, header_url, rows):
    """Kartu judul (opsional dibungkus link) + baris tile yang menempel. rows = [[(file, lebar, url, alt), ...], ...]"""
    head = picture(dirname, base, header_alt)
    if header_url:
        head = f'<a href="{esc(header_url)}">\n{head}\n</a>'
    body = "<br>\n".join("".join(tile_img(dirname, *t) for t in row) for row in rows)
    return head + "<br>\n" + body + "\n"
