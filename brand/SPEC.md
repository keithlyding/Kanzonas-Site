# Kanzonas logos: specification

The record of how the logos are drawn. **The source of truth is `brand/make_logos.py`** (in this
repo); if this page and the script ever disagree, the script wins, so update this page with it.
Values checked against the script on 5 Nov 2026.

Pixel values are for the 1x canvas (936 x 325 px); the @2x files are the same layout doubled.

Notes:
- The "≈" numbers are rounded. The two rule-start colors and the x positions with decimals
  come from the script's arithmetic; they can be off by one color step or a fraction of a pixel.
- Rebuilding the logo in CSS won't match it exactly: browsers draw text a little differently
  from the image library that makes the PNGs, and the mark is a picture anyway. The website
  uses the PNG files; this page records how they were made.

## Fonts

All free from Google Fonts, SIL Open Font License 1.1; the files and licenses are in
`brand/fonts/`.

| Text | Font | File |
| --- | --- | --- |
| "Kanzonas" | Roboto Condensed, weight 500 (Medium) | `RobotoCondensed[wght].ttf` (variable, wght = 500) |
| "PDF" / "CAD" | Saira Condensed, weight 600 (SemiBold) | `SairaCondensed-SemiBold.ttf` |
| Tagline | Inter, weight 450 (between Regular 400 and Medium 500) | `Inter[opsz,wght].ttf` (variable, wght = 450) |

## Colors

| Part | Color |
| --- | --- |
| Background (opaque files) | `#F9F9F9` rgb(249, 249, 249) |
| "Kanzonas" | `#0B0C10` rgb(11, 12, 16), near black, solid |
| "PDF", vertical gradient over the capital height | top `#B30000` rgb(179, 0, 0), bottom `#800000` rgb(128, 0, 0) |
| "CAD", vertical gradient over the capital height | top `#7150B8` rgb(113, 80, 184), bottom `#4B3285` rgb(75, 50, 133) (violet, as the KanzonasCAD icon's tile; green until Nov 2026) |
| Tagline text | `#646468` rgb(100, 100, 104) |
| Tagline bullets (•) | the word's top color (`#B30000` for PDF, `#7150B8` for CAD) |

Rule under the words:
- Starts at the midpoint of the word's top and bottom colors: PDF ≈ `#9A0000`,
  CAD ≈ `#5E419F` (exactly rgb(94, 65, 158.5)).
- Fades to `#B2B2B2` rgb(178, 178, 178).
- Fade curve: color = start + (end − start) × t^0.8 (t = 0 at the rule's left end, 1 at its
  right end).

## Sizes and layout (px, 1x canvas 936 x 325)

Capital height of "Kanzonas" and "PDF"/"CAD": **85 px** (both words the same). Top of the
capitals: y = 156.

Font sizes that give that capital height: Roboto Condensed 119.75 px, Saira Condensed
123.25 px. For CSS, with "Kanzonas" at font-size S: PDF/CAD = 1.0292 × S, tagline = 0.1691 × S.

"Kanzonas":
- Left edge of its ink x = 306, letter-spacing −0.02 em.
- Right edge of its ink x ≈ 740.9.

Gap to the colored word:
- PDF: 16 px (starts x ≈ 756.9).
- CAD: 13 px (starts x ≈ 753.9). A round C looks further away than a straight P, so it's
  moved 3 px closer.

Colored word letter-spacing: PDF −0.02 em, CAD −0.0175 em. Both words end at the same
x ≈ 909.4, so the two logos line up on the left and the right when stacked.

Rule (the line under the words), centered at y = 261:
- Dot: an 8 px circle at the left, center x = 309.
- Line: 2.5 px thick, from x = 309 to x ≈ 909.4 (it ends where the word ends).

Tagline:
- Capital height 15 px, top of the capitals at y = 284, starts at x = 308.
- Font size 20.25 px, letter-spacing +0.0807 em. That spacing makes the PDF tagline exactly
  399 px wide; the CAD tagline uses the same spacing.
- PDF: `VIEW • EDIT • ANNOTATE • REVIEW`
- CAD: `SCHEMATICS • PANELS • WIRE NUMBERS`
- All caps; the bullets are U+2022 with a space on each side.

Mark (cactus, sunflower, page) at the left, x = 0 to 296: **not a font**. It's the owner's
original artwork, kept as a bitmap (`brand/artwork/kanzonas-logo-artwork.png`, its left 296 px).
It can't be rebuilt from this spec.

Letters are placed one at a time, with **no kerning**. To match in CSS: `font-kerning: none;`.

## kanzonas.com's logo

The mark and "Kanzonas" alone: no colored word, rule or tagline. "Kanzonas" is drawn exactly
as above (same font, size, spacing and x = 306) but with the top of its capitals at y = 120, so
the capitals are centered on the 325 px height. The canvas ends 8 px after the word:
749 x 325 at 1x, 1496 x 650 at 2x.

## Files (`brand/out/web/`)

| File | Size | Background |
| --- | --- | --- |
| `kanzonaspdf-logo.png` | 936 x 325 | `#F9F9F9` |
| `kanzonaspdf-logo@2x.png` | 1872 x 650 | `#F9F9F9` |
| `kanzonaspdf-logo-transparent.png` | 936 x 325 | transparent |
| `kanzonaspdf-logo-transparent@2x.png` | 1872 x 650 | transparent |
| `kanzonascad-logo*.png` | the same four for CAD | |
| `kanzonas-logo*.png` | the same four for kanzonas.com (749 x 325 / 1496 x 650) | |

The transparent files are for light backgrounds only: "Kanzonas" is near black and would
vanish on a dark one. The apps' own copies (`brand/out/kanzonas-logo-source.png`,
`brand/out/kanzonascad-logo.png`) are the opaque 1x files; `brand/README.md` says where each
one goes.

## App icons (separate from the logos, still made in each app's repo)

KanzonasPDF icon (`KanzonasPDF/tools_make_assets.py`):
- Red tile gradient `#B30000` → `#800000` (top to bottom).
- Installer icon tile `#2B88E8` → `#0A4EA8` (blue, so setup.exe can't be mistaken for the
  program itself).
- "PDF" tag letters: Inter, weight Black (900), squeezed to 78.3% width, gradient
  `#B30000` → `#800000`.
- Tag border `#0A100E`, 3.5 units thick, corner radius 11 (tile = 256 units).

KanzonasCAD icon: a ready-made picture (`KanzonasCAD/assets/kanzonascad-icon-source.png`); no
script draws it. Its tile and its tag's "CAD" letters are violet, `#7150B8` → `#4B3285` (top to
bottom), as "CAD" in the logo; the installer icon keeps a blue tile with the same violet letters.
KanzonasCAD's `tools/make_icons.py` makes its .png and .ico files from the picture.
