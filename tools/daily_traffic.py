"""The daily traffic report: yesterday's website visitors and this week's downloads.

    python tools/daily_traffic.py            (yesterday, US Eastern time)
    python tools/daily_traffic.py 2026-11-17 (another day)

Reads only, prints a plain-text report; changes nothing. A scheduled task runs it every morning
and sends the owner a short summary of it.

- Visitors: Cloudflare Web Analytics (real browsers that ran the page; most bots aren't in it),
  through the GraphQL API with a token that has Account > Account Analytics > Read. The token is
  CF_ANALYTICS_TOKEN if set; otherwise the request goes out without one and the cloud
  environment's network secret for api.cloudflare.com adds it.
- Downloads: GitHub's public release counts, compared with the weekly summary's snapshot
  (docs/stats/snapshot.json), so "this week so far".
- Nothing is collected inside the apps (the owner's promise: no telemetry, ever).
"""
import datetime
import json
import os
import sys
import time
import urllib.request
import zoneinfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weekly_stats  # noqa: E402  (its GitHub reading and "probably people" counting)

ACCOUNT = "3148e7ce611b08b82ffba66d703d90a8"      # the Cloudflare account (not secret)
TZ = zoneinfo.ZoneInfo("America/New_York")
SHARE_HINTS = ("teams", "slack", "outlook", "office", "mail", "linkedin", "reddit", "discord",
               "news.ycombinator", "facebook", "twitter", "x.com", "t.co", "whatsapp")

QUERY = """query($a: String!, $s: Time!, $e: Time!, $w: Time!) { viewer { accounts(filter: {accountTag: $a}) {
  hosts: rumPageloadEventsAdaptiveGroups(limit: 20, filter: {datetime_geq: $s, datetime_lt: $e}, orderBy: [sum_visits_DESC]) { count sum { visits } dimensions { requestHost } }
  pages: rumPageloadEventsAdaptiveGroups(limit: 15, filter: {datetime_geq: $s, datetime_lt: $e}, orderBy: [count_DESC]) { count dimensions { requestHost requestPath } }
  refs: rumPageloadEventsAdaptiveGroups(limit: 25, filter: {datetime_geq: $s, datetime_lt: $e}, orderBy: [sum_visits_DESC]) { sum { visits } dimensions { refererHost } }
  countries: rumPageloadEventsAdaptiveGroups(limit: 15, filter: {datetime_geq: $s, datetime_lt: $e}, orderBy: [sum_visits_DESC]) { sum { visits } dimensions { countryName } }
  hours: rumPageloadEventsAdaptiveGroups(limit: 200, filter: {datetime_geq: $w, datetime_lt: $e}, orderBy: [datetimeHour_ASC]) { sum { visits } dimensions { datetimeHour } }
} } }"""


