# assets/data

Semua isian ada di satu file: `profile.json`. Setelah mengedit: `git push` (build otomatis) atau jalankan
`python scripts/build_all.py --sample` untuk pratinjau lokal. Cek isian: `python scripts/tools/check.py`.

| Berkas | Isi |
| --- | --- |
| `profile.json` | identitas, teks kartu, tombol, urutan bagian, dan semua blok opsional |
| `schema/profile.schema.json` | skema untuk saran dan peringatan di editor, dibuat otomatis |
| `examples/` | contoh isian siap salin (`profile.pawang.json` lengkap, `profile.minimal.json` ringkas) |

- Teks yang melebihi batas dipotong otomatis dan dilaporkan sebagai peringatan.
- Kunci yang tidak dikenal diabaikan dengan peringatan.
- JSON tidak boleh berisi komentar.
- Kartu identitas (`hero`, `neofetch`, `terminal`, `brand`, `sheet`, `typing`) menaut ke https://www.pawang.dev (tautan bawaan template, tidak bisa diubah lewat JSON).

## Identitas

Wajib: `name`. Sisanya opsional.

- `language`: `id` atau `en`. Bahasa teks bawaan kartu.
- `username`: username GitHub. Kosong = pemilik repo.
- `name`: nama brand atau nama kamu (maks 24). `suffix`: akhiran berwarna aksen, contoh `.dev` (maks 10).
- `domain`: domain tanpa `https://`. `email`: alamat email.
- `tagline`: kalimat utama (maks 60). `tagline_accent`: bagian tagline yang berwarna aksen.
- `description`: 1 atau 2 baris, maks 56 karakter per baris.
- `audience`, `mode`, `badge`: teks pendek di kartu.
- `mascot.name`, `mascot.caption`: nama dan keterangan maskot.
- `buttons`: 1 atau 2 tombol (`label`, `url`). `button_mode`: `each` (di bawah tiap kartu), `last`, `none`.
- `info`: baris info, maks 7 (`label`, `value`, `terminal`: `false` = tidak tampil di kartu terminal hijau). `prompt`: baris perintah kartu neofetch.
- `hero`: `line1`, `line2`, `accent`, `chips` (maks 6).
- `services` (maks 6, maks 5 jika ada `packages`): `icon`, `title`, `promise` (maks 2 baris), `detail`.
  Ikon: `web`, `seo`, `sheet`, `otomasi`, `rawat`, `code`, `design`, `chart`, `chat`, `mail`, `star`.
- `packages` (maks 3) dan `values` (maks 3): `name`, `desc`.
- `sheet`: `labels` (2), `messy` (maks 12), `caption`, `accent`. `typing`: `command`, `steps` (maks 6), `stats_command`.

## sections

Daftar bagian yang tampil di README. Urutannya = urutan tampil.

| Nilai | Isi | Data |
| --- | --- | --- |
| `hero` | banner pembuka | identitas, `hero` |
| `neofetch` | kartu info dan kalender kontribusi | `info`, `prompt`, data GitHub |
| `terminal` | kartu terminal hijau | `info` (maks 5 baris), data GitHub |
| `brand` | layanan, paket, nilai | `services` (wajib), `packages`, `values` |
| `sheet` | data berantakan jadi dashboard | `sheet`, data GitHub |
| `typing` | terminal yang mengetik | `typing`, data GitHub |
| `skills` | Skill Set | blok `skills` |
| `connect` | Connect with me | blok `connect` |
| `featured` | Featured projects | blok `featured` |
| `portfolio` | hasil kerja | blok `portfolio` |
| `articles` | artikel terbaru | blok `articles` |
| `activity` | aktivitas terbaru | blok `activity` |

Bagian opsional yang datanya kosong tidak tampil.

## connect

- `title` (bawaan "Connect with me"), `subtitle`.
- `style`: `auto` (logo dan teks untuk 1-4 akun, ikon saja jika lebih), `text`, `icon`.
- `links`: isi platform yang dipakai (maks 10). Nilai berupa teks, atau `{"url": "...", "label": "..."}`.

