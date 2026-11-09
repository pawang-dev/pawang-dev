#!/usr/bin/env python3
"""Buat paket ikon devicon yang ringkas untuk build_skills.py (dijalankan manual saat mau memperbarui).

Pemakaian:  python scripts/make_devicon_pack.py /jalur/ke/devicon-master

Hasil di assets/vendor/devicon/:
  icons.zip     hanya SVG versi original, plain, line (tanpa wordmark), tersimpan sebagai <nama>/<berkas>.svg
  devicon.json  indeks ringkas: nama, altnames, warna, versi yang tersedia
  LICENSE       lisensi MIT devicon (wajib disertakan)
  VERSION.txt   asal dan versi
"""
import json
import shutil
import sys
import zipfile
from pathlib import Path

VARIANTS = ("original", "plain", "line")


def main(src):
    src = Path(src)
    out = Path(__file__).resolve().parent.parent / "assets" / "vendor" / "devicon"
    out.mkdir(parents=True, exist_ok=True)
    meta = json.loads((src / "devicon.json").read_text(encoding="utf-8"))
    index, n_files = [], 0
    with zipfile.ZipFile(out / "icons.zip", "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for e in sorted(meta, key=lambda e: e["name"]):
            name = e["name"]
            have = [v for v in VARIANTS if (src / "icons" / name / f"{name}-{v}.svg").exists()]
            if not have:
                continue
            for v in have:
                z.write(src / "icons" / name / f"{name}-{v}.svg", f"{name}/{name}-{v}.svg")
                n_files += 1
            index.append({"name": name, "altnames": e.get("altnames", []), "color": e.get("color", ""), "variants": have})
    (out / "devicon.json").write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    shutil.copy(src / "LICENSE", out / "LICENSE")
    ver = json.loads((src / "package.json").read_text(encoding="utf-8")).get("version", "?")
    (out / "VERSION.txt").write_text(f"devicon {ver}\nhttps://github.com/devicons/devicon (lisensi MIT, lihat LICENSE)\n", encoding="utf-8")
    print(f"{len(index)} teknologi, {n_files} SVG -> {out}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