def cloudflare(start, end, week_start):
    z = lambda t: t.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = json.dumps({"query": QUERY, "variables": {"a": ACCOUNT, "s": z(start), "e": z(end), "w": z(week_start)}}).encode()
    headers = {"Content-Type": "application/json", "User-Agent": "kanzonas-daily-traffic"}
    if os.environ.get("CF_ANALYTICS_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["CF_ANALYTICS_TOKEN"]
    for attempt in range(5):                       # Cloudflare limits how often it may be asked
        try:
            with urllib.request.urlopen(urllib.request.Request(
                    "https://api.cloudflare.com/client/v4/graphql", data=body, headers=headers), timeout=60) as r:
                d = json.load(r)
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 4:
                raise
            time.sleep(30 * (attempt + 1))
    if d.get("errors"):
        raise SystemExit("Cloudflare refused: " + "; ".join(x.get("message", "?") for x in d["errors"]))
    return d["data"]["viewer"]["accounts"][0]



def downloads():
    """Downloads from the nightly snapshots (docs/stats/downloads-*.json, saved by GitHub's own
    servers), so this works in a session that can't read GitHub's counts itself; GitHub directly
    only when there are no snapshots yet."""
    daily_path = os.path.join(weekly_stats.OUT, "downloads-daily.json")
    latest_path = os.path.join(weekly_stats.OUT, "downloads-latest.json")
    week_path = os.path.join(weekly_stats.OUT, "snapshot.json")
    week = json.load(open(week_path)) if os.path.exists(week_path) else None
    daily = json.load(open(daily_path)) if os.path.exists(daily_path) else []
    if daily and os.path.exists(latest_path):
        last = daily[-1]
        latest = json.load(open(latest_path))
        when = lambda s: datetime.datetime.fromisoformat(s).astimezone(TZ).strftime("%a %d %b %I:%M %p")
        age = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(last["taken"])
        if last.get("since"):
            print("Downloads from %s to %s (US Eastern), nightly snapshots:" % (when(last["since"]), when(last["taken"])))
        else:
            print("Downloads: the first nightly snapshot was taken %s; daily counts start with the next one." % when(last["taken"]))
        for name, e in last["apps"].items():
            day = "%d new, about %d by people" % (e["new"], e["people"]) if "new" in e else "no earlier snapshot"
            wk = ""
            prev = (week or {}).get("apps", {}).get(name)
            if prev and name in latest.get("apps", {}):
                t, auto, _k, _r = weekly_stats.week_numbers(latest["apps"][name], prev)
                wk = "; since the weekly summary of %s: %d, about %d by people" % (week.get("date", "?"), t, t - auto)
            print("  %s: %s%s; all-time %d, stars %d" % (name, day, wk, e["total"], e["stars"]))
        if age > datetime.timedelta(hours=30):
            print("  (The newest snapshot is %d hours old: the nightly job may have been delayed or failed.)" % (age.total_seconds() // 3600))
        return
    print("Downloads since the weekly summary of %s (no nightly snapshots yet):" % (week or {}).get("date", "?"))
    for name, repo in weekly_stats.APPS.items():
        try:
            now = weekly_stats.read_app(repo)
        except Exception as e:                     # reported in the report, not hidden
            print("  %s: couldn't read GitHub (%s)" % (name, e))
            continue
        prev = (week or {}).get("apps", {}).get(name)
        if not prev:
            print("  %s: no weekly summary yet (all-time %d)" % (name, sum(sum(r["files"].values()) for r in now["releases"].values())))
            continue
        t, auto, _kinds, _rel = weekly_stats.week_numbers(now, prev)
        print("  %s: %d downloads, about %d by people; stars %d" % (name, t, t - auto, now["stars"]))


def asked():
    """What other people asked for on GitHub (issues and pull requests not by the owner), from the
    nightly snapshot's requests.json. Emails to support@kanzonas.com aren't in it."""
    path = os.path.join(weekly_stats.OUT, "requests.json")
    if not os.path.exists(path):
        print("Requests on GitHub: none saved yet (the nightly snapshot saves them).")
        return
    data = json.load(open(path))
    taken = datetime.datetime.fromisoformat(data["taken"])
    recent = taken - datetime.timedelta(days=2)
    print("Requests on GitHub by other people (as of %s, US Eastern):" % taken.astimezone(TZ).strftime("%a %d %b %I:%M %p"))
    any_ = False
    for app, items in data["apps"].items():
        for i in items:
            created = datetime.datetime.fromisoformat(i["created"].replace("Z", "+00:00"))
            updated = datetime.datetime.fromisoformat(i["updated"].replace("Z", "+00:00"))
            if i["state"] != "open" and updated < recent:
                continue                       # closed and quiet: not news
            tag = "NEW " if created >= recent else ("updated " if updated >= recent else "")
            print("  %s%s #%d (%s, %s) by %s: %s, %d comments, %s" % (tag, app, i["number"], i["kind"], i["state"],
                  i["author"], i["title"], i["comments"], i["url"]))
            any_ = True
    if not any_:
        print("  none open, and nothing new in the last two days")
    print("  (Emails to support@kanzonas.com aren't included.)")

def main():
    if len(sys.argv) > 1:
        day = datetime.date.fromisoformat(sys.argv[1])
    else:
        day = datetime.datetime.now(TZ).date() - datetime.timedelta(days=1)
    start = datetime.datetime.combine(day, datetime.time(), TZ)
    end = start + datetime.timedelta(days=1)
    a = cloudflare(start, end, end - datetime.timedelta(days=7))

    total = sum(h["sum"]["visits"] for h in a["hosts"])
    print("KANZONAS TRAFFIC, %s (US Eastern day)" % day.strftime("%A %d %B %Y"))
    print()
    print("Website visits: %d (page views %d)" % (total, sum(h["count"] for h in a["hosts"])))
    for h in a["hosts"]:
        print("  %s: %d" % (h["dimensions"]["requestHost"], h["sum"]["visits"]))
    print("Pages: " + ", ".join("%s%s %d" % (p["dimensions"]["requestHost"], p["dimensions"]["requestPath"], p["count"])
                                for p in a["pages"]))
    refs = [(r["dimensions"]["refererHost"] or "(direct)", r["sum"]["visits"]) for r in a["refs"]]
    print("Came from: " + ", ".join("%s %d" % r for r in refs))
    shares = [r for r in refs if any(k in r[0] for k in SHARE_HINTS)]
    print("Shared links (Teams, Reddit, email...): " + (", ".join("%s %d" % r for r in shares) or "none"))
    print("Countries: " + ", ".join("%s %d" % (c["dimensions"]["countryName"], c["sum"]["visits"]) for c in a["countries"]))
    by_day = {}
    for h in a["hours"]:                           # hours in UTC, counted on US Eastern days
        when = datetime.datetime.fromisoformat(h["dimensions"]["datetimeHour"].replace("Z", "+00:00")).astimezone(TZ)
        by_day[when.date()] = by_day.get(when.date(), 0) + h["sum"]["visits"]
    print("Last 7 days: " + ", ".join("%s %d" % (d.strftime("%a %d"), by_day.get(d, 0))
                                      for d in (day - datetime.timedelta(days=i) for i in range(6, -1, -1))))
    print()

    downloads()
    print()
    asked()
    print()
    print("Read-only report by tools/daily_traffic.py. Nothing is collected inside the apps.")


if __name__ == "__main__":
    main()
