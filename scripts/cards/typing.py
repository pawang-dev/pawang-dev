"""Terminal yang mengetik perintah, langkah, dan statistik (animasi SMIL; teks tetap terbaca tanpa animasi)."""
from common import ORANGE, SAGE, NAVY, card_path, esc, idn
from cards._kit import T, logo_img, mascot_img, open_svg, sparkle

NAME = "typing"
THEMED = True
W = 960
CW = 8.4          # lebar karakter monospace perkiraan (font 14px)
TOTAL = 19.0      # durasi satu putaran animasi (detik)


def type_clip(cid, x, y, h, n, start, step):
    full = round(n * CW + 40, 1)
    times, vals = [0.0], [0]
    for k in range(1, n + 1):
        times.append(start + (k - 1) * step)
        vals.append(round(k * CW, 1))
    times.append(start + n * step)
    vals.append(full)
    kt = ";".join(f"{min(t / TOTAL, 1):.4f}" for t in times)
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{full}" height="{h}">'
            f'<animate attributeName="width" values="{";".join(str(v) for v in vals)}" keyTimes="{kt}" calcMode="discrete" '
            f'dur="{TOTAL}s" repeatCount="indefinite"/></rect></clipPath>'), start + n * step


def render(theme, ctx, attached=True):
    c, p, S, data = T(theme), ctx.p, ctx.S, ctx.data
    P, OK = c["orange_txt"], c["sage"]
    ty = p["typing"]
    pad = lambda k: k.ljust(12)  # noqa: E731
    lines = [([("~ $ ", P), (ty["command"], c["text"])], .05, .5)]
    lines += [([("[ok] ", OK), (s, c["text"])], .028, .35) for s in ty["steps"]]
    lines.append(None)
    lines += [
        ([("~ $ ", P), (ty["stats_command"], c["text"])], .06, .6),
        ([(pad(S["typing_contrib"]), c["muted"]), (f'{idn(data["total"])} {S["typing_suffix"]}', c["text"])], .025, .4),
        ([(pad(S["typing_repo"]), c["muted"]), (idn(data["repos"]), c["text"])], .025, .25),
        ([(pad(S["typing_commits"]), c["muted"]), (idn(data["commits"]), c["text"])], .025, .25),
        ([("~ $ ", P)], .08, .6)]
    rows = sum(1 for ln in lines if ln)
    H = max(372, 92 + (rows - 1) * 26 + 16 + 32)
    o = [open_svg(W, H, f'{p["name"]}{p["suffix"]}: {ty["command"]}', c)]
    a = o.append
    a(f'<path d="{card_path(W, H, attached=attached)}" fill="{c["bg"]}"/>')
    a(f'<path transform="translate(.5 .5)" d="{card_path(W-1, H-1, attached=attached)}" fill="none" stroke="{c["line"]}"/>')
    a(f'<path d="M0 14a14 14 0 0 1 14-14h{W-28}a14 14 0 0 1 14 14v34H0z" fill="{c["panel"]}"/>')
    a(f'<line x1="0" y1="48" x2="{W}" y2="48" stroke="{c["line"]}"/>')
    for i, col in enumerate((ORANGE, SAGE, c["muted"])):
        a(f'<circle cx="{26+i*20}" cy="24" r="6" fill="{col}"/>')
    a(logo_img(ctx, 100, 11, 28, 27))
    title = f'{p["username"]} — {p["domain"]} — zsh' if p["domain"] else f'{p["username"]} — zsh'
    a(f'<text x="138" y="29" class="m mono" style="font-size:14px">{esc(title)}</text>')
    t, y = 0.4, 92
    defs, texts, end_last, cur = [], [], 0.4, (0, 0)
    for i, ln in enumerate(lines):
        if ln is None:
            y += 16
            continue
        segs, step, gap = ln
        n = sum(len(s) for s, _ in segs)
        t += gap
        clip, t_end = type_clip(f"k{i}", 40, y - 17, 24, n, t, step)
        defs.append(clip)
        tsp = "".join(f'<tspan fill="{col}">{esc(s).replace(" ", chr(160))}</tspan>' for s, col in segs)
        texts.append(f'<text x="40" y="{y}" class="mono" clip-path="url(#k{i})" style="font-size:14px">{tsp}</text>')
        t, end_last, cur = t_end, t_end, (40 + n * CW + 2, y - 14)
        y += 26
    a("<defs>" + "".join(defs) + "</defs>" + "".join(texts))
    times, vals, tt = [0.0, end_last / TOTAL], [0, 1], end_last
    while tt < TOTAL - 0.6:
        tt += 0.5
        times.append(tt / TOTAL)
        vals.append(0 if vals[-1] else 1)
    a(f'<rect x="{cur[0]:.1f}" y="{cur[1]}" width="9" height="18" fill="{ORANGE}" opacity="0">'
      f'<animate attributeName="opacity" values="{";".join(map(str, vals))}" keyTimes="{";".join(f"{x:.4f}" for x in times)}" '
      f'calcMode="discrete" dur="{TOTAL}s" repeatCount="indefinite"/></rect>')
    a(f'<rect x="724" y="76" width="196" height="256" rx="16" fill="{c["spot"]}" stroke="{c["card_line"]}"/>')
    a(mascot_img(ctx, 822, 190, 0.78))
    a(sparkle(890, 104, 8, ORANGE) + sparkle(876, 128, 5, ORANGE, 1.1))
    if p["mascot"]["name"]:
        a(f'<text x="822" y="316" text-anchor="middle" class="b" style="font-size:15px;fill:{NAVY}">{esc(p["mascot"]["name"])}</text>')
    a("</svg>")
    return "".join(o)
