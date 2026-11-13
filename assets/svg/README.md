# assets/svg

Hasil build. Jangan diedit: isinya ditimpa setiap build. Ubah `assets/data/profile.json`, lalu build ulang.

| Folder | Isi |
| --- | --- |
| `cards/` | kartu utama |
| `buttons/` | baris tombol yang menempel di bawah kartu |
| `skills/` | kartu Skill Set |
| `connect/` | Connect with me |
| `featured/` | Featured projects |
| `portfolio/` | portofolio |
| `articles/` | artikel terbaru |
| `activity/` | aktivitas terbaru |

Hanya bagian yang ada di `sections` (dan datanya terisi) yang dibuat. Sisanya dihapus saat build.

## cards/

| File | Bagian | Mode | Ukuran |
| --- | --- | --- | --- |
| `neofetch_dark.svg`, `neofetch_light.svg` | `neofetch` | gelap, terang | 960 × 624 |
| `terminal_green.svg` | `terminal` | gelap saja | 960 × 690 |
| `hero_dark.svg`, `hero_light.svg` | `hero` | gelap, terang | 960 × 330 |
| `brand_dark.svg`, `brand_light.svg` | `brand` | gelap, terang | 960 × 568 |
| `sheet_dark.svg`, `sheet_light.svg` | `sheet` | gelap, terang | 960 × 420 |
| `typing_dark.svg`, `typing_light.svg` | `typing` | gelap, terang | 960 × (mengikuti isi) |

## buttons/

| File | Dipakai |
| --- | --- |
| `bar_brand_left.svg`, `bar_brand_right.svg` | dua tombol di bawah kartu bertema |
| `bar_brand_full.svg` | satu tombol di bawah kartu bertema |
| `bar_green_left.svg`, `bar_green_right.svg`, `bar_green_full.svg` | di bawah kartu terminal hijau |

## Bagian bergaya kartu judul + isi menempel

| Folder | File |
| --- | --- |
| `connect/` | `header_dark.svg`, `header_light.svg`, `NN-<platform>.svg` (satu segmen per akun) |
| `featured/` | `header_*.svg`, `NN-<repo>.svg` (satu kartu per repo) |
| `portfolio/` | `header_*.svg`, `NN.svg` (satu kartu per karya) |
| `articles/` | `header_*.svg`, `NN.svg` (satu baris per artikel) |
| `activity/` | `header_*.svg`, `NN.svg` (satu baris per aktivitas) |
| `skills/` | `skills_dark.svg`, `skills_light.svg` (layout `card`) atau `skills_row.svg` (layout `row`) |

- Kartu judul punya versi gelap dan terang. Isinya (segmen, kartu, baris) selalu krem.
- `NN` = nomor urut dua digit sesuai urutan tampil.

## Catatan

- Semua SVG berdiri sendiri: gambar dan ikon sudah tertanam, tidak ada permintaan jaringan saat dilihat.
- SVG di README tidak bisa diklik per bagian. Tiap segmen, kartu, atau baris adalah gambar sendiri yang dibungkus `<a>`.
- Animasi (kursor, kilau, ketikan, panah) memakai CSS dan SMIL. Pengunjung dengan "kurangi gerakan" melihat versi diam.
