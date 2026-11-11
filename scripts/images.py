"""Logo dan maskot pengguna: file di assets/images/brand/, atau cadangan otomatis kalau tidak ada."""
import base64
import urllib.request

from common import BRAND, NAVY, ORANGE, REPORT, rel

MIME = {".png": "image/png", ".svg": "image/svg+xml", ".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
MAX_BYTES = 400 * 1024


def _find(stem):
    for ext in MIME:
        p = BRAND / f"{stem}{ext}"
        if p.is_file():
            return p
    return None


def _uri(path):
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        REPORT.warn(rel(path), f"ukuran {len(data)//1024} KB, disarankan di bawah {MAX_BYTES//1024} KB (lihat assets/images/README.md)")
    return f"data:{MIME[path.suffix.lower()]};base64," + base64.b64encode(data).decode()


def _svg_uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def _initial(name):
    return (name.strip()[:1] or "?").upper()


def logo_uri(name):
    p = _find("logo")
    if p:
        return _uri(p)
    REPORT.warn("assets/images/brand/logo.(png|svg|webp)", "tidak ada, memakai monogram inisial")
    return _svg_uri(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 132 126"><rect x="3" y="3" width="126" height="120" rx="28" '
                    f'fill="{NAVY}"/><text x="66" y="86" font-size="76" font-weight="800" text-anchor="middle" '
                    f'font-family="Arial,Helvetica,sans-serif" fill="{ORANGE}">{_initial(name)}</text></svg>')


def avatar_uri(user):
    try:
        with urllib.request.urlopen(f"https://github.com/{user}.png?size=256", timeout=15) as r:
            return f"data:{r.headers.get_content_type()};base64," + base64.b64encode(r.read()).decode()
    except Exception:  # noqa: BLE001
        return None


def mascot_uri(name, user, allow_network):
    """-> (data URI, file_asli_atau_None)"""
    p = _find("mascot")
    if p:
        return _uri(p), p
    if allow_network and user:
        a = avatar_uri(user)
        if a:
            REPORT.warn("assets/images/brand/mascot.(png|svg|webp)", "tidak ada, memakai foto profil GitHub")
            return a, None
    REPORT.warn("assets/images/brand/mascot.(png|svg|webp)", "tidak ada, memakai monogram inisial")
    return _svg_uri(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 226 257"><circle cx="113" cy="128" r="100" fill="{NAVY}"/>'
                    f'<text x="113" y="168" font-size="120" font-weight="800" text-anchor="middle" '
                    f'font-family="Arial,Helvetica,sans-serif" fill="{ORANGE}">{_initial(name)}</text></svg>'), None
