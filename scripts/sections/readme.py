"""Merakit README.md dari daftar "sections" di profile.json."""
from common import README, esc

BASE = "assets/svg"


def _alt(p):
    return esc(f'{p["name"]}{p["suffix"]}: {p["tagline"]}'.rstrip(": ")).replace('"', "&quot;")


def card_block(card, p, buttons=None):
    """Kartu (dibungkus link ke website) + baris tombol yang menempel di bawahnya."""
    alt = _alt(p)
    if card.THEMED:
        img = ("<picture>\n"
               f'  <source media="(prefers-color-scheme: dark)" srcset="{BASE}/cards/{card.NAME}_dark.svg">\n'
               f'  <source media="(prefers-color-scheme: light)" srcset="{BASE}/cards/{card.NAME}_light.svg">\n'
               f'  <img alt="{alt}" src="{BASE}/cards/{card.NAME}_dark.svg" width="100%" align="top">\n</picture>')
    else:
        img = f'<img alt="{alt}" src="{BASE}/cards/{card.FILE}" width="100%" align="top">'
    html = f'<a href="{esc(p["website"])}">\n{img}\n</a>' if p["website"] else img
    if buttons:
        html += "<br>\n" + "".join(
            f'<a href="{esc(url)}"><img alt="{esc(label)}" src="{BASE}/buttons/{fname}" width="{pct}%" align="top"></a>'
            for fname, _svg, pct, url, label in buttons)
    return html + "\n"


def assemble(blocks, S):
    body = "\n<br><br>\n".join(b.rstrip("\n") + "\n" for b in blocks if b)
    return f'<!-- {S["generated"]} -->\n<div align="center">\n\n{body}\n</div>\n'


def write(text):
    if not README.exists() or README.read_text(encoding="utf-8") != text:
        README.write_text(text, encoding="utf-8")
