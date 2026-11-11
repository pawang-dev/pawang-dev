# assets/data

Satu-satunya tempat mengubah isi profil. Setelah mengedit: `git push` (build otomatis) atau jalankan
`python scripts/build_all.py --sample` untuk pratinjau lokal. Cek isian: `python scripts/tools/check.py`.

| File | Isi |
| --- | --- |
| `profile.json` | identitas, teks kartu, tombol, daftar bagian README |
| `social.json` | akun sosial media (opsional) |
| `skills.json` | teknologi dan skill (opsional) |
| `schema/` | skema untuk saran dan peringatan di editor, dibuat otomatis |
| `examples/` | contoh isian siap salin |

Batas panjang teks dipotong otomatis dan dilaporkan sebagai peringatan.

## profile.json

Wajib: `name`. Sisanya opsional dan punya nilai bawaan.

- `language`: `id` atau `en`. Bahasa teks bawaan kartu.
- `username`: username GitHub. Kosong = pemilik repo.
- `name`: nama brand atau nama kamu (maks 24).
- `suffix`: akhiran nama berwarna aksen, contoh `.dev` (maks 10).
- `domain`: domain tanpa `https://`.
- `website`: URL lengkap. Tujuan saat kartu diklik.
- `email`: alamat email kontak.
- `tagline`: kalimat utama (maks 60). `tagline_accent`: bagian tagline yang berwarna aksen.
- `description`: 1 atau 2 baris, maks 56 karakter per baris.
- `audience`: untuk siapa layananmu.
- `mode`: kata suasana di kartu terminal hijau.
- `badge`: teks kecil pojok kanan atas kartu.
- `mascot.name`, `mascot.caption`: nama dan keterangan maskot.
- `sections`: bagian yang tampil, urutannya = urutan di README.
- `buttons`: 1 atau 2 tombol, masing-masing `label` dan `url`.
- `button_mode`: `each` (di bawah tiap kartu), `last` (hanya kartu terakhir), `none`.
- `info`: baris info, maks 7. Isi: `label`, `value`, `terminal` (`false` = tidak tampil di kartu terminal hijau).
- `prompt`: perintah di baris prompt kartu neofetch.
- `hero`: `line1`, `line2`, `accent` (bagian `line2` yang berwarna), `chips` (maks 6).
- `services`: maks 6 (maks 5 jika ada `packages`). Isi: `icon`, `title`, `promise` (maks 2 baris), `detail`.
- `packages`: maks 3. Isi: `name`, `desc`.
- `values`: maks 3. Isi: `name`, `desc`.
- `sheet`: `labels` (2), `messy` (maks 12 isi sel), `caption`, `accent`.
- `typing`: `command`, `steps` (maks 6), `stats_command`.

Nilai `sections` dan data yang dipakainya:

| Bagian | Data yang dipakai | Syarat |
| --- | --- | --- |
| `hero` | `name`, `suffix`, `hero`, `description`, `services` (chips bawaan) | `tagline` atau `hero.line1` |
| `neofetch` | `info`, `prompt`, `badge`, `mascot.name`, data GitHub | - |
| `terminal` | `info` (yang `terminal` bukan `false`, maks 5), `mode`, `badge`, data GitHub | - |
| `brand` | `services`, `packages`, `values`, `mascot`, `tagline` | `services` terisi |
| `sheet` | `sheet`, `mascot.name`, data GitHub | - |
| `typing` | `typing`, `prompt`, data GitHub | - |
| `skills` | `skills.json` | tidak tampil jika kosong |
| `social` | `social.json` | tidak tampil jika kosong |

Nilai `services[].icon`: `web`, `seo`, `sheet`, `otomasi`, `rawat`, `code`, `design`, `chart`, `chat`, `mail`, `star`.

## social.json

- `style`: `auto` (tombol untuk 1-3 platform, ikon jika lebih), `pill` (tombol), `icon` (ikon saja).
- `title`: judul bagian.
- `links`: isi platform yang dipakai, kosongkan sisanya. Nilai berupa teks, atau `{"url": "...", "label": "..."}`.

| Platform | Isian |
| --- | --- |
| `instagram`, `tiktok`, `youtube`, `x`, `threads` | handle, `@` boleh dihilangkan |
| `facebook`, `pinterest` | handle atau nama halaman |
| `linkedin` | `in/nama`, `company/nama`, atau URL. Handle polos dianggap `in/nama` |
| `discord` | kode undangan atau URL |
| `google-business-profile` | wajib URL lengkap |

## skills.json

- `style`: `original` (berwarna), `plain` (satu warna resmi), `line` (garis). Versi yang tidak tersedia diganti yang terdekat.
- `layout`: `card` (kartu berkelompok) atau `row` (baris ikon tanpa kartu).
- `title`, `subtitle`: teks kartu.
- `skills`: daftar tanpa grup.
- `groups`: `{"Nama Grup": ["python", "docker"]}`. Boleh dipakai bersama `skills`.
- Nama: nama devicon (`python`, `nodejs`, `postgresql`), alias (`js`, `ts`), atau ikon kustom (`googlesheets`, `whatsapp`, `gmail`, `excel`, `telegram`).
- Ikon sendiri: taruh file di `assets/images/skills/`, lalu tulis nama file tanpa ekstensi atau `{"custom": "file.png", "label": "Teks"}`.
- Ubah teks yang tampil: `{"name": "githubactions", "label": "GitHub Actions"}`.
- Maks 60 skill. Nama yang salah dilewati dengan peringatan dan saran.
