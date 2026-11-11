"""Memuat assets/data/profile.json: melengkapi nilai bawaan dan memvalidasi dengan pesan yang jelas."""
import os
import re
from urllib.parse import urlparse

from common import DATA, REPORT, read_json, rel, trunc
from i18n import LANGUAGES, strings

PROFILE_FILE = DATA / "profile.json"
CARD_SECTIONS = ("hero", "neofetch", "terminal", "brand", "sheet", "typing")
SECTIONS = CARD_SECTIONS + ("skills", "social")
ICONS = ("web", "seo", "sheet", "otomasi", "rawat", "code", "design", "chart", "chat", "mail", "star")
BUTTON_MODES = ("each", "last", "none")
USERNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
KNOWN = {"$schema", "language", "username", "name", "suffix", "domain", "website", "email", "tagline",
         "tagline_accent", "description", "audience", "mode", "badge", "mascot", "sections", "buttons",
         "button_mode", "info", "prompt", "hero", "services", "packages", "values", "sheet", "typing"}


class _V:
    """Pembantu validasi: mencatat masalah dengan jalur bidang."""

    def __init__(self):
        self.f = rel(PROFILE_FILE)

    def err(self, path, msg):
        REPORT.error(self.f, f"{path}: {msg}")

    def warn(self, path, msg):
        REPORT.warn(self.f, f"{path}: {msg}")

    def text(self, v, path, maxlen=None, default=""):
        if v is None or v == "":
            return default
        if not isinstance(v, str):
            self.err(path, f"harus berupa teks, bukan {type(v).__name__}")
            return default
        v = v.strip()
        if maxlen and len(v) > maxlen:
            self.warn(path, f"terlalu panjang ({len(v)} karakter), dipotong jadi {maxlen}")
            v = trunc(v, maxlen)
        return v

    def lst(self, v, path):
        if v is None:
            return []
        if not isinstance(v, list):
            self.err(path, f"harus berupa daftar [ ... ], bukan {type(v).__name__}")
            return []
        return v

    def obj(self, v, path):
        if v is None:
            return {}
        if not isinstance(v, dict):
            self.err(path, f"harus berupa objek {{ ... }}, bukan {type(v).__name__}")
            return {}
        return v

    def url(self, v, path):
        v = self.text(v, path)
        if v and (urlparse(v).scheme not in ("http", "https") or not urlparse(v).netloc):
            self.err(path, f"'{v}' bukan URL http(s) yang valid")
            return ""
        return v

    def cap(self, items, path, n):
        if len(items) > n:
            self.warn(path, f"hanya {n} item pertama yang dipakai (ada {len(items)})")
        return items[:n]


def _split_tagline(tagline):
    m = re.match(r"^(.*?[?!.])\s+(.+)$", tagline)
    return (m.group(1), m.group(2)) if m else (tagline, "")


