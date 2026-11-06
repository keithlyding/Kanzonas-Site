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
and `download.js` (in `pdf/` and `cad/`) are copies, as is `_headers` (the security headers,
in all three). Keep the copies identical. The icons
are copied from each app's `assets/` folder. The logos are made in `brand/`, the single source
of truth for every Kanzonas logo, the apps' too: see [brand/README.md](brand/README.md).
