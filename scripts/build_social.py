#!/usr/bin/env python3
"""Profil Sosial Media (opsional).

Membaca social.json di root repo. Platform yang diisi dibuatkan satu tombol SVG sendiri
(assets/svg/social/<platform>.svg) supaya tiap tombol bisa punya link sendiri, lalu blok
HTML-nya ditulis ke README.md di antara penanda:

    <!-- SOCIAL:START ... -->
    <!-- SOCIAL:END -->

Platform yang kosong dilewati. Kalau semuanya kosong, blok (termasuk judul) dikosongkan.
style: "auto" (bawaan) | "pill" | "icon". Hanya memakai pustaka standar Python.
"""
import base64
import json
import re
import sys
from html import escape
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
LOGOS = ROOT / "assets" / "images" / "logos"
OUT = ROOT / "assets" / "svg" / "social"
CONFIG = ROOT / "social.json"
README = ROOT / "README.md"

NAVY, ORANGE, CREAM = "#14213D", "#FF8A3D", "#FFF6E9"
SANS = "'Plus Jakarta Sans','Inter','Segoe UI','Helvetica Neue',Arial,sans-serif"
HEIGHT = 56
MAX_ROW = 780          # batas lebar total tombol "pill" pada mode auto (isi README di halaman profil sekitar 830 px)
GAP = 8

# kunci: (nama tampil, templat URL untuk handle, tampilkan dengan "@")
PLATFORMS = {
    "instagram": ("INSTAGRAM", "https://www.instagram.com/{h}/", True),
    "tiktok": ("TIKTOK", "https://www.tiktok.com/@{h}", True),
    "youtube": ("YOUTUBE", "https://www.youtube.com/@{h}", True),
    "linkedin": ("LINKEDIN", "https://www.linkedin.com/{h}", False),   # handle polos -> in/<handle>
    "facebook": ("FACEBOOK", "https://www.facebook.com/{h}", False),
    "x": ("X", "https://x.com/{h}", True),
    "threads": ("THREADS", "https://www.threads.com/@{h}", True),
    "pinterest": ("PINTEREST", "https://www.pinterest.com/{h}/", False),
    "discord": ("DISCORD", "https://discord.gg/{h}", False),            # kode undangan
    "google-business-profile": ("GOOGLE BISNIS", None, False),          # wajib URL
}
ALIASES = {"x-twitter": "x", "twitter": "x", "google_business_profile": "google-business-profile"}
SAFE_HANDLE = re.compile(r"^[A-Za-z0-9._\-/]{1,80}$")


def warn(msg):
    print("PERINGATAN:", msg, file=sys.stderr)


def parse_entry(key, raw):
    """-> (url, label) atau None kalau kosong/tidak valid."""
    name, template, at = PLATFORMS[key]
    label = None
    if isinstance(raw, dict):
        label = (raw.get("label") or "").strip() or None
        raw = raw.get("url") or raw.get("handle") or ""
    raw = str(raw or "").strip()
    if not raw:
        return None
    if raw.lower().startswith(("http://", "https://")):
        u = urlparse(raw)
        if not u.netloc:
            warn(f"{key}: URL tidak valid, dilewati")
            return None
        url = raw
        seg = [s for s in u.path.split("/") if s]
        derived = seg[-1].lstrip("@") if seg else u.netloc
        if key == "google-business-profile" and not label:
            derived = "Profil Bisnis"
        handle = derived
    else:
        h = raw.lstrip("@").strip("/")
        if not SAFE_HANDLE.match(h):
            warn(f"{key}: handle '{raw}' mengandung karakter tidak valid, dilewati")
            return None
        if template is None:
            warn(f"{key}: wajib berupa URL lengkap, dilewati")
            return None
        if key == "linkedin" and "/" not in h:
            h = f"in/{h}"
        url = template.format(h=h)
        handle = h.split("/")[-1]
    if not label:
        label = ("@" if at else "") + handle
    return url, (label if len(label) <= 22 else label[:21] + "…")


def logo_uri(key):
    p = LOGOS / f"{key}.svg"
    if not p.exists():
        raise FileNotFoundError(p)
    return "data:image/svg+xml;base64," + base64.b64encode(p.read_bytes()).decode()


def arrow(x, y):
    return (f'<g transform="translate({x} {y})"><path d="M0 11L10 1M2 1H10V9" fill="none" stroke="{ORANGE}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<animateTransform attributeName="transform" type="translate" additive="sum" '
            f'values="0 0;2 -2;0 0" dur="1.8s" repeatCount="indefinite"/></g>')


