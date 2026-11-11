"""Daftar kartu yang tersedia. Nama = nilai yang dipakai di "sections" pada profile.json."""
from cards import brand, hero, neofetch, sheet, terminal, typing

CARDS = {m.NAME: m for m in (hero, neofetch, terminal, brand, sheet, typing)}
