# Troubleshooting

| Gejala | Penyebab dan solusi |
| --- | --- |
| Workflow gagal dengan pesan `KESALAHAN assets/data/profile.json: ...` | Isian JSON salah. Pesan menyebut bidang dan alasannya. Perbaiki lalu push. README dan SVG tidak diubah saat gagal |
| `JSON tidak valid (baris X, kolom Y)` | Koma kurang atau lebih, tanda kutip hilang. JSON tidak boleh berisi komentar |
| `'social' sudah diganti 'connect'` | Ganti `social` di `sections` menjadi `connect`, dan pindahkan isi `social.json` ke `connect.links` di `profile.json` |
| `social.json` atau `skills.json` tidak dipakai lagi | Pindahkan isinya ke blok `connect.links` dan `skills` di `profile.json`, lalu hapus file lama |
| `Build dihentikan ... data contoh tidak diterbitkan` | API GitHub gagal dan belum ada data tersimpan. Cek token dan log langkah Build, lalu jalankan ulang workflow. Setelah satu build sukses, data tersimpan di `assets/cache/github.json` |
| `memakai data tersimpan dari ...` | API GitHub sedang gagal. Profil memakai data live terakhir, bukan data contoh. Tidak perlu tindakan |
| `403` atau `Permission denied` saat push | Settings → Actions → General → Workflow permissions harus **Read and write** |
| README tidak berubah setelah push | Push yang hanya mengubah `README.md` atau `assets/svg/` tidak memicu build. Ubah `assets/data`, `assets/images`, atau `scripts`, atau jalankan workflow manual |
| Heatmap bertuliskan "(data contoh)" | Hanya muncul lewat `--sample` atau lokal tanpa token. Di GitHub Actions data contoh tidak pernah diterbitkan |
| Kontribusi privat tidak terhitung | Buat secret `GH_STATS_TOKEN` (scope `read:user`). Jumlahnya juga mengikuti pengaturan Private contributions di GitHub |
| Featured projects menampilkan repo populer, bukan pilihanmu | Belum ada pin. Pin repo di GitHub (Customize your pins), atau pakai `"source": "manual"` |
| Bagian artikel tidak tampil | `articles.feeds` kosong atau semua feed gagal dan belum ada artikel tersimpan. Lihat peringatan di log Build |
| Nomor WhatsApp ditolak | Tulis nomor internasional tanpa `0` dan `+` di depan, contoh `6281234567890` |
| `Peringatan: ... dipotong jadi N` | Teks melebihi batas panjang kartu. Persingkat teks, batas ada di `assets/data/README.md` |
| `skill 'xxx' tidak dikenal, maksudmu: ...` | Nama tidak ada di devicon atau ikon kustom. Ikuti saran, atau tambah ikon di `assets/images/skills/` |
| Gambar tidak muncul di README | Pastikan `assets/svg/` ikut ter-commit. Jangan mengabaikannya di `.gitignore` |
| Commit bot tidak memakai nama app milikmu | Secret `APP_CLIENT_ID` dan `APP_PRIVATE_KEY` belum ada, atau app belum dipasang di repo |
| Potret pixel di kartu terminal tidak berubah | Maskot baru butuh Pillow: jalankan `python scripts/tools/make_portrait.py` lokal, atau workflow memasangnya otomatis |
| Tombol turun ke baris baru | Layar sempit. Pakai `"style": "icon"` di `connect` atau kurangi akun |
