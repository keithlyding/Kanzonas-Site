# docs/stats (public)

Only numbers that are public on GitHub anyway are kept here, because the scheduled morning report
reads them without any GitHub access:

- `downloads-latest.json`: every release file's download count at the last nightly snapshot;
- `downloads-daily.json`: one line per night: each app's all-time total, the downloads since the
  night before (`new`) and about how many of them were people (`people`), and its stars;
- `requests.json`: every issue and pull request someone other than the owner opened, open now or
  changed in the last 30 days (feature requests, bug reports, contributions).

`.github/workflows/download-snapshot.yml` runs `tools/download_snapshot.py` every evening at 22:37
UTC (GitHub often starts it hours late). The morning report is `tools/daily_traffic.py`.

**Website visitor numbers, the weekly summary and all the history are not here:** they're in the
private repository keithlyding/Kanzonas-Site-Data. Never put them in this public repository.
