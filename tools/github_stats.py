"""GitHub's public numbers for the apps: release download counts, stars and open issues.

Used by tools/download_snapshot.py (the nightly snapshot) and tools/daily_traffic.py (the morning
report). Download counts are read carefully, as they over-count people: when every file of a
release was downloaded at least N times in a period, those N rounds are counted as a bot or mirror
fetching everything ("probably automated"). Updates count as downloads. The weekly summary and the
website visitor numbers live in the private Kanzonas-Site-Data repository. Nothing is collected
inside the apps.
"""
import json
import os
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "stats")
APPS = {"KanzonasPDF": "keithlyding/KanzonasPDF", "KanzonasCAD": "keithlyding/KanzonasCAD",
        "KanzonasSVG": "keithlyding/KanzonasSVG"}
SKIP = (".txt", "winget-manifests.zip")      # not the app itself


def get(url):
    headers = {"User-Agent": "kanzonas-site-stats", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
        return json.load(r)


def kind(name):
    n = name.lower()
    if n.endswith("setup.exe"):
        return "Windows installer"
    if "portable" in n or n.endswith(".paf.exe"):
        return "Windows portable"
    if n.endswith("windows.zip"):
        return "Windows zip"
    if n.endswith(".appimage"):
        return "Linux AppImage"
    if n.endswith(".tar.gz"):
        return "Linux tar.gz"
    if n.endswith(".dmg"):
        return "Mac"
    return "Other"


def read_app(repo):
    releases = []
    page = 1
    while True:
        batch = get("https://api.github.com/repos/%s/releases?per_page=100&page=%d" % (repo, page))
        releases += batch
        if len(batch) < 100:
            break
        page += 1
    info = get("https://api.github.com/repos/" + repo)
    # GitHub's open_issues_count includes open pull requests: count only issues people opened
    prs = get("https://api.github.com/repos/%s/pulls?state=open&per_page=100" % repo)
    issues = max(info.get("open_issues_count", 0) - len(prs), 0)
    out = {"stars": info.get("stargazers_count", 0), "open_issues": issues,
           "releases": {}}
    for r in releases:
        if r.get("draft"):
            continue
        files = {a["name"]: a["download_count"] for a in r.get("assets", [])
                 if not a["name"].endswith(SKIP)}
        out["releases"][r["tag_name"]] = {"published": r.get("published_at", ""), "files": files}
    return out


def week_numbers(now, before):
    """Downloads since the last snapshot: total, probably automated, by kind, by release."""
    total = auto = 0
    by_kind, by_release = {}, []
    for tag, rel in now["releases"].items():
        old = (before or {}).get("releases", {}).get(tag, {}).get("files", {})
        gained = {f: c - old.get(f, 0) for f, c in rel["files"].items()}
        g = sum(max(v, 0) for v in gained.values())
        if g <= 0:
            continue
        # files downloaded at least `rounds` times each, this week: counted as automated
        rounds = min(gained.values()) if len(gained) > 1 else 0
        a = max(rounds, 0) * len(gained)
        total += g
        auto += a
        for f, v in gained.items():
            k = kind(f)
            by_kind[k] = by_kind.get(k, 0) + max(v - max(rounds, 0), 0)
        by_release.append((rel["published"][:10], tag, g, g - a))
    by_release.sort(reverse=True)
    return total, auto, by_kind, by_release
