# assets/svg

Hasil build. Jangan diedit: isinya ditimpa setiap build. Ubah `assets/data/*.json` lalu build ulang.

| Folder | Isi |
| --- | --- |
| `cards/` | kartu utama |
| `buttons/` | baris tombol yang menempel di bawah kartu |
| `skills/` | kartu Skill Set |
| `social/` | satu tombol per platform sosial media |

## cards/

| File | Bagian | Mode | Ukuran |
| --- | --- | --- | --- |
| `neofetch_dark.svg`, `neofetch_light.svg` | `neofetch` | gelap, terang | 960 × 624 |
| `terminal_green.svg` | `terminal` | gelap saja | 960 × 690 |
| `hero_dark.svg`, `hero_light.svg` | `hero` | gelap, terang | 960 × 330 |
| `brand_dark.svg`, `brand_light.svg` | `brand` | gelap, terang | 960 × 568 |
| `sheet_dark.svg`, `sheet_light.svg` | `sheet` | gelap, terang | 960 × 420 |
| `typing_dark.svg`, `typing_light.svg` | `typing` | gelap, terang | 960 × (tinggi mengikuti isi) |

- Hanya kartu yang ada di `sections` yang dibuat. Sisanya dihapus saat build.
- Mode gelap/terang dipilih otomatis di README lewat `<picture>`.

## buttons/

| File | Dipakai |
| --- | --- |
| `bar_brand_left.svg`, `bar_brand_right.svg` | dua tombol di bawah kartu bertema (oranye, sage) |
| `bar_brand_full.svg` | satu tombol di bawah kartu bertema |
| `bar_green_left.svg`, `bar_green_right.svg`, `bar_green_full.svg` | di bawah kartu terminal hijau |

## skills/

| File | Layout |
| --- | --- |
| `skills_dark.svg`, `skills_light.svg` | `card` |
| `skills_row.svg` | `row` |

## social/

- `<platform>.svg`, misalnya `instagram.svg`. Hanya platform yang diisi di `social.json`.
- Bentuk (tombol atau ikon) mengikuti `style` di `social.json`.

## Catatan

- Semua SVG berdiri sendiri: gambar dan ikon sudah tertanam, tidak ada permintaan jaringan.
- SVG di README tidak bisa diklik per bagian. Tautan ada di tag `<a>` yang membungkus gambar.
- Animasi (kursor, kilau, ketikan) memakai CSS dan SMIL. Pengunjung dengan "kurangi gerakan" melihat versi diam.
