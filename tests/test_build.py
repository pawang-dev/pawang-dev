"""Tes build: semua kartu dan bagian menghasilkan SVG valid, validasi memberi pesan jelas, data contoh tidak pernah
menimpa data asli, dan hasil bisa diulang.

Tes build berjalan di salinan sementara folder assets (PAWANG_ROOT), repo asli tidak disentuh.
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
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / "tools")]

CARDS = ["hero", "neofetch", "terminal", "brand", "sheet", "typing"]
NEW_SECTIONS = ["skills", "connect", "featured", "portfolio", "articles", "activity"]
ALL_SECTIONS = CARDS + NEW_SECTIONS
DEFAULT_LINK = "https://www.pawang.dev"


def load(rel):
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


class Sandbox:
    """Salinan assets (vendor ditautkan, bukan disalin) di folder sementara."""

    def __init__(self, profile=None, drop=(), extra_files=None):
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
        for rel, content in (extra_files or {}).items():
            f = assets / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(content if isinstance(content, bytes) else content.encode())
        if profile is not None:
            (assets / "data" / "profile.json").write_text(
                profile if isinstance(profile, str) else json.dumps(profile, ensure_ascii=False), encoding="utf-8")

    def run(self, *args, env_extra=None):
        env = dict(os.environ, PAWANG_ROOT=str(self.root), GH_USER="test-user", **(env_extra or {}))
        for k in ("GH_TOKEN", "GITHUB_TOKEN", "GITHUB_ACTIONS"):
            env.pop(k, None)
        env.update(env_extra or {})
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

    def profile(self, **over):
        p = load("assets/data/profile.json")
        p.update(over)
        return p

    def full_profile(self, **over):
        p = load("assets/data/examples/profile.pawang.json")
        p["sections"] = ALL_SECTIONS
        p.update(over)
        return p

    def assert_valid_output(self, sb):
        self.assertTrue(sb.svgs(), "tidak ada SVG yang dihasilkan")
        for f in sb.svgs():
            try:
                minidom.parse(str(f))
            except Exception as e:  # noqa: BLE001
                self.fail(f"{f.name} bukan XML valid: {e}")
        for ref in re.findall(r'(?:src|srcset)="(assets/[^"]+)"', sb.readme):
            self.assertTrue((sb.root / ref).exists(), f"README merujuk file yang tidak ada: {ref}")


class TestBuild(BuildCase):
    def test_default_data_builds(self):
        sb = self.sandbox()
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("assets/svg/cards/neofetch_dark.svg", sb.readme)
        self.assert_valid_output(sb)

    def test_all_sections(self):
        sb = self.sandbox(profile=self.full_profile())
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assert_valid_output(sb)
        names = {f.name for f in sb.svgs()}
        for card in ("hero", "neofetch", "brand", "sheet", "typing"):
            self.assertIn(f"{card}_dark.svg", names)
            self.assertIn(f"{card}_light.svg", names)
        self.assertIn("terminal_green.svg", names)
        for d in ("skills", "connect", "featured", "portfolio", "articles", "activity"):
            self.assertTrue(list((sb.root / "assets/svg" / d).glob("*.svg")), f"folder {d} kosong")

    def test_each_section_alone(self):
        for sec in CARDS + NEW_SECTIONS:
            with self.subTest(section=sec):
                sb = self.sandbox(profile=self.full_profile(sections=[sec]))
                r = sb.build()
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assert_valid_output(sb)

    def test_empty_optional_sections_are_skipped(self):
        p = self.profile(sections=["neofetch", "skills", "connect", "portfolio"])
        p["skills"], p["connect"], p["portfolio"] = {}, {}, {}
        sb = self.sandbox(profile=p)
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("assets/svg/skills", sb.readme)
        self.assertNotIn("assets/svg/connect", sb.readme)
        self.assertNotIn("assets/svg/portfolio", sb.readme)
        self.assertIn("dilewati", r.stdout)

    def test_default_link_is_in_script_not_in_data(self):
        sb = self.sandbox(profile=self.profile(sections=["hero", "neofetch"]))
        self.assertEqual(sb.build().returncode, 0)
        self.assertGreaterEqual(sb.readme.count(f'<a href="{DEFAULT_LINK}">'), 2)
        for path in ("assets/data/profile.json", "assets/data/schema/profile.schema.json"):
            text = (REPO / path).read_text(encoding="utf-8")
            self.assertNotIn("website", text, f"{path} tidak boleh punya bidang website")
        data = load("assets/data/profile.json")
        data["website"] = "https://contoh.com"
        sb2 = self.sandbox(profile=dict(data, sections=["hero"]))
        r = sb2.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("website: kunci tidak dikenal", r.stderr)
        self.assertNotIn("contoh.com", sb2.readme)
        self.assertIn(DEFAULT_LINK, sb2.readme)

    def test_section_links_point_to_owner_not_default(self):
        p = self.full_profile(sections=["featured", "activity", "portfolio"])
        sb = self.sandbox(profile=p)
        self.assertEqual(sb.build().returncode, 0)
        self.assertIn(f'href="https://github.com/{p["username"]}?tab=repositories"', sb.readme)
        self.assertIn(f'href="https://github.com/{p["username"]}"', sb.readme)
        self.assertNotIn(DEFAULT_LINK, sb.readme)

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
        sb = self.sandbox(profile=self.full_profile(sections=["hero", "neofetch", "terminal", "brand", "connect"]),
                          drop=("images/brand/logo.png", "images/brand/mascot.png"))
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("monogram", r.stderr)
        self.assert_valid_output(sb)

    def test_english(self):
        sb = self.sandbox(profile=self.full_profile(language="en", sections=["neofetch", "activity", "articles"]))
        self.assertEqual(sb.build().returncode, 0)
        self.assertIn("contributions in the last year", (sb.root / "assets/svg/cards/neofetch_dark.svg").read_text(encoding="utf-8"))
        self.assertIn("Pushed 3 commits", (sb.root / "assets/svg/activity/00.svg").read_text(encoding="utf-8"))

    def test_minimal_profile(self):
        sb = self.sandbox(profile=load("assets/data/examples/profile.minimal.json"))
        self.assertEqual(sb.build().returncode, 0)
        self.assert_valid_output(sb)

    def test_idempotent_and_cleanup(self):
        sb = self.sandbox(profile=self.full_profile(sections=["hero", "neofetch", "connect"]))
        self.assertEqual(sb.build().returncode, 0)
        first = sb.readme, {f.name: f.read_bytes() for f in sb.svgs()}
        self.assertEqual(sb.build().returncode, 0)
        self.assertEqual(first, (sb.readme, {f.name: f.read_bytes() for f in sb.svgs()}))
        (sb.root / "assets/data/profile.json").write_text(json.dumps(self.full_profile(sections=["neofetch"])), encoding="utf-8")
        self.assertEqual(sb.build().returncode, 0)
        names = {f.name for f in sb.svgs()}
        self.assertNotIn("hero_dark.svg", names)
        self.assertFalse((sb.root / "assets/svg/connect").exists())

    def test_actions_without_data_stops_and_keeps_readme(self):
        sb = self.sandbox(profile=self.profile(sections=["neofetch"]))
        r = sb.run(env_extra={"GITHUB_ACTIONS": "true"})
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("data contoh", r.stderr)
        self.assertIn("Build dihentikan", r.stderr)
        self.assertIsNone(sb.readme)
        self.assertEqual(sb.svgs(), [])

    def test_local_without_token_falls_back_to_sample_with_warning(self):
        sb = self.sandbox(profile=self.profile(sections=["neofetch"]))
        r = sb.run()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("memakai data contoh", r.stderr)
        self.assertIn("(data contoh)", (sb.root / "assets/svg/cards/neofetch_dark.svg").read_text(encoding="utf-8"))

    def test_check_writes_nothing(self):
        sb = self.sandbox(profile=self.full_profile())
        r = sb.run("--check")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIsNone(sb.readme)
        self.assertEqual(sb.svgs(), [])
        self.assertEqual(list((sb.root / "assets/cache").iterdir()), [])


class TestConnect(BuildCase):
    def connect(self, links, **over):
        p = self.full_profile(sections=["connect"])
        p["connect"] = dict({"links": links}, **over)
        sb = self.sandbox(profile=p)
        return sb, sb.build()

    def segments(self, sb):
        return len(re.findall(r'assets/svg/connect/\d\d-', sb.readme))

    def test_counts_and_modes(self):
        four = {"instagram": "a", "tiktok": "a", "threads": "a", "linkedin": "a"}
        six = dict(four, youtube="a", facebook="a")
        for links, n, mode in ((dict(instagram="a"), 1, "text"), (four, 4, "text"), (six, 6, "icon")):
            with self.subTest(n=n):
                sb, r = self.connect(links)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(self.segments(sb), n)
                svg = (next((sb.root / "assets/svg/connect").glob("00-*.svg"))).read_text(encoding="utf-8")
                self.assertEqual("<text" in svg, mode == "text")
                self.assert_valid_output(sb)

    def test_style_override(self):
        sb, r = self.connect({"instagram": "a", "tiktok": "a"}, style="icon")
        self.assertNotIn("<text", next((sb.root / "assets/svg/connect").glob("00-*.svg")).read_text(encoding="utf-8"))

    def test_whatsapp_telegram_email(self):
        sb, r = self.connect({"whatsapp": "+62 812-3456-7890", "telegram": "@pawang_dev", "email": "halo@pawang.dev"})
        self.assertEqual(r.returncode, 0, r.stderr)
        for url in ("https://wa.me/6281234567890", "https://t.me/pawang_dev", "mailto:halo@pawang.dev"):
            self.assertIn(url, sb.readme)

    def test_bad_entries_are_skipped_with_warning(self):
        sb, r = self.connect({"whatsapp": "0812345678", "email": "bukan-email", "instagram": "javascript:alert(1)",
                              "foo": "bar", "tiktok": "ok"})
        self.assertEqual(r.returncode, 0, r.stderr)
        for text in ("kode negara", "bukan alamat email", "karakter tidak valid", "platform tidak dikenal"):
            self.assertIn(text, r.stderr)
        self.assertEqual(self.segments(sb), 1)
        self.assertNotIn("javascript:", sb.readme)

    def test_custom_label_and_url(self):
        sb, r = self.connect({"google-business-profile": {"url": "https://g.page/r/abc/review", "label": "Ulasan Google"}})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("https://g.page/r/abc/review", sb.readme)

    def test_header_has_no_link(self):
        sb, _ = self.connect({"instagram": "a"})
        self.assertNotIn("</picture>\n</a>", sb.readme, "kartu judul Connect tidak boleh dibungkus link")


class TestSections(BuildCase):
    def test_featured_manual_and_popular(self):
        for source, extra in (("popular", {}), ("manual", {"repos": ["alpha", {"repo": "beta", "description": "Deskripsi sendiri"}, "org/gamma"]})):
            with self.subTest(source=source):
                p = self.full_profile(sections=["featured"])
                p["featured"] = dict({"source": source, "limit": 3}, **extra)
                sb = self.sandbox(profile=p)
                r = sb.build()
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assert_valid_output(sb)
                if source == "manual":
                    self.assertIn("github.com/org/gamma", sb.readme)

    def test_featured_odd_count_last_is_full_width(self):
        p = self.full_profile(sections=["featured"])
        p["featured"] = {"source": "popular", "limit": 3}
        sb = self.sandbox(profile=p)
        self.assertEqual(sb.build().returncode, 0)
        self.assertEqual(sb.readme.count('width="100%" align="top" alt="'), 1)
        self.assertEqual(sb.readme.count('width="50%"'), 2)

    def test_featured_bad_name_warns(self):
        p = self.full_profile(sections=["featured"])
        p["featured"] = {"source": "manual", "repos": ["ok-repo", "tidak valid!"]}
        sb = self.sandbox(profile=p)
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("nama repo tidak valid", r.stderr)

    def test_portfolio_layouts_and_image(self):
        png = (REPO / "assets/images/brand/mascot.png").read_bytes()
        for n, rows in ((1, 1), (2, 1), (3, 1), (4, 2), (5, 2), (6, 2)):
            with self.subTest(n=n):
                p = self.full_profile(sections=["portfolio"])
                p["portfolio"] = {"items": [{"title": f"Karya {i}", "tag": "WEBSITE", "description": "Deskripsi",
                                             "image": "foto.png" if i == 0 else "", "url": f"https://contoh.com/{i}"} for i in range(n)]}
                sb = self.sandbox(profile=p, extra_files={"images/portfolio/foto.png": png})
                r = sb.build()
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(len(list((sb.root / "assets/svg/portfolio").glob("[0-9]*.svg"))), n)
                self.assertIn("data:image/png;base64", (sb.root / "assets/svg/portfolio/00.svg").read_text(encoding="utf-8"))
                self.assert_valid_output(sb)

    def test_portfolio_missing_image_falls_back_to_sketch(self):
        p = self.full_profile(sections=["portfolio"])
        p["portfolio"] = {"items": [{"title": "Karya", "image": "tidak-ada.png"}]}
        sb = self.sandbox(profile=p)
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("tidak ditemukan", r.stderr)

    def test_articles_sample_and_limit(self):
        p = self.full_profile(sections=["articles"])
        p["articles"]["limit"] = 2
        sb = self.sandbox(profile=p)
        self.assertEqual(sb.build().returncode, 0)
        self.assertEqual(len(list((sb.root / "assets/svg/articles").glob("[0-9]*.svg"))), 2)

    def test_activity_limit(self):
        p = self.full_profile(sections=["activity"])
        p["activity"] = {"limit": 2}
        sb = self.sandbox(profile=p)
        self.assertEqual(sb.build().returncode, 0)
        self.assertEqual(len(list((sb.root / "assets/svg/activity").glob("[0-9]*.svg"))), 2)

    def test_skills_in_profile(self):
        p = self.full_profile(sections=["skills"])
        p["skills"] = {"layout": "row", "skills": ["python", {"name": "docker", "label": "Docker CLI"}, "whatsapp", "gmail", "pyton"]}
        sb = self.sandbox(profile=p)
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("maksudmu", r.stderr)
        self.assertIn("skills_row.svg", sb.readme)


class TestValidation(BuildCase):
    def fails(self, profile=None, expect=(), extra_files=None):
        sb = self.sandbox(profile=profile, extra_files=extra_files)
        r = sb.build()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        for text in expect:
            self.assertIn(text, r.stderr)
        self.assertIsNone(sb.readme, "README tidak boleh dibuat saat ada kesalahan")
        return r

    def test_broken_json(self):
        self.fails(profile="{ rusak", expect=("profile.json", "baris"))

    def test_unknown_section(self):
        self.fails(profile=self.profile(sections=["neofetch", "foo"]), expect=("sections[1]", "foo"))

    def test_old_social_section_name(self):
        self.fails(profile=self.profile(sections=["neofetch", "social"]), expect=("'social' sudah diganti 'connect'", "connect.links"))

    def test_legacy_files_warn(self):
        sb = self.sandbox(extra_files={"data/social.json": "{}", "data/skills.json": "{}"})
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("assets/data/social.json", r.stderr)
        self.assertIn("connect.links", r.stderr)
        self.assertIn("assets/data/skills.json", r.stderr)

    def test_brand_needs_services(self):
        p = self.profile(sections=["brand"])
        p["services"] = []
        self.fails(profile=p, expect=("'brand'", "services"))

    def test_articles_needs_feeds(self):
        p = self.profile(sections=["articles"])
        p["articles"] = {"limit": 3}
        self.fails(profile=p, expect=("articles.feeds",))

    def test_featured_manual_needs_repos(self):
        p = self.profile(sections=["featured"])
        p["featured"] = {"source": "manual"}
        self.fails(profile=p, expect=("featured.repos",))

    def test_bad_enums_and_limits(self):
        p = self.profile(language="fr", sections=["featured", "activity"])
        p["featured"] = {"source": "semua", "limit": 99}
        p["activity"] = {"limit": 0}
        p["connect"] = {"style": "neon"}
        p["skills"] = {"layout": "grid", "style": "hologram"}
        self.fails(profile=p, expect=("language", "featured.source", "featured.limit", "activity.limit", "connect.style", "skills.layout", "skills.style"))

    def test_portfolio_item_errors(self):
        p = self.profile(sections=["portfolio"])
        p["portfolio"] = {"items": [{"tag": "WEB"}, {"title": "A", "image": "../rahasia.png", "url": "ftp://x"}]}
        self.fails(profile=p, expect=("portfolio.items[0].title", "portfolio.items[1].image", "portfolio.items[1].url"))

    def test_missing_name_and_bad_email(self):
        p = self.profile(email="bukan-email")
        del p["name"]
        self.fails(profile=p, expect=("name", "email"))

    def test_unknown_block_key_warns(self):
        p = self.profile(sections=["neofetch"])
        p["connect"] = {"links": {}, "warna": "merah"}
        sb = self.sandbox(profile=p)
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("connect.warna", r.stderr)

    def test_long_text_is_truncated_with_warning(self):
        sb = self.sandbox(profile=self.profile(tagline="x" * 90, tagline_accent=""))
        r = sb.build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("dipotong", r.stderr)


class TestFeeds(unittest.TestCase):
    RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel><title>T</title><link>https://site.example/</link>
<item><title>Lama</title><link>https://site.example/a</link><pubDate>Sat, 01 Nov 2026 10:00:00 +0700</pubDate></item>
<item><title>  Baru   &amp; <b>Bagus</b> </title><link>https://site.example/b</link><pubDate>Sun, 08 Nov 2026 10:00:00 +0700</pubDate>
<category>Sheet</category><category>sheet</category><category>Otomasi</category></item>
<item><title>Sama Tanggal</title><link>https://site.example/c</link><pubDate>Sun, 08 Nov 2026 08:00:00 +0700</pubDate></item>
<item><title>Tanpa tanggal</title><link>https://site.example/d</link></item>
<item><title>Tautan jahat</title><link>javascript:alert(1)</link><pubDate>Sun, 08 Nov 2026 08:00:00 +0700</pubDate></item>
</channel></rss>"""
    ATOM = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><title>T</title><link rel="alternate" href="https://site.example/"/>
