#!/usr/bin/env python3
"""Empat template tambahan, semuanya memakai palet brand Pawang
(Biru Malam, Api Dupa, Krem, Hijau Sage, Putih Tulang), masing-masing versi dark dan light:

  1. hero_*.svg    banner pembuka: headline + Dev di atas pegunungan
  2. brand_*.svg   kartu brand: lima layanan + paket + nilai
  3. sheet_*.svg   "data liar jadi jinak": sel berantakan -> dashboard rapi (data asli)
  4. typing_*.svg  terminal bergaya ketik (data asli)

Semua kartu berbentuk sama dengan kartu lain: sudut bawah rata supaya baris tombol
(bar-website.svg + bar-konsultasi.svg) bisa menempel di bawahnya.
"""
import random
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import MONO, MONTHS, ROOT, THEMES, b64, card_path, get_data, idn  # noqa: E402

SANS = "'Plus Jakarta Sans','Inter','Segoe UI','Helvetica Neue',Arial,sans-serif"
NAVY, ORANGE, CREAM, SAGE, BONE = "#14213D", "#FF8A3D", "#FFF6E9", "#A7C4A0", "#FAFAF7"
W = 960


def T(theme):
    c = dict(THEMES[theme])
    dark = theme == "dark"
    c.update(
        dark=dark,
        panel2="#22345C" if dark else "#FFF0DC",
        spot=CREAM if dark else "#FFFFFF",      # "lampu sorot" di belakang Dev
        on_card=NAVY,                            # teks di atas kartu krem/putih
        orange_txt=ORANGE if dark else "#C85A12",
        sage=SAGE if dark else "#6E9468",
    )
    return c


def open_svg(w, h, label, c, extra_css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(label)}"><style>'
        f"text{{font-family:{SANS};fill:{c['text']}}}"
        f".mono{{font-family:{MONO}}} .m{{fill:{c['muted']}}} .b{{font-weight:700}}"
        f".tw{{animation:tw 2.6s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}"
        "@keyframes tw{0%,100%{opacity:.25;transform:scale(.7)}50%{opacity:1;transform:scale(1.15)}}"
        f"{extra_css}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
        "</style>"
    )


def frame(w, h, c):
    return (f'<path d="{card_path(w, h)}" fill="{c["bg"]}"/>'
            f'<path transform="translate(.5 .5)" d="{card_path(w-1, h-1)}" fill="none" stroke="{c["line"]}"/>')


def sparkle(x, y, s, color, delay=0.0):
    return (f'<path class="tw" style="animation-delay:{delay}s" d="M{x} {y-s}Q{x} {y} {x+s} {y}'
            f'Q{x} {y} {x} {y+s}Q{x} {y} {x-s} {y}Q{x} {y} {x} {y-s}z" fill="{color}"/>')


def spotlight(cx, cy, r, c):
    """Lingkaran terang di belakang Dev (maskot berwarna biru gelap, jadi butuh latar terang)."""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c["spot"]}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r+10}" fill="none" stroke="{ORANGE}" stroke-width="2.5" '
            f'stroke-dasharray="4 10" stroke-linecap="round" opacity=".9">'
            f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" '
            f'to="360 {cx} {cy}" dur="40s" repeatCount="indefinite"/></circle>')


def mascot_img(mascot, cx, cy, scale=1.0):
    w, h = 226 * scale, 257 * scale
    return f'<image x="{cx - w/2:.1f}" y="{cy - h/2:.1f}" width="{w:.1f}" height="{h:.1f}" href="data:image/png;base64,{mascot}"/>'


