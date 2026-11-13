"""Connect with me: kartu judul + segmen akun yang menempel rapat. Satu segmen = satu gambar = satu link."""
import re

from common import SVG, VENDOR, SKILL_ICONS, emit, http_url, trunc, REPORT, esc
from sections._tiles import CREAM, INK, SUB, TILE_LINE, T, arrow, assemble, header_svg, pct, R, uri

OUT = SVG / "connect"
LOGOS = VENDOR / "social-logos"
WHERE = "assets/data/profile.json"
MAX_LINKS = 10
# kunci: (nama tampil, templat URL untuk handle, tampilkan dengan "@")
PLATFORMS = {
    "instagram": ("INSTAGRAM", "https://www.instagram.com/{h}/", True),
    "tiktok": ("TIKTOK", "https://www.tiktok.com/@{h}", True),
    "youtube": ("YOUTUBE", "https://www.youtube.com/@{h}", True),
    "linkedin": ("LINKEDIN", "https://www.linkedin.com/{h}", False),    # handle polos -> in/<handle>
    "facebook": ("FACEBOOK", "https://www.facebook.com/{h}", False),
    "x": ("X", "https://x.com/{h}", True),
    "threads": ("THREADS", "https://www.threads.com/@{h}", True),
    "pinterest": ("PINTEREST", "https://www.pinterest.com/{h}/", False),
    "discord": ("DISCORD", "https://discord.gg/{h}", False),             # kode undangan
    "google-business-profile": ("GOOGLE BUSINESS", None, False),         # wajib URL
    "whatsapp": ("WHATSAPP", None, False),                               # nomor internasional
    "telegram": ("TELEGRAM", "https://t.me/{h}", True),
    "email": ("EMAIL", None, False),
}
ALIASES = {"x-twitter": "x", "twitter": "x", "google_business_profile": "google-business-profile", "wa": "whatsapp"}
SAFE_HANDLE = re.compile(r"^[A-Za-z0-9._\-/]{1,80}$")
EMAIL_RE = re.compile(r"^[^@\s<>\"']+@[^@\s<>\"']+\.[^@\s<>\"']+$")


def _warn(key, msg):
    REPORT.warn(WHERE, f"connect.links.{key}: {msg}")


def parse_entry(key, raw):
    """-> (url, label) atau None kalau kosong atau tidak valid (alasannya dicatat sebagai peringatan)."""
    name, template, at = PLATFORMS[key]
    label = None
    if isinstance(raw, dict):
        label = str(raw.get("label") or "").strip() or None
        raw = raw.get("url") or raw.get("handle") or ""
    raw = str(raw or "").strip()
    if not raw:
        return None
    if key == "email":
        if not EMAIL_RE.match(raw):
            _warn(key, f"'{raw}' bukan alamat email yang valid, dilewati")
            return None
        return f"mailto:{raw}", label or raw
    if key == "whatsapp":
        if http_url(raw):
            return raw, label or "WhatsApp"
        digits = re.sub(r"[\s\-().+]", "", raw)
        if not digits.isdigit() or not 8 <= len(digits) <= 15:
            _warn(key, f"'{raw}' bukan nomor yang valid. Tulis nomor internasional, contoh 6281234567890")
            return None
        if digits.startswith("0"):
            _warn(key, "nomor harus memakai kode negara tanpa 0 di depan (contoh 6281234567890), dilewati")
            return None
        return f"https://wa.me/{digits}", label or f"+{digits}"
    if raw.lower().startswith(("http://", "https://")):
        if not http_url(raw):
            _warn(key, "URL tidak valid, dilewati")
            return None
        seg = [s for s in raw.split("?")[0].split("/")[3:] if s]
        derived = seg[-1].lstrip("@") if seg else name.title()
        if key == "google-business-profile" and not label:
            derived = "Google Business"
        return raw, label or (("@" if at and key != "google-business-profile" else "") + derived)
    h = raw.lstrip("@").strip("/")
    if not SAFE_HANDLE.match(h):
        _warn(key, f"handle '{raw}' mengandung karakter tidak valid, dilewati")
        return None
    if template is None:
        _warn(key, "wajib berupa URL lengkap, dilewati")
        return None
    if key == "linkedin" and "/" not in h:
        h = f"in/{h}"
    return template.format(h=h), label or (("@" if at else "") + h.split("/")[-1])


