# Kanzonas-Site roadmap

Open work for the website and logos, and the owner's decisions. Update it when a piece of work
lands or a decision changes. (The apps' own work is in their repos, handled in their own
sessions: see AGENTS.md.)

## Email and domain
- **SPF and DMARC records for kanzonas.com** (the owner: later). Email today: Cloudflare Email
  Routing receives (keithlyding@kanzonas.com; support@kanzonas.com to be added) and forwards to
  Gmail; nothing sends as @kanzonas.com yet. Sending will be Gmail "Send mail as" through
  smtp.gmail.com. When that starts:
  1. Read the domain's TXT records first (Cloudflare > DNS). Cloudflare's email setup may have
     added an SPF record already: edit it, never add a second one (two break both).
  2. SPF: the domain already has `v=spf1 include:_spf.mx.cloudflare.net ~all` (added by
     Email Routing; checked Nov 2026). Edit that record to
     `v=spf1 include:_spf.mx.cloudflare.net include:_spf.google.com ~all`; don't add a second.
  3. DMARC, starting report-only: TXT `_dmarc` = `v=DMARC1; p=none; rua=mailto:<address>`;
     after a week or two of passing reports, `p=quarantine`, then `p=reject`.
- **support@kanzonas.com** in Cloudflare Email Routing (the owner): the site's footer shows it
  since Nov 2026.

## Cloudflare settings (reviewed Nov 2026, with a scoped API token)
- Done: Always Use HTTPS on; minimum TLS 1.2 (was 1.0); Pages projects: preview deployments
  off and build watch paths `home/*`, `pdf/*`, `cad/*` (a push rebuilds only the site whose
  folder changed; a change outside them, like docs/ or brand/ alone, rebuilds none).
- **DNSSEC** (the owner, in the dashboard): DNS > Settings > Enable DNSSEC, then add the DS
  record it shows at the domain's registrar (automatic if the registrar is Cloudflare).
- **www.kanzonas.com -> kanzonas.com** permanent redirect (the owner, in the dashboard):
  Rules > Redirect Rules, template "Redirect from WWW to root". Today www serves a copy of the
  home page (its canonical tag points at kanzonas.com).
- **Not-found pages** (proposed): a 404.html in each site, so unknown addresses (scanners'
  `/.env`, `/.git/config`...) get a real 404 instead of the home page with 200.

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
Three sites on Cloudflare Pages; download buttons that find the newest release (checked to be
the app's own GitHub releases); logos made in brand/ (the single source of truth); SEO
(titles, canonical links, link previews, structured data, sitemaps; Search Console verified);
comparison tables (PDF, CAD) with sources; KanzonasCAD in violet; Cloudflare Web Analytics with
a privacy note; security headers (_headers); contact address in the footer.