# =============================================================== 1. HERO
def render_hero(theme, data, mascot, logo):
    c = T(theme)
    H = 330
    o = [open_svg(W, H, "Pawang.dev: Digitalmu liar? Serahkan ke Pawang.", c)]
    a = o.append
    sky2 = "#1B2B4F" if c["dark"] else "#FFEBD2"
    a(f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["bg"]}"/>'
      f'<stop offset="1" stop-color="{sky2}"/></linearGradient></defs>')
    a(f'<path d="{card_path(W, H)}" fill="url(#sky)"/>')
    if c["dark"]:                                     # bintang malam
        rnd = random.Random(7)
        for i in range(26):
            x, y, r = rnd.randint(24, 936), rnd.randint(14, 150), rnd.choice([1, 1, 1.4, 1.8])
            a(f'<circle class="tw" style="animation-delay:{rnd.random()*3:.1f}s" cx="{x}" cy="{y}" r="{r}" fill="{BONE}" opacity=".7"/>')
    # pegunungan
    a(f'<path d="M0 275L110 250L210 268L330 240L430 270L560 235L680 262L800 215L920 250L960 238V{H}H0Z" fill="{SAGE}" opacity="{.22 if c["dark"] else .35}"/>')
    a(f'<path d="M0 300L130 278L250 296L390 266L520 298L660 272L790 296L960 268V{H}H0Z" fill="{SAGE}" opacity="{.38 if c["dark"] else .6}"/>')
    # Dev
    a(spotlight(772, 160, 118, c))
    a(mascot_img(mascot, 772, 160, 0.98))
    a(sparkle(905, 70, 11, ORANGE) + sparkle(640, 60, 8, ORANGE, .8) + sparkle(890, 250, 7, ORANGE, 1.4))
    # teks
    a(f'<image x="48" y="26" width="38" height="36" href="data:image/png;base64,{logo}"/>')
    a(f'<text x="96" y="52" class="b" style="font-size:22px">Pawang<tspan fill="{c["orange_txt"]}">.dev</tspan></text>')
    a(f'<text x="48" y="122" class="b" style="font-size:46px;letter-spacing:-1px">Digitalmu liar?</text>')
    a(f'<text x="48" y="174" class="b" style="font-size:46px;letter-spacing:-1px">Serahkan ke <tspan fill="{c["orange_txt"]}">Pawang.</tspan></text>')
    a(f'<text x="48" y="212" class="m" style="font-size:14.5px">Website, dashboard, dan sistem otomatis yang jinak,</text>')
    a(f'<text x="48" y="233" class="m" style="font-size:14.5px">rapi, dan gampang dipakai. Tanpa istilah ribet.</text>')
    x = 48
    for label in ("Web", "SEO", "Sheet", "Otomasi", "Rawat"):
        w = len(label) * 7.6 + 26
        a(f'<rect x="{x:.0f}" y="252" width="{w:.0f}" height="26" rx="13" fill="{c["panel"]}" stroke="{c["line"]}"/>')
        a(f'<text x="{x + w/2:.0f}" y="269" text-anchor="middle" style="font-size:12.5px;font-weight:600">{label}</text>')
        x += w + 8
    a("</svg>")
    return "".join(o)


# ============================================================ 2. BRAND CARD
def icon(kind, x, y, c):
    col = c["orange_txt"]
    s = f'fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    box = f'<rect x="{x}" y="{y}" width="44" height="44" rx="12" fill="{ORANGE}" opacity=".16"/>'
    g = {
        "web": f'<rect x="{x+10}" y="{y+12}" width="24" height="20" rx="3" {s}/><path d="M{x+10} {y+19}H{x+34}" {s}/>',
        "seo": f'<circle cx="{x+20}" cy="{y+20}" r="8" {s}/><path d="M{x+26} {y+26}L{x+33} {y+33}" {s}/>',
        "sheet": (f'<rect x="{x+11}" y="{y+11}" width="22" height="22" rx="3" {s}/>'
                  f'<path d="M{x+18.3} {y+11}V{y+33}M{x+25.7} {y+11}V{y+33}M{x+11} {y+18.3}H{x+33}M{x+11} {y+25.7}H{x+33}" {s}/>'),
        "otomasi": (f'<circle cx="{x+22}" cy="{y+22}" r="5" {s}/>'
                    + "".join(f'<path d="M{x+22+9*dx:.1f} {y+22+9*dy:.1f}L{x+22+12.5*dx:.1f} {y+22+12.5*dy:.1f}" {s}/>'
                              for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, .7), (.7, -.7), (-.7, -.7)))),
        "rawat": (f'<path d="M{x+22} {y+10}L{x+33} {y+14}V{y+23}C{x+33} {y+29} {x+28} {y+33} {x+22} {y+35}'
                  f'C{x+16} {y+33} {x+11} {y+29} {x+11} {y+23}V{y+14}Z" {s}/><path d="M{x+17} {y+23}L{x+21} {y+27}L{x+28} {y+19}" {s}/>'),
    }[kind]
    return box + g


