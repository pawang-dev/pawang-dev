"""Konstanta dan helper bersama. Hanya memakai pustaka standar Python."""
import json
import os
import re
from html import escape
from pathlib import Path

ROOT = Path(os.environ.get("PAWANG_ROOT") or Path(__file__).resolve().parent.parent).resolve()
ASSETS = ROOT / "assets"
DATA = ASSETS / "data"
IMAGES = ASSETS / "images"
BRAND = IMAGES / "brand"
SKILL_ICONS = IMAGES / "skills"
SVG = ASSETS / "svg"
CACHE = ASSETS / "cache"
VENDOR = ASSETS / "vendor"
README = ROOT / "README.md"

# palet brand
NAVY, ORANGE, CREAM, SAGE, BONE = "#14213D", "#FF8A3D", "#FFF6E9", "#A7C4A0", "#FAFAF7"
SANS = "'Plus Jakarta Sans','Inter','Segoe UI','Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','SF Mono','Menlo','Consolas','DejaVu Sans Mono',monospace"
THEMES = {
    "dark": dict(bg=NAVY, panel="#1B2B4F", line="#2A3B63", text=BONE, muted="#9AA6C2", key=ORANGE,
                 accent=SAGE, cell0="#22345C", card=CREAM, card_line=CREAM, orange=ORANGE),
    "light": dict(bg=CREAM, panel="#FFFFFF", line="#E6D6BB", text=NAVY, muted="#5B6784", key="#C85A12",
                  accent="#6E9468", cell0="#EBDDC4", card="#FFFFFF", card_line="#E6D6BB", orange=ORANGE),
}
CARD_R = 14

# Tautan bawaan kartu identitas (hero, neofetch, terminal, brand, sheet, typing). Sengaja di skrip, bukan di JSON.
DEFAULT_LINK = "https://www.pawang.dev"
IN_ACTIONS = os.environ.get("GITHUB_ACTIONS") == "true"


class BuildError(Exception):
    """Kesalahan fatal yang sudah dijelaskan ke pengguna."""


class Report:
    """Mengumpulkan masalah dengan lokasi file dan bidang yang jelas."""

    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")

    def show(self):
        import sys
        for w in self.warnings:
            print("PERINGATAN", w, file=sys.stderr)
        for e in self.errors:
            print("KESALAHAN ", e, file=sys.stderr)


REPORT = Report()
EMITTED = set()     # semua file hasil build pada run ini, dipakai untuk membersihkan sisa lama
DRY = False         # True = jalankan semuanya tanpa menulis berkas (mode --check)


def rel(path):
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def read_json(path, required=False):
    """Baca JSON. Mengembalikan dict, atau None bila hilang/rusak (masalahnya dicatat di REPORT)."""
    path = Path(path)
    if not path.exists():
        if required:
            REPORT.error(rel(path), "file tidak ditemukan")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        REPORT.error(rel(path), f"JSON tidak valid (baris {e.lineno}, kolom {e.colno}): {e.msg}")
        return None
    if not isinstance(data, dict):
        REPORT.error(rel(path), "isi file harus berupa objek JSON { ... }")
        return None
    return data


def emit(path, text):
    path = Path(path)
    EMITTED.add(path.resolve())
    if DRY:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")


def cleanup(dirs):
    """Hapus berkas hasil build lama (yang tidak dihasilkan pada run ini) di folder yang dikelola."""
    for d in dirs:
        d = Path(d)
        if d.exists():
            for f in d.glob("*.svg"):
                if f.resolve() not in EMITTED:
                    f.unlink()
            if not any(d.iterdir()):
                d.rmdir()


def card_path(w, h, r=CARD_R, attached=True):
    """Kartu: sudut atas membulat. Sudut bawah rata kalau ada tombol menempel, membulat kalau tidak."""
    if attached:
        return f"M0 {r}A{r} {r} 0 0 1 {r} 0H{w-r}A{r} {r} 0 0 1 {w} {r}V{h}H0Z"
    return (f"M0 {r}A{r} {r} 0 0 1 {r} 0H{w-r}A{r} {r} 0 0 1 {w} {r}V{h-r}A{r} {r} 0 0 1 {w-r} {h}H{r}"
            f"A{r} {r} 0 0 1 0 {h-r}Z")


def esc(s):
    return escape(str(s))


def idn(n):
    return f"{n:,}".replace(",", ".")


def trunc(s, n):
    s = str(s)
    return s if len(s) <= n else s[: n - 1] + "…"


def split_accent(text, accent):
    """-> (sebelum, aksen, sesudah); aksen dicari dari belakang. Tanpa aksen: (text, '', '')."""
    if accent:
        i = text.rfind(accent)
        if i >= 0:
            return text[:i], accent, text[i + len(accent):]
    return text, "", ""


def safe_stem(s, fallback="mascot"):
    s = re.sub(r"[^a-z0-9_-]", "", str(s).lower())
    return s or fallback


def wrap_text(text, width, max_lines):
    """Bungkus teks per kata, maksimal max_lines baris; sisanya dipotong dengan elipsis."""
    import textwrap
    lines = textwrap.wrap(str(text), width=width, break_long_words=True, break_on_hyphens=False) or [""]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = trunc(lines[-1] + "…", width) if len(lines[-1]) < width else lines[-1][: width - 1] + "…"
    return lines


def short_date(day, month, S, lang):
    mon = S["months"][month - 1]
    return f"{day} {mon}" if lang == "id" else f"{mon} {day}"


def http_url(v):
    """True kalau v adalah URL http(s) dengan host."""
    from urllib.parse import urlparse
    u = urlparse(str(v))
    return u.scheme in ("http", "https") and bool(u.netloc)
