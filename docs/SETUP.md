# Setup

## Langkah awal

1. Buat repo **publik** di GitHub dengan nama sama persis dengan username kamu (`<username>/<username>`).
2. Unggah seluruh isi proyek ini ke repo itu.
3. Settings → Actions → General → Workflow permissions → pilih **Read and write permissions**.
4. Edit `assets/data/profile.json` (wajib: `name`). Contoh siap salin ada di `assets/data/examples/`.
5. Ganti gambar di `assets/images/brand/` dengan logo dan maskotmu (lihat `assets/images/README.md`). Boleh dikosongkan.
6. Tab Actions → **Update profile** → Run workflow. Selanjutnya build berjalan tiap 12 jam dan setiap `assets/data`, `assets/images`, atau `scripts` berubah.

## Opsional

- **Kontribusi privat ikut terhitung:** buat Personal Access Token dengan scope `read:user`, simpan sebagai secret `GH_STATS_TOKEN`.
- **Commit atas nama bot milikmu (`<nama-app>[bot]`):** buat GitHub App dengan izin Repository → Contents: Read and write, pasang di repo, lalu simpan secret `APP_CLIENT_ID` (Client ID app) dan `APP_PRIVATE_KEY` (isi file `.pem`). Tanpa dua secret ini, commit memakai `github-actions[bot]`.
- **Sosial media dan skill:** isi `assets/data/social.json` dan `assets/data/skills.json`. Kosong = bagian tidak tampil.

## Pratinjau lokal

```bash
python scripts/build_all.py --sample   # data contoh, tanpa token dan tanpa jaringan
python scripts/tools/check.py          # hanya validasi isian
python -m unittest discover -s tests   # tes
```

- Diuji dengan Python 3.12 (versi di workflow). Tidak perlu `pip install`, kecuali mengganti maskot (butuh `pillow` untuk memperbarui potret pixel).
- Hasil build: `README.md` dan `assets/svg/`. Jangan diedit manual.

## Perintah gh (opsional)

```bash
gh repo create <username> --public --source=. --remote=origin --push
gh api -X PUT repos/<username>/<username>/actions/permissions/workflow -f default_workflow_permissions=write
gh secret set GH_STATS_TOKEN
gh workflow run update-profile.yml && gh run watch
```
