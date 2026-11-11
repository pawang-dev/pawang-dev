"""Data GitHub: statistik dan kontribusi (live lewat GraphQL, atau data contoh)."""
import datetime as dt
import json
import os
import random
import urllib.request

from common import REPORT

SAMPLE_TOTAL = 1804
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


def fetch_live(token, user):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "pawang-profile-builder"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors") or not (payload.get("data") or {}).get("user"):
        raise RuntimeError((payload.get("errors") or [{"message": f"user '{user}' tidak ditemukan"}])[0]["message"])
    u = payload["data"]["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    return dict(
        repos=u["repositories"]["totalCount"],
        stars=sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
        commits=u["contributionsCollection"]["totalCommitContributions"],
        followers=u["followers"]["totalCount"],
        total=cal["totalContributions"],
        weeks=[[(d["date"], d["contributionCount"], d["weekday"]) for d in w["contributionDays"]] for w in cal["weeks"]],
        sample=False)


def sample_data():
    """Data contoh deterministik untuk pratinjau tanpa token."""
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
            busy = 0.25 if wd in (0, 6) else 0.7
            n = rnd.choice([1, 2, 3, 5, 8, 12]) if rnd.random() < busy else 0
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
    weeks = [[(d, cnt[(i, j)], wd) for j, (d, _, wd) in enumerate(w)] for i, w in enumerate(weeks)]
    return dict(repos=0, stars=0, commits=0, followers=0, total=SAMPLE_TOTAL, weeks=weeks, sample=True)


def get_data(user, force_sample=False):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if force_sample:
        return sample_data()
    if not token:
        REPORT.warn("data GitHub", "tidak ada token (GH_TOKEN), memakai data contoh")
        return sample_data()
    try:
        return fetch_live(token, user)
    except Exception as e:  # noqa: BLE001
        REPORT.warn("data GitHub", f"gagal mengambil data live ({e}), memakai data contoh")
        return sample_data()
