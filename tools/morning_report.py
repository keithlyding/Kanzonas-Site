"""The detailed morning report: yesterday's website traffic in depth, the weeks around it, the
downloads and the requests, as text and graphs.

    python tools/morning_report.py OUT_DIR [--day YYYY-MM-DD]    (needs matplotlib)

Reads Cloudflare Web Analytics directly (the token comes from CF_ANALYTICS_TOKEN or from the
Claude environment's saved credential) and the public download and request snapshots in
docs/stats/. Prints the report and writes its graphs to OUT_DIR. **It never writes visitor
numbers into this repository** (they're private: the full history is kept in the private
Kanzonas-Site-Data repo). Read only. Nothing is collected inside the apps.

Cloudflare keeps exact counts for about a week, then a 1-in-10 sample: older days are marked as
estimates.
"""
import argparse
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.request
import zoneinfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
STATS = os.path.join(os.path.dirname(HERE), "docs", "stats")
TZ = zoneinfo.ZoneInfo("America/New_York")
ACCOUNT = "3148e7ce611b08b82ffba66d703d90a8"      # the Cloudflare account (not secret)
SITES = {"kanzonas.com": "#2a78d6", "pdf.kanzonas.com": "#eb6834", "cad.kanzonas.com": "#1baf7a", "svg.kanzonas.com": "#eda100"}
APPS = {"KanzonasPDF": "#eb6834", "KanzonasCAD": "#1baf7a", "KanzonasSVG": "#eda100"}
ALIAS = {"kanzonas-home.pages.dev": "kanzonas.com", "kanzonas-pdf.pages.dev": "pdf.kanzonas.com",
         "kanzonas-cad.pages.dev": "cad.kanzonas.com", "kanzonas-svg.pages.dev": "svg.kanzonas.com"}
SHARE = ("teams", "slack", "outlook", "office", "mail", "linkedin", "reddit", "discord", "ycombinator",
         "facebook", "twitter", "t.co", "whatsapp", "x.com")
SURF, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK, "figure.facecolor": SURF,
                     "axes.facecolor": SURF})


# ---------- reading ----------

def cloudflare(start, end, parts):
    """One GraphQL request with several named groups. A part is "dimensions" (over start..end) or
    ("dimensions", its_start, its_end): Cloudflare samples a group by its own size, so a long
    span is asked day by day to keep the days it still has exactly, exact."""
    z = lambda t: t.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    groups = []
    for n, d in parts.items():
        dims, s0, e0 = (d, None, None) if isinstance(d, str) else d
        flt = "{datetime_geq: $s, datetime_lt: $e}" if s0 is None else '{datetime_geq: "%s", datetime_lt: "%s"}' % (z(s0), z(e0))
        groups.append("%s: rumPageloadEventsAdaptiveGroups(limit: 5000, filter: %s) "
                      "{ count sum { visits } avg { sampleInterval } dimensions { %s } }" % (n, flt, dims))
    q = "query($a: String!, $s: Time!, $e: Time!) { viewer { accounts(filter: {accountTag: $a}) { %s } } }" % " ".join(groups)
    body = json.dumps({"query": q, "variables": {"a": ACCOUNT, "s": z(start), "e": z(end)}}).encode()
    headers = {"Content-Type": "application/json", "User-Agent": "kanzonas-morning-report"}
    if os.environ.get("CF_ANALYTICS_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["CF_ANALYTICS_TOKEN"]
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request("https://api.cloudflare.com/client/v4/graphql",
                                                               data=body, headers=headers), timeout=90) as r:
                d = json.load(r)
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 5:
                raise
            time.sleep(30 * (attempt + 1))
    if d.get("errors"):
        raise SystemExit("Cloudflare refused: " + "; ".join(x.get("message", "?") for x in d["errors"]))
    return d["data"]["viewer"]["accounts"][0]


def site(h):
    return ALIAS.get(h, h)


