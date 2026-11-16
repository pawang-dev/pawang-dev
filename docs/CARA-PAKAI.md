# Cara pakai (Pawang.dev, tema Pawang Hujan, gaya terminal)

Repo ini adalah profil GitHub `pawang-dev/pawang-dev`. `README.md` dan semua `assets/*.svg`, `assets/trace-3d.webp` dibuat otomatis oleh `scripts/generate.mjs`. Jangan diedit tangan.

## Alur otomatis (workflow "Update profile")
- Jalan sekali sehari (07.17 WIB), lewat tombol **Run workflow**, dan saat `scripts/**`, `profile.config.json`, font, atau aset brand berubah.
- Bot memakai GitHub App Anda: rahasia `APP_CLIENT_ID` dan `APP_PRIVATE_KEY`. Tanpa keduanya, commit memakai `github-actions[bot]`.
- Data hanya yang publik (`GITHUB_TOKEN`). Rahasia `GH_STATS_TOKEN` dari versi lama sengaja **tidak** dipakai lagi, supaya aktivitas dan nama repo privat tidak ikut tergambar.
- Workflow "Test" menjalankan `npm test` (tanpa jaringan dan tanpa token).
- Setelah patch ini diterapkan, jalankan workflow sekali untuk pengisian data pertama. Sebelum itu gambar masih berupa keadaan kosong (langit cerah, tanpa data karangan).

## Desain
Tema **Cyber-Nusantara / Mystical Terminal**, hanya mode gelap (latar SVG selalu Void Dark, jadi tampil sama di tema terang maupun gelap GitHub).
- Warna: Void Dark `#0B0E14`, Smoke Incense `#151A23`, Cloud Slate `#1F2633`, Lightning Gold `#FACC15` (teks di atas emas `#0B0E14`), Tamed Emerald `#10B981`, Danger Bug `#EF4444`, teks `#F8FAFC` dan `#94A3B8`.
- Font: Plus Jakarta Sans (heading dan isi) dan JetBrains Mono (kode, badge, istilah teknis), dijadikan outline di SVG sehingga tidak butuh font eksternal.
- Metafora: awan = server infrastruktur, dupa = uap kopi dan terminal `>_`, petir = bug dan error yang dikendalikan.
- Lima divisi punya warna sendiri: Web `#06B6D4`, Sheet `#10B981`, SEO `#FACC15`, Otomasi `#A855F7`, Rawat `#F97316`. Teks "liar" dan "mantra" tiap divisi ada di `profile.config.json`.
- Hover glow tidak bisa dipakai di SVG profil GitHub (gambar tidak menerima hover), jadi glow dibuat statis.
- Section berjendela terminal: Mantra Pilihan (`ls -l`, uap kopi makin tinggi bila repo makin baru), Detak Server (kontribusi), Meter Angin (`htop`), dan footer ala status bar tmux.
- Bila belum ada repo yang dipin, "Mantra Pilihan" memakai repo publik yang paling baru diperbarui (bukan fork, bukan privat) dan menyatakannya di subjudul.

## Gerak 3D (three.js)
Section "Detak Server" memakai adegan **three.js + WebGL** yang dirender di Actions dengan Chromium headless (SwiftShader), lalu disimpan sebagai animasi **WebP** (`assets/trace-3d.webp`, 54 frame, berulang). GitHub tidak menjalankan JavaScript atau WebGL di README, jadi yang tampil adalah hasil render, bukan WebGL langsung. Pembaca dengan "reduce motion" melihat gambar diam (`assets/trace-3d-still.png`).
- Ridge hijau = kontribusi per pekan, kamera mengorbit pelan, petir emas dalam `{ }` = hari paling ramai yang sudah "ditangkap" (cincin oranye).
- Bila render gagal: animasi sebelumnya dipertahankan; bila belum pernah ada, dipakai SVG 2D.
- Lokal: `npm run generate` (butuh Chromium; set `PAWANG_CHROME=/jalur/ke/chrome` bila perlu). `--no3d` melewati render 3D.
- Animasi dirakit dari 54 frame WebP dengan `node-webpmux` (loop tak berhingga, 18 fps).

## Aset brand asli
Logo, wordmark, monogram, dan maskot Dev di `assets/brand/` dipotong langsung dari brandboard (`Pawang_dev_Brand_Identity_Board.png`), bukan digambar ulang. Resolusinya mengikuti board (±650 px untuk lockup, ±250 px untuk maskot). Kalau punya file master (SVG/PNG besar), ganti file di folder itu dengan nama yang sama. Oranye pada logo dan Dev berasal dari brandboard dan sengaja tidak diubah.

## Yang bisa diubah
- `profile.config.json`: headline hero, kalimat "apa ini", divisi (liar, mantra, warna, ikon), paket, sosial, tautan CTA, jumlah artikel.
- `assets/icons/png/`: ikon (PNG 96 px). Ikon baru taruh di `assets/icons/custom/` dan daftarkan di config.

## Perintah lokal
- `npm ci`, lalu `npm run offline` (keadaan kosong, tanpa jaringan) atau `npm test`.
- `npm run preview` menulis **data contoh** ke `preview/` untuk melihat tampilan penuh. Itu bukan data Pawang.dev.
- `GH_TOKEN=<token> npm run generate` memakai data live.

## Privasi
Hanya data publik yang dibaca (tanpa token tambahan). Repo privat disaring di `scripts/lib/data.mjs` sebelum digambar, dan namanya tidak pernah ditulis ke SVG.

## Gagal baik-baik
Jika API GitHub gagal, generator keluar dengan error dan tidak menulis apa pun, jadi gambar lama tetap utuh. Jika RSS gagal, section artikel lama dipertahankan. Jika `og:image` sebuah artikel gagal, karcis memakai ilustrasi tema.

## Lisensi font dan ikon
Font Plus Jakarta Sans dan JetBrains Mono (OFL) ada di `fonts/`. Ikon: lihat `assets/icons/LICENSES.md`.
