# Kanzonas-Site roadmap

Open work for the website and logos, and the owner's decisions. Update it when a piece of work
lands or a decision changes. (The apps' own work is in their repos, handled in their own
sessions: see AGENTS.md.)

## Email and domain
- Done (7 Nov 2026): email. Cloudflare Email Routing receives keithlyding@ and support@kanzonas.com
  into Gmail; Gmail sends as both ("Send mail as" through smtp.gmail.com, an App Password each).
  SPF: `v=spf1 include:_spf.mx.cloudflare.net include:_spf.google.com ~all` (one record).
  DMARC: `_dmarc` = `v=DMARC1; p=none; rua=mailto:keithlyding@kanzonas.com` (report-only).
- Keep DMARC at `p=none` while mail is sent through Gmail: Gmail signs it as gmail.com, not
  kanzonas.com, so quarantine/reject would catch the owner's own mail. Tighten only after moving
  to a sender that signs as kanzonas.com (Google Workspace, Zoho, a sending service).

## Cloudflare settings (reviewed Nov 2026, with a scoped API token)
- Done: Always Use HTTPS on; minimum TLS 1.2 (was 1.0); Pages projects: preview deployments
  off and build watch paths `home/*`, `pdf/*`, `cad/*` (a push rebuilds only the site whose
  folder changed; a change outside them, like docs/ or brand/ alone, rebuilds none).
- Done: DNSSEC enabled (7 Nov 2026; the registrar is Cloudflare, which adds the DS record
  itself). Status "pending" until the registry has it; then "active".
- Done: www.kanzonas.com -> kanzonas.com, a Single Redirect rule (301, path and query string
  kept), checked live.
- Done: not-found pages (404.html in each site): unknown addresses (scanners' `/.env`,
  `/.git/config`...) get a real 404 instead of the home page with 200.
- Done: Browser Cache TTL "Respect existing headers" (was 4 hours, which overrode the site's
  own max-age=0 on CSS, JS and pictures: a returning visitor could get a new page with the old
  stylesheet).
- Known, accepted: on 404 responses Cloudflare Pages sets its own `Cache-Control: no-store`
  (overriding `_headers`), so Cloudflare still inserts its bot-detection script there and the
  policy blocks it (a console error on not-found pages only). A fix would be a Cloudflare
  Transform Rule adding no-transform to 404 responses, if ever wanted.

## Website
- **macOS for KanzonasPDF** (planned for its 1.9): the PDF page's macOS link and "No macOS
  version yet" switch over by themselves when a release has a .dmg or a mac .zip
  (download.js, `data-reveal`). Then also: macOS in the page's structured data
  (`operatingSystem`), in the titles and descriptions that say "Windows and Linux", and on the
  home page.
- **KanzonasCAD reports**: the CAD page's comparison says "Coming next"; update it (and
  "Good to know") when they ship.
- **KanzonasCAD drag-and-drop of DXF/DWG** (requested from its own session): mention it on the
  CAD page when it ships.
- **CAD page, two Windows zips** (suggested, waiting for the owner): drop "Windows without
  installing (zip)" and keep "Portable for Windows (zip)", as the PDF page does.

## Done (Nov 2026)
AlternativeTo badges on the PDF and CAD pages (the owner confirmed they show); the Kanzonas mark
top left on every page, linking to kanzonas.com. Three sites on Cloudflare Pages; download buttons that find the newest release (checked to be
the app's own GitHub releases); logos made in brand/ (the single source of truth); SEO
(titles, canonical links, link previews, structured data, sitemaps; Search Console verified);
comparison tables (PDF, CAD) with sources; KanzonasCAD in violet; Cloudflare Web Analytics with
a privacy note; security headers (_headers); contact address in the footer.
