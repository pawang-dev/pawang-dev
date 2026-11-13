"""Skill Set / teknologi (opsional), dibaca dari blok "skills" di assets/data/profile.json.

Ikon: paket devicon (assets/vendor/devicon) atau ikon kustom (assets/images/skills/), ditanam ke SVG
sebagai data URI sehingga tidak ada permintaan jaringan saat profil dilihat.
"""
import base64
import difflib
import json
import math
import re
import zipfile

from common import NAVY, ORANGE, CREAM, REPORT, SANS, SKILL_ICONS as CUSTOM, SVG, VENDOR, emit, esc

PACK = VENDOR / "devicon"
WHERE = "assets/data/profile.json"
OUT = SVG / "skills"
SVG_DIR_REL = "assets/svg/skills"

MAX_SKILLS = 60
CUSTOM_EXT = {".svg": "image/svg+xml", ".png": "image/png", ".webp": "image/webp",
              ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
STYLES = {"original": ("original", "plain", "line"), "plain": ("plain", "original", "line"),
          "line": ("line", "plain", "original")}

LABELS = {
    "javascript": "JavaScript", "typescript": "TypeScript", "nodejs": "Node.js", "nextjs": "Next.js",
    "nuxtjs": "Nuxt", "vuejs": "Vue.js", "angular": "Angular", "react": "React", "svelte": "Svelte",
    "tailwindcss": "Tailwind CSS", "bootstrap": "Bootstrap", "sass": "Sass", "html5": "HTML5", "css3": "CSS3",
    "php": "PHP", "laravel": "Laravel", "wordpress": "WordPress", "mysql": "MySQL", "postgresql": "PostgreSQL",
    "mongodb": "MongoDB", "redis": "Redis", "sqlite": "SQLite", "supabase": "Supabase", "firebase": "Firebase",
    "docker": "Docker", "kubernetes": "Kubernetes", "git": "Git", "github": "GitHub", "gitlab": "GitLab",
    "githubactions": "GitHub Actions", "vscode": "VS Code", "figma": "Figma", "linux": "Linux", "ubuntu": "Ubuntu",
    "nginx": "Nginx", "apache": "Apache", "python": "Python", "django": "Django", "flask": "Flask",
    "fastapi": "FastAPI", "java": "Java", "spring": "Spring", "kotlin": "Kotlin", "swift": "Swift", "go": "Go",
    "rust": "Rust", "c": "C", "cplusplus": "C++", "csharp": "C#", "dotnetcore": ".NET", "flutter": "Flutter",
    "dart": "Dart", "npm": "npm", "yarn": "Yarn", "webpack": "Webpack", "vitejs": "Vite",
    "googlecloud": "Google Cloud", "amazonwebservices": "AWS", "azure": "Azure", "cloudflare": "Cloudflare",
    "vercel": "Vercel", "netlify": "Netlify", "heroku": "Heroku", "digitalocean": "DigitalOcean",
    "postman": "Postman", "jira": "Jira", "slack": "Slack", "notion": "Notion", "photoshop": "Photoshop",
    "illustrator": "Illustrator", "bash": "Bash", "markdown": "Markdown", "jquery": "jQuery", "express": "Express",
    # ikon kustom bawaan
    "googlesheets": "Google Sheets", "whatsapp": "WhatsApp", "gmail": "Gmail", "excel": "Excel", "telegram": "Telegram",
}


def warn(msg):
    REPORT.warn(WHERE, f"skills: {msg}")


def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


# ------------------------------------------------------------------ sumber ikon
class Icons:
    def __init__(self):
        self.index, self.alias = {}, {}
        meta = PACK / "devicon.json"
        self.zip = zipfile.ZipFile(PACK / "icons.zip") if (PACK / "icons.zip").exists() and meta.exists() else None
        if self.zip:
            for e in json.loads(meta.read_text(encoding="utf-8")):
                self.index[e["name"]] = e
                self.alias[norm(e["name"])] = e["name"]
                for a in e.get("altnames", []):
                    self.alias.setdefault(norm(a), e["name"])
        else:
            warn("paket devicon tidak ditemukan (assets/vendor/devicon), hanya ikon kustom yang tersedia")
        self.custom = {}
        if CUSTOM.exists():
            for p in sorted(CUSTOM.iterdir()):
                if p.suffix.lower() in CUSTOM_EXT:
                    self.custom.setdefault(norm(p.stem), p)

    def suggest(self, word):
        w = norm(word)
        if len(w) < 3:
            return []
        pool = [k for k in list(self.alias) + list(self.custom) if len(k) >= 3]
        return difflib.get_close_matches(w, pool, n=3, cutoff=0.6)

    def resolve(self, entry):
        """-> dict(key, label, kind, ...) atau None."""
        label = None
        custom_file = None
        if isinstance(entry, dict):
            label = (entry.get("label") or "").strip() or None
            custom_file = entry.get("custom")
            name = entry.get("name") or ""
        else:
            name = entry
        if custom_file:
            p = (CUSTOM / str(custom_file)).resolve()
            if CUSTOM.resolve() not in p.parents or p.suffix.lower() not in CUSTOM_EXT or not p.is_file():
                warn(f"ikon kustom '{custom_file}' tidak ditemukan di assets/images/skills/ atau tidak valid, dilewati")
                return None
            return dict(key=norm(p.stem), label=label or LABELS.get(norm(p.stem)) or p.stem.replace("-", " ").replace("_", " ").title(),
                        kind="custom", path=p)
        key = norm(name)
        if not key:
            return None
        if key in self.custom:                   # ikon kustom lebih diutamakan daripada devicon
            p = self.custom[key]
            return dict(key=key, label=label or LABELS.get(key) or p.stem.replace("-", " ").replace("_", " ").title(),
                        kind="custom", path=p)
        if key in self.alias:
            dev = self.alias[key]
            return dict(key=dev, label=label or LABELS.get(dev) or dev.capitalize(), kind="devicon", dev=dev)
        sug = self.suggest(name)
        warn(f"skill '{name}' tidak dikenal" + (f", maksudmu: {', '.join(sug)}?" if sug else ""))
        return None

    def data_uri(self, item, style):
        if item["kind"] == "custom":
            p = item["path"]
            return f"data:{CUSTOM_EXT[p.suffix.lower()]};base64," + base64.b64encode(p.read_bytes()).decode()
        dev = item["dev"]
        have = self.index[dev]["variants"]
        v = next(x for x in STYLES[style] if x in have)
        s = self.zip.read(f"{dev}/{dev}-{v}.svg").decode("utf-8")
        s = re.sub(r"<\?xml[^>]*\?>\s*|<!--.*?-->|<!DOCTYPE[^>]*>\s*", "", s, flags=re.S).strip()
        root = re.search(r"<svg[^>]*>", s).group(0)
        if v != "original" and "fill=" not in root:      # plain/line: warnai dengan warna resmi teknologinya
            col = self.index[dev].get("color") or NAVY
            if col.lower() in ("#000", "#000000", "#181616"):
                col = NAVY
            s = s.replace("<svg", f'<svg fill="{col}"', 1)
        return "data:image/svg+xml;base64," + base64.b64encode(s.encode("utf-8")).decode()


# ------------------------------------------------------------------- konfigurasi
def load_config(icons, S, cfg):
    """cfg = p["skills"] (struktur sudah divalidasi di profile_loader)."""
    title = cfg["title"] or S["skills_title"]
    flat, groups_cfg = cfg["skills"], cfg["groups"]
    raw_groups = []
    if flat:
        raw_groups.append((S["skills_other"] if groups_cfg else "", flat))
    for gname, items in groups_cfg.items():
        if isinstance(items, list):
            raw_groups.append((str(gname).strip()[:28], items))
    groups, total, seen = [], 0, set()
    for gname, items in raw_groups:
        resolved = []
        for it in items:
            if total >= MAX_SKILLS:
                warn(f"maksimal {MAX_SKILLS} skill, sisanya dilewati")
                break
            r = icons.resolve(it)
            if not r or (gname, r["key"]) in seen:
                continue
            seen.add((gname, r["key"]))
            resolved.append(r)
            total += 1
        if resolved:
            groups.append((gname, resolved))
    return dict(style=cfg["style"], layout=cfg["layout"], title=title, subtitle=cfg["subtitle"], groups=groups)


# ------------------------------------------------------------------------ gambar
def theme(t):
    d = t == "dark"
    return dict(bg=NAVY if d else CREAM, line="#2A3B63" if d else "#E6D6BB", text="#FAFAF7" if d else NAVY,
                muted="#9AA6C2" if d else "#5B6784", key=ORANGE if d else "#C85A12",
                tile=CREAM if d else "#FFFFFF", tline=CREAM if d else "#E6D6BB")


def tile(icons, c, x, y, item, style, label=True):
    out = [f'<rect x="{x}" y="{y}" width="64" height="64" rx="14" fill="{c["tile"]}" stroke="{c["tline"]}"/>',
           f'<image x="{x+14}" y="{y+14}" width="36" height="36" preserveAspectRatio="xMidYMid meet" href="{icons.data_uri(item, style)}"/>']
    if label:
        lab = item["label"] if len(item["label"]) <= 15 else item["label"][:14] + "…"
        size = 11.5 if len(lab) <= 12 else 10.5
        out.append(f'<text x="{x+32}" y="{y+82}" text-anchor="middle" font-family="{SANS}" font-size="{size}" '
                   f'font-weight="600" fill="{c["text"]}">{esc(lab)}</text>')
    return "".join(out)


def card_svg(icons, cfg, t, S):
    c = theme(t)
    W = 960
    named = any(g for g, _ in cfg["groups"])
    x0, pitch, per = (230, 90, 7) if named else (32, 96, 9)
    y = 74
    body = []
    for gi, (gname, items) in enumerate(cfg["groups"]):
        rows = math.ceil(len(items) / per)
        if named:
            body.append(f'<text x="32" y="{y+30}" font-family="{SANS}" font-size="12" font-weight="700" '
                        f'letter-spacing="1.4" fill="{c["key"]}">{esc(gname.upper())}</text>'
                        f'<text x="32" y="{y+48}" font-family="{SANS}" font-size="12" fill="{c["muted"]}">{esc(S["skills_count"].format(n=len(items)))}</text>')
        for i, item in enumerate(items):
            body.append(tile(icons, c, x0 + (i % per) * pitch, y + (i // per) * 104, item, cfg["style"]))
        y += rows * 104
        if gi < len(cfg["groups"]) - 1:
            body.append(f'<line x1="32" y1="{y}" x2="{W-32}" y2="{y}" stroke="{c["line"]}" opacity=".6"/>')
            y += 8
    H = y + 14
    head = f'<text x="32" y="46" font-family="{SANS}" font-size="22" font-weight="700" fill="{c["text"]}">{esc(cfg["title"])}</text>'
    if cfg["subtitle"]:
        head += (f'<text x="{W-32}" y="44" text-anchor="end" font-family="{SANS}" font-size="12.5" fill="{c["muted"]}">'
                 f'{esc(cfg["subtitle"])}</text>')
    names = ", ".join(i["label"] for _, g in cfg["groups"] for i in g)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{esc(cfg["title"])}: {esc(names)}"><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" '
            f'fill="{c["bg"]}" stroke="{c["line"]}"/>{head}{"".join(body)}</svg>')


def row_svg(icons, cfg):
    c = dict(tile=CREAM, tline="#E6D6BB", text=NAVY)
    items = [i for _, g in cfg["groups"] for i in g]
    cols = min(len(items), 11)
    rows = math.ceil(len(items) / cols)
    W, H = cols * 76 - 12, rows * 76 - 12
    parts = []
    for i, it in enumerate(items):
        r, k = divmod(i, cols)
        in_row = min(cols, len(items) - r * cols)
        x = (W - (in_row * 76 - 12)) / 2 + k * 76
        parts.append(tile(icons, c, round(x, 1), r * 76, it, cfg["style"], label=False))
    names = ", ".join(i["label"] for i in items)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{esc(cfg["title"])}: {esc(names)}">{"".join(parts)}</svg>')


# -------------------------------------------------------------------- blok README
def build(ctx):
    """Tulis SVG dan kembalikan blok HTML untuk README ('' kalau tidak ada skill)."""
    S = ctx.S
    icons = Icons()
    cfg = load_config(icons, S, ctx.p["skills"])
    if not cfg or not cfg["groups"]:
        return ""
    names = ", ".join(i["label"] for _, g in cfg["groups"] for i in g)
    alt = esc(f'{cfg["title"]}: {names}').replace('"', "&quot;")
    if cfg["layout"] == "row":
        emit(OUT / "skills_row.svg", row_svg(icons, cfg))
        return (f'<h3 align="center">{esc(cfg["title"])}</h3>\n'
                f'<img alt="{alt}" src="{SVG_DIR_REL}/skills_row.svg" align="top">\n')
    for t in ("dark", "light"):
        emit(OUT / f"skills_{t}.svg", card_svg(icons, cfg, t, S))
    return ('<picture>\n'
            f'  <source media="(prefers-color-scheme: dark)" srcset="{SVG_DIR_REL}/skills_dark.svg">\n'
            f'  <source media="(prefers-color-scheme: light)" srcset="{SVG_DIR_REL}/skills_light.svg">\n'
            f'  <img alt="{alt}" src="{SVG_DIR_REL}/skills_dark.svg" width="100%" align="top">\n</picture>\n')
