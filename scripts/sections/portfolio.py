"""Portofolio: kartu hasil kerja (thumbnail, tag, judul, deskripsi, hasil). Gambar opsional dari assets/images/portfolio/."""
import re

from common import IMAGES, ORANGE, SAGE, SVG, REPORT, emit, rel
from sections._tiles import INK, SUB, TILE_LINE, T, arrow, assemble, header_svg, pct, tpath, uri, wrap_tile

OUT = SVG / "portfolio"
PHOTOS = IMAGES / "portfolio"
WHERE = "assets/data/profile.json"
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
MAX_BYTES = 300 * 1024
THUMB_H, TILE_H = 120, 232
ROWS = {1: [1], 2: [2], 3: [3], 4: [2, 2], 5: [3, 2], 6: [3, 3]}


def kind_of(item):
    if item["thumb"]:
        return item["thumb"]
    t = f'{item["tag"]} {item["title"]}'.lower()
    if re.search(r"dashboard|sheet|laporan|report|data", t):
        return "chart"
    if re.search(r"otomasi|automation|chat|whatsapp|bot", t):
        return "chat"
    return "web"


def sketch(kind, w, h):
    s = []
    if kind == "web":
        s += [f'<rect width="{w}" height="{h}" fill="#FFE7CF"/>', f'<rect x="22" y="16" width="{w-44}" height="{h-24}" rx="8" fill="#fff" stroke="{TILE_LINE}"/>',
              f'<rect x="22" y="16" width="{w-44}" height="14" rx="8" fill="{ORANGE}" opacity=".85"/>', f'<rect x="36" y="42" width="{(w-44)*.5:.0f}" height="8" rx="4" fill="#14213D" opacity=".8"/>',
              f'<rect x="36" y="58" width="{(w-44)*.7:.0f}" height="6" rx="3" fill="{SUB}" opacity=".4"/>', f'<rect x="36" y="72" width="{(w-44)*.35:.0f}" height="18" rx="9" fill="{ORANGE}"/>']
    elif kind == "chart":
        s += [f'<rect width="{w}" height="{h}" fill="#DCEBD8"/>', f'<rect x="22" y="16" width="{w-44}" height="{h-24}" rx="8" fill="#fff" stroke="{TILE_LINE}"/>']
        for i, hh in enumerate((26, 44, 34, 58, 40, 66)):
            s.append(f'<rect x="{38 + i * ((w-90)/6):.0f}" y="{h-18-hh}" width="{(w-90)/6-8:.0f}" height="{hh}" rx="4" fill="{SAGE if i < 5 else ORANGE}"/>')
    else:
        s += [f'<rect width="{w}" height="{h}" fill="#DDE6F6"/>', f'<rect x="26" y="18" width="{w*.55:.0f}" height="26" rx="13" fill="#fff" stroke="{TILE_LINE}"/>',
              f'<rect x="{w-26-w*.5:.0f}" y="52" width="{w*.5:.0f}" height="26" rx="13" fill="#25D366" opacity=".9"/>', f'<rect x="26" y="86" width="{w*.4:.0f}" height="22" rx="11" fill="#fff" stroke="{TILE_LINE}"/>']
    return "".join(s)


def photo_uri(item):
    if not item["image"]:
        return None
    f = PHOTOS / item["image"]
    if not f.is_file() or f.suffix.lower() not in MIME:
        REPORT.warn(WHERE, f"portfolio '{item['title']}': gambar '{item['image']}' tidak ditemukan di {rel(PHOTOS)}/ (png, jpg, webp), memakai sketsa")
        return None
    data = f.read_bytes()
    if len(data) > MAX_BYTES:
        REPORT.warn(rel(f), f"ukuran {len(data)//1024} KB, disarankan di bawah {MAX_BYTES//1024} KB")
    return uri(data, MIME[f.suffix.lower()])


def tile_svg(item, w, bl, br, divr, divb):
    clip = f'<clipPath id="c"><path d="{tpath(w, THUMB_H)}"/></clipPath>'
    photo = photo_uri(item)
    thumb = (f'<image x="0" y="0" width="{w}" height="{THUMB_H}" preserveAspectRatio="xMidYMid slice" href="{photo}"/>' if photo
             else sketch(kind_of(item), w, THUMB_H))
    body = [f'<g clip-path="url(#c)">{thumb}</g>']
    if item["tag"]:
        body.append(T(20, 150, item["tag"].upper(), 10.5, 800, "#C85A12", 'letter-spacing="1.4"'))
    body.append(T(20, 174, item["title"], 17, 800, INK))
    if item["description"]:
        body.append(T(20, 196, item["description"], 12.5, 500, SUB))
    if item["result"]:
        body.append(T(20, 216, item["result"], 12, 700, "#2E7D32"))
    if item["url"]:
        body.append(arrow(w - 38, 140))
    return wrap_tile(w, TILE_H, "".join(body), f'{item["title"]}: {item["description"]}'.strip(": "), divr=divr, divb=divb, bl=bl, br=br, defs=clip)


def build(ctx):
    p, S = ctx.p, ctx.S
    cfg = p["portfolio"]
    items = cfg["items"]
    if not items:
        return ""
    title = cfg["title"] or S["portfolio_title"]
    for theme in ("dark", "light"):
        emit(OUT / f"header_{theme}.svg", header_svg(theme, title, cfg["subtitle"], ic="web"))
    layout = ROWS[len(items)]
    rows, i = [], 0
    for ri, per in enumerate(layout):
        row, last_row = [], ri == len(layout) - 1
        for j in range(per):
            it, w = items[i], round(960 / per, 2)
            fname = f"{i:02d}.svg"
            emit(OUT / fname, tile_svg(it, w, bl=last_row and j == 0, br=last_row and j == per - 1, divr=j < per - 1, divb=not last_row))
            row.append((fname, pct(per), it["url"], f'{it["title"]}: {it["description"]}'.strip(": ")))
            i += 1
        rows.append(row)
    return assemble("portfolio", "header", title, None, rows)
