#!/usr/bin/env python3
"""Ubah maskot PNG jadi grid pixel (assets/data/portrait.json) untuk versi terminal hijau.
Dijalankan sekali saja (butuh Pillow: pip install pillow). Hasil JSON sudah ikut di repo,
jadi workflow tidak perlu Pillow."""
import json
from pathlib import Path
from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parent.parent
COLS, ROWS = 48, 55

im = Image.open(ROOT / "assets" / "images" / "maskot-dev.png").convert("RGBA")
alpha = im.split()[3].resize((COLS, ROWS), Image.LANCZOS)
bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
bg.alpha_composite(im)
rgb = bg.convert("RGB")
# warna oranye (tongkat/syal) dan krem (mata/bintang) dibuat lebih terang dari badan biru
lum = rgb.convert("L").resize((COLS, ROWS), Image.LANCZOS)
sat = rgb.convert("HSV").split()[1].resize((COLS, ROWS), Image.LANCZOS)

grid = []
for y in range(ROWS):
    row = []
    for x in range(COLS):
        a = alpha.getpixel((x, y)) / 255
        if a < 0.4:
            row.append(0)
            continue
        l = lum.getpixel((x, y)) / 255
        s = sat.getpixel((x, y)) / 255
        v = l + s * 0.12
        lv = 1 if v < 0.20 else 2 if v < 0.33 else 3 if v < 0.47 else 4
        row.append(lv)
    grid.append(row)
(ROOT / "assets" / "data" / "portrait.json").write_text(json.dumps({"cols": COLS, "rows": ROWS, "grid": grid}))
print("ok", COLS, "x", ROWS)
