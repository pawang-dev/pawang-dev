#!/usr/bin/env python3
"""Membuat JSON Schema (assets/data/schema/profile.schema.json) dari konstanta di kode, supaya editor
(VS Code dan sejenisnya) memberi saran dan peringatan saat mengisi assets/data/profile.json.

Dijalankan setiap kali daftar bagian, ikon, platform, atau paket ikon berubah.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import DATA, SKILL_ICONS, VENDOR  # noqa: E402
from i18n import LANGUAGES  # noqa: E402
from profile_loader import (BUTTON_MODES, CONNECT_STYLES, FEATURED_SOURCES, ICONS, SECTIONS, SKILL_LAYOUTS,  # noqa: E402
                            SKILL_STYLES, THUMBS)
from sections.connect import PLATFORMS  # noqa: E402

DRAFT = "http://json-schema.org/draft-07/schema#"
SCHEMA_DIR = DATA / "schema"


def s(desc, **kw):
    return {"type": "string", "description": desc, **kw}


def arr(items, desc, **kw):
    return {"type": "array", "description": desc, "items": items, **kw}


LINK_ENTRY = {"oneOf": [{"type": "string"}, {"type": "object", "additionalProperties": False,
                                "properties": {"url": {"type": "string", "pattern": "^https?://"}, "handle": {"type": "string"}, "label": {"type": "string"}}}]}
LINK_HINTS = {"linkedin": "Tulis in/nama, company/nama, atau URL", "discord": "Kode undangan atau URL",
              "google-business-profile": "Wajib URL lengkap", "whatsapp": "Nomor internasional tanpa 0 di depan, contoh 6281234567890",
              "telegram": "Handle tanpa @", "email": "Alamat email"}
SKILL_ITEM = {"oneOf": [{"$ref": "#/definitions/skillName"}, {"type": "object", "additionalProperties": False, "properties": {
    "name": {"$ref": "#/definitions/skillName"}, "label": {"type": "string", "description": "Teks yang tampil"},
    "custom": {"type": "string", "description": "Nama file di assets/images/skills/"}}}]}


def skill_names():
    names = set()
    idx = VENDOR / "devicon" / "devicon.json"
    if idx.exists():
        names.update(e["name"] for e in json.loads(idx.read_text(encoding="utf-8")))
    if SKILL_ICONS.exists():
        names.update(p.stem.lower() for p in SKILL_ICONS.iterdir() if p.suffix.lower() in (".png", ".svg", ".webp", ".jpg", ".jpeg"))
    return sorted(names)


def profile_schema():
    url = {"type": "string", "pattern": "^https?://", "description": "URL lengkap diawali http:// atau https://"}
    return {
        "$schema": DRAFT, "title": "profile.json", "type": "object", "additionalProperties": False,
        "required": ["name"],
        "definitions": {"skillName": {"type": "string", "description": "Nama teknologi (devicon) atau nama ikon kustom", "examples": skill_names()}},
        "properties": {
            "$schema": {"type": "string"},
            "language": {"enum": list(LANGUAGES), "description": "Bahasa teks bawaan kartu (id atau en)"},
            "username": s("Username GitHub. Kosong = pemilik repo (otomatis di GitHub Actions)", pattern="^[A-Za-z0-9][A-Za-z0-9-]{0,38}$"),
            "name": s("Nama brand atau nama kamu", minLength=1, maxLength=24),
            "suffix": s("Akhiran nama yang diberi warna aksen, contoh: .dev", maxLength=10),
            "domain": s("Domain tanpa https://, contoh: pawang.dev", maxLength=40),
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
            "connect": {"type": "object", "additionalProperties": False, "description": "Connect with me: akun yang mau ditampilkan. Kosong = bagian tidak tampil", "properties": {
                "title": s("Judul kartu", maxLength=40), "subtitle": s("Keterangan di bawah judul", maxLength=60),
                "style": {"enum": list(CONNECT_STYLES), "description": "auto = logo dan teks untuk 1-4 akun, ikon saja jika lebih; text; icon"},
                "links": {"type": "object", "additionalProperties": False, "description": "Isi handle atau URL. Kosongkan untuk melewati.",
                          "properties": {k: {**LINK_ENTRY, "description": LINK_HINTS.get(k, "Handle (tanpa @) atau URL lengkap")} for k in PLATFORMS}}}},
            "skills": {"type": "object", "additionalProperties": False, "description": "Skill Set. Kosong = bagian tidak tampil", "properties": {
                "style": {"enum": list(SKILL_STYLES), "description": "original = berwarna, plain = satu warna, line = garis"},
                "layout": {"enum": list(SKILL_LAYOUTS), "description": "card = kartu berkelompok, row = baris ikon tanpa kartu"},
                "title": s("Judul", maxLength=40), "subtitle": s("Keterangan di kanan judul", maxLength=60),
                "skills": arr(SKILL_ITEM, "Daftar tanpa grup", maxItems=60),
                "groups": {"type": "object", "description": "Nama grup: daftar skill", "additionalProperties": arr(SKILL_ITEM, "Daftar skill dalam grup")}}},
            "featured": {"type": "object", "additionalProperties": False, "description": "Featured projects dari GitHub", "properties": {
                "title": s("Judul", maxLength=40), "subtitle": s("Keterangan", maxLength=60),
                "source": {"enum": list(FEATURED_SOURCES), "description": "pinned = pin GitHub (tanpa pin: populer), popular = repo terpopuler, manual = daftar repos"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 6, "description": "Jumlah repo"},
                "repos": arr({"oneOf": [s("Nama repo atau pemilik/repo"), {"type": "object", "additionalProperties": False, "required": ["repo"], "properties": {
                    "repo": s("Nama repo atau pemilik/repo"), "description": s("Deskripsi pengganti", maxLength=120)}}]}, "Dipakai jika source = manual", maxItems=6)}},
            "portfolio": {"type": "object", "additionalProperties": False, "description": "Portofolio hasil kerja. Kosong = bagian tidak tampil", "properties": {
                "title": s("Judul", maxLength=40), "subtitle": s("Keterangan", maxLength=60),
                "items": arr({"type": "object", "additionalProperties": False, "required": ["title"], "properties": {
                    "title": s("Judul karya", maxLength=24), "tag": s("Jenis, contoh: WEBSITE", maxLength=14),
                    "description": s("Deskripsi singkat", maxLength=40), "result": s("Hasil (isi hanya klaim yang benar)", maxLength=36),
                    "url": {"type": "string", "pattern": "^https?://", "description": "Tautan saat kartu diklik"},
                    "image": s("Nama file di assets/images/portfolio/ (png, jpg, webp)", maxLength=80),
                    "thumb": {"enum": list(THUMBS), "description": "Sketsa bawaan jika tanpa gambar"}}}, "Maksimal 6 karya", maxItems=6)}},
            "articles": {"type": "object", "additionalProperties": False, "description": "Artikel terbaru dari feed RSS atau Atom", "properties": {
                "title": s("Judul", maxLength=40), "subtitle": s("Keterangan", maxLength=60),
                "feeds": arr({"type": "string", "pattern": "^https?://"}, "Alamat feed, dicoba berurutan", maxItems=3),
                "limit": {"type": "integer", "minimum": 1, "maximum": 6, "description": "Jumlah artikel"}}},
            "activity": {"type": "object", "additionalProperties": False, "description": "Aktivitas publik terbaru di GitHub", "properties": {
                "title": s("Judul", maxLength=40), "subtitle": s("Keterangan", maxLength=60),
                "limit": {"type": "integer", "minimum": 1, "maximum": 8, "description": "Jumlah baris"}}},
        },
    }


def main():
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    text = json.dumps(profile_schema(), ensure_ascii=False, indent=1)
    (SCHEMA_DIR / "profile.schema.json").write_text(text + "\n", encoding="utf-8")
    print("tulis assets/data/schema/profile.schema.json")


if __name__ == "__main__":
    main()
