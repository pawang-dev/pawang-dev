"""Tes build: semua kartu dan bagian menghasilkan SVG valid, validasi memberi pesan jelas, hasil bisa diulang.

Setiap tes berjalan di salinan sementara folder assets (PAWANG_ROOT), repo asli tidak disentuh.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.dom.minidom as minidom
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
ALL_SECTIONS = ["hero", "neofetch", "terminal", "brand", "sheet", "typing", "skills", "social"]
CARDS = ["hero", "neofetch", "terminal", "brand", "sheet", "typing"]


def load(rel):
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


class Sandbox:
    """Salinan assets (vendor ditautkan, bukan disalin) di folder sementara."""

    def __init__(self, profile=None, social=None, skills=None, drop=()):
        self.root = Path(tempfile.mkdtemp(prefix="pawang-test-"))
        assets = self.root / "assets"
        for sub in ("data", "images"):
            shutil.copytree(REPO / "assets" / sub, assets / sub)
        (assets / "vendor").symlink_to(REPO / "assets" / "vendor")
        for sub in ("svg", "cache"):
            (assets / sub).mkdir()
        for rel in drop:
            target = assets / rel
            shutil.rmtree(target) if target.is_dir() else target.unlink()
        for name, value in (("profile", profile), ("social", social), ("skills", skills)):
            if value is not None:
                text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
                (assets / "data" / f"{name}.json").write_text(text, encoding="utf-8")

    def run(self, *args):
        env = dict(os.environ, PAWANG_ROOT=str(self.root), GH_USER="test-user")
        env.pop("GH_TOKEN", None)
        env.pop("GITHUB_TOKEN", None)
        return subprocess.run([sys.executable, str(SCRIPTS / "build_all.py"), *args], capture_output=True, text=True, env=env)

    def build(self, *args):
        return self.run("--sample", *args)

    @property
    def readme(self):
        p = self.root / "README.md"
        return p.read_text(encoding="utf-8") if p.exists() else None

    def svgs(self):
        return sorted((self.root / "assets" / "svg").rglob("*.svg"))

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


class BuildCase(unittest.TestCase):
    def sandbox(self, **kw):
        sb = Sandbox(**kw)
        self.addCleanup(sb.cleanup)
        return sb

    def assert_valid_output(self, sb):
        self.assertTrue(sb.svgs(), "tidak ada SVG yang dihasilkan")
        for f in sb.svgs():
            try:
                minidom.parse(str(f))
            except Exception as e:  # noqa: BLE001
                self.fail(f"{f.name} bukan XML valid: {e}")
        for ref in re.findall(r'(?:src|srcset)="(assets/[^"]+)"', sb.readme):
            self.assertTrue((sb.root / ref).exists(), f"README merujuk file yang tidak ada: {ref}")

    def profile(self, **over):
        p = load("assets/data/profile.json")
        p.update(over)
        return p


class TestBuild(BuildCase):
    def test_default_data_builds(self):
        sb = self.sandbox()
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("assets/svg/cards/neofetch_dark.svg", sb.readme)
        self.assert_valid_output(sb)

    def test_all_sections_with_data(self):
        social = {"links": {"instagram": "pawang.dev", "tiktok": "pawang.dev", "linkedin": "company/pawang-dev"}}
        skills = load("assets/data/examples/skills.example.json")
        sb = self.sandbox(profile=self.profile(sections=ALL_SECTIONS), social=social, skills=skills)
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assert_valid_output(sb)
        names = {f.name for f in sb.svgs()}
        for card in ("hero", "neofetch", "brand", "sheet", "typing"):
            self.assertIn(f"{card}_dark.svg", names)
            self.assertIn(f"{card}_light.svg", names)
        self.assertIn("terminal_green.svg", names)
        self.assertIn("skills_dark.svg", names)
        self.assertIn("instagram.svg", names)

    def test_each_card_alone(self):
        for card in CARDS:
            with self.subTest(card=card):
                sb = self.sandbox(profile=self.profile(sections=[card]))
                r = sb.build()
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assert_valid_output(sb)

    def test_empty_optional_sections_are_skipped(self):
        sb = self.sandbox(profile=self.profile(sections=["neofetch", "skills", "social"]))
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("skills_", sb.readme)
        self.assertNotIn("Profil Sosial Media", sb.readme)
        self.assertFalse(list((sb.root / "assets/svg/social").glob("*.svg")))

    def test_button_modes(self):
        counts = {}
        for mode in ("each", "last", "none"):
            sb = self.sandbox(profile=self.profile(sections=["hero", "neofetch"], button_mode=mode))
            self.assertEqual(sb.build().returncode, 0)
            counts[mode] = sb.readme.count("assets/svg/buttons/")
        self.assertEqual(counts, {"each": 4, "last": 2, "none": 0})

    def test_single_button_is_full_width(self):
        p = self.profile(sections=["neofetch"])
        p["buttons"] = p["buttons"][:1]
        sb = self.sandbox(profile=p)
        self.assertEqual(sb.build().returncode, 0)
        self.assertIn("bar_brand_full.svg", sb.readme)
        self.assert_valid_output(sb)

    def test_no_logo_no_mascot_uses_fallback(self):
        sb = self.sandbox(profile=self.profile(sections=["hero", "neofetch", "terminal", "brand"]),
                          drop=("images/brand/logo.png", "images/brand/mascot.png"))
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("monogram", r.stderr)
        self.assert_valid_output(sb)

    def test_english(self):
        sb = self.sandbox(profile=self.profile(language="en", sections=["neofetch"]))
        self.assertEqual(sb.build().returncode, 0)
        svg = (sb.root / "assets/svg/cards/neofetch_dark.svg").read_text(encoding="utf-8")
        self.assertIn("contributions in the last year", svg)

    def test_minimal_profile(self):
        ex = load("assets/data/examples/profile.minimal.json")
        sb = self.sandbox(profile=ex)
        self.assertEqual(sb.build().returncode, 0)
        self.assert_valid_output(sb)

    def test_pawang_example(self):
        ex = load("assets/data/examples/profile.pawang.json")
        ex["sections"] = ALL_SECTIONS
        sb = self.sandbox(profile=ex)
        self.assertEqual(sb.build().returncode, 0)
        self.assert_valid_output(sb)

    def test_idempotent_and_cleanup(self):
        sb = self.sandbox(profile=self.profile(sections=["hero", "neofetch"]))
        self.assertEqual(sb.build().returncode, 0)
        first = sb.readme, {f.name: f.read_bytes() for f in sb.svgs()}
        self.assertEqual(sb.build().returncode, 0)
        self.assertEqual(first, (sb.readme, {f.name: f.read_bytes() for f in sb.svgs()}))
        (sb.root / "assets/data/profile.json").write_text(json.dumps(self.profile(sections=["neofetch"])), encoding="utf-8")
        self.assertEqual(sb.build().returncode, 0)
        self.assertNotIn("hero_dark.svg", {f.name for f in sb.svgs()})

    def test_check_writes_nothing(self):
        sb = self.sandbox(profile=self.profile(sections=ALL_SECTIONS))
        r = sb.run("--check")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIsNone(sb.readme)
        self.assertEqual(sb.svgs(), [])

    def test_custom_icon_and_label(self):
        skills = {"layout": "row", "skills": ["python", {"name": "docker", "label": "Docker CLI"}, "whatsapp", "gmail"]}
        sb = self.sandbox(profile=self.profile(sections=["skills"]), skills=skills)
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("skills_row.svg", sb.readme)


class TestValidation(BuildCase):
    def fails(self, profile=None, social=None, skills=None, expect=()):
        sb = self.sandbox(profile=profile, social=social, skills=skills)
        before = sb.readme
        r = sb.build()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        for text in expect:
            self.assertIn(text, r.stderr)
        self.assertEqual(sb.readme, before, "README tidak boleh berubah saat ada kesalahan")
        return r

    def test_broken_json(self):
        self.fails(profile="{ rusak", expect=("profile.json", "baris"))

    def test_unknown_section(self):
        self.fails(profile=self.profile(sections=["neofetch", "foo"]), expect=("sections[1]", "foo"))

    def test_brand_needs_services(self):
        p = self.profile(sections=["brand"])
        p["services"] = []
        self.fails(profile=p, expect=("'brand'", "services"))

    def test_missing_name(self):
        p = self.profile()
        del p["name"]
        self.fails(profile=p, expect=("name",))

    def test_bad_email_and_url(self):
        self.fails(profile=self.profile(email="bukan-email", website="ftp://x"), expect=("email", "website"))

    def test_bad_language_and_icon(self):
        p = self.profile(language="fr", sections=["brand"])
        p["services"][0]["icon"] = "roket"
        self.fails(profile=p, expect=("language", "services[0].icon"))

    def test_bad_social_style(self):
        self.fails(social={"style": "neon", "links": {}}, expect=("social.json", "style"))

    def test_bad_skills_layout(self):
        self.fails(skills={"layout": "grid", "skills": ["python"]}, expect=("skills.json", "layout"))

    def test_warnings_do_not_fail(self):
        sb = self.sandbox(profile=self.profile(sections=["neofetch", "skills"]), skills={"skills": ["pyton", "docker"]})
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("maksudmu", r.stderr)

    def test_long_text_is_truncated_with_warning(self):
        sb = self.sandbox(profile=self.profile(tagline="x" * 90, tagline_accent=""))
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("dipotong", r.stderr)


class TestRepo(unittest.TestCase):
    def test_schemas_are_up_to_date(self):
        sys.path.insert(0, str(SCRIPTS))
        sys.path.insert(0, str(SCRIPTS / "tools"))
        import make_schema  # noqa: PLC0415
        for name, fn in (("profile", make_schema.profile_schema), ("social", make_schema.social_schema),
                         ("skills", make_schema.skills_schema)):
            on_disk = json.loads((REPO / "assets/data/schema" / f"{name}.schema.json").read_text(encoding="utf-8"))
            self.assertEqual(on_disk, fn(), f"{name}.schema.json usang: jalankan python scripts/tools/make_schema.py")

    def test_data_files_match_schemas(self):
        try:
            import jsonschema  # noqa: PLC0415
        except ImportError:
            self.skipTest("jsonschema belum terpasang")
        pairs = [("profile", "profile"), ("social", "social"), ("skills", "skills")]
        pairs += [(f"examples/{n}", n.split(".")[0]) for n in ("profile.pawang", "profile.minimal", "social.example", "skills.example")]
        for data, schema in pairs:
            with self.subTest(data=data):
                jsonschema.validate(load(f"assets/data/{data}.json"), load(f"assets/data/schema/{schema}.schema.json"))

    def test_data_files_have_no_comment_keys(self):
        for name in ("profile", "social", "skills"):
            data = load(f"assets/data/{name}.json")
            self.assertFalse([k for k in data if k.startswith("_")], f"{name}.json tidak boleh punya kunci _")


if __name__ == "__main__":
    unittest.main()
