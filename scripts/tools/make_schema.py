#!/usr/bin/env python3
"""Membuat JSON Schema (assets/data/schema/*.schema.json) dari konstanta di kode, supaya editor
(VS Code dan sejenisnya) memberi saran dan peringatan saat mengisi assets/data/*.json.

Dijalankan setiap kali daftar bagian, ikon, platform, atau paket ikon berubah.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import DATA, SKILL_ICONS, VENDOR  # noqa: E402
from i18n import LANGUAGES  # noqa: E402
from profile_loader import BUTTON_MODES, ICONS, SECTIONS  # noqa: E402
from sections.social import PLATFORMS  # noqa: E402
from sections.skills import STYLES  # noqa: E402

DRAFT = "http://json-schema.org/draft-07/schema#"
SCHEMA_DIR = DATA / "schema"


def s(desc, **kw):
    return {"type": "string", "description": desc, **kw}


def arr(items, desc, **kw):
    return {"type": "array", "description": desc, "items": items, **kw}


def profile_schema():
    url = {"type": "string", "pattern": "^https?://", "description": "URL lengkap diawali http:// atau https://"}
    return {
        "$schema": DRAFT, "title": "profile.json", "type": "object", "additionalProperties": False,
        "required": ["name"],
        "properties": {
            "$schema": {"type": "string"},
            "language": {"enum": list(LANGUAGES), "description": "Bahasa teks bawaan kartu (id atau en)"},
            "username": s("Username GitHub. Kosong = pemilik repo (otomatis di GitHub Actions)", pattern="^[A-Za-z0-9][A-Za-z0-9-]{0,38}$"),
            "name": s("Nama brand atau nama kamu", minLength=1, maxLength=24),
            "suffix": s("Akhiran nama yang diberi warna aksen, contoh: .dev", maxLength=10),
            "domain": s("Domain tanpa https://, contoh: pawang.dev", maxLength=40),
            "website": {**url, "description": "Tautan saat kartu diklik dan tombol pertama"},
            "email": s("Alamat email kontak", maxLength=50),
            "tagline": s("Kalimat utama", maxLength=60),
            "tagline_accent": s("Bagian tagline yang diberi warna aksen (harus ada di dalam tagline)", maxLength=60),
            "description": {"description": "Deskripsi singkat, maksimal 2 baris",
                            "oneOf": [s("Satu baris", maxLength=56), arr(s("Satu baris", maxLength=56), "Maksimal 2 baris", maxItems=2)]},
            "audience": s("Untuk siapa layananmu", maxLength=40),
            "mode": s("Kata suasana di kartu terminal hijau, contoh: jinak", maxLength=16),
            "badge": s("Teks kecil di pojok kanan atas kartu", maxLength=20),
            "mascot": {"type": "object", "additionalProperties": False, "properties": {
                "name": s("Nama maskot", maxLength=14), "caption": s("Keterangan di bawah maskot", maxLength=30)}},
            "sections": arr({"enum": list(SECTIONS)}, "Bagian yang tampil di README, urutannya = urutan tampil", uniqueItems=True),
            "button_mode": {"enum": list(BUTTON_MODES), "description": "each = tombol di bawah tiap kartu, last = hanya kartu terakhir, none = tanpa tombol"},
            "buttons": arr({"type": "object", "additionalProperties": False, "required": ["label", "url"],
                            "properties": {"label": s("Teks tombol", maxLength=24), "url": url}}, "Satu atau dua tombol", maxItems=2),
            "info": arr({"type": "object", "additionalProperties": False, "required": ["label", "value"],
                         "properties": {"label": s("Label", maxLength=12), "value": s("Isi", maxLength=52),
                                        "terminal": {"type": "boolean", "description": "false = tidak ditampilkan di kartu terminal hijau"}}},
                        "Baris info kartu neofetch dan terminal", maxItems=7),
            "prompt": s("Perintah di baris prompt kartu neofetch", maxLength=60),
            "hero": {"type": "object", "additionalProperties": False, "properties": {
                "line1": s("Baris 1 headline", maxLength=22), "line2": s("Baris 2 headline", maxLength=26),
                "accent": s("Bagian baris 2 yang diberi warna aksen", maxLength=26),
                "chips": arr(s("Label", maxLength=10), "Label kecil di bawah deskripsi", maxItems=6)}},
            "services": arr({"type": "object", "additionalProperties": False, "required": ["title"], "properties": {
                "icon": {"enum": list(ICONS)}, "title": s("Nama layanan", maxLength=18),
                "promise": arr(s("Satu baris", maxLength=30), "Janji layanan, maksimal 2 baris", maxItems=2),
                "detail": s("Rincian singkat", maxLength=36)}}, "Daftar layanan untuk kartu brand (maks 5 jika ada paket, 6 jika tidak)", maxItems=6),
            "packages": arr({"type": "object", "additionalProperties": False, "required": ["name"], "properties": {
                "name": s("Nama paket", maxLength=9), "desc": s("Keterangan", maxLength=10)}}, "Paket, maksimal 3", maxItems=3),
            "values": arr({"type": "object", "additionalProperties": False, "required": ["name"], "properties": {
                "name": s("Nilai", maxLength=8), "desc": s("Keterangan", maxLength=16)}}, "Nilai brand, maksimal 3", maxItems=3),
            "sheet": {"type": "object", "additionalProperties": False, "properties": {
                "labels": arr(s("Label", maxLength=16), "Dua label: sebelum dan sesudah", minItems=2, maxItems=2),
                "messy": arr(s("Isi sel", maxLength=14), "Isi sel berantakan, maksimal 12", maxItems=12),
                "caption": s("Kalimat bawah", maxLength=50), "accent": s("Lanjutan kalimat bawah (berwarna aksen)", maxLength=50)}},
            "typing": {"type": "object", "additionalProperties": False, "properties": {
                "command": s("Perintah yang diketik", maxLength=60),
                "steps": arr(s("Langkah", maxLength=40), "Langkah yang tampil setelah perintah", maxItems=6),
                "stats_command": s("Perintah untuk blok statistik", maxLength=30)}},
        },
    }


def social_schema():
    entry = {"oneOf": [{"type": "string"}, {"type": "object", "additionalProperties": False,
                       "properties": {"url": {"type": "string", "pattern": "^https?://"}, "handle": {"type": "string"}, "label": {"type": "string"}}}]}
    hints = {"linkedin": "Tulis in/nama atau company/nama atau URL", "discord": "Kode undangan atau URL",
             "google-business-profile": "Wajib URL lengkap"}
    return {
        "$schema": DRAFT, "title": "social.json", "type": "object", "additionalProperties": False,
        "properties": {
            "$schema": {"type": "string"},
            "style": {"enum": ["auto", "pill", "icon"], "description": "auto = tombol untuk 1-3 platform, ikon jika lebih; pill = tombol; icon = ikon saja"},
            "title": s("Judul bagian", maxLength=40),
            "links": {"type": "object", "additionalProperties": False, "description": "Isi handle atau URL. Kosongkan untuk melewati.",
                      "properties": {k: {**entry, "description": hints.get(k, "Handle (tanpa @) atau URL lengkap")} for k in PLATFORMS}},
        },
    }


def skills_schema():
    names = set()
    idx = VENDOR / "devicon" / "devicon.json"
    if idx.exists():
        for e in json.loads(idx.read_text(encoding="utf-8")):
            names.add(e["name"])
    if SKILL_ICONS.exists():
        names.update(p.stem.lower() for p in SKILL_ICONS.iterdir() if p.suffix.lower() in (".png", ".svg", ".webp", ".jpg", ".jpeg"))
    name_ref = {"$ref": "#/definitions/skillName"}
    item = {"oneOf": [
        name_ref,
        {"type": "object", "additionalProperties": False, "properties": {
            "name": name_ref, "label": {"type": "string", "description": "Teks yang tampil"},
            "custom": {"type": "string", "description": "Nama file di assets/images/skills/"}}}]}
    return {
        "$schema": DRAFT, "title": "skills.json", "type": "object", "additionalProperties": False,
        "definitions": {"skillName": {"type": "string", "description": "Nama teknologi (devicon) atau nama ikon kustom",
                                      "examples": sorted(names)}},
        "properties": {
            "$schema": {"type": "string"},
            "style": {"enum": list(STYLES), "description": "original = berwarna, plain = satu warna, line = garis"},
            "layout": {"enum": ["card", "row"], "description": "card = kartu berkelompok, row = baris ikon tanpa kartu"},
            "title": s("Judul", maxLength=40), "subtitle": s("Keterangan di kanan judul", maxLength=60),
            "skills": arr(item, "Daftar tanpa grup", maxItems=60),
            "groups": {"type": "object", "description": "Nama grup: daftar skill", "additionalProperties": arr(item, "Daftar skill dalam grup")},
        },
    }


def main():
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    for name, fn in (("profile", profile_schema), ("social", social_schema), ("skills", skills_schema)):
        text = json.dumps(fn(), ensure_ascii=False, separators=(",", ":")) if name == "skills" else json.dumps(fn(), ensure_ascii=False, indent=2)
        (SCHEMA_DIR / f"{name}.schema.json").write_text(text + "\n", encoding="utf-8")
        print("tulis", f"assets/data/schema/{name}.schema.json")


if __name__ == "__main__":
    main()
