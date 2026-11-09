#!/usr/bin/env python3
"""Generator SVG profil GitHub Pawang.

Menghasilkan dark_mode.svg dan light_mode.svg di assets/svg/.
Data kontribusi diambil dari GitHub GraphQL API jika ada token
(env GH_TOKEN). Tanpa token, dipakai data contoh supaya tampilan
tetap bisa dilihat.

Hanya memakai pustaka standar Python (tanpa pip install).
"""
import base64
import datetime as dt
import json
import os
import random
import urllib.request
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- KONFIGURASI
USERNAME = os.environ.get("GH_USER", "pawang-dev")

# Baris info di panel kanan: (label, nilai). Silakan ubah sesuka hati.
INFO = [
    ("Brand", "Pawang.dev"),
    ("Tagline", "Digitalmu liar? Serahkan ke Pawang."),
    ("Layanan", "Web · SEO · Sheet · Otomasi · Rawat"),
    ("Paket", "Jinak → Piawai → Sakti"),
    ("Nilai", "Tenang, Paham, Jinak"),
    ("Untuk", "UMKM Indonesia"),
    ("Kontak", "halo@pawang.dev"),
]
PROMPT = "pawang --jinakkan DEV (digital, efisien, valid)"

# ------------------------------------------------------------------- TEMA
THEMES = {
    "dark": dict(
        bg="#14213D", panel="#1B2B4F", line="#2A3B63", text="#FAFAF7",
        muted="#9AA6C2", key="#FF8A3D", accent="#A7C4A0", cell0="#22345C",
        card="#FFF6E9", card_line="#FFF6E9", orange="#FF8A3D",
    ),
    "light": dict(
        bg="#FFF6E9", panel="#FFFFFF", line="#E6D6BB", text="#14213D",
        muted="#5B6784", key="#C85A12", accent="#6E9468", cell0="#EBDDC4",
        card="#FFFFFF", card_line="#E6D6BB", orange="#FF8A3D",
    ),
}
MONO = "'JetBrains Mono','SF Mono','Menlo','Consolas','DejaVu Sans Mono',monospace"

SAMPLE_TOTAL = 1804   # total kontribusi pada data contoh
W, H = 960, 624
MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
          "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


# --------------------------------------------------------------------- DATA
QUERY = """
query($login:String!){
  user(login:$login){
    followers{totalCount}
    repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:100){
      totalCount
      nodes{stargazerCount}
    }
    contributionsCollection{
      totalCommitContributions
      contributionCalendar{
        totalContributions
        weeks{contributionDays{contributionCount date weekday}}
      }
    }
  }
}
"""


