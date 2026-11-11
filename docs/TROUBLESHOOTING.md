# Troubleshooting

| Gejala | Penyebab dan solusi |
| --- | --- |
| Workflow gagal dengan pesan `KESALAHAN assets/data/...` | Isian JSON salah. Pesan menyebut file, bidang, dan alasannya. Perbaiki lalu push. README dan SVG tidak diubah saat gagal |
| `JSON tidak valid (baris X, kolom Y)` | Koma kurang atau lebih, tanda kutip hilang. JSON tidak boleh berisi komentar |
| `403` atau `Permission denied` saat push | Settings → Actions → General → Workflow permissions harus **Read and write** |
| README tidak berubah setelah push | Push yang hanya mengubah `README.md` atau `assets/svg/` tidak memicu build. Ubah `assets/data`, `assets/images`, atau `scripts`, atau jalankan workflow manual |
| Heatmap bertuliskan "(data contoh)" | Token tidak ada atau gagal. Di Actions memakai `GITHUB_TOKEN`, cek log langkah Build. Lokal: set `GH_TOKEN` |
| Kontribusi privat tidak terhitung | Buat secret `GH_STATS_TOKEN` (scope `read:user`) |
| `Peringatan: ... dipotong jadi N` | Teks melebihi batas panjang kartu. Persingkat teks, batas ada di `assets/data/README.md` |
| `skill 'xxx' tidak dikenal, maksudmu: ...` | Nama tidak ada di devicon atau ikon kustom. Ikuti saran, atau tambah ikon di `assets/images/skills/` |
| Bagian `skills` atau `social` tidak tampil | Daftarnya kosong. Isi `assets/data/skills.json` atau `social.json` |
| Gambar tidak muncul di README | Pastikan `assets/svg/` ikut ter-commit. Jangan mengabaikannya di `.gitignore` |
| Commit bot tidak memakai nama app milikmu | Secret `APP_CLIENT_ID` dan `APP_PRIVATE_KEY` belum ada, atau app belum dipasang di repo |
| Potret pixel di kartu terminal tidak berubah | Maskot baru butuh Pillow: jalankan `python scripts/tools/make_portrait.py` lokal, atau workflow memasangnya otomatis |
| Tombol turun ke baris baru | Layar sempit. Pakai `"style": "icon"` di `social.json` atau kurangi platform |
