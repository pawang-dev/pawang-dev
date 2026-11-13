"""Konteks build yang dibagikan ke semua kartu."""
from dataclasses import dataclass, field


@dataclass
class Ctx:
    p: dict                 # profil (sudah divalidasi dan dilengkapi)
    data: dict              # data GitHub
    S: dict                 # teks bawaan sesuai bahasa
    logo: str               # data URI logo
    mascot: str             # data URI maskot
    portrait: dict = None   # potret pixel (kartu terminal hijau)
    sample: bool = False    # True = tanpa jaringan (--sample dan --check)
    dry: bool = False       # True = tidak menulis berkas apa pun (--check)
    extra: dict = field(default_factory=dict)
