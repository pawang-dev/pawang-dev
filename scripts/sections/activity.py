"""Aktivitas terbaru: commit, pull request, dan repo baru dari event PUBLIK GitHub (aktivitas privat tidak pernah ikut)."""
import datetime as dt

from common import ORANGE, SAGE, SVG, emit, short_date
from sections._tiles import INK, SUB, T, assemble, header_svg, wrap_tile

OUT = SVG / "activity"
DOT = {"commit": ORANGE, "pr_open": SAGE, "pr_merge": SAGE, "pr_close": SAGE, "repo": "#7C9CE0", "fork": "#7C9CE0",
       "issue": "#E0B34F", "release": "#B48CE0"}
TEXT = {"commit": "act_push", "pr_open": "act_pr_open", "pr_merge": "act_pr_merge", "pr_close": "act_pr_close",
        "repo": "act_repo", "issue": "act_issue", "release": "act_release", "fork": "act_fork"}


def row_svg(ev, S, lang, bl, br, divb):
    w, h = 960, 60
    text = S[TEXT[ev["k"]]].format(n=ev.get("n", 0), tag=ev.get("tag", ""))
    d = dt.date.fromisoformat(ev["date"])
    body = (f'<circle cx="46" cy="30" r="14" fill="{DOT[ev["k"]]}" opacity=".25"/><circle cx="46" cy="30" r="5" fill="{DOT[ev["k"]]}"/>'
            + T(76, 27, text, 14.5, 700, INK) + T(76, 46, ev["repo"], 12, 500, SUB)
            + T(w - 32, 36, short_date(d.day, d.month, S, lang), 12.5, 700, SUB, 'text-anchor="end"'))
    return wrap_tile(w, h, body, f'{text} {ev["repo"]}', divr=False, divb=divb, bl=bl, br=br)


def build(ctx):
    p, S = ctx.p, ctx.S
    cfg = p["activity"]
    events = [e for e in (ctx.data or {}).get("events", []) if e.get("k") in TEXT][: cfg["limit"]]
    if not events:
        return ""
    title = cfg["title"] or S["activity_title"]
    for theme in ("dark", "light"):
        emit(OUT / f"header_{theme}.svg", header_svg(theme, title, cfg["subtitle"], ic="chart"))
    rows = []
    for i, ev in enumerate(events):
        last = i == len(events) - 1
        fname = f"{i:02d}.svg"
        emit(OUT / fname, row_svg(ev, S, p["language"], bl=last, br=last, divb=not last))
        rows.append([(fname, "100%", ev.get("url"), f'{S[TEXT[ev["k"]]].format(n=ev.get("n", 0), tag=ev.get("tag", ""))} {ev["repo"]}')])
    return assemble("activity", "header", title, f'https://github.com/{p["username"]}', rows)
