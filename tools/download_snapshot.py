"""The nightly download snapshot: every app's download totals, saved so each day can be counted.

    python tools/download_snapshot.py     (.github/workflows/download-snapshot.yml runs it nightly)

GitHub only keeps running totals per release file, with no history, and a Claude session can't
always read them (a scheduled session has no repositories attached). So this runs on GitHub's own
servers every night, reads KanzonasPDF's, KanzonasCAD's and KanzonasSVG's releases (the same way
tools/weekly_stats.py does), and saves in docs/stats/ (not published on the website):

- downloads-latest.json: every release file's count now (to compare with tomorrow night's);
- downloads-daily.json: one line per night: each app's total, the downloads since the night
  before and about how many of them were people (weekly_stats' "probably automated" rounds left
  out), and its stars.

tools/daily_traffic.py (the morning report) reads both. Nothing is collected inside the apps.
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weekly_stats  # noqa: E402  (its GitHub reading and "probably people" counting)

LATEST = os.path.join(weekly_stats.OUT, "downloads-latest.json")
DAILY = os.path.join(weekly_stats.OUT, "downloads-daily.json")


def load(path, default):
    return json.load(open(path)) if os.path.exists(path) else default


def main():
    os.makedirs(weekly_stats.OUT, exist_ok=True)
    before = load(LATEST, None)
    daily = load(DAILY, [])
    taken = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    now = {"taken": taken, "apps": {}}
    line = {"taken": taken, "since": (before or {}).get("taken"), "apps": {}}
    for name, repo in weekly_stats.APPS.items():
        data = weekly_stats.read_app(repo)          # an error fails the run: no half snapshot
        now["apps"][name] = data
        total = sum(sum(r["files"].values()) for r in data["releases"].values())
        entry = {"total": total, "stars": data["stars"], "releases": len(data["releases"])}
        prev = (before or {}).get("apps", {}).get(name)
        if prev:
            new, auto, _kinds, _rel = weekly_stats.week_numbers(data, prev)
            entry["new"], entry["people"] = new, new - auto
        line["apps"][name] = entry
    daily.append(line)
    json.dump(now, open(LATEST, "w"), indent=1, sort_keys=True)
    json.dump(daily, open(DAILY, "w"), indent=1)
    for name, e in line["apps"].items():
        print("%s: %d all-time%s" % (name, e["total"], ", %d new (about %d by people) since %s"
                                     % (e["new"], e["people"], line["since"]) if "new" in e else ""))


if __name__ == "__main__":
    main()
