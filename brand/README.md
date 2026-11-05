# Kanzonas logos: the single source of truth

Every Kanzonas logo comes from this folder: kanzonas.com's, KanzonasPDF's and KanzonasCAD's.
Change a logo **here**, never in the app repos, then copy the results into them.

## Make them

```
pip install pillow numpy
python brand/make_logos.py
```

It reads the owner's artwork (`artwork/kanzonas-logo-artwork.png`: its left part, the cactus,
sunflower and page, is kept as drawn) and the fonts in `fonts/`, and writes `out/` plus the
three website pages' logos (`home/`, `pdf/`, `cad/`). Commit all of it. The app files below are copied in by each app's own session
(this repo's sessions don't change the app repos). Checked on 5 Nov 2026: with these inputs it makes every logo file in KanzonasPDF 1.8.3
and KanzonasCAD 0.11.5 pixel for pixel (with Pillow 12.3.0 and NumPy 2.5.3; another Pillow version may draw
the letters' edges very slightly differently).

Then `python brand/make_social.py` makes the link-preview pictures (1200 x 630, shown when a
link to a site is shared) from those logos: `home/`, `pdf/` and `cad/og-image.png`.

## Where each file goes

| File in `brand/out/` | Copy to |
| --- | --- |
| `kanzonas-logo-source.png` | KanzonasPDF `assets/kanzonas-logo-source.png`, then run its `tools_make_assets.py` (puts it in `kanzonas/branding_data.py`, shown in Help > About) |
| `kanzonascad-logo.png` | KanzonasCAD `assets/kanzonascad-logo.png` (its README) |
| `web/kanzonascad-logo@2x.png` | KanzonasCAD `kanzonascad/resources/logo.png` (Help > About) |
| `web/kanzonaspdf-logo*.png`, `web/kanzonascad-logo*.png` | KanzonasCAD `assets/web/` (until it's removed there; this folder replaces it) |
| `web/kanzonas-logo*.png` | kanzonas.com's logo; the script copies the transparent 2x one to `home/` |

The script copies `web/kanzonaspdf-logo-transparent@2x.png` to `pdf/` and
`web/kanzonascad-logo-transparent@2x.png` to `cad/` itself.

In the apps, a logo change is a user-facing change: follow that repo's AGENTS.md (version,
CHANGELOG, release notes).

## What's in the logos

The full specification (every size, position and color) is in [SPEC.md](SPEC.md). In short:


- "Kanzonas": Roboto Condensed Medium, a little tighter than normal, near black (#0b0c10).
- "PDF": Saira Condensed SemiBold, red shading from #b30000 to #800000 (as the app icon's tag).
- "CAD": the same font, violet shading from #7150b8 to #4b3285 (as the app icon's tile).
- Under the word: a dot in its color and a line fading to grey, ending with the word.
- The tagline: Inter, grey (#646468), its bullets in the word's color.
- kanzonas.com's logo: the mark and "Kanzonas" alone, the word centered on the mark.

Files: `.png` 936 x 325 on the logos' off-white (#f9f9f9); `@2x` 1872 x 650 (the lettering
drawn at full resolution, the artwork enlarged, so a little softer); `-transparent` with no
background, for light backgrounds.

## Licenses

The cactus, sunflower and page are the owner's artwork. The fonts are under the SIL Open Font
License 1.1 (Google Fonts); each license is beside its font in `fonts/`.
