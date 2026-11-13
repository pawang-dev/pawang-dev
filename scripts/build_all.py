#!/usr/bin/env python3
"""Satu pintu untuk semua: validasi data, buat kartu, bagian opsional, lalu README.md.

  python scripts/build_all.py            build memakai data asli (butuh GH_TOKEN), atau data contoh tanpa token
  python scripts/build_all.py --sample   paksa data contoh (pratinjau lokal, tanpa token dan tanpa jaringan)
  python scripts/build_all.py --check    hanya validasi assets/data/*.json

Yang diedit pengguna hanya assets/data/*.json dan gambar di assets/images/. Hanya memakai pustaka standar
(Pillow hanya dipakai kalau maskot berubah, untuk memperbarui potret pixel).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "tools"))

import cards as card_registry  # noqa: E402
import common  # noqa: E402
from cards import buttons  # noqa: E402
from common import REPORT, SVG, emit  # noqa: E402
from context import Ctx  # noqa: E402
from github_data import get_data  # noqa: E402
from i18n import strings  # noqa: E402
from images import logo_uri, mascot_uri  # noqa: E402
from profile_loader import CARD_SECTIONS, load_profile  # noqa: E402
from sections import activity, articles, connect, featured, portfolio, readme, skills  # noqa: E402

NEEDS_DATA = ("neofetch", "terminal", "sheet", "typing", "featured", "activity")
SVG_DIRS = ("cards", "buttons", "skills", "connect", "featured", "portfolio", "articles", "activity", "social")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    sample, check_only = "--sample" in argv, "--check" in argv
    unknown = [a for a in argv if a not in ("--sample", "--check")]
    if unknown:
        print(__doc__)
        return 2

    p = load_profile()
    if p is None:
        REPORT.show()
        print("\nBuild dihentikan: perbaiki kesalahan di atas. README dan SVG tidak diubah.", file=sys.stderr)
        return 1
    S = strings(p["language"])
    if check_only:                      # jalankan semuanya tanpa menulis berkas dan tanpa jaringan
        common.DRY, sample = True, True

    sections = p["sections"]
    wanted_cards = [s for s in sections if s in CARD_SECTIONS]
    data = None
    if any(s in NEEDS_DATA for s in sections):
        manual = featured.manual_names(p["featured"]["repos"], p["username"]) if "featured" in sections and p["featured"]["source"] == "manual" else ()
        data = get_data(p["username"], manual, S, force_sample=sample, dry=common.DRY)
        if data is None:
            REPORT.show()
            print("\nBuild dihentikan. README dan SVG tidak diubah.", file=sys.stderr)
            return 1
    logo = logo_uri(p["name"])
    mascot, mascot_file = mascot_uri(p["name"], p["username"], allow_network=not sample)
    portrait = None
    if "terminal" in sections:
        from make_portrait import ensure_portrait  # noqa: PLC0415
        portrait = ensure_portrait(mascot_file)
    ctx = Ctx(p=p, data=data, S=S, logo=logo, mascot=mascot, portrait=portrait, sample=sample, dry=common.DRY)

    # tombol: tiap kartu / hanya kartu terakhir / tidak ada
    mode = p["button_mode"] if p["buttons"] else "none"
    with_bar = set(wanted_cards) if mode == "each" else ({wanted_cards[-1]} if mode == "last" and wanted_cards else set())

    blocks, bar_cache = [], {}
    for s in sections:
        if s in CARD_SECTIONS:
            card = card_registry.CARDS[s]
            attached = s in with_bar
            if card.THEMED:
                for theme in ("dark", "light"):
                    emit(SVG / "cards" / f"{card.NAME}_{theme}.svg", card.render(theme, ctx, attached))
            else:
                emit(SVG / "cards" / card.FILE, card.render(ctx, attached))
            bars = None
            if attached:
                variant = "brand" if card.THEMED else "green"
                if variant not in bar_cache:
                    bar_cache[variant] = buttons.build(p["buttons"], variant)
                    for fname, svg, *_ in bar_cache[variant]:
                        emit(SVG / "buttons" / fname, svg)
                bars = bar_cache[variant]
            blocks.append(readme.card_block(card, p, bars))
        else:
            blocks.append({"skills": skills, "connect": connect, "featured": featured, "portfolio": portfolio,
                           "articles": articles, "activity": activity}[s].build(ctx))

    REPORT.show()
    if REPORT.errors:
        print("\nBuild dihentikan: perbaiki kesalahan di atas. README tidak diubah.", file=sys.stderr)
        return 1
    if check_only:
        print("OK:", ", ".join(sections), f"({len(REPORT.warnings)} peringatan)")
        return 0
    common.cleanup([SVG / d for d in SVG_DIRS])
    readme.write(readme.assemble(blocks, S))
    shown = [s for s, b in zip(sections, blocks) if b]
    skipped = [s for s, b in zip(sections, blocks) if not b]
    print("README.md:", ", ".join(shown) or "(kosong)", f"| SVG: {len(common.EMITTED)} berkas",
          "| data contoh" if (data or {}).get("sample") else "")
    if skipped:
        print("dilewati (kosong):", ", ".join(skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