def eastern_hour(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(TZ)


# ---------- charts ----------

def frame(ax, title, sub, grid="y"):
    ax.set_title(title, loc="left", fontsize=15, fontweight="bold", color=INK, pad=26)
    ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=10.5, color=INK2, va="bottom")
    for s in ("top", "right", "left" if grid == "y" else "bottom"):
        ax.spines[s].set_visible(False)
    ax.grid(axis=grid, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def save(fig, path, note=""):
    if note:
        fig.text(0.012, 0.012, note, fontsize=9, color=MUTED, ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.05 if note else 0, 1, 1))
    fig.savefig(path)
    plt.close(fig)
    return path


def hbar(path, title, sub, items, color="#2a78d6", note=""):
    items = sorted(items, key=lambda kv: kv[1])[-12:]
    fig, ax = plt.subplots(figsize=(10, 0.55 * len(items) + 2.2), dpi=200)
    ax.barh([k for k, _ in items], [v for _, v in items], color=color, height=0.6, edgecolor=SURF, linewidth=2)
    top = max([v for _, v in items] or [1])
    for i, (_k, v) in enumerate(items):
        ax.text(v + top * 0.01, i, str(v), va="center", fontsize=10, color=INK2)
    ax.tick_params(axis="y", labelcolor=INK)
    frame(ax, title, sub, grid="x")
    return save(fig, path, note)


