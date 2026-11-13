"""Artikel terbaru dari feed RSS 2.0 atau Atom. Gagal ambil -> pakai artikel tersimpan terakhir."""
import datetime as dt
import email.utils
import json
import re
import urllib.request
import xml.etree.ElementTree as ET

from common import CACHE, REPORT, SVG, emit, http_url, trunc
from sections._tiles import INK, T, arrow, assemble, header_svg, wrap_tile

OUT = SVG / "articles"
CACHE_FILE = CACHE / "articles.json"
WHERE = "assets/data/profile.json"
MAX_FEED_BYTES = 1_000_000
TITLE_MAX = 82


def _clean(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


def _txt(el):
    return _clean("".join(el.itertext())) if el is not None else ""


def parse_feed(data):
    """-> (daftar artikel terbaru dulu, tautan situs atau ''). Menolak DOCTYPE/ENTITY (hindari entity expansion)."""
    if b"<!DOCTYPE" in data[:4096].upper() or b"<!ENTITY" in data.upper():
        raise ValueError("feed berisi DOCTYPE/ENTITY, ditolak")
    root = ET.fromstring(data)
    name = root.tag.split("}")[-1]
    items, site = [], ""
    if name == "rss":
        ch = root.find("channel")
        if ch is None:
            raise ValueError("RSS tanpa <channel>")
        site = _txt(ch.find("link"))
        for it in ch.findall("item"):
            raw = _txt(it.find("pubDate"))
            try:
                d = email.utils.parsedate_to_datetime(raw).date()
            except (TypeError, ValueError):
                continue
            items.append((_txt(it.find("title")), _txt(it.find("link")), d, [_txt(c) for c in it.findall("category")]))
    elif name == "feed":
        for l in root.findall("{*}link"):
            if l.get("rel", "alternate") == "alternate" and l.get("href"):
                site = l.get("href")
                break
        for en in root.findall("{*}entry"):
            raw = _txt(en.find("{*}published")) or _txt(en.find("{*}updated"))
            try:
                d = dt.datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
            except ValueError:
                continue
            href = next((l.get("href") for l in en.findall("{*}link") if l.get("rel", "alternate") == "alternate" and l.get("href")), "")
            items.append((_txt(en.find("{*}title")), href, d, [c.get("label") or c.get("term") or "" for c in en.findall("{*}category")]))
    else:
        raise ValueError(f"bukan RSS atau Atom (elemen akar <{name}>)")
    out = []
    for title, url, d, cats in items:
        if not title or not http_url(url):
            continue
        seen, uniq = set(), []
        for c in cats:
            c = _clean(c)
            if c and c.lower() not in seen:
                seen.add(c.lower())
                uniq.append(c)
        out.append({"title": title, "url": url, "date": d.isoformat(), "cats": uniq})
    out.sort(key=lambda x: x["date"], reverse=True)       # sort stabil: tanggal sama tetap mengikuti urutan feed
    return out, (site if http_url(site) else "")


def fetch_bytes(url):
    req = urllib.request.Request(url, headers={"User-Agent": "pawang-profile-builder", "Accept": "application/rss+xml, application/atom+xml, application/xml"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read(MAX_FEED_BYTES + 1)
    if len(data) > MAX_FEED_BYTES:
        raise ValueError("feed lebih dari 1 MB")
    return data


def load_items(feeds, limit, fetch=fetch_bytes, cache_file=CACHE_FILE, dry=False):
    """-> (items, link). Coba tiap feed berurutan; semua gagal -> cache; tanpa cache -> ([], '')."""
    errors = []
    for url in feeds:
        try:
            items, link = parse_feed(fetch(url))
            if items:
                if not dry:
                    cache_file.parent.mkdir(parents=True, exist_ok=True)
                    cache_file.write_text(json.dumps({"fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                                                      "feed": url, "link": link, "items": items}, ensure_ascii=False), encoding="utf-8")
                return items[:limit], link
            errors.append(f"{url}: tidak ada artikel yang valid")
        except Exception as e:  # noqa: BLE001
            errors.append(f"{url}: {e}")
    try:
        blob = json.loads(cache_file.read_text(encoding="utf-8"))
        REPORT.warn(WHERE, f"articles.feeds: {'; '.join(errors)}. Memakai artikel tersimpan dari {blob.get('fetched_at', '?')}")
        return blob["items"][:limit], blob.get("link", "")
    except (OSError, ValueError, KeyError):
        REPORT.warn(WHERE, f"articles.feeds: {'; '.join(errors)}. Bagian artikel dilewati")
        return [], ""


def row_svg(it, S, lang, bl, br, divb):
    w, h = 960, 84
    d = dt.date.fromisoformat(it["date"])
    cats = " · ".join(c.upper() for c in it["cats"][:2])
    body = ['<rect x="28" y="16" width="52" height="52" rx="12" fill="#FF8A3D" opacity=".16"/>',
            T(54, 38, str(d.day), 20, 800, INK, 'text-anchor="middle"'), T(54, 56, S["months"][d.month - 1].upper(), 11, 700, "#C85A12", 'text-anchor="middle" letter-spacing="1"'),
            T(100, 36 if cats else 47, trunc(it["title"], TITLE_MAX), 17, 800, INK), arrow(w - 52, 28)]
    if cats:
        body.append(T(100, 58, trunc(cats, 70), 10.5, 800, "#C85A12", 'letter-spacing="1.4"'))
    return wrap_tile(w, h, "".join(body), it["title"], divr=False, divb=divb, bl=bl, br=br)


def build(ctx):
    p, S = ctx.p, ctx.S
    cfg = p["articles"]
    if ctx.sample:
        today = dt.date.today()
        items = [{"title": t, "url": f"https://example.com/artikel-{i + 1}", "date": (today - dt.timedelta(days=i * 6)).isoformat(), "cats": c}
                 for i, (t, c) in enumerate(S["sample_articles"])][: cfg["limit"]]
        link = ""
    else:
        items, link = load_items(cfg["feeds"], cfg["limit"], dry=ctx.dry)
    if not items:
        return ""
    title = cfg["title"] or S["articles_title"]
    for theme in ("dark", "light"):
        emit(OUT / f"header_{theme}.svg", header_svg(theme, title, cfg["subtitle"], ic="doc"))
    rows = []
    for i, it in enumerate(items):
        last = i == len(items) - 1
        fname = f"{i:02d}.svg"
        emit(OUT / fname, row_svg(it, S, p["language"], bl=last, br=last, divb=not last))
        rows.append([(fname, "100%", it["url"], it["title"])])
    return assemble("articles", "header", title, link or None, rows)
