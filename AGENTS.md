# Kanzonas-Site: rules for every change (all AI agents and people)

Static sites, no build step. Each folder is its own Cloudflare Pages project, deployed from
`main` (see README.md): `home/` is kanzonas.com, `pdf/` is pdf.kanzonas.com, `cad/` is
cad.kanzonas.com.

- **Push straight to `main`.** A push to `main` goes live within a minute or two. Don't push
  working branches: Cloudflare builds a preview of all three sites for every branch push.
- Before pushing, open the changed pages in a browser at desktop and phone width (about
  390 px): no sideways scrolling, no console errors.
- `style.css` and `_headers` (in all three folders), and `download.js` and `gallery.js` (in
  `pdf/` and `cad/`) are copies: change every copy the same way.
- Screenshots (`pdf/shots/`, `cad/shots/`) follow the apps' READMEs by themselves: every hour
  `.github/workflows/screenshots.yml` runs `tools/update_screenshots.py`, which takes the
  screenshots each README shows (`docs/screenshot-NAME.png`), in its order and with its
  descriptions, makes the 600 px thumbnails, writes the gallery between the `gallery:start` and
  `gallery:end` markers in `index.html`, and pushes only when something changed. Don't edit
  those files or that part of the page by hand; to change a screenshot or its description,
  change the app's README. The short label under each thumbnail is in `screenshots.json`.
- `_headers` sets the security headers, including a Content-Security-Policy: only the site's
  own files run, plus Cloudflare Web Analytics, the download buttons may call
  api.github.com, and the AlternativeTo badge (pdf/, cad/) is a picture from alternativeto.net. A new outside script, font, picture or API needs adding there, or the
  browser blocks it. Keep pages free of inline scripts, inline styles and `on...=` handlers.
- `download.js` links only to files in the app's own GitHub releases (`isOwnRelease`).
- "What's new" on the PDF and CAD pages is the newest release's own notes (the part between
  `<!-- ...-notes -->` and `<!-- /...-notes -->` in its GitHub release text), filled in by
  `download.js` from the same request as the download buttons, as text only. Hidden until it
  loads. If an app changes how it marks its notes, update `showNotes`.
- kanzonas.com also has `about.html` (/about: the owner's own words; change it only as he
  asks), `help.html` (/help) and `privacy.html` (/privacy), and the menu and footer of every
  page link them. Their statements come from the apps' READMEs: when an app
  changes how it installs, updates, keeps settings or goes online, update them (and the date
  on the privacy page).
- Each site has a `404.html` (Cloudflare Pages serves it, with status 404, for any unknown
  address, at any depth): its stylesheet, icon and pictures use root paths (`/style.css`),
  never relative ones. Change its header and footer along with the site's `index.html`.
- The download buttons find the newest installer through GitHub's API; don't replace them
  with fixed links (release file names carry the version).
- American spelling in all visible text.

## Logos: this repo is the single source of truth
- Every Kanzonas logo (kanzonas.com's, KanzonasPDF's, KanzonasCAD's) is made here, by
  `brand/make_logos.py` from `brand/artwork/` and `brand/fonts/`. Change a logo only here,
  never in KanzonasPDF or KanzonasCAD.
- **Work on this repo stays in this repo** (the owner's decision): a session working on the
  website and logos does not build, branch or open pull requests in KanzonasPDF or
  KanzonasCAD; those are handled in their own sessions. When a logo changes, say which files
  in `brand/out/` go where (`brand/README.md`) so the app's own session copies them in.
- Never edit a logo PNG by hand: change the script or the artwork and run it again.
