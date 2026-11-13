"""Featured projects: kartu repo dari pin GitHub (atau populer, atau daftar manual)."""
import re

from common import SVG, REPORT, emit, wrap_text
from sections._tiles import INK, SUB, T, arrow, assemble, fork_mini, header_svg, pct, repo_icon, star_mini, wrap_tile

OUT = SVG / "featured"
WHERE = "assets/data/profile.json"
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
REPO_RE = re.compile(r"^[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)?$")


def manual_names(entries, user):
    """-> daftar nama lengkap 'pemilik/repo' dari isian manual (untuk diambil datanya)."""
    out = []
    for e in entries:
        name = e.get("repo") if isinstance(e, dict) else e
        if isinstance(name, str) and REPO_RE.match(name.strip()):
            name = name.strip()
            out.append(name if "/" in name else f"{user}/{name}")
    return out


def pick_repos(cfg, data, user):
    src, limit = cfg["source"], cfg["limit"]
    if src == "manual":
        repos = []
        for i, e in enumerate(cfg["repos"]):
            name = e.get("repo") if isinstance(e, dict) else e
            if not isinstance(name, str) or not REPO_RE.match(name.strip()):
                REPORT.warn(WHERE, f"featured.repos[{i}]: nama repo tidak valid, dilewati (contoh: \"nama-repo\" atau \"pemilik/nama-repo\")")
                continue
            full = name.strip() if "/" in name else f"{user}/{name.strip()}"
            r = (data.get("repo_map") or {}).get(full.lower())
            if not r:
                REPORT.warn(WHERE, f"featured.repos[{i}]: repo '{full}' tidak ditemukan atau tidak publik, dilewati")
                continue
            r = dict(r)
            if isinstance(e, dict) and e.get("description"):
                r["description"] = str(e["description"]).strip()[:120]
            repos.append(r)
        return repos[:limit]
    repos = list(data.get("pinned") or []) if src == "pinned" else []
    if not repos:                                  # sama seperti GitHub: tanpa pin = tampilkan yang populer
        repos = list(data.get("popular") or [])
    return repos[:limit]


def tile_svg(r, w, bl, br, divr, divb):
    chars = max(40, int((w - 100) / 6.4))
    lines = wrap_text(r["description"] or "", chars, 2)
    body = [repo_icon(24, 22), T(56, 36, r["name"], 17, 800, INK), arrow(w - 40, 26)]
    for i, line in enumerate(lines):
        if line:
            body.append(T(56, 58 + i * 18, line, 12.5, 500, SUB))
    x, y = 30, 104
    if r["lang"]:
        color = r["color"] if HEX.match(r["color"] or "") else "#8b949e"
        body.append(f'<circle cx="{x}" cy="{y-4}" r="6" fill="{color}"/>')
        body.append(T(x + 12, y, r["lang"], 12, 600, INK))
        x += 12 + len(r["lang"]) * 7 + 14
    body += [star_mini(x, y - 10, "#C85A12"), T(x + 16, y, str(r["stars"]), 12, 600, INK)]
    x += 16 + len(str(r["stars"])) * 7 + 16
    body += [fork_mini(x, y - 10, "#C85A12"), T(x + 16, y, str(r["forks"]), 12, 600, INK)]
    return wrap_tile(w, 128, "".join(body), f'{r["name"]}: {r["description"]}'.strip(": "), divr=divr, divb=divb, bl=bl, br=br)


def build(ctx):
    p, S, data = ctx.p, ctx.S, ctx.data
    cfg = p["featured"]
    repos = pick_repos(cfg, data, p["username"])
    if not repos:
        return ""
    title = cfg["title"] or S["featured_title"]
    for theme in ("dark", "light"):
        emit(OUT / f"header_{theme}.svg", header_svg(theme, title, cfg["subtitle"], ic="star"))
    n = len(repos)
    rows, i = [], 0
    while i < n:
        full = n - i == 1                          # sisa satu = selebar penuh
        take = 1 if full else 2
        row = []
        last_row = i + take >= n
        for j in range(take):
            r, col = repos[i + j], j
            w = 960 if full else 480
            fname = f"{i + j:02d}-{re.sub(r'[^A-Za-z0-9._-]', '', r['name'])[:30]}.svg"
            emit(OUT / fname, tile_svg(r, w, bl=last_row and col == 0, br=last_row and col == take - 1,
                                       divr=not full and col == 0, divb=not last_row))
            row.append((fname, pct(take), r["url"], f'{r["name"]}: {r["description"]}'.strip(": ")))
        rows.append(row)
        i += take
    return assemble("featured", "header", title, f'https://github.com/{p["username"]}?tab=repositories', rows)