def fetch_live(token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USERNAME}}).encode(),
        headers={"Authorization": f"bearer {token}",
                 "Content-Type": "application/json",
                 "User-Agent": "pawang-profile-builder"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    u = payload["data"]["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    return dict(
        repos=u["repositories"]["totalCount"],
        stars=sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
        commits=u["contributionsCollection"]["totalCommitContributions"],
        followers=u["followers"]["totalCount"],
        total=cal["totalContributions"],
        weeks=[[(d["date"], d["contributionCount"], d["weekday"])
                for d in w["contributionDays"]] for w in cal["weeks"]],
        sample=False,
    )


def sample_data():
    """Data contoh deterministik, dipakai kalau tidak ada token."""
    rnd = random.Random(42)
    today = dt.date.today()
    start = today - dt.timedelta(days=today.weekday() + 1 + 52 * 7)  # minggu mulai Minggu
    weeks, total, d = [], 0, start
    while d <= today:
        week = []
        for wd in range(7):
            day = d + dt.timedelta(days=wd)
            if day > today:
                break
            busy = 0.25 if wd in (0, 6) else 0.7
            n = rnd.choice([1, 2, 3, 5, 8, 12]) if rnd.random() < busy else 0
            total += n
            week.append((day.isoformat(), n, wd))
        weeks.append(week)
        d += dt.timedelta(days=7)
    # skala + koreksi supaya total tepat SAMPLE_TOTAL
    days = [(i, j) for i, w in enumerate(weeks) for j in range(len(w))]
    factor = SAMPLE_TOTAL / max(total, 1)
    cnt = {k: round(weeks[k[0]][k[1]][1] * factor) for k in days}
    diff = SAMPLE_TOTAL - sum(cnt.values())
    while diff != 0:
        k = rnd.choice(days)
        if diff > 0 and cnt[k] > 0:
            cnt[k] += 1; diff -= 1
        elif diff < 0 and cnt[k] > 0:
            cnt[k] -= 1; diff += 1
    weeks = [[(d, cnt[(i, j)], wd) for j, (d, _, wd) in enumerate(w)] for i, w in enumerate(weeks)]
    return dict(repos=0, stars=0, commits=0, followers=0,
                total=SAMPLE_TOTAL, weeks=weeks, sample=True)


def get_data():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        try:
            return fetch_live(token)
        except Exception as e:  # noqa: BLE001
            print("Gagal ambil data live, pakai data contoh:", e)
    return sample_data()


# ------------------------------------------------------------------- RENDER
def b64(path):
    return base64.b64encode((ROOT / "assets" / "images" / path).read_bytes()).decode()


def idn(n):
    return f"{n:,}".replace(",", ".")


def level(n, mx):
    if n <= 0:
        return 0
    r = n / mx
    return 1 if r <= .25 else 2 if r <= .5 else 3 if r <= .75 else 4


def render(theme, data, mascot, logo):
    c = THEMES[theme]
    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
      f'viewBox="0 0 {W} {H}" role="img" '
      f'aria-label="Profil GitHub Pawang.dev: Digitalmu liar? Serahkan ke Pawang.">')
    a(f"""<style>
text{{font-family:{MONO};font-size:14px;fill:{c['text']}}}
.k{{fill:{c['key']};font-weight:700}}
.m{{fill:{c['muted']}}}
.h{{font-size:15px;font-weight:700}}
.s{{font-size:12px;fill:{c['muted']}}}
.cur{{animation:blink 1.1s steps(1) infinite}}
.tw{{animation:tw 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
.cell{{animation:pop .5s ease-out both}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes tw{{0%,100%{{opacity:.25;transform:scale(.7)}}50%{{opacity:1;transform:scale(1.15)}}}}
@keyframes pop{{from{{opacity:0}}to{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{.cur,.tw,.cell{{animation:none}}}}
</style>""")
    # jendela
    a(f'<path d="{card_path(W, H)}" fill="{c["bg"]}"/>')
    a(f'<path transform="translate(.5 .5)" d="{card_path(W-1, H-1)}" fill="none" stroke="{c["line"]}"/>')
    # title bar
    a(f'<path d="M0 14a14 14 0 0 1 14-14h{W-28}a14 14 0 0 1 14 14v34H0z" fill="{c["panel"]}"/>')
    a(f'<line x1="0" y1="48" x2="{W}" y2="48" stroke="{c["line"]}"/>')
    for i, col in enumerate((c["orange"], c["accent"], c["muted"])):
        a(f'<circle cx="{26+i*20}" cy="24" r="6" fill="{col}"/>')
    a(f'<image x="100" y="11" width="28" height="27" href="data:image/png;base64,{logo}"/>')
    a(f'<text x="138" y="29" class="m">{USERNAME} — pawang.dev — zsh</text>')
    a(f'<text x="{W-24}" y="29" text-anchor="end" class="s">v1.0 · jinak</text>')

    # kartu maskot
    a(f'<rect x="30" y="70" width="270" height="302" rx="16" fill="{c["card"]}" stroke="{c["card_line"]}"/>')
    a(f'<image x="52" y="80" width="226" height="257" href="data:image/png;base64,{mascot}"/>')
    a(f'<text x="165" y="361" text-anchor="middle" style="fill:#14213D;font-weight:700">Dev</text>')
    for (x, y, d) in ((262, 100, 0), (252, 126, 0.8)):
        a(f'<path class="tw" style="animation-delay:{d}s" d="M{x} {y-8}Q{x} {y} {x+8} {y}'
          f'Q{x} {y} {x} {y+8}Q{x} {y} {x-8} {y}Q{x} {y} {x} {y-8}z" fill="{c["orange"]}"/>')

    # panel info (neofetch)
    X, VX = 340, 440
    a(f'<text x="{X}" y="92" class="h"><tspan class="k">{USERNAME}</tspan>@pawang.dev</text>')
    a(f'<line x1="{X}" y1="104" x2="{W-30}" y2="104" stroke="{c["line"]}"/>')
    y = 130
    for key, val in INFO:
        a(f'<text x="{X}" y="{y}" class="k">{escape(key)}</text>')
        a(f'<text x="{VX}" y="{y}">{escape(val)}</text>')
        y += 23
    # GitHub stats
    y += 10
    a(f'<text x="{X}" y="{y}" class="h">GitHub Stats</text>')
    a(f'<line x1="{X+118}" y1="{y-5}" x2="{W-30}" y2="{y-5}" stroke="{c["line"]}"/>')
    y += 26
    stats = [("Repo", data["repos"]), ("Bintang", data["stars"]),
             ("Komit", data["commits"]), ("Pengikut", data["followers"])]
    for i, (k, v) in enumerate(stats):
        col, row = i % 2, i // 2
        sx = X + col * 280
        sy = y + row * 23
        a(f'<text x="{sx}" y="{sy}" class="k">{k}</text>')
        a(f'<text x="{sx+100}" y="{sy}">{idn(v)}</text>')
    # prompt
    a(f'<text x="{X}" y="372"><tspan class="k">~ $</tspan> {escape(PROMPT)}'
      f'<tspan class="cur" style="fill:{c["orange"]}"> █</tspan></text>')

    # heatmap
    weeks = data["weeks"]
    mx = max([n for w in weeks for _, n, _ in w] + [1])
    a(f'<line x1="30" y1="398" x2="{W-30}" y2="398" stroke="{c["line"]}"/>')
    a(f'<text x="30" y="428" class="h">{idn(data["total"])} kontribusi dalam setahun terakhir'
      + (' <tspan class="s">(data contoh)</tspan>' if data["sample"] else '') + '</text>')
    cell, gap = 13, 3
    step = cell + gap
    gx, gy = 30, 466
    ncols = len(weeks)
    # label bulan
    last = -1
    for i, wk in enumerate(weeks):
        m = int(wk[0][0][5:7]) - 1
        if m != last and i < ncols - 2:
            a(f'<text x="{gx+i*step}" y="{gy-10}" class="s">{MONTHS[m]}</text>')
            last = m
    opac = {1: .3, 2: .55, 3: .8, 4: 1}
    for i, wk in enumerate(weeks):
        for (_, n, wd) in wk:
            lv = level(n, mx)
            x, yy = gx + i * step, gy + wd * step
            delay = f"animation-delay:{i*0.015:.2f}s"
            if lv == 0:
                a(f'<rect class="cell" style="{delay}" x="{x}" y="{yy}" width="{cell}" height="{cell}" rx="3" fill="{c["cell0"]}"/>')
            else:
                a(f'<rect class="cell" style="{delay}" x="{x}" y="{yy}" width="{cell}" height="{cell}" rx="3" fill="{c["orange"]}" fill-opacity="{opac[lv]}"/>')
    # legenda
    ly = gy + 7 * step + 12
    a(f'<text x="30" y="{ly+10}" class="s">github.com/{USERNAME}</text>')
    lx = W - 30 - (5 * step) - 108
    a(f'<text x="{lx}" y="{ly+10}" class="s">Sedikit</text>')
    for i in range(5):
        fill = c["cell0"] if i == 0 else c["orange"]
        fo = "" if i == 0 else f' fill-opacity="{opac[i]}"'
        a(f'<rect x="{lx+56+i*step}" y="{ly}" width="{cell}" height="{cell}" rx="3" fill="{fill}"{fo}/>')
    a(f'<text x="{lx+56+5*step+4}" y="{ly+10}" class="s">Banyak</text>')
    a("</svg>")
    return "\n".join(o)


