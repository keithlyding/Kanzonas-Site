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
- Done: DNSSEC active (enabled 7 Nov 2026 02:11 UTC, active by 04:17 UTC; the registrar is
  Cloudflare, which added the DS record itself).
- Done: www.kanzonas.com -> kanzonas.com, a Single Redirect rule (301, path and query string
  kept), checked live.
- Done: not-found pages (404.html in each site): unknown addresses (scanners' `/.env`,
  `/.git/config`...) get a real 404 instead of the home page with 200.
- Done: Browser Cache TTL "Respect existing headers" (was 4 hours, which overrode the site's
  own max-age=0 on CSS, JS and pictures: a returning visitor could get a new page with the old
  stylesheet).
- Done (15 Nov 2026): the `.pages.dev` addresses redirect to the sites' own domains
  (kanzonas-home -> kanzonas.com, kanzonas-pdf -> pdf., kanzonas-cad -> cad., kanzonas-svg ->
  svg.; 301, path and query string kept): an account-level Bulk Redirect list
  `pages_dev_redirects` and its rule in the account's http_request_redirect phase. Deployment
  addresses (`<id>.kanzonas-svg.pages.dev`) aren't redirected, so a deployment can still be
  checked. A new site's project needs its line added to that list. Also: svg/ in the build
  watch paths; Web Analytics on for all four projects (svg since 15 Nov); Crawler Hints
  (IndexNow) on since 14 Nov.
- Known, accepted: on 404 responses Cloudflare Pages sets its own `Cache-Control: no-store`
  (overriding `_headers`), so Cloudflare still inserts its bot-detection script there and the
  policy blocks it (a console error on not-found pages only). A fix would be a Cloudflare
  Transform Rule adding no-transform to 404 responses, if ever wanted.

## Open items (handed over 20 Nov 2026, from the session that built the sites)
- Done (20 Nov 2026): the morning report couldn't read downloads (its scheduled sessions have no
  repositories attached, so GitHub's API answered 403). Now a nightly GitHub Action
  (`download-snapshot.yml`, 05:07 UTC) saves every app's download totals in `docs/stats/`, and
  `tools/daily_traffic.py` reads them: downloads per day for all three apps. First snapshot the
  night of 19/20 Nov, so the first full day counted is Friday 20 Nov (in Saturday's report).
- **KanzonasSVG** was added to the Kanzonas environment's repositories on 20 Nov 2026 (and attached
  to the session that built the sites), so sessions can read its download counts and stars.
- **Offered, not yet decided by the owner:** download-click counting through small pages on the
  sites (`/download/windows` ...) so Cloudflare counts download clicks anonymously (true
  conversion rate, no tracking); Spanish and Italian KanzonasPDF pages (`pdf.kanzonas.com/es/`,
  `/it/`); a shot-by-shot script for a first YouTube demo (KanzonasPDF takeoff on a floor plan).
- **Code signing:** SignPath application resent 19 Nov 2026 (see the code signing item below);
  the reviewer looks for stars, forks, contributors, outside articles and independent
  discussions. Microsoft Artifact Signing next if declined.
- Visitor history: Cloudflare keeps only a 10% sample of visits older than about a week (days
  before 12 Nov show as tens), so save numbers while they're exact.

