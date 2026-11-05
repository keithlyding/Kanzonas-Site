# Kanzonas-Site

Static websites for Kanzonas: plain HTML, CSS and one small script, no build step.

| Folder  | Site                                   | Cloudflare Pages project |
| ------- | -------------------------------------- | ------------------------ |
| `home/` | [kanzonas.com](https://kanzonas.com)   | build output directory `home` |
| `pdf/`  | [pdf.kanzonas.com](https://pdf.kanzonas.com) | build output directory `pdf` |
| `cad/`  | [cad.kanzonas.com](https://cad.kanzonas.com) | build output directory `cad` |

## Deploying on Cloudflare Pages

Create three Pages projects, each connected to this repository (branch `main`):

- **Framework preset:** None
- **Build command:** leave empty (or `exit 0` if the form insists on one)
- **Build output directory:** `home`, `pdf` or `cad`
- **Root directory:** leave as the repository root
- **Custom domain:** `kanzonas.com` (and `www.kanzonas.com` if wanted), `pdf.kanzonas.com`,
  `cad.kanzonas.com`

Optionally, under each project's *Settings > Builds > Build watch paths*, include only that
project's folder (for example `pdf/*`) so a change to one site doesn't redeploy the other two.

## How the download buttons work

`pdf/download.js` and `cad/download.js` (identical copies) ask GitHub's API for the newest
releases of `keithlyding/KanzonasPDF` and `keithlyding/KanzonasCAD`, and point each download
link at the first file whose name matches the link's `data-asset` pattern (for example
`-setup\.exe$`) in the newest release that is not a draft or a pre-release. Release file names
carry the version (`KanzonasPDF-v1.8-setup.exe`), so a fixed link would go stale.

Each link's `href` in the HTML is the GitHub releases page, so the buttons still work if
JavaScript is off or the API can't be reached (GitHub allows 60 unauthenticated API
requests an hour per visitor IP).

## Shared files

Each folder is deployed on its own and can't see the others, so `style.css` (in all three)
and `download.js` (in `pdf/` and `cad/`) are copies. Keep the copies identical. The icons
are copied from each app's `assets/` folder. The page logos are the website versions that
KanzonasCAD's `tools/make_logos.py --web` makes in its `assets/web/` folder (both apps' logos:
twice the size, for sharp high-density screens, with a transparent background):
`kanzonaspdf-logo-transparent@2x.png` and `kanzonascad-logo-transparent@2x.png`.
The home page's `kanzonas-logo.png` is cut from `kanzonaspdf-logo-transparent@2x.png`: its
mark and "Kanzonas" kept as drawn (identical in both apps' logos), "PDF", the rule and the
tagline left out, and the word centered on the mark. Make it again the same way if the app
logos change.