# ---------- the report ----------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("out")
    p.add_argument("--day", help="the day to report on (default: yesterday, US Eastern)")
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    day = datetime.date.fromisoformat(a.day) if a.day else datetime.datetime.now(TZ).date() - datetime.timedelta(days=1)
    d0 = datetime.datetime.combine(day, datetime.time(), TZ)
    week_start = day - datetime.timedelta(days=day.weekday())
    span_start = datetime.datetime.combine(week_start - datetime.timedelta(days=21), datetime.time(), TZ)  # 4 weeks
    d1 = d0 + datetime.timedelta(days=1)

    # four weeks, hour by hour per site (one request), and yesterday in detail (another)
    n_days = (d1 - span_start).days
    starts = [datetime.datetime.combine(span_start.date() + datetime.timedelta(days=i), datetime.time(), TZ) for i in range(n_days)]
    per_day = cloudflare(span_start, d1, {"d%d" % i: ("datetimeHour requestHost", t, t + datetime.timedelta(days=1))
                                          for i, t in enumerate(starts)})
    wide = {"h": [x for i in range(n_days) for x in per_day["d%d" % i]]}
    time.sleep(2)
    det = cloudflare(d0, d1, {"pages": "requestHost requestPath", "sources": "refererHost", "countries": "countryName",
                              "devices": "deviceType", "browsers": "userAgentBrowser", "os": "userAgentOS"})

    days, sampled = {}, {}
    hours_y = {s: [0] * 24 for s in SITES}
    for x in wide["h"]:
        t = eastern_hour(x["dimensions"]["datetimeHour"])
        s = site(x["dimensions"]["requestHost"])
        if s not in SITES:
            continue
        days.setdefault(t.date(), {k: 0 for k in SITES})[s] += x["sum"]["visits"]
        if x["avg"]["sampleInterval"] > 1:
            sampled[t.date()] = True
        if t.date() == day:
            hours_y[s][t.hour] += x["sum"]["visits"]
    all_days = [week_start - datetime.timedelta(days=21) + datetime.timedelta(days=i) for i in range((day - week_start).days + 22)]
    total = {d: sum(days.get(d, {}).values()) for d in all_days}
    y = total[day]
    prev7 = [total[day - datetime.timedelta(days=i)] for i in range(1, 8)]
    avg7 = sum(prev7) / 7
    best = max(total.values())
    est = lambda d: "~" if sampled.get(d) else ""

    out = []
    w = out.append
    w("KANZONAS MORNING REPORT: %s (US Eastern)" % day.strftime("%A %d %B %Y"))
    w("")
    w("HEADLINE")
    w("- %d visits yesterday%s; the 7 days before averaged %.0f (%+.0f%%). Same weekday last week: %s%d."
      % (y, " (the best day in these four weeks)" if y == best else "", avg7, (y - avg7) / avg7 * 100 if avg7 else 0,
         est(day - datetime.timedelta(days=7)), total[day - datetime.timedelta(days=7)]))
    w("")
    w("SITES YESTERDAY (visits; same weekday last week in brackets)")
    for s in SITES:
        last = days.get(day - datetime.timedelta(days=7), {}).get(s, 0)
        w("- %s: %d (%s%d)" % (s, days.get(day, {}).get(s, 0), est(day - datetime.timedelta(days=7)), last))
    w("")
    pages = sorted(((site(r["dimensions"]["requestHost"]) + r["dimensions"]["requestPath"], r["count"]) for r in det["pages"]), key=lambda kv: -kv[1])
    w("TOP PAGES (page views): " + ", ".join("%s %d" % kv for kv in pages[:12]))
    srcs = {}
    for r in det["sources"]:
        k = r["dimensions"]["refererHost"] or "(direct)"
        srcs[k] = srcs.get(k, 0) + r["sum"]["visits"]
    w("WHERE THEY CAME FROM: " + ", ".join("%s %d" % kv for kv in sorted(srcs.items(), key=lambda kv: -kv[1])))
    shares = [(k, v) for k, v in srcs.items() if any(h in k for h in SHARE)]
    w("SHARED LINKS (Teams, Reddit, email, social...): " + (", ".join("%s %d" % kv for kv in shares) or "none"))
    ctry = sorted(((r["dimensions"]["countryName"] or "?", r["sum"]["visits"]) for r in det["countries"]), key=lambda kv: -kv[1])
    w("COUNTRIES (%d): " % len(ctry) + ", ".join("%s %d" % kv for kv in ctry))
    w("DEVICES: " + ", ".join("%s %d" % (r["dimensions"]["deviceType"], r["sum"]["visits"]) for r in sorted(det["devices"], key=lambda r: -r["sum"]["visits"])))
    w("BROWSERS: " + ", ".join("%s %d" % (r["dimensions"]["userAgentBrowser"], r["sum"]["visits"]) for r in sorted(det["browsers"], key=lambda r: -r["sum"]["visits"])[:8]))
    w("SYSTEMS: " + ", ".join("%s %d" % (r["dimensions"]["userAgentOS"], r["sum"]["visits"]) for r in sorted(det["os"], key=lambda r: -r["sum"]["visits"])[:8]))
    hours = [sum(hours_y[s][h] for s in SITES) for h in range(24)]
    top_h = sorted(range(24), key=lambda h: -hours[h])[:3]
    w("BUSIEST HOURS (Eastern): " + ", ".join("%02d:00 %d" % (h, hours[h]) for h in top_h))
    w("")
    w("LAST 14 DAYS: " + ", ".join("%s %s%d" % (d.strftime("%a %d"), est(d), total[d]) for d in all_days[-14:]))
    weeks = []
    for i in range(4):
        ws = week_start - datetime.timedelta(days=7 * (3 - i))
        ds = [ws + datetime.timedelta(days=k) for k in range(7) if ws + datetime.timedelta(days=k) <= day]
        weeks.append((ws, ds, {s: sum(days.get(d, {}).get(s, 0) for d in ds) for s in SITES}, any(sampled.get(d) for d in ds)))
    w("WEEKS (Mon-Sun): " + "; ".join("%s%s %s%d%s" % ("week of ", ws.strftime("%d %b"), "~" if smp else "", sum(per.values()),
                                                          " (%d days)" % len(ds) if len(ds) < 7 else "") for ws, ds, per, smp in weeks))
    w("")

    # downloads and requests (public snapshots)
    daily_path = os.path.join(STATS, "downloads-daily.json")
    daily = json.load(open(daily_path)) if os.path.exists(daily_path) else []
    per_day = {}
    for l in daily:
        if not l.get("since"):
            continue
        dd = datetime.datetime.fromisoformat(l["taken"]).astimezone(TZ).date()
        for n in APPS:
            per_day.setdefault(dd, {k: 0 for k in APPS})[n] += l["apps"].get(n, {}).get("people", 0)
    if daily:
        last = daily[-1]
        w("DOWNLOADS (newest snapshot %s Eastern)" % datetime.datetime.fromisoformat(last["taken"]).astimezone(TZ).strftime("%a %d %b %I:%M %p"))
        monday = datetime.datetime.combine(datetime.datetime.now(TZ).date() - datetime.timedelta(days=datetime.datetime.now(TZ).weekday()), datetime.time(), TZ)
        wk = [l for l in daily if l.get("since") and datetime.datetime.fromisoformat(l["taken"]) >= monday]
        for n, e in last["apps"].items():
            w("- %s: last snapshot %s; this week %d (about %d by people); all-time %d; stars %d"
              % (n, "%d new, about %d by people" % (e["new"], e["people"]) if "new" in e else "first snapshot",
                 sum(l["apps"].get(n, {}).get("new", 0) for l in wk), sum(l["apps"].get(n, {}).get("people", 0) for l in wk),
                 e["total"], e["stars"]))
        age = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(last["taken"])
        if age > datetime.timedelta(hours=30):
            w("  (the newest snapshot is %d hours old: the nightly job may be late or have failed)" % (age.total_seconds() // 3600))
    req_path = os.path.join(STATS, "requests.json")
    if os.path.exists(req_path):
        r = json.load(open(req_path))
        recent = datetime.datetime.fromisoformat(r["taken"]) - datetime.timedelta(days=2)
        lines = []
        for app, items in r["apps"].items():
            for i in items:
                upd = datetime.datetime.fromisoformat(i["updated"].replace("Z", "+00:00"))
                if i["state"] == "open" or upd >= recent:
                    lines.append("- %s %s #%d (%s, %s) by %s: %s (%d comments) %s" % (
                        "NEW" if datetime.datetime.fromisoformat(i["created"].replace("Z", "+00:00")) >= recent else "",
                        app, i["number"], i["kind"], i["state"], i["author"], i["title"], i["comments"], i["url"]))
        w("FEATURE REQUESTS AND BUG REPORTS ON GITHUB:")
        out.extend(lines or ["- none open, nothing new in two days"])
    print("\n".join(out))

    # ---------- graphs ----------
    files = []
    # 1. last 28 days, stacked by site
    fig, ax = plt.subplots(figsize=(11, 5.8), dpi=200)
    bottom = [0] * len(all_days)
    for s, c in SITES.items():
        for i, d in enumerate(all_days):
            n = days.get(d, {}).get(s, 0)
            if n:
                ax.bar(d, n, bottom=bottom[i], width=0.72, color=c, alpha=0.45 if sampled.get(d) else 1,
                       edgecolor=SURF, linewidth=1.5, hatch="///" if sampled.get(d) else None)
            bottom[i] += n
    for d, t in zip(all_days, bottom):
        ax.text(d, t + max(bottom) * 0.015, "%s%d" % (est(d), t), ha="center", fontsize=7.5, color=INK2)
    ax.set_xlim(mdates.date2num(all_days[0]) - 0.6, mdates.date2num(all_days[-1]) + 0.6)
    ax.set_ylim(0, max(bottom) * 1.15 or 1)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    frame(ax, "Visits per day, last four weeks", "All four sites, US Eastern days")
    ax.legend(handles=[Patch(color=c, label=s) for s, c in SITES.items()], loc="upper center", frameon=False, ncol=4,
              fontsize=10, bbox_to_anchor=(0.5, -0.2))
    files.append(save(fig, os.path.join(a.out, "1-visits-28-days.png"), "Hatched: estimates (Cloudflare keeps a 1-in-10 sample of days older than about a week)."))
    # 2. weeks by site
    fig, ax = plt.subplots(figsize=(10, 5.4), dpi=200)
    bot = [0] * 4
    for s, c in SITES.items():
        vals = [per[s] for _ws, _ds, per, _smp in weeks]
        ax.bar(range(4), vals, bottom=bot, width=0.6, color=c, edgecolor=SURF, linewidth=2)
        bot = [b + v for b, v in zip(bot, vals)]
    for i, (ws, ds, per, smp) in enumerate(weeks):
        ax.text(i, bot[i] + max(bot) * 0.015, "%s%d" % ("~" if smp else "", bot[i]), ha="center", fontsize=10, color=INK2)
    ax.set_xticks(range(4), ["%s\n%s" % (ws.strftime("week of %d %b"), "(%d days so far)" % len(ds) if len(ds) < 7 else "") for ws, ds, _p, _s in weeks])
    ax.set_ylim(0, max(bot) * 1.15 or 1)
    frame(ax, "Visits per week", "Monday to Sunday, US Eastern, all four sites")
    ax.legend(handles=[Patch(color=c, label=s) for s, c in SITES.items()], loc="upper left", frameon=False, ncol=4, fontsize=10)
    files.append(save(fig, os.path.join(a.out, "2-visits-per-week.png"), "~ : includes estimated days."))
    # 3. yesterday hour by hour
    fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
    bot = [0] * 24
    for s, c in SITES.items():
        ax.bar(range(24), hours_y[s], bottom=bot, width=0.75, color=c, edgecolor=SURF, linewidth=1.2)
        bot = [b + v for b, v in zip(bot, hours_y[s])]
    ax.set_xticks(range(0, 24, 2), ["%02d" % h for h in range(0, 24, 2)])
    frame(ax, "Yesterday hour by hour", "%s, US Eastern hours, all four sites" % day.strftime("%A %d %B"))
    ax.legend(handles=[Patch(color=c, label=s) for s, c in SITES.items()], loc="upper left", frameon=False, ncol=4, fontsize=10)
    files.append(save(fig, os.path.join(a.out, "3-yesterday-by-hour.png")))
    # 4-6. yesterday's sources, countries, pages
    files.append(hbar(os.path.join(a.out, "4-sources.png"), "Where yesterday's visitors came from", day.strftime("%A %d %B"),
                      list(srcs.items()), note="\"(direct)\" includes links opened from apps that don't say where the click came from."))
    files.append(hbar(os.path.join(a.out, "5-countries.png"), "Yesterday's countries", day.strftime("%A %d %B") + ", visits", ctry))
    files.append(hbar(os.path.join(a.out, "6-pages.png"), "Yesterday's most viewed pages", day.strftime("%A %d %B") + ", page views", pages))
    # 7. downloads by people per day
    if per_day:
        keys = sorted(per_day)[-14:]
        fig, ax = plt.subplots(figsize=(10, 5.4), dpi=200)
        wdt = 0.26
        for j, (n, c) in enumerate(APPS.items()):
            xs = [i + (j - 1) * wdt for i in range(len(keys))]
            ys = [per_day[k][n] for k in keys]
            ax.bar(xs, ys, width=wdt, color=c, edgecolor=SURF, linewidth=1.5, label=n)
            for xx, yy in zip(xs, ys):
                ax.text(xx, yy + 0.2, str(yy), ha="center", fontsize=8.5, color=INK2)
        ax.set_xticks(range(len(keys)), [k.strftime("%a %d") for k in keys])
        frame(ax, "Downloads by people", "Per nightly snapshot, by the US Eastern day it was taken (bots' rounds left out)")
        ax.legend(loc="upper center", frameon=False, fontsize=10, ncol=3, bbox_to_anchor=(0.5, -0.08))
        files.append(save(fig, os.path.join(a.out, "7-downloads.png"), "GitHub sometimes runs the snapshot late, so a bar can cover more or less than 24 hours."))
    print("")
    print("GRAPHS: " + " ".join(files))


if __name__ == "__main__":
    main()
