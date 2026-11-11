"""Profil sosial media (opsional), dibaca dari assets/data/social.json.

Satu SVG per platform (assets/svg/social/<platform>.svg) supaya tiap tombol punya link sendiri.
Platform yang kosong dilewati.
"""
import base64
import re
from urllib.parse import urlparse

from common import DATA, NAVY, ORANGE, CREAM, REPORT, SANS, SVG, VENDOR, emit, esc, read_json, rel

LOGOS = VENDOR / "social-logos"
OUT = SVG / "social"
CONFIG = DATA / "social.json"
SVG_DIR_REL = "assets/svg/social"
HEIGHT = 56
MAX_ROW = 780          # batas lebar total tombol "pill" pada mode auto (isi README di halaman profil sekitar 830 px)
GAP = 8
KNOWN_KEYS = {"$schema", "style", "title", "links"}

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
    "google-business-profile": ("GOOGLE BUSINESS", None, False),          # wajib URL
}
ALIASES = {"x-twitter": "x", "twitter": "x", "google_business_profile": "google-business-profile"}
SAFE_HANDLE = re.compile(r"^[A-Za-z0-9._\-/]{1,80}$")


def warn(msg):
    REPORT.warn(rel(CONFIG), msg)


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
            f'role="img" aria-label="{esc(name)} {esc(label)}">'
            f'<rect x=".5" y=".5" width="{w-1}" height="{HEIGHT-1}" rx="14" fill="{CREAM}" stroke="#E6D6BB"/>'
            f'<image x="14" y="10" width="36" height="36" href="{logo_uri(key)}"/>'
            f'<text x="62" y="23" font-family="{SANS}" font-size="10" font-weight="700" letter-spacing="1.4" fill="#5B6784">{esc(name)}</text>'
            f'<text x="62" y="42" font-family="{SANS}" font-size="14" font-weight="700" fill="{NAVY}">{esc(label)}</text>'
            f'{arrow(w-30, 22)}</svg>'), w


def icon_svg(key, name):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" viewBox="0 0 56 56" '
            f'role="img" aria-label="{esc(name)}">'
            f'<rect x=".5" y=".5" width="55" height="55" rx="14" fill="{CREAM}" stroke="#E6D6BB"/>'
            f'<image x="10" y="10" width="36" height="36" href="{logo_uri(key)}"/></svg>'), 56



def load_config(S):
    cfg = read_json(CONFIG)
    if cfg is None:
        return {}, "auto", S["social_title"]
    where = rel(CONFIG)
    for k in cfg:
        if k not in KNOWN_KEYS and not k.startswith("_"):
            hint = ", pindahkan ke dalam 'links'" if k in PLATFORMS or ALIASES.get(k) else ""
            REPORT.warn(where, f"{k}: kunci tidak dikenal{hint}, diabaikan")
    style = str(cfg.get("style", "auto")).strip().lower()
    if style not in ("auto", "pill", "icon"):
        REPORT.error(where, f"style: '{style}' tidak dikenal (pilihan: auto, pill, icon)")
        style = "auto"
    title = str(cfg.get("title") or S["social_title"]).strip()[:40]
    links = cfg.get("links") or {}
    if not isinstance(links, dict):
        REPORT.error(where, "links: harus berupa objek { \"instagram\": \"nama\", ... }")
        links = {}
    entries = {}
    for k, v in links.items():
        key = ALIASES.get(k.lower(), k.lower())
        if key not in PLATFORMS:
            warn(f"links.{k}: platform tidak dikenal, dilewati (pilihan: {', '.join(PLATFORMS)})")
            continue
        e = parse_entry(key, v)
        if e:
            entries[key] = e
    return {k: entries[k] for k in PLATFORMS if k in entries}, style, title


def build(S):
    """Tulis SVG dan kembalikan blok HTML untuk README ('' kalau tidak ada platform yang diisi)."""
    entries, style, title = load_config(S)
    if not entries:
        return ""
    names = {k: (S["google_business"] if k == "google-business-profile" else PLATFORMS[k][0]) for k in entries}
    pill_total = sum(pill_width(names[k], lab) + GAP for k, (_, lab) in entries.items())
    mode = style if style != "auto" else ("pill" if pill_total <= MAX_ROW else "icon")
    items = []
    for key, (url, label) in entries.items():
        name = names[key]
        svg = pill_svg(key, name, label)[0] if mode == "pill" else icon_svg(key, name)[0]
        emit(OUT / f"{key}.svg", svg)
        alt = f"{name.title()} {label}" if mode == "pill" else name.title()
        items.append(f'<a href="{esc(url).replace(chr(34), "&quot;")}"><img src="{SVG_DIR_REL}/{key}.svg" '
                     f'height="{HEIGHT}" align="top" alt="{esc(alt).replace(chr(34), "&quot;")}"></a>')
    return f'<h3 align="center">{esc(title)}</h3>\n' + "&nbsp;&nbsp;".join(items) + "\n"
