#!/usr/bin/env python3
"""Potret pixel maskot untuk kartu terminal hijau -> assets/cache/portrait.json.

Dipanggil otomatis oleh build_all.py kalau maskot berubah (butuh Pillow: pip install pillow).
Dijalankan langsung = paksa buat ulang.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import common  # noqa: E402
from common import CACHE, REPORT, rel  # noqa: E402

CACHE_FILE = CACHE / "portrait.json"
BOX_W, BOX_H = 48, 55


def _sha(path):
    return hashlib.sha1(Path(path).read_bytes()).hexdigest()


def _build(path):
    from PIL import Image, ImageChops  # noqa: PLC0415
    im = Image.open(path)
    rgba = im.convert("RGBA")
    a = rgba.getchannel("A")
    if a.getextrema()[0] == 255:                       # tanpa transparansi: anggap putih = latar
        r, g, b = rgba.convert("RGB").split()
        lo = ImageChops.darker(ImageChops.darker(r, g), b)
        a = lo.point(lambda v: 255 if v < 240 else 0)
    w, h = rgba.size
    s = min(BOX_W / w, BOX_H / h)
    cols, rows = max(1, round(w * s)), max(1, round(h * s))
    bg = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
    bg.alpha_composite(rgba)
    rgb = bg.convert("RGB")
    alpha = a.resize((cols, rows), Image.LANCZOS)
    lum = rgb.convert("L").resize((cols, rows), Image.LANCZOS)
    sat = rgb.convert("HSV").split()[1].resize((cols, rows), Image.LANCZOS)
    grid = []
    for y in range(rows):
        row = []
        for x in range(cols):
            if alpha.getpixel((x, y)) / 255 < 0.4:
                row.append(0)
                continue
            v = lum.getpixel((x, y)) / 255 + sat.getpixel((x, y)) / 255 * 0.12
            row.append(1 if v < 0.20 else 2 if v < 0.33 else 3 if v < 0.47 else 4)
        grid.append(row)
    return {"cols": cols, "rows": rows, "grid": grid}


def ensure_portrait(mascot_path, force=False):
    """-> dict potret atau None (kalau tidak ada maskot raster / Pillow tidak tersedia)."""
    if not mascot_path:
        return None
    mascot_path = Path(mascot_path)
    if mascot_path.suffix.lower() == ".svg":
        REPORT.warn(rel(mascot_path), "maskot berformat SVG tidak bisa dijadikan potret pixel, kartu terminal memakai inisial")
        return None
    sha = _sha(mascot_path)
    if not force and CACHE_FILE.exists():
        try:
            cached = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            if cached.get("sha") == sha:
                return cached
        except (json.JSONDecodeError, OSError):
            pass
    try:
        data = _build(mascot_path)
    except ImportError:
        REPORT.warn(rel(CACHE_FILE), "maskot berubah tetapi Pillow belum terpasang (pip install pillow), potret lama dipakai kalau ada")
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
    data["sha"] = sha
    if common.DRY:
        return data
    CACHE.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    return data


if __name__ == "__main__":
    from images import _find  # noqa: PLC0415
    p = _find("mascot")
    d = ensure_portrait(p, force=True)
    REPORT.show()
    print("potret:", f"{d['cols']}x{d['rows']}" if d else "tidak dibuat")
