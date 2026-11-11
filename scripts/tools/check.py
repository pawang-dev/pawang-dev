#!/usr/bin/env python3
"""Validasi assets/data/*.json tanpa mengubah apa pun. Pemakaian: python scripts/tools/check.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from build_all import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(["--check"]))
