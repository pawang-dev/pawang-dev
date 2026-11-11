"""Baris tombol yang menempel di bawah kartu (satu atau dua tombol)."""
from common import CARD_R, MONO, esc

BAR_H = 56
COLORS = {"brand": [("#FF8A3D", "#14213D"), ("#A7C4A0", "#14213D")],
          "green": [("#4dff7c", "#040905"), ("#22a24c", "#040905")]}


def _bar(label, w, round_left, round_right, bg, fg, divider, green):
    h, r = BAR_H, CARD_R
    d = f"M0 0H{w}"
    d += f"V{h-r}A{r} {r} 0 0 1 {w-r} {h}" if round_right else f"V{h}"
    d += f"H{r}A{r} {r} 0 0 1 0 {h-r}" if round_left else "H0"
    d += "Z"
    tw = len(label) * 9.9
    x0 = (w - (tw + 8 + 11)) / 2
    defs = overlay = ""
    if green:
        defs = '<pattern id="sc" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.4" fill="#000" opacity=".22"/></pattern>'
        overlay = f'<path d="{d}" fill="url(#sc)"/>'
    div = f'<rect x="{divider}" y="0" width="1" height="{h}" fill="#000" opacity=".22"/>' if divider is not None else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
            f'<title>{esc(label)}</title><defs>{defs}</defs><path d="{d}" fill="{bg}"/>{overlay}{div}'
            f'<text x="{x0:.1f}" y="33" font-family="{MONO}" font-size="14" font-weight="700" letter-spacing="1.5" fill="{fg}">{esc(label)}</text>'
            f'<g transform="translate({x0 + tw + 8:.1f} 23)"><path d="M0 11L10 1M2 1H10V9" fill="none" stroke="{fg}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round"/><animateTransform attributeName="transform" type="translate" additive="sum" '
            f'values="0 0;2 -2;0 0" dur="1.8s" repeatCount="indefinite"/></g></svg>')


def build(buttons, variant):
    """-> daftar (nama_file, svg, lebar_persen, url, label). Dua tombol = dua separuh, satu tombol = selebar kartu."""
    cols = COLORS[variant]
    green = variant == "green"
    if len(buttons) == 1:
        b = buttons[0]
        return [(f"bar_{variant}_full.svg", _bar(b["label"], 960, True, True, *cols[0], None, green), 100, b["url"], b["label"])]
    out = []
    for i, b in enumerate(buttons):
        left = i == 0
        out.append((f"bar_{variant}_{'left' if left else 'right'}.svg",
                    _bar(b["label"], 480, left, not left, *cols[i], 479 if left else 0, green), 50, b["url"], b["label"]))
    return out