def load_profile():
    """-> dict profil yang sudah dilengkapi, atau None kalau ada kesalahan (lihat REPORT)."""
    raw = read_json(PROFILE_FILE, required=True)
    if raw is None:
        return None
    v = _V()
    for k in raw:
        if k not in KNOWN and not k.startswith("_"):
            v.warn(k, "kunci tidak dikenal, diabaikan")

    p = {}
    lang = v.text(raw.get("language"), "language", default="id")
    if lang not in LANGUAGES:
        v.err("language", f"'{lang}' tidak dikenal (pilihan: {', '.join(LANGUAGES)})")
        lang = "id"
    p["language"], S = lang, strings(lang)

    user = v.text(raw.get("username"), "username") or os.environ.get("GH_USER") or os.environ.get("GITHUB_REPOSITORY_OWNER") or ""
    if not user:
        v.err("username", "kosong. Isi username GitHub, atau jalankan lewat GitHub Actions (otomatis memakai pemilik repo)")
    elif not USERNAME_RE.match(user):
        v.err("username", f"'{user}' bukan username GitHub yang valid")
    p["username"] = user

    p["name"] = v.text(raw.get("name"), "name", 24)
    if not p["name"]:
        v.err("name", "wajib diisi (nama brand atau nama kamu)")
    p["suffix"] = v.text(raw.get("suffix"), "suffix", 10)
    p["domain"] = v.text(raw.get("domain"), "domain", 40)
    p["website"] = v.url(raw.get("website"), "website")
    email = v.text(raw.get("email"), "email", 50)
    if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        v.err("email", f"'{email}' bukan alamat email yang valid")
        email = ""
    p["email"] = email
    p["tagline"] = v.text(raw.get("tagline"), "tagline", 60)
    p["tagline_accent"] = v.text(raw.get("tagline_accent"), "tagline_accent", 60)
    if p["tagline_accent"] and p["tagline_accent"] not in p["tagline"]:
        v.warn("tagline_accent", "tidak ditemukan di dalam tagline, aksen warna tidak dipakai")
        p["tagline_accent"] = ""
    desc = raw.get("description")
    desc = [desc] if isinstance(desc, str) else v.lst(desc, "description")
    p["description"] = [v.text(d, f"description[{i}]", 56) for i, d in enumerate(desc[:2]) if d]
    p["audience"] = v.text(raw.get("audience"), "audience", 40)
    p["mode"] = v.text(raw.get("mode"), "mode", 16)
    p["badge"] = v.text(raw.get("badge"), "badge", 20)
    m = v.obj(raw.get("mascot"), "mascot")
    p["mascot"] = {"name": v.text(m.get("name"), "mascot.name", 14), "caption": v.text(m.get("caption"), "mascot.caption", 30)}

    # bagian yang ditampilkan di README (urutannya = urutan tampil)
    secs = v.lst(raw.get("sections"), "sections") or ["neofetch"]
    p["sections"] = []
    for i, s in enumerate(secs):
        if s not in SECTIONS:
            v.err(f"sections[{i}]", f"'{s}' tidak dikenal (pilihan: {', '.join(SECTIONS)})")
        elif s in p["sections"]:
            v.warn(f"sections[{i}]", f"'{s}' muncul dua kali, yang kedua diabaikan")
        else:
            p["sections"].append(s)

    # tombol
    p["button_mode"] = v.text(raw.get("button_mode"), "button_mode", default="each")
    if p["button_mode"] not in BUTTON_MODES:
        v.err("button_mode", f"'{p['button_mode']}' tidak dikenal (pilihan: {', '.join(BUTTON_MODES)})")
        p["button_mode"] = "each"
    p["buttons"] = []
    for i, b in enumerate(v.cap(v.lst(raw.get("buttons"), "buttons"), "buttons", 2)):
        b = v.obj(b, f"buttons[{i}]")
        label = v.text(b.get("label"), f"buttons[{i}].label", 24)
        url = v.url(b.get("url"), f"buttons[{i}].url")
        if not label or not url:
            v.err(f"buttons[{i}]", "label dan url wajib diisi")
            continue
        p["buttons"].append({"label": label, "url": url})

    # info (neofetch dan terminal)
    info = []
    for i, r in enumerate(v.lst(raw.get("info"), "info")):
        r = v.obj(r, f"info[{i}]")
        label, value = v.text(r.get("label"), f"info[{i}].label", 12), v.text(r.get("value"), f"info[{i}].value", 52)
        if not label or not value:
            v.err(f"info[{i}]", "label dan value wajib diisi")
            continue
        info.append({"label": label, "value": value, "terminal": r.get("terminal", True) is not False})
    if not info:
        info = [{"label": "Brand", "value": p["name"] + p["suffix"], "terminal": False}]
        if p["tagline"]:
            info.append({"label": "Tagline", "value": p["tagline"], "terminal": False})
        if p["audience"]:
            info.append({"label": "Untuk" if lang == "id" else "For", "value": p["audience"], "terminal": True})
        if p["email"]:
            info.append({"label": "Kontak" if lang == "id" else "Contact", "value": p["email"], "terminal": True})
    p["info"] = v.cap(info, "info", 7)
    p["prompt"] = v.text(raw.get("prompt"), "prompt", 60)

    # hero
    h = v.obj(raw.get("hero"), "hero")
    l1, l2 = _split_tagline(p["tagline"])
    p["hero"] = {"line1": v.text(h.get("line1"), "hero.line1", 22, l1), "line2": v.text(h.get("line2"), "hero.line2", 26, l2),
                 "accent": v.text(h.get("accent"), "hero.accent", 26)}
    if p["hero"]["accent"] and p["hero"]["accent"] not in p["hero"]["line2"]:
        v.warn("hero.accent", "tidak ditemukan di dalam hero.line2, aksen warna tidak dipakai")
        p["hero"]["accent"] = ""
    chips = [v.text(c, f"hero.chips[{i}]", 10) for i, c in enumerate(v.cap(v.lst(h.get("chips"), "hero.chips"), "hero.chips", 6))]
    p["hero"]["chips"] = [c for c in chips if c]

    # layanan, paket, nilai
    packages = []
    for i, k in enumerate(v.cap(v.lst(raw.get("packages"), "packages"), "packages", 3)):
        k = v.obj(k, f"packages[{i}]")
        n = v.text(k.get("name"), f"packages[{i}].name", 9)
        if n:
            packages.append({"name": n, "desc": v.text(k.get("desc"), f"packages[{i}].desc", 10)})
    p["packages"] = packages
    services = []
    for i, s in enumerate(v.cap(v.lst(raw.get("services"), "services"), "services", 5 if packages else 6)):
        s = v.obj(s, f"services[{i}]")
        title = v.text(s.get("title"), f"services[{i}].title", 18)
        if not title:
            v.err(f"services[{i}].title", "wajib diisi")
            continue
        icon = v.text(s.get("icon"), f"services[{i}].icon", default="star")
        if icon not in ICONS:
            v.err(f"services[{i}].icon", f"'{icon}' tidak dikenal (pilihan: {', '.join(ICONS)})")
            icon = "star"
        promise = v.lst(s.get("promise"), f"services[{i}].promise")
        if isinstance(s.get("promise"), str):
            promise = [s["promise"]]
        promise = [v.text(x, f"services[{i}].promise[{j}]", 30) for j, x in enumerate(promise[:2])]
        services.append({"icon": icon, "title": title, "promise": [x for x in promise if x],
                         "detail": v.text(s.get("detail"), f"services[{i}].detail", 36)})
    p["services"] = services
    values = []
    for i, k in enumerate(v.cap(v.lst(raw.get("values"), "values"), "values", 3)):
        k = v.obj(k, f"values[{i}]")
        n = v.text(k.get("name"), f"values[{i}].name", 8)
        if n:
            values.append({"name": n, "desc": v.text(k.get("desc"), f"values[{i}].desc", 16)})
    p["values"] = values

    # kartu data liar -> jinak
    sh = v.obj(raw.get("sheet"), "sheet")
    labels = [v.text(x, f"sheet.labels[{i}]", 16) for i, x in enumerate(v.cap(v.lst(sh.get("labels"), "sheet.labels"), "sheet.labels", 2))]
    labels = [x for x in labels if x]
    messy = [v.text(x, f"sheet.messy[{i}]", 14) for i, x in enumerate(v.cap(v.lst(sh.get("messy"), "sheet.messy"), "sheet.messy", 12))]
    messy = [x for x in messy if x]
    p["sheet"] = {"labels": labels if len(labels) == 2 else S["sheet_labels"], "messy": messy or S["sheet_messy"],
                  "caption": v.text(sh.get("caption"), "sheet.caption", 50, S["sheet_caption"]),
                  "accent": v.text(sh.get("accent"), "sheet.accent", 50, S["sheet_accent"])}

    # kartu terminal ketik
    ty = v.obj(raw.get("typing"), "typing")
    steps = [v.text(x, f"typing.steps[{i}]", 40) for i, x in enumerate(v.cap(v.lst(ty.get("steps"), "typing.steps"), "typing.steps", 6))]
    p["typing"] = {"command": v.text(ty.get("command"), "typing.command", 60, p["prompt"] or "profile --show"),
                   "steps": [x for x in steps if x],
                   "stats_command": v.text(ty.get("stats_command"), "typing.stats_command", 30, "stats")}

    # syarat tiap bagian
    for s in p["sections"]:
        if s == "brand" and not p["services"]:
            v.err("sections", "'brand' dipilih tetapi 'services' kosong. Isi services atau hapus 'brand' dari sections")
        if s == "hero" and not (p["hero"]["line1"] or p["tagline"]):
            v.err("sections", "'hero' dipilih tetapi 'tagline' dan 'hero.line1' kosong")
        if s == "typing" and not p["typing"]["steps"]:
            v.warn("sections", "'typing' dipilih tetapi 'typing.steps' kosong, hanya perintah dan statistik yang tampil")
    if p["button_mode"] != "none" and not p["buttons"] and any(s in CARD_SECTIONS for s in p["sections"]):
        v.warn("buttons", "kosong, kartu tampil tanpa tombol")
    return None if REPORT.errors else p