## Website
- Done (7 Nov 2026): content brought up to KanzonasPDF 1.9 (macOS for Apple silicon: the
  download link, "Good to know", structured data; Scan, styled text editing, Dimension and
  Legend markups, Replace pages, PDF/A) and KanzonasCAD 0.14.1 (panel layouts, bill of
  materials, revisions, blocks and AutoCAD Electrical data from DXF/DWG, drag and drop; the
  comparison's Reports row). Screenshots as a gallery of thumbnails with a viewer.
- Done (15 Nov 2026), to bring more people to the apps (the owner's go-ahead): "free alternative
  to..." pages for the searches people make (pdf.kanzonas.com/bluebeam-alternative,
  cad.kanzonas.com/autocad-electrical-alternative, svg.kanzonas.com/vectorizer-alternative, each
  with an honest comparison, its sources and what the app doesn't do), a press kit
  (kanzonas.com/press, Press in every footer), and drafts of posts for Hacker News and Reddit in
  docs/outreach/posts.md for the owner to edit and post himself. Also: the SVG page's logo is now
  the transparent one, as on the other pages (it had the light-background one).
- Ideas for the apps' own sessions (not this repo): Flathub, winget/Scoop/Chocolatey, the
  PortableApps.com listing, download directories, a "star us on GitHub" line in the About box,
  short demo videos.
- Done (17 Nov 2026): the PDF page brought up to KanzonasPDF 1.15.7 (colors of the page's own
  drawing and text, rotating pictures and shapes, SVG drawings placed as real lines, File
  Explorer thumbnails); the SVG page mentions placing an SVG in KanzonasPDF.
- Done (17 Nov 2026): the CAD pages brought up to KanzonasCAD 0.16.7 (printing, wires that
  route around symbols and land on pins, buses by poles, wire gauge and color, ratings, fused
  disconnects, starters, drive terminals, Array and Offset, a second screen); also the
  AutoCAD Electrical page, the kanzonas.com card, the press kit and the r/PLC draft.
- **KanzonasCAD wire lists** (its README: coming next, with assigning parts to devices and
  shared libraries): update the CAD page's comparison and "Good to know" when they ship.
- Done (13 Nov 2026): **KanzonasSVG** on the website (the owner tested it): svg.kanzonas.com
  (`svg/`, its own Cloudflare Pages project, orange accent), a card on kanzonas.com, KanzonasSVG
  in every menu and footer, Help and Privacy, the screenshot updates and the weekly summary.
  Its releases mark their notes (`<!-- kanzonas-notes -->`, from 1.1.1), so "What's new" shows.
  Still to do: an AlternativeTo listing for it, if the owner wants one.
- Done (13 Nov 2026): content brought up to KanzonasPDF 1.14 (comments review, smart forms,
  accessibility, batch processing, split view, rulers, groups, layers, spaces, sets, numbered
  dots, Italian), KanzonasCAD 0.15.12 (wire tools, duct sizes) and KanzonasSVG 1.1.1 (it now
  checks for updates and updates itself: the SVG page, Help and Privacy say so; crop; line art;
  the comparison with Inkscape 1.4.4 from its README).
- Done: the CAD page shows the portable zip only (the owner, Nov 2026), as the PDF page does;
  the plain Windows zip stays on the GitHub releases page.

- **Code signing** (the owner to decide): unsigned downloads get Windows SmartScreen's warning,
  and its reputation is per file, so every new version starts over: with frequent releases the
  warning effectively never goes away. Signing builds reputation on the publisher, carried to
  new versions (even EV certificates no longer skip the warning). Options: SignPath again (free
  for open source; declined once as too new), Microsoft Artifact Signing (~$10/month;
  eligibility to check), or fewer, bigger releases. The download note on the PDF and CAD pages
  says this plainly; update it if signing arrives.
  Update 19 Nov 2026: the owner applied to SignPath Foundation again for KanzonasPDF; if it's
  declined, Microsoft Artifact Signing next (individuals in the US qualify), Certum's open-source
  certificate as the fallback. When signing arrives, update the download notes and Help.

## Done (Nov 2026)
Weekly summary of downloads, stars and issues (Mondays, as a GitHub issue; never anything from inside the apps). Screenshots follow the apps' READMEs automatically (an hourly GitHub Action). About page (/about, the owner's own words, 7 Nov 2026). Help page (/help) and privacy page (/privacy) on kanzonas.com, linked from every page; "What's new" from the newest release on the PDF and CAD pages. AlternativeTo badges on the PDF and CAD pages (the owner confirmed they show); the Kanzonas mark
top left on every page, linking to kanzonas.com. Three sites on Cloudflare Pages; download buttons that find the newest release (checked to be
the app's own GitHub releases); logos made in brand/ (the single source of truth); SEO
(titles, canonical links, link previews, structured data, sitemaps; Search Console verified);
comparison tables (PDF, CAD) with sources; KanzonasCAD in violet; Cloudflare Web Analytics with
a privacy note; security headers (_headers); contact address in the footer.
