"""The weekly summary of KanzonasPDF and KanzonasCAD downloads and interest.

    python tools/weekly_stats.py     (the GitHub Action .github/workflows/weekly-stats.yml runs it)

Reads, from GitHub's public API, each app's releases (download counts per file), stars and open
issues; compares them with the previous week's snapshot in docs/stats/snapshot.json; writes this
week's summary to docs/stats/<date>.md and a fresh snapshot; and prints the summary (the Action
posts it as an issue, so GitHub emails it).

Downloads are read carefully (they over-count real people):
- "Probably automated": for each release, when every one of its files was downloaded at least N
  times, those N rounds are counted as a bot or mirror fetching everything (that pattern is
  rarely people: a person downloads one file, not all of them).
- Updates count as downloads: someone updating is a returning user, not a new one.
- Nothing is collected from inside the apps (no telemetry: the owner's promise). Website visits
  are in Cloudflare Web Analytics (each Pages project's Metrics), not here.
"""
import datetime
import json
import os
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "stats")
APPS = {"KanzonasPDF": "keithlyding/KanzonasPDF", "KanzonasCAD": "keithlyding/KanzonasCAD"}
SKIP = (".txt", "winget-manifests.zip")      # not the app itself


def get(url):
    headers = {"User-Agent": "kanzonas-weekly-stats", "Accept": "application/vnd.github+json"}
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


def main():
    os.makedirs(OUT, exist_ok=True)
    snap_path = os.path.join(OUT, "snapshot.json")
    before = json.load(open(snap_path)) if os.path.exists(snap_path) else None
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    now = {"date": today, "apps": {name: read_app(repo) for name, repo in APPS.items()}}

    since = before["date"] if before else None
    lines = ["# Kanzonas weekly summary, %s" % today, ""]
    if since:
        lines.append("Since %s. Downloads of the apps' files on GitHub (installers, zips, "
                     "AppImages, Mac); \"probably people\" leaves out the rounds where every file "
                     "of a release was downloaded once each (a bot or mirror)." % since)
    else:
        lines.append("First summary: this records today's totals. From next week it shows what "
                     "changed in the week.")
    lines.append("")
    for name, data in now["apps"].items():
        prev = (before or {}).get("apps", {}).get(name)
        lines.append("## %s" % name)
        all_time = sum(sum(r["files"].values()) for r in data["releases"].values())
        if prev:
            total, auto, by_kind, by_release = week_numbers(data, prev)
            people = total - auto
            lines.append("- **Downloads this week: %d** (probably people: **%d**; probably "
                         "automated: %d)" % (total, people, auto))
            if by_kind:
                lines.append("- By kind (probably people): " + ", ".join(
                    "%s %d" % (k, v) for k, v in sorted(by_kind.items(), key=lambda x: -x[1]) if v))
            for date, tag, g, p in by_release[:5]:
                lines.append("  - %s (%s): %d downloads, about %d by people" % (tag, date, g, p))
            ds = data["stars"] - prev.get("stars", 0)
            lines.append("- GitHub stars: %d (%+d), open issues: %d (%+d)"
                         % (data["stars"], ds, data["open_issues"],
                            data["open_issues"] - prev.get("open_issues", 0)))
        else:
            lines.append("- Stars: %d, open issues: %d" % (data["stars"], data["open_issues"]))
        newest = max(data["releases"].items(), key=lambda kv: kv[1]["published"], default=None)
        if newest:
            lines.append("- Newest release: %s (%s), %d downloads so far"
                         % (newest[0], newest[1]["published"][:10], sum(newest[1]["files"].values())))
        lines.append("- All-time downloads: %d over %d releases" % (all_time, len(data["releases"])))
        lines.append("")
    lines += ["## Also look at",
              "- Website visitors (real browsers, not bots): Cloudflare > Workers & Pages > each "
              "project > Metrics (Web Analytics).",
              "- Google searches: Search Console > Performance (clicks and impressions).",
              "- Messages to support@kanzonas.com, and new GitHub issues from people you don't know.",
              "",
              "_Made by tools/weekly_stats.py in Kanzonas-Site. Nothing is collected inside the apps._"]
    report = "\n".join(lines) + "\n"
    open(os.path.join(OUT, today + ".md"), "w").write(report)
    json.dump(now, open(snap_path, "w"), indent=1, sort_keys=True)
    print(report)


if __name__ == "__main__":
    main()