SERVICES = [
    ("web", "Pawang Web", ("Website yang jinak: cepat,", "rapi, mudah diurus."), "Company profile & landing page"),
    ("seo", "Pawang SEO", ("Biar usahamu ditemukan,", "bukan sekadar tampil."), "Riset kata kunci & laporan bulanan"),
    ("sheet", "Pawang Sheet", ("Angka berantakan", "jadi jelas."), "Dashboard & laporan otomatis"),
    ("otomasi", "Pawang Otomasi", ("Kerja berulang", "dikerjakan sendiri."), "Notifikasi WhatsApp & sinkron data"),
    ("rawat", "Pawang Rawat", ("Setelah proyek selesai,", "tetap ada yang jaga."), "Perawatan & update bulanan"),
]


def render_brand(theme, data, mascot, logo):
    c = T(theme)
    H = 568
    o = [open_svg(W, H, "Kartu brand Pawang.dev: layanan, paket, dan nilai", c)]
    a = o.append
    a(frame(W, H, c))
    # header
    a(f'<image x="32" y="20" width="46" height="44" href="data:image/png;base64,{logo}"/>')
    a(f'<text x="90" y="50" class="b" style="font-size:26px">Pawang<tspan fill="{c["orange_txt"]}">.dev</tspan></text>')
    a(f'<text x="928" y="48" text-anchor="end" class="b" style="font-size:15px">Digitalmu liar? <tspan fill="{c["orange_txt"]}">Serahkan ke Pawang.</tspan></text>')
    a(f'<line x1="32" y1="76" x2="928" y2="76" stroke="{c["line"]}"/>')
    # kartu Dev
    a(f'<rect x="32" y="92" width="240" height="446" rx="16" fill="{c["spot"]}" stroke="{c["card_line"]}"/>')
    a(mascot_img(mascot, 152, 228))
    a(sparkle(236, 120, 9, ORANGE) + sparkle(222, 148, 6, ORANGE, 1))
    a(f'<text x="152" y="378" text-anchor="middle" class="b" style="font-size:20px;fill:{NAVY}">Dev</text>')
    a(f'<text x="152" y="398" text-anchor="middle" style="font-size:12px;fill:#5B6784">Maskot resmi Pawang</text>')
    a(f'<line x1="52" y1="414" x2="252" y2="414" stroke="#E6D6BB"/>')
    a(f'<text x="52" y="436" class="b" style="font-size:11px;letter-spacing:1.5px;fill:#5B6784">NILAI BRAND</text>')
    for i, (k, d) in enumerate((("Tenang", "tidak panik"), ("Paham", "mengerti dulu"), ("Jinak", "mudah dipakai"))):
        yy = 462 + i * 24
        a(f'<circle cx="58" cy="{yy-4}" r="5" fill="{SAGE}"/>')
        a(f'<text x="72" y="{yy}" class="b" style="font-size:14px;fill:{NAVY}">{k}</text>')
        a(f'<text x="136" y="{yy}" style="font-size:12px;fill:#5B6784">{d}</text>')
    # kartu layanan
    for i, (kind, title, promise, isi) in enumerate(SERVICES):
        x, y = 296 + (i % 2) * 324, 92 + (i // 2) * 154
        a(f'<rect x="{x}" y="{y}" width="308" height="138" rx="14" fill="{c["panel"]}" stroke="{c["line"]}"/>')
        a(icon(kind, x + 16, y + 16, c))
        a(f'<text x="{x+72}" y="{y+44}" class="b" style="font-size:17px">{title}</text>')
        for j, line in enumerate(promise):
            a(f'<text x="{x+18}" y="{y+84+j*20}" class="b" style="font-size:13.5px;fill:{c["orange_txt"]}">{escape(line)}</text>')
        a(f'<text x="{x+18}" y="{y+126}" class="m" style="font-size:12px">{escape(isi)}</text>')
    # kartu paket
    x, y = 296 + 324, 92 + 2 * 154
    a(f'<rect x="{x}" y="{y}" width="308" height="138" rx="14" fill="{c["panel"]}" stroke="{c["line"]}"/>')
    a(f'<text x="{x+18}" y="{y+34}" class="b" style="font-size:17px">Paket</text>')
    chips = (("Jinak", SAGE, NAVY, None, "Dasar"), ("Piawai", ORANGE, NAVY, None, "Menengah"),
             ("Sakti", "none", c["text"], c["text"], "Premium"))
    for k, (lab, fill, tc, stroke, desc) in enumerate(chips):
        cx = x + 18 + k * 96
        st = f' stroke="{stroke}" stroke-width="1.5"' if stroke else ""
        a(f'<rect x="{cx}" y="{y+50}" width="86" height="30" rx="15" fill="{fill}"{st}/>')
        a(f'<text x="{cx+43}" y="{y+70}" text-anchor="middle" class="b" style="font-size:13px;fill:{tc}">{lab}</text>')
        a(f'<text x="{cx+43}" y="{y+100}" text-anchor="middle" class="m" style="font-size:12px">{desc}</text>')
    a(f'<text x="{x+18}" y="{y+126}" class="m" style="font-size:12px">Tiap layanan punya tiga paket</text>')
    a("</svg>")
    return "".join(o)


# ============================================================ 3. DATA LIAR -> JINAK
def monthly(data):
    sums = {}
    for wk in data["weeks"]:
        for d, n, _ in wk:
            sums[d[:7]] = sums.get(d[:7], 0) + n
    keys = sorted(sums)[-12:]
    return [(int(k[5:7]) - 1, sums[k]) for k in keys]


def render_sheet(theme, data, mascot, logo):
    c = T(theme)
    H = 420
    css = (".wob{animation:wob 3.2s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}"
           "@keyframes wob{0%{transform:translate(0,0) rotate(-3deg)}100%{transform:translate(3px,-4px) rotate(3deg)}}"
           ".flow{stroke-dasharray:6 8;animation:flow 1.1s linear infinite}"
           "@keyframes flow{to{stroke-dashoffset:-28}}"
           ".bar{transform-box:fill-box;transform-origin:50% 100%;animation:grow 1s cubic-bezier(.2,.8,.2,1) both}"
           "@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}")
    o = [open_svg(W, H, "Data liar jadi jinak: sel berantakan dirapikan menjadi dashboard", c, css)]
    a = o.append
    a(frame(W, H, c))
    # label
    a(f'<rect x="32" y="22" width="112" height="28" rx="14" fill="{ORANGE}" opacity=".18"/>')
    a(f'<text x="88" y="41" text-anchor="middle" class="b" style="font-size:12.5px;letter-spacing:1px;fill:{c["orange_txt"]}">DATA LIAR</text>')
    a(f'<rect x="608" y="22" width="122" height="28" rx="14" fill="{SAGE}" opacity="{.28 if c["dark"] else .4}"/>')
    a(f'<text x="669" y="41" text-anchor="middle" class="b" style="font-size:12.5px;letter-spacing:1px;fill:{c["sage"]}">JADI JINAK</text>')
    # sel berantakan
    rnd = random.Random(11)
    vals = ["#REF!", "???", "12/3", "Rp ?", "N/A", "0,0", "dup?", "KOSONG", "3x lipat", "revisi_final2", "xlsx (1)", "#N/A"]
    for i, v in enumerate(vals):
        col, row = i % 3, i // 3
        x, y = 36 + col * 104 + rnd.randint(-5, 5), 86 + row * 64 + rnd.randint(-6, 6)
        rot = rnd.randint(-13, 13)
        bad = v.startswith("#") or v in ("???", "dup?")
        a(f'<g transform="translate({x} {y}) rotate({rot})"><g class="wob" style="animation-delay:{rnd.random()*2:.1f}s">'
          f'<rect width="96" height="32" rx="6" fill="{c["panel"]}" stroke="{ORANGE if bad else c["line"]}" stroke-width="{1.6 if bad else 1}"/>'
          f'<text x="48" y="21" text-anchor="middle" class="mono" style="font-size:11px;fill:{c["orange_txt"] if bad else c["text"]}">{escape(v)}</text></g></g>')
    # tengah: Dev + panah
    a(f'<path class="flow" d="M352 200H394" fill="none" stroke="{ORANGE}" stroke-width="3" stroke-linecap="round"/>')
    a(f'<path d="M392 192L402 200L392 208" fill="none" stroke="{ORANGE}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    a(spotlight(480, 196, 74, c))
    a(mascot_img(mascot, 480, 196, 0.6))
    a(f'<text x="480" y="298" text-anchor="middle" class="b" style="font-size:14px">Dev</text>')
    a(f'<path class="flow" d="M566 200H600" fill="none" stroke="{SAGE}" stroke-width="3" stroke-linecap="round"/>')
    a(f'<path d="M598 192L608 200L598 208" fill="none" stroke="{SAGE}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    # dashboard
    dx, dy, dw, dh = 616, 70, 312, 284
    a(f'<rect x="{dx}" y="{dy}" width="{dw}" height="{dh}" rx="14" fill="{c["panel"]}" stroke="{c["line"]}"/>')
    for i, col in enumerate((ORANGE, SAGE, c["muted"])):
        a(f'<circle cx="{dx+20+i*16}" cy="{dy+20}" r="4.5" fill="{col}"/>')
    a(f'<text x="{dx+dw-16}" y="{dy+24}" text-anchor="end" class="m mono" style="font-size:11px">dashboard.pawang</text>')
    kp = (("Kontribusi", idn(data["total"])), ("Repo", idn(data["repos"])), ("Komit", idn(data["commits"])))
    for i, (k, v) in enumerate(kp):
        x = dx + 16 + i * 98
        a(f'<rect x="{x}" y="{dy+40}" width="90" height="56" rx="10" fill="{c["panel2"]}"/>')
        a(f'<text x="{x+12}" y="{dy+60}" class="m" style="font-size:11px">{k}</text>')
        a(f'<text x="{x+12}" y="{dy+84}" class="b" style="font-size:20px">{v}</text>')
    series = monthly(data)
    top = max([n for _, n in series] + [1])
    base_y, max_h = dy + dh - 34, 112
    for i, (m, n) in enumerate(series):
        h = max(4, n / top * max_h)
        x = dx + 16 + i * 24.5
        last = i == len(series) - 1
        a(f'<rect class="bar" style="animation-delay:{i*0.07:.2f}s" x="{x:.1f}" y="{base_y-h:.1f}" width="17" height="{h:.1f}" rx="4" '
          f'fill="{ORANGE if last else SAGE}"/>')
        a(f'<text x="{x+8.5:.1f}" y="{base_y+16}" text-anchor="middle" class="m" style="font-size:10px">{MONTHS[m][0]}</text>')
    a(f'<text x="480" y="394" text-anchor="middle" class="b" style="font-size:15px">Data tercecer di lima tempat? '
      f'<tspan fill="{c["orange_txt"]}">Kami kumpulkan jadi satu dashboard.</tspan></text>')
    a("</svg>")
    return "".join(o)


# ============================================================ 4. TERMINAL KETIK
def type_clip(cid, x, y, h, n, start, step, total, cw=8.4):
    times, vals = [0.0], [0]
    for k in range(1, n + 1):
        times.append(start + (k - 1) * step)
        vals.append(round(k * cw, 1))
    times.append(start + n * step)
    vals.append(round(n * cw + 40, 1))
    kt = ";".join(f"{min(t / total, 1):.4f}" for t in times)
    vv = ";".join(str(v) for v in vals)
    full = round(n * cw + 40, 1)   # lebar dasar = penuh, supaya teks tetap terbaca kalau animasi tidak jalan
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{full}" height="{h}">'
            f'<animate attributeName="width" values="{vv}" keyTimes="{kt}" calcMode="discrete" '
            f'dur="{total}s" repeatCount="indefinite"/></rect></clipPath>'), start + n * step


def render_typing(theme, data, mascot, logo):
    c = T(theme)
    H = 400
    o = [open_svg(W, H, "Terminal Pawang: perintah pawang --jinakkan DEV diketik dan dijalankan", c)]
    a = o.append
    a(frame(W, H, c))
    a(f'<path d="M0 14a14 14 0 0 1 14-14h{W-28}a14 14 0 0 1 14 14v34H0z" fill="{c["panel"]}"/>')
    a(f'<line x1="0" y1="48" x2="{W}" y2="48" stroke="{c["line"]}"/>')
    for i, col in enumerate((ORANGE, SAGE, c["muted"])):
        a(f'<circle cx="{26+i*20}" cy="24" r="6" fill="{col}"/>')
    a(f'<image x="100" y="11" width="28" height="27" href="data:image/png;base64,{logo}"/>')
    a(f'<text x="138" y="29" class="m mono" style="font-size:14px">pawang-dev — pawang.dev — zsh</text>')

    P, OK = c["orange_txt"], c["sage"]
    lines = [  # (segmen [(teks, warna)], kecepatan per karakter, jeda sebelum baris)
        ([("~ $ ", P), ("pawang --jinakkan DEV (digital, efisien, valid)", c["text"])], .05, .5),
        ([("[ok] ", OK), ("memahami dulu masalahnya", c["text"])], .028, .45),
        ([("[ok] ", OK), ("merapikan data yang tercecer", c["text"])], .028, .3),
        ([("[ok] ", OK), ("mengotomasi kerja berulang", c["text"])], .028, .3),
        ([("[ok] ", OK), ("menjinakkan digitalmu", c["text"])], .028, .3),
        None,
        ([("~ $ ", P), ("pawang stats", c["text"])], .06, .6),
        ([("kontribusi  ", c["muted"]), (f"{idn(data['total'])} setahun terakhir", c["text"])], .025, .4),
        ([("repo        ", c["muted"]), (idn(data["repos"]), c["text"])], .025, .25),
        ([("komit       ", c["muted"]), (idn(data["commits"]), c["text"])], .025, .25),
        ([("~ $ ", P)], .08, .6),
    ]
    TOTAL = 19.0
    t = 0.4
    defs, texts = [], []
    y = 92
    end_last = t
    for i, ln in enumerate(lines):
        if ln is None:
            y += 16
            continue
        segs, step, gap = ln
        n = sum(len(s) for s, _ in segs)
        t += gap
        clip, t_end = type_clip(f"k{i}", 40, y - 17, 24, n, t, step, TOTAL)
        defs.append(clip)
        tsp = "".join(f'<tspan fill="{col}">{escape(s).replace(" ", chr(160))}</tspan>' for s, col in segs)
        texts.append(f'<text x="40" y="{y}" class="mono" clip-path="url(#k{i})" style="font-size:14px">{tsp}</text>')
        t, end_last = t_end, t_end
        cur_x, cur_y = 40 + n * 8.4 + 2, y - 14
        y += 26
    a("<defs>" + "".join(defs) + "</defs>")
    a("".join(texts))
    # kursor berkedip setelah baris terakhir selesai diketik
    times, vals, tt, on = [0.0], [0], end_last, 1
    times.append(tt / TOTAL); vals.append(1)
    while tt < TOTAL - 0.6:
        tt += 0.5
        times.append(tt / TOTAL); vals.append(0 if vals[-1] else 1)
    a(f'<rect x="{cur_x:.1f}" y="{cur_y}" width="9" height="18" fill="{ORANGE}" opacity="0">'
      f'<animate attributeName="opacity" values="{";".join(map(str, vals))}" '
      f'keyTimes="{";".join(f"{x:.4f}" for x in times)}" calcMode="discrete" dur="{TOTAL}s" repeatCount="indefinite"/></rect>')
    # kartu Dev di kanan
    a(f'<rect x="724" y="76" width="196" height="256" rx="16" fill="{c["spot"]}" stroke="{c["card_line"]}"/>')
    a(mascot_img(mascot, 822, 190, 0.78))
    a(sparkle(890, 104, 8, ORANGE) + sparkle(876, 128, 5, ORANGE, 1.1))
    a(f'<text x="822" y="316" text-anchor="middle" class="b" style="font-size:15px;fill:{NAVY}">Dev</text>')
    a("</svg>")
    return "".join(o)


RENDERERS = {"hero": render_hero, "brand": render_brand, "sheet": render_sheet, "typing": render_typing}


def main():
    data = get_data()
    mascot, logo = b64("maskot-dev.png"), b64("logo-pawang.png")
    out_dir = ROOT / "assets" / "svg"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, fn in RENDERERS.items():
        for theme in ("dark", "light"):
            p = out_dir / f"{name}_{theme}.svg"
            p.write_text(fn(theme, data, mascot, logo), encoding="utf-8")
            print("tulis", p.relative_to(ROOT), f"({p.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
