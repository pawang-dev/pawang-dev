"""Data GitHub: statistik, kalender kontribusi, repo (pin/populer/manual), dan aktivitas publik.

Aturan keselamatan data (supaya angka palsu tidak pernah terbit di profil):
  - Berhasil ambil data live  -> disimpan ke assets/cache/github.json
  - Gagal/tanpa token         -> pakai data tersimpan terakhir (dengan peringatan)
  - Di GitHub Actions tanpa data tersimpan -> build berhenti, TIDAK memakai data contoh
  - Data contoh hanya untuk --sample dan pemakaian lokal tanpa data tersimpan
"""
import datetime as dt
import json
import os
import random
import urllib.request

from common import CACHE, IN_ACTIONS, REPORT, rel

SAMPLE_TOTAL = 1804
CACHE_FILE = CACHE / "github.json"
API = "https://api.github.com"
REPO_FIELDS = "name nameWithOwner description url stargazerCount forkCount primaryLanguage{name color}"
QUERY = """
query($login:String!){
  user(login:$login){
    followers{totalCount}
    repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:100){
      totalCount
      nodes{stargazerCount}
    }
    pinnedItems(first:6, types:REPOSITORY){ nodes{ ... on Repository{ %(f)s } } }
    popular: repositories(ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false, first:6,
                          orderBy:{field:STARGAZERS, direction:DESC}){ nodes{ %(f)s } }
    contributionsCollection{
      totalCommitContributions
      contributionCalendar{
        totalContributions
        weeks{contributionDays{contributionCount date weekday}}
      }
    }
  }
}
""" % {"f": REPO_FIELDS}
REPO_QUERY = "query($o:String!,$n:String!){repository(owner:$o,name:$n){ %s }}" % REPO_FIELDS