| Platform | Isian |
| --- | --- |
| `instagram`, `tiktok`, `youtube`, `x`, `threads`, `telegram` | handle, `@` boleh dihilangkan |
| `facebook`, `pinterest` | handle atau nama halaman |
| `linkedin` | `in/nama`, `company/nama`, atau URL. Handle polos dianggap `in/nama` |
| `discord` | kode undangan atau URL |
| `google-business-profile` | URL lengkap |
| `whatsapp` | nomor internasional tanpa `0` di depan, contoh `6281234567890` |
| `email` | alamat email |

## skills

- `style`: `original` (berwarna), `plain` (satu warna resmi), `line` (garis). Versi yang tidak ada diganti yang terdekat.
- `layout`: `card` (kartu berkelompok) atau `row` (baris ikon). `title`, `subtitle`.
- `skills`: daftar tanpa grup. `groups`: `{"Nama Grup": ["python", "docker"]}`. Boleh dipakai bersamaan.
- Nama: nama devicon (`python`, `nodejs`), alias (`js`, `ts`), atau ikon kustom (`googlesheets`, `whatsapp`, `gmail`, `excel`, `telegram`).
- Ikon sendiri: file di `assets/images/skills/`, tulis namanya tanpa ekstensi, atau `{"custom": "file.png", "label": "Teks"}`.
- Ubah teks yang tampil: `{"name": "githubactions", "label": "GitHub Actions"}`. Maks 60 skill.

## featured

- `source`: `pinned` (pin GitHub; tanpa pin = repo populer), `popular`, `manual`. `limit`: 1-6 (bawaan 4). `title`, `subtitle`.
- `repos` (untuk `manual`): `"nama-repo"`, `"pemilik/nama-repo"`, atau `{"repo": "...", "description": "..."}`.
- Hanya repo publik. Pin diatur di GitHub (Customize your pins), tidak bisa lewat JSON.

## portfolio

- `items` (maks 6): `title` (wajib, maks 24), `tag` (maks 14), `description` (maks 40), `result` (maks 36), `url`, `image`, `thumb`.
- `image`: nama file di `assets/images/portfolio/`. Tanpa gambar dipakai sketsa; `thumb` memilihnya: `web`, `chart`, `chat`.
- `result` hanya diisi dengan klaim yang benar-benar terjadi.
- Tata letak: 1 karya = 1 kolom, 2 = 2 kolom, 3 = 3 kolom, 4 = 2 × 2, 5 = 3 + 2, 6 = 3 + 3. Karya tanpa `url` tidak bisa diklik.

## articles

- `feeds` (wajib, maks 3): alamat RSS 2.0 atau Atom, dicoba berurutan. `limit`: 1-6 (bawaan 3). `title`, `subtitle`.
- Tampil: tanggal, judul (maks 82 karakter), dan hingga 2 kategori. Kategori kembar dibuang.
- Semua feed gagal = artikel tersimpan terakhir (`assets/cache/articles.json`). Tanpa artikel tersimpan = bagian dilewati.
- Feed lebih dari 1 MB atau berisi DOCTYPE/ENTITY ditolak.

## activity

- `limit`: 1-8 (bawaan 5). `title`, `subtitle`.
- Hanya aktivitas publik: push (digabung per repo per hari), pull request (dibuka, digabung, ditutup), repo baru, issue baru, release, fork.
- Tanggal ditulis absolut, karena README hanya diperbarui berkala.

## Data GitHub

- Statistik, kalender, repo, dan aktivitas diambil saat build, lalu disimpan di `assets/cache/github.json`.
- API gagal = data tersimpan terakhir dipakai (dengan peringatan).
- Di GitHub Actions tanpa data tersimpan, build berhenti. Data contoh tidak pernah diterbitkan.
- Data contoh hanya muncul lewat `--sample` atau pemakaian lokal tanpa token.
