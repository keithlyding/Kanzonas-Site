# Kanzonas-Site: rules for every change (all AI agents and people)

Static sites, no build step. Each folder is its own Cloudflare Pages project, deployed from
`main` (see README.md): `home/` is kanzonas.com, `pdf/` is pdf.kanzonas.com, `cad/` is
cad.kanzonas.com.

- **Push straight to `main`.** A push to `main` goes live within a minute or two. Don't push
  working branches: Cloudflare builds a preview of all three sites for every branch push.
- Before pushing, open the changed pages in a browser at desktop and phone width (about
  390 px): no sideways scrolling, no console errors.
- `style.css` (in all three folders) and `download.js` (in `pdf/` and `cad/`) are copies:
  change every copy the same way.
- The download buttons find the newest installer through GitHub's API; don't replace them
  with fixed links (release file names carry the version).
- American spelling in all visible text.