def parse_links(links):
    entries = {}
    for k, v in links.items():
        key = ALIASES.get(str(k).lower(), str(k).lower())
        if key not in PLATFORMS:
            REPORT.warn(WHERE, f"connect.links.{k}: platform tidak dikenal, dilewati (pilihan: {', '.join(PLATFORMS)})")
            continue
        e = parse_entry(key, v)
        if e:
            entries[key] = e
    return {k: entries[k] for k in PLATFORMS if k in entries}


def logo_uri(key):
    if key == "email":
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect x="6" y="14" width="52" height="36" rx="8" fill="#FF8A3D"/>'
               '<path d="M10 20 L32 38 L54 20" fill="none" stroke="#14213D" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
        return uri(svg.encode(), "image/svg+xml")
    svg = LOGOS / f"{key}.svg"
    if svg.exists():
        return uri(svg.read_bytes(), "image/svg+xml")
    png = SKILL_ICONS / f"{key}.png"
    if png.exists():
        return uri(png.read_bytes(), "image/png")
    raise FileNotFoundError(f"logo untuk '{key}' tidak ada")


def segment_svg(i, n, key, name, label, mode):
    w, h = round(960 / n, 2), 64
    first, last = i == 0, i == n - 1
    d = (f"M0 0H{w}" + (f"V{h-R}A{R} {R} 0 0 1 {w-R} {h}" if last else f"V{h}") + (f"H{R}A{R} {R} 0 0 1 0 {h-R}" if first else "H0") + "Z")
    div = "" if last else f'<rect x="{w-1}" y="0" width="1" height="{h}" fill="{TILE_LINE}"/>'
    if mode == "text":
        shown = trunc(label, max(6, int((w - 62 - 44) / 8.3)))
        body = (f'<image x="18" y="16" width="32" height="32" preserveAspectRatio="xMidYMid meet" href="{logo_uri(key)}"/>'
                + T(62, 29, name, 10, 700, SUB, 'letter-spacing="1.4"') + T(62, 47, shown, 14, 700, INK) + arrow(w - 32, 26))
    else:
        body = f'<image x="{w/2-17:.1f}" y="15" width="34" height="34" preserveAspectRatio="xMidYMid meet" href="{logo_uri(key)}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{esc(name)} {esc(label)}"><path d="{d}" fill="{CREAM}"/>{div}{body}</svg>')


def build(ctx):
    p, S = ctx.p, ctx.S
    cfg = p["connect"]
    entries = parse_links(cfg["links"])
    if not entries:
        return ""
    if len(entries) > MAX_LINKS:
        entries = dict(list(entries.items())[:MAX_LINKS])
    n = len(entries)
    mode = cfg["style"] if cfg["style"] != "auto" else ("text" if n <= 4 else "icon")
    title = cfg["title"] or S["connect_title"]
    for theme in ("dark", "light"):
        emit(OUT / f"header_{theme}.svg", header_svg(theme, title, cfg["subtitle"], mascot=ctx.mascot))
    row = []
    for i, (key, (url, label)) in enumerate(entries.items()):
        name = S["google_business"] if key == "google-business-profile" else PLATFORMS[key][0]
        fname = f"{i:02d}-{key}.svg"
        emit(OUT / fname, segment_svg(i, n, key, name, label, mode))
        row.append((fname, pct(n), url, f"{name.title()} {label}" if mode == "text" else name.title()))
    return assemble("connect", "header", title, None, [row])