def pill_width(name, label):
    return int(14 + 36 + 12 + max(len(label) * 8.0, len(name) * 7.4) + 22 + 14 + 14)


def pill_svg(key, name, label):
    w = pill_width(name, label)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{HEIGHT}" viewBox="0 0 {w} {HEIGHT}" '
            f'role="img" aria-label="{escape(name)} {escape(label)}">'
            f'<rect x=".5" y=".5" width="{w-1}" height="{HEIGHT-1}" rx="14" fill="{CREAM}" stroke="#E6D6BB"/>'
            f'<image x="14" y="10" width="36" height="36" href="{logo_uri(key)}"/>'
            f'<text x="62" y="23" font-family="{SANS}" font-size="10" font-weight="700" letter-spacing="1.4" fill="#5B6784">{escape(name)}</text>'
            f'<text x="62" y="42" font-family="{SANS}" font-size="14" font-weight="700" fill="{NAVY}">{escape(label)}</text>'
            f'{arrow(w-30, 22)}</svg>'), w


def icon_svg(key, name):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" viewBox="0 0 56 56" '
            f'role="img" aria-label="{escape(name)}">'
            f'<rect x=".5" y=".5" width="55" height="55" rx="14" fill="{CREAM}" stroke="#E6D6BB"/>'
            f'<image x="10" y="10" width="36" height="36" href="{logo_uri(key)}"/></svg>'), 56


def load_config():
    if not CONFIG.exists():
        warn("social.json tidak ditemukan, bagian sosial media dikosongkan")
        return {}, "auto"
    try:
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"social.json bukan JSON yang valid: {e}")
    style = str(cfg.get("style", "auto")).strip().lower()
    if style not in ("auto", "pill", "icon"):
        warn(f"style '{style}' tidak dikenal, memakai auto")
        style = "auto"
    entries = {}
    for k, v in cfg.items():
        if k == "style" or k.startswith("_"):
            continue
        key = ALIASES.get(k.lower(), k.lower())
        if key not in PLATFORMS:
            warn(f"platform '{k}' tidak dikenal, dilewati (pilihan: {', '.join(PLATFORMS)})")
            continue
        e = parse_entry(key, v)
        if e:
            entries[key] = e
    # urutan mengikuti PLATFORMS, bukan urutan di file
    return {k: entries[k] for k in PLATFORMS if k in entries}, style


def build(entries, style):
    if OUT.exists():
        for old in OUT.glob("*.svg"):      # buang tombol platform yang sudah tidak diisi
            old.unlink()
    if not entries:
        return "", style
    pill_total = sum(pill_width(PLATFORMS[k][0], lab) + GAP for k, (_, lab) in entries.items())
    mode = style if style != "auto" else ("pill" if pill_total <= MAX_ROW else "icon")
    OUT.mkdir(parents=True, exist_ok=True)
    items = []
    for key, (url, label) in entries.items():
        name = PLATFORMS[key][0]
        svg, _ = pill_svg(key, name, label) if mode == "pill" else icon_svg(key, name)
        (OUT / f"{key}.svg").write_text(svg, encoding="utf-8")
        alt = f"{name.title()} {label}" if mode == "pill" else name.title()
        items.append(f'<a href="{escape(url, quote=True)}"><img src="assets/svg/social/{key}.svg" '
                     f'height="{HEIGHT}" align="top" alt="{escape(alt, quote=True)}"></a>')
    html = ('<br><br>\n<h3 align="center">Profil Sosial Media</h3>\n' + "&nbsp;&nbsp;".join(items) + "\n")
    return html, mode


def write_readme(html):
    if not README.exists():
        warn("README.md tidak ditemukan")
        return
    text = README.read_text(encoding="utf-8")
    pat = re.compile(r"(<!-- SOCIAL:START[^>]*-->\n?)(.*?)(<!-- SOCIAL:END -->)", re.S)
    if not pat.search(text):
        warn("penanda <!-- SOCIAL:START --> ... <!-- SOCIAL:END --> tidak ada di README.md, README tidak diubah")
        return
    new = pat.sub(lambda m: m.group(1) + html + m.group(3), text, count=1)
    if new != text:
        README.write_text(new, encoding="utf-8")


def main():
    entries, style = load_config()
    html, mode = build(entries, style)
    write_readme(html)
    if entries:
        print(f"sosial media: {len(entries)} platform ({', '.join(entries)}), gaya {mode}"
              + (f" (auto dari {style})" if style == "auto" else ""))
    else:
        print("sosial media: tidak ada platform yang diisi, bagian dikosongkan")


if __name__ == "__main__":
    main()
