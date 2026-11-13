"""Bring the PDF, CAD and SVG pages' screenshot galleries up to date with the apps' READMEs.

    python tools/update_screenshots.py            (the GitHub Action runs it every hour)

For each app it reads the README on the app's `main` branch on GitHub and takes the
screenshots it shows (`docs/screenshot-NAME.png`, or a plain `docs/screenshot.png`, which is named
"screenshot"; as a Markdown image or an <img> tag), in the
README's order and with the README's description (its alt text). For each one:

- the full picture goes to SITE/shots/NAME.png, and a 600 px wide SITE/shots/NAME-thumb.jpg is
  made from it (only when the picture changed, so an unchanged picture gives no new commit);
- pictures the README no longer shows are removed from SITE/shots/;
- the page's gallery, between the <!-- gallery:start ... --> and <!-- gallery:end --> markers in
  SITE/index.html, is written again: each thumbnail with the README's description (alt text and
  the viewer's caption) and a short label under it from screenshots.json ("labels"), or one
  made from the file name for a screenshot that isn't listed there;
- the page's structured data ("screenshot") points at the first picture.

Nothing is changed when the READMEs and pictures are the same as last time. It needs Pillow.
The apps' repositories are only read (raw.githubusercontent.com).
"""
import html
import io
import json
import os
import re
import sys
import urllib.request

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = json.load(open(os.path.join(ROOT, "screenshots.json"), encoding="utf-8"))
THUMB_W = 600
RAW = "https://raw.githubusercontent.com/{repo}/{branch}/{path}"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "kanzonas-site-screenshots"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def readme_screenshots(text):
    """[(name, alt)] in the README's order, each screenshot once."""
    found = []
    md = r"!\[([^\]]*)\]\((?:\./)?docs/screenshot(?:-([a-z0-9-]+))?\.png\)"
    tag = r"<img\b[^>]*>"
    for m in re.finditer(md + "|" + tag, text, re.I):
        if m.group(0).startswith("!"):
            name, alt = m.group(2) or "screenshot", m.group(1)
        else:
            t = m.group(0)
            s = re.search(r'src="(?:\./)?docs/screenshot(?:-([a-z0-9-]+))?\.png"', t, re.I)
            if not s:
                continue
            a = re.search(r'alt="([^"]*)"', t, re.I)
            name, alt = s.group(1) or "screenshot", (a.group(1) if a else "")
        if name not in [n for n, _a in found]:
            found.append((name, html.unescape(alt).strip()))
    return found


def label_for(site, name):
    labels = CONFIG.get("labels", {}).get(site, {})
    return labels.get(name) or name.replace("-", " ").strip().capitalize()


def write_if_changed(path, data):
    if os.path.exists(path) and open(path, "rb").read() == data:
        return False
    with open(path, "wb") as f:
        f.write(data)
    return True


def update(site, app):
    repo, branch = app["repo"], app.get("branch", "main")
    readme = fetch(RAW.format(repo=repo, branch=branch, path="README.md")).decode("utf-8")
    shots = readme_screenshots(readme)
    if not shots:
        print("%s: no screenshots found in %s's README; left as it is" % (site, repo))
        return False
    folder = os.path.join(ROOT, site, "shots")
    os.makedirs(folder, exist_ok=True)
    changed = False
    sizes = {}
    for name, _alt in shots:
        path = "docs/screenshot.png" if name == "screenshot" else "docs/screenshot-%s.png" % name
        png = fetch(RAW.format(repo=repo, branch=branch, path=path))
        full = os.path.join(folder, name + ".png")
        thumb = os.path.join(folder, name + "-thumb.jpg")
        new_png = write_if_changed(full, png)
        im = Image.open(io.BytesIO(png)).convert("RGB")
        th_h = round(im.height * THUMB_W / im.width)
        if new_png or not os.path.exists(thumb):
            im.resize((THUMB_W, th_h), Image.LANCZOS).save(thumb, quality=82, optimize=True,
                                                            progressive=True)
            changed = True
            print("%s: %s %s" % (site, "updated" if new_png else "thumbnail for", name))
        sizes[name] = th_h
    keep = set()
    for name, _alt in shots:
        keep |= {name + ".png", name + "-thumb.jpg"}
    for f in os.listdir(folder):
        if f not in keep:
            os.remove(os.path.join(folder, f))
            changed = True
            print("%s: removed %s" % (site, f))
    # the gallery
    items = []
    for name, alt in shots:
        a = html.escape(alt or label_for(site, name), quote=True)
        items.append('          <li><a href="shots/%s.png" data-caption="%s"><img src="shots/%s-thumb.jpg" '
                     'alt="%s" width="%d" height="%d" loading="lazy"><span>%s</span></a></li>'
                     % (name, a, name, a, THUMB_W, sizes[name], html.escape(label_for(site, name))))
    page_path = os.path.join(ROOT, site, "index.html")
    page = open(page_path, encoding="utf-8").read()
    start, end = "<!-- gallery:start", "<!-- gallery:end -->"
    if start not in page or end not in page:
        sys.exit("%s: the gallery markers are missing from index.html" % site)
    i = page.index("-->", page.index(start)) + len("-->")
    j = page.index(end)
    new = page[:i] + "\n" + "\n".join(items) + "\n          " + page[j:]
    first = "https://%s/shots/%s.png" % (app["host"], shots[0][0])
    new = re.sub(r'("screenshot": ")[^"]*(")', lambda m: m.group(1) + first + m.group(2), new, count=1)
    if new != page:
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(new)
        changed = True
        print("%s: gallery written (%s)" % (site, ", ".join(n for n, _a in shots)))
    return changed


if __name__ == "__main__":
    any_change = False
    for site, app in CONFIG["apps"].items():
        any_change |= update(site, app)
    print("changed" if any_change else "no changes")