def _post(token, query, variables):
    req = urllib.request.Request(
        f"{API}/graphql", data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "pawang-profile-builder"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _repo(n):
    if not n:
        return None
    lang = n.get("primaryLanguage") or {}
    return {"name": n["name"], "full": n["nameWithOwner"], "description": n.get("description") or "", "url": n["url"],
            "stars": n["stargazerCount"], "forks": n["forkCount"], "lang": lang.get("name") or "", "color": lang.get("color") or ""}


def normalize_events(events, limit=30):
    """Ringkas event publik GitHub menjadi baris aktivitas. Event privat tidak pernah ada di API publik."""
    out = []
    for e in events:
        t, repo, pl = e.get("type"), (e.get("repo") or {}).get("name", ""), e.get("payload") or {}
        date = (e.get("created_at") or "")[:10]
        if not repo or not date:
            continue
        base = {"repo": repo, "date": date, "url": f"https://github.com/{repo}"}
        if t == "PushEvent":
            n = pl.get("distinct_size") or pl.get("size") or len(pl.get("commits") or []) or 1
            prev = out[-1] if out else None
            if prev and prev["k"] == "commit" and prev["repo"] == repo and prev["date"] == date:
                prev["n"] += n
            else:
                out.append({**base, "k": "commit", "n": n})
        elif t == "PullRequestEvent":
            pr, action = pl.get("pull_request") or {}, pl.get("action")
            kind = ("pr_merge" if action == "closed" and pr.get("merged") else "pr_close" if action == "closed"
                    else "pr_open" if action == "opened" else None)
            if kind:
                out.append({**base, "k": kind, "n": pl.get("number") or pr.get("number") or 0, "url": pr.get("html_url") or base["url"]})
        elif t == "CreateEvent" and pl.get("ref_type") == "repository":
            out.append({**base, "k": "repo", "n": 0})
        elif t == "IssuesEvent" and pl.get("action") == "opened":
            issue = pl.get("issue") or {}
            out.append({**base, "k": "issue", "n": issue.get("number", 0), "url": issue.get("html_url") or base["url"]})
        elif t == "ReleaseEvent" and pl.get("action") == "published":
            r = pl.get("release") or {}
            out.append({**base, "k": "release", "n": 0, "tag": r.get("tag_name") or "", "url": r.get("html_url") or base["url"]})
        elif t == "ForkEvent":
            out.append({**base, "k": "fork", "n": 0})
    return out[:limit]


def fetch_live(token, user, manual=()):
    payload = _post(token, QUERY, {"login": user})
    if payload.get("errors") or not (payload.get("data") or {}).get("user"):
        raise RuntimeError((payload.get("errors") or [{"message": f"user '{user}' tidak ditemukan"}])[0]["message"])
    u = payload["data"]["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    repos = {}
    for full in manual:
        owner, _, name = full.partition("/")
        try:
            r = (_post(token, REPO_QUERY, {"o": owner, "n": name}).get("data") or {}).get("repository")
        except Exception:  # noqa: BLE001
            r = None
        if r:
            repos[full.lower()] = _repo(r)
    ev_req = urllib.request.Request(f"{API}/users/{user}/events/public?per_page=100",
                                    headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                                             "User-Agent": "pawang-profile-builder"})
    try:
        with urllib.request.urlopen(ev_req, timeout=30) as r:
            events = normalize_events(json.load(r))
    except Exception:  # noqa: BLE001
        events = []
    return dict(
        repos=u["repositories"]["totalCount"], stars=sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
        commits=u["contributionsCollection"]["totalCommitContributions"], followers=u["followers"]["totalCount"],
        total=cal["totalContributions"],
        weeks=[[(d["date"], d["contributionCount"], d["weekday"]) for d in w["contributionDays"]] for w in cal["weeks"]],
        pinned=[_repo(n) for n in u["pinnedItems"]["nodes"] if n], popular=[_repo(n) for n in u["popular"]["nodes"] if n],
        repo_map=repos, events=events, sample=False)


def sample_data(user="user", manual=(), S=None):
    """Data contoh deterministik untuk pratinjau tanpa token dan tanpa jaringan."""
    rnd = random.Random(42)
    today = dt.date.today()
    start = today - dt.timedelta(days=(today.weekday() + 1) % 7 + 52 * 7)
    weeks, total, d = [], 0, start
    while d <= today:
        week = []
        for wd in range(7):
            day = d + dt.timedelta(days=wd)
            if day > today:
                break
            n = rnd.choice([1, 2, 3, 5, 8, 12]) if rnd.random() < (0.25 if wd in (0, 6) else 0.7) else 0
            total += n
            week.append((day.isoformat(), n, wd))
        weeks.append(week)
        d += dt.timedelta(days=7)
    days = [(i, j) for i, w in enumerate(weeks) for j in range(len(w))]
    factor = SAMPLE_TOTAL / max(total, 1)
    cnt = {k: round(weeks[k[0]][k[1]][1] * factor) for k in days}
    diff = SAMPLE_TOTAL - sum(cnt.values())
    while diff != 0:
        k = rnd.choice(days)
        if cnt[k] > 0:
            cnt[k] += 1 if diff > 0 else -1
            diff += -1 if diff > 0 else 1
    weeks = [[(d_, cnt[(i, j)], wd) for j, (d_, _, wd) in enumerate(w)] for i, w in enumerate(weeks)]
    desc = (S or {}).get("sample_repo_desc", "Sample repository.")
    fulls = list(manual) or [f"{user}/{n}" for n in (user, "sheet-kit", "wa-notifier", "seo-audit")]
    langs = [("Python", "#3572A5"), ("JavaScript", "#f1e05a"), ("Python", "#3572A5"), ("TypeScript", "#3178c6")]
    sample_repos = [{"name": full.split("/")[-1], "full": full, "description": desc, "url": f"https://github.com/{full}",
                     "stars": 12 - i * 3, "forks": max(0, 2 - i), "lang": langs[i % 4][0], "color": langs[i % 4][1]}
                    for i, full in enumerate(fulls[:6])]
    iso = lambda back: (today - dt.timedelta(days=back)).isoformat()  # noqa: E731
    first, last = fulls[0], fulls[min(len(fulls), 6) - 1]
    events = [
        {"k": "commit", "n": 3, "repo": first, "date": iso(0), "url": f"https://github.com/{first}"},
        {"k": "pr_open", "n": 12, "repo": first, "date": iso(1), "url": f"https://github.com/{first}/pull/12"},
        {"k": "repo", "n": 0, "repo": last, "date": iso(3), "url": f"https://github.com/{last}"},
        {"k": "commit", "n": 5, "repo": last, "date": iso(3), "url": f"https://github.com/{last}"},
        {"k": "pr_merge", "n": 11, "repo": first, "date": iso(5), "url": f"https://github.com/{first}/pull/11"}]
    return dict(repos=0, stars=0, commits=0, followers=0, total=SAMPLE_TOTAL, weeks=weeks,
                pinned=sample_repos[:4], popular=sample_repos[:4], repo_map={r["full"].lower(): r for r in sample_repos},
                events=events, sample=True)


def save_cache(data, user, path=CACHE_FILE):
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = dict(data, fetched_at=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), user=user)
    path.write_text(json.dumps(blob, separators=(",", ":")), encoding="utf-8")


def load_cache(user, path=CACHE_FILE):
    try:
        blob = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if blob.get("user") != user or blob.get("sample"):
        return None
    return blob


def get_data(user, manual=(), S=None, force_sample=False, dry=False, token=None, fetch=None,
             cache_file=CACHE_FILE, in_actions=None):
    """-> dict data, atau None kalau build harus berhenti (kesalahan sudah dicatat di REPORT)."""
    if force_sample:
        return sample_data(user, manual, S)
    in_actions = IN_ACTIONS if in_actions is None else in_actions
    token = token if token is not None else (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
    fetch = fetch or fetch_live
    why = "tidak ada token (GH_TOKEN)"
    if token:
        try:
            data = fetch(token, user, tuple(manual))
            if not dry:
                save_cache(data, user, cache_file)
            return data
        except Exception as e:  # noqa: BLE001
            why = f"gagal mengambil data live ({e})"
    cached = load_cache(user, cache_file)
    if cached:
        REPORT.warn("data GitHub", f"{why}; memakai data tersimpan dari {cached.get('fetched_at', '?')}")
        return cached
    if in_actions:
        REPORT.error("data GitHub", f"{why} dan belum ada data tersimpan ({rel(cache_file)}). Build dihentikan supaya data contoh "
                                    "tidak diterbitkan. Cek token dan log, lalu jalankan ulang workflow")
        return None
    REPORT.warn("data GitHub", f"{why}; memakai data contoh (hanya untuk pratinjau lokal)")
    return sample_data(user, manual, S)