<entry><title>Satu</title><link rel="alternate" href="https://site.example/1"/><published>2026-11-08T10:00:00+07:00</published>
<category term="Sheet"/><category label="Sheet"/></entry>
<entry><title>Dua</title><link href="https://site.example/2"/><updated>2026-11-01T00:00:00Z</updated></entry></feed>"""

    def setUp(self):
        from sections import articles
        self.a = articles
        self.tmp = Path(tempfile.mkdtemp(prefix="pawang-feed-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        import common
        common.REPORT.errors.clear()
        common.REPORT.warnings.clear()
        self.report = common.REPORT

    def test_rss(self):
        items, link = self.a.parse_feed(self.RSS)
        self.assertEqual(link, "https://site.example/")
        self.assertEqual([i["title"] for i in items], ["Baru & Bagus", "Sama Tanggal", "Lama"])   # tanggal sama: urutan feed
        self.assertEqual(items[0]["cats"], ["Sheet", "Otomasi"])                                   # duplikat dibuang
        self.assertEqual(items[0]["date"], "2026-11-08")                                           # tanggal lokal dari feed

    def test_atom(self):
        items, link = self.a.parse_feed(self.ATOM)
        self.assertEqual(link, "https://site.example/")
        self.assertEqual([i["title"] for i in items], ["Satu", "Dua"])
        self.assertEqual(items[0]["cats"], ["Sheet"])

    def test_rejects_entities_and_non_feed(self):
        with self.assertRaises(ValueError):
            self.a.parse_feed(b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "b">]><rss><channel/></rss>')
        with self.assertRaises(ValueError):
            self.a.parse_feed(b"<html><body/></html>")

    def test_second_feed_and_cache_fallback(self):
        cache = self.tmp / "articles.json"
        calls = []

        def fetch(url):
            calls.append(url)
            if url.endswith("rss.xml"):
                raise OSError("down")
            return self.ATOM
        items, _ = self.a.load_items(["https://x/rss.xml", "https://x/atom.xml"], 5, fetch=fetch, cache_file=cache)
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(items), 2)
        self.assertTrue(cache.exists())

        def down(url):
            raise OSError("down")
        items, _ = self.a.load_items(["https://x/rss.xml"], 5, fetch=down, cache_file=cache)
        self.assertEqual(len(items), 2, "harus memakai artikel tersimpan")
        self.assertTrue(any("tersimpan" in w for w in self.report.warnings))
        cache.unlink()
        items, _ = self.a.load_items(["https://x/rss.xml"], 5, fetch=down, cache_file=cache)
        self.assertEqual(items, [])

    def test_dry_does_not_write_cache(self):
        cache = self.tmp / "articles.json"
        self.a.load_items(["https://x/atom.xml"], 5, fetch=lambda u: self.ATOM, cache_file=cache, dry=True)
        self.assertFalse(cache.exists())


class TestGithubData(unittest.TestCase):
    def setUp(self):
        import github_data
        import common
        self.g = github_data
        self.tmp = Path(tempfile.mkdtemp(prefix="pawang-gh-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.cache = self.tmp / "github.json"
        common.REPORT.errors.clear()
        common.REPORT.warnings.clear()
        self.report = common.REPORT
        self.live = dict(repos=3, stars=7, commits=60, followers=2, total=163, weeks=[[("2026-11-09", 4, 1)]], pinned=[],
                         popular=[], repo_map={}, events=[], sample=False)

    def get(self, **kw):
        return self.g.get_data("u", cache_file=self.cache, **kw)

    def test_live_success_writes_cache(self):
        d = self.get(token="t", fetch=lambda *a: self.live, in_actions=True)
        self.assertEqual(d["total"], 163)
        self.assertEqual(json.loads(self.cache.read_text())["user"], "u")

    def test_failure_uses_cache_never_sample(self):
        self.get(token="t", fetch=lambda *a: self.live, in_actions=True)

        def boom(*a):
            raise OSError("api down")
        d = self.get(token="t", fetch=boom, in_actions=True)
        self.assertEqual(d["total"], 163)
        self.assertFalse(d["sample"])
        self.assertTrue(any("tersimpan" in w for w in self.report.warnings))

    def test_actions_without_cache_stops(self):
        def boom(*a):
            raise OSError("api down")
        self.assertIsNone(self.get(token="t", fetch=boom, in_actions=True))
        self.assertTrue(any("data contoh" in e for e in self.report.errors))
        self.report.errors.clear()
        self.assertIsNone(self.get(token="", fetch=boom, in_actions=True))
        self.assertTrue(self.report.errors)

    def test_local_without_cache_uses_sample_with_warning(self):
        d = self.get(token="", in_actions=False)
        self.assertTrue(d["sample"])
        self.assertEqual(d["total"], self.g.SAMPLE_TOTAL)
        self.assertTrue(self.report.warnings)

    def test_force_sample_never_touches_cache(self):
        self.get(token="t", fetch=lambda *a: self.live, in_actions=True)
        before = self.cache.read_text()
        d = self.g.get_data("u", force_sample=True, cache_file=self.cache)
        self.assertTrue(d["sample"])
        self.assertEqual(self.cache.read_text(), before)

    def test_cache_of_other_user_or_sample_is_ignored(self):
        self.g.save_cache(self.live, "someone-else", self.cache)
        self.assertIsNone(self.g.load_cache("u", self.cache))
        self.g.save_cache(dict(self.live, sample=True), "u", self.cache)
        self.assertIsNone(self.g.load_cache("u", self.cache))

    def test_dry_does_not_write_cache(self):
        self.get(token="t", fetch=lambda *a: self.live, in_actions=True, dry=True)
        self.assertFalse(self.cache.exists())

    def test_normalize_events(self):
        ev = [
            {"type": "PushEvent", "repo": {"name": "u/a"}, "created_at": "2026-11-09T10:00:00Z", "payload": {"size": 2, "distinct_size": 2}},
            {"type": "PushEvent", "repo": {"name": "u/a"}, "created_at": "2026-11-09T08:00:00Z", "payload": {"size": 3, "distinct_size": 3}},
            {"type": "PullRequestEvent", "repo": {"name": "u/a"}, "created_at": "2026-11-08T08:00:00Z",
             "payload": {"action": "closed", "number": 5, "pull_request": {"merged": True, "html_url": "https://github.com/u/a/pull/5"}}},
            {"type": "CreateEvent", "repo": {"name": "u/b"}, "created_at": "2026-11-07T08:00:00Z", "payload": {"ref_type": "branch"}},
            {"type": "CreateEvent", "repo": {"name": "u/b"}, "created_at": "2026-11-06T08:00:00Z", "payload": {"ref_type": "repository"}},
            {"type": "WatchEvent", "repo": {"name": "x/y"}, "created_at": "2026-11-05T08:00:00Z", "payload": {}},
        ]
        out = self.g.normalize_events(ev)
        self.assertEqual([(e["k"], e["n"]) for e in out], [("commit", 5), ("pr_merge", 5), ("repo", 0)])
        self.assertEqual(out[1]["url"], "https://github.com/u/a/pull/5")


class TestRepo(unittest.TestCase):
    def test_schema_is_up_to_date(self):
        import make_schema
        on_disk = json.loads((REPO / "assets/data/schema/profile.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(on_disk, json.loads(json.dumps(make_schema.profile_schema())),
                         "profile.schema.json usang: jalankan python scripts/tools/make_schema.py")

    def test_data_files_match_schema(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema belum terpasang")
        schema = load("assets/data/schema/profile.schema.json")
        jsonschema.Draft7Validator.check_schema(schema)
        for f in ("profile", "examples/profile.pawang", "examples/profile.minimal"):
            with self.subTest(file=f):
                jsonschema.validate(load(f"assets/data/{f}.json"), schema)

    def test_single_data_file(self):
        names = sorted(p.name for p in (REPO / "assets/data").glob("*.json"))
        self.assertEqual(names, ["profile.json"], "semua isian harus ada di profile.json")

    def test_data_has_no_comment_keys(self):
        def walk(o, path=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    self.assertFalse(k.startswith("_"), f"kunci '{path}{k}' tidak boleh diawali _")
                    walk(v, f"{path}{k}.")
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    walk(v, f"{path}[{i}].")
        walk(load("assets/data/profile.json"))


if __name__ == "__main__":
    unittest.main()