CARD_R = 14


def card_path(w, h, r=CARD_R):
    """Bentuk kartu: sudut atas membulat, sudut bawah rata (karena tombol menempel di bawahnya)."""
    return f"M0 {r}A{r} {r} 0 0 1 {r} 0H{w-r}A{r} {r} 0 0 1 {w} {r}V{h}H0Z"


# Baris aksi yang menempel di bawah kartu: (nama file, teks, sisi, latar, teks, hijau?)
BARS = [
    ("bar-website.svg", "PAWANG.DEV", "left", "#FF8A3D", "#14213D", False),
    ("bar-konsultasi.svg", "KONSULTASI GRATIS", "right", "#A7C4A0", "#14213D", False),
    ("bar-website-green.svg", "PAWANG.DEV", "left", "#4dff7c", "#040905", True),
    ("bar-konsultasi-green.svg", "KONSULTASI GRATIS", "right", "#22a24c", "#040905", True),
]


def bar_svg(label, side, bg, fg, green=False):
    """Separuh baris aksi (480x56). Dua separuh ditaruh bersebelahan di README,
    masing-masing dibungkus <a> sehingga tiap tombol punya link sendiri."""
    w, h, r = 480, 56, CARD_R
    d = (f"M0 0H{w}V{h}H{r}A{r} {r} 0 0 1 0 {h-r}Z" if side == "left"
         else f"M0 0H{w}V{h-r}A{r} {r} 0 0 1 {w-r} {h}H0Z")
    tw = len(label) * 9.9
    x0 = (w - (tw + 8 + 11)) / 2
    divider_x = w - 1 if side == "left" else 0
    extra_defs = extra_overlay = ""
    if green:
        extra_defs = ('<pattern id="sc" width="4" height="4" patternUnits="userSpaceOnUse">'
                      '<rect width="4" height="1.4" fill="#000" opacity=".22"/></pattern>')
        extra_overlay = f'<path d="{d}" fill="url(#sc)"/>'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>'
        f'<defs>{extra_defs}</defs>'
        f'<path d="{d}" fill="{bg}"/>{extra_overlay}'
        f'<rect x="{divider_x}" y="0" width="1" height="{h}" fill="#000" opacity=".22"/>'
        f'<text x="{x0:.1f}" y="33" font-family="{MONO}" font-size="14" font-weight="700" '
        f'letter-spacing="1.5" fill="{fg}">{escape(label)}</text>'
        f'<g transform="translate({x0 + tw + 8:.1f} 23)">'
        f'<path d="M0 11L10 1M2 1H10V9" fill="none" stroke="{fg}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<animateTransform attributeName="transform" type="translate" additive="sum" '
        f'values="0 0;2 -2;0 0" dur="1.8s" repeatCount="indefinite"/></g>'
        f'</svg>')


def main():
    data = get_data()
    (ROOT / "assets" / "svg").mkdir(parents=True, exist_ok=True)
    for name, label, side, bg, fg, green in BARS:
        (ROOT / "assets" / "svg" / name).write_text(bar_svg(label, side, bg, fg, green), encoding="utf-8")
    for old in ("btn-website.svg", "btn-konsultasi.svg"):   # sisa versi lama
        (ROOT / "assets" / "svg" / old).unlink(missing_ok=True)
    mascot, logo = b64("maskot-dev.png"), b64("logo-pawang.png")
    for theme in ("dark", "light"):
        out = ROOT / "assets" / "svg" / f"{theme}_mode.svg"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(theme, data, mascot, logo), encoding="utf-8")
        print("tulis", out.relative_to(ROOT), f"({out.stat().st_size // 1024} KB)",
              "[data contoh]" if data["sample"] else "[data live]")


if __name__ == "__main__":
    main()
