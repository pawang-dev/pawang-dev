# assets/images

Gambar milikmu. Semua opsional: jika tidak ada, build memakai cadangan otomatis.

## brand/

| File | Rasio | Ukuran disarankan | Format | Tampil sebagai |
| --- | --- | --- | --- | --- |
| `logo.png` (atau `.svg`, `.webp`) | persegi, 1:1 | 256 × 256 px atau lebih | PNG transparan, SVG, WebP | ± 28 sampai 46 px di kepala kartu |
| `mascot.png` (atau `.svg`, `.webp`) | potret, 226:257 (≈ 0,88) | 452 × 514 px | PNG transparan | hingga 226 × 257 px, di dalam kotak terang |

- Nama file harus persis `logo` dan `mascot`.
- Batas ukuran file: 400 KB per gambar. Lebih dari itu kena peringatan dan memperberat SVG.
- Maskot tampil di atas kotak atau lingkaran terang, jadi maskot berwarna gelap tetap terlihat.
- Beri ruang kosong tipis di tepi maskot. Latar harus transparan.
- Gambar dengan rasio lain tetap muat (diskalakan utuh, tidak terpotong).
- Kartu terminal hijau membuat potret pixel dari `mascot.png`. Potret dibuat ulang otomatis saat maskot berubah (butuh Pillow). Maskot `.svg` tidak bisa dijadikan potret pixel, kartu memakai inisial.
- Tanpa `logo`: monogram inisial `name`. Tanpa `mascot`: foto profil GitHub, atau monogram jika tidak tersedia.

## portfolio/

Gambar thumbnail untuk `portfolio.items[].image`. Opsional: tanpa gambar dipakai sketsa.

| Aturan | Nilai |
| --- | --- |
| Rasio | 8:3 (lebar : tinggi) |
| Ukuran | 960 × 360 px |
| Format | PNG, JPG, WebP |
| Ukuran file | di bawah 300 KB |
| Tampil sebagai | strip setinggi 120 px, lebar 320 / 480 / 960 px sesuai jumlah karya |

- Gambar diisi penuh dan dipotong dari tengah (tidak ada ruang kosong). Taruh bagian penting di tengah.
- Nama file ditulis di `profile.json`, contoh `"image": "klien-a.png"`.

## skills/

Ikon kustom untuk `skills.json`. Bawaan: `googlesheets`, `whatsapp`, `gmail`, `excel`, `telegram`.

| Aturan | Nilai |
| --- | --- |
| Rasio | persegi, 1:1 |
| Ukuran | 128 × 128 px atau lebih |
| Format | PNG transparan, SVG, WebP, JPG |
| Ukuran file | di bawah 40 KB |
| Tampil sebagai | 36 × 36 px di dalam kotak 64 px |

- Nama file (tanpa ekstensi) = nama yang ditulis di `skills.json`. Contoh: `notion.png` dipakai sebagai `"notion"`.
- Ikon kustom mengalahkan ikon devicon yang namanya sama.
- JPG punya latar putih. Pakai PNG transparan agar bersih.
