"""The Kanzonas logos: kanzonas.com's, KanzonasPDF's, KanzonasCAD's and KanzonasSVG's, all from here.

    python brand/make_logos.py

This folder (Kanzonas-Site's brand/) is the single source of truth for the logos. Change the
logos here, run this, commit, then copy the files in brand/out/ into the apps (brand/README.md
says which file goes where). Don't edit a logo in KanzonasPDF or KanzonasCAD.

Reads brand/artwork/kanzonas-logo-artwork.png (the owner's logo, whose left part, the cactus,
sunflower and page, is kept as is) and the fonts in brand/fonts/. Writes brand/out/ and the
three pages' logos (home/, pdf/, cad/).

- "Kanzonas": Roboto Condensed Medium, a little tighter than normal, near black.
- "PDF" (red, as its app icon: #b30000 to #800000), "CAD" (violet, as its app icon: #7150b8
  to #4b3285) and "SVG" (orange, as its app icon: #ef7d00 to #b34f00): Saira Condensed SemiBold,
  the same size; each spaced so that all the words end at the same place (where "PDF" and
  "CAD" end), so the logos line up on the left and the right when stacked.
- A rule under them, from a dot in the word's color fading to grey, ending with the word.
- The tagline: Inter, grey, its bullets in the word's color.
- kanzonas.com's logo: the mark and "Kanzonas" alone, the word centered on the mark.
Fonts (all SIL Open Font License 1.1, Google Fonts; licenses beside them): RobotoCondensed[wght].ttf,
SairaCondensed-SemiBold.ttf, Inter[opsz,wght].ttf.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
MARK = os.path.join(HERE, "artwork", "kanzonas-logo-artwork.png")
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
WEB = True                               # the website files too (brand/out/web/)
SS = 4                                   # drawn 4x and reduced: smooth edges
W, H = 936, 325                          # the layout, in px at 1x
BG = (249, 249, 249)
INK = (11, 12, 16)
CAP = 85                                 # capital height, px
CAP_TOP = 156
X0 = 306                                 # left edge of "Kanzonas"
WORDS = {
    "PDF": dict(top=(179, 0, 0), bottom=(128, 0, 0),
                tag="VIEW • EDIT • ANNOTATE • REVIEW", out="kanzonas-logo-source.png"),
    "CAD": dict(top=(113, 80, 184), bottom=(75, 50, 133),
                tag="SCHEMATICS • PANELS • WIRE NUMBERS", out="kanzonascad-logo.png"),
    "SVG": dict(top=(239, 125, 0), bottom=(179, 79, 0),
                tag="LOGOS • DRAWINGS • SCANS", out="kanzonassvg-logo.png"),
}


def font(name, cap_px, **axes):
    """The font with its capital H cap_px tall (measured as drawn)."""
    path = os.path.join(FONTS, name)
    size = cap_px * 1.4
    for _i in range(6):
        f = ImageFont.truetype(path, max(1, round(size)))
        if axes:
            ax = f.get_variation_axes()
            names = [a['name'] if isinstance(a['name'], str) else a['name'].decode() for a in ax]
            f.set_variation_by_axes([axes.get(n, a['default']) for n, a in zip(names, ax)])
        b = ink(f, "H")
        size *= cap_px / float(b[3] - b[1])
    return f


def ink(f, text):
    """The drawn box of text at (0, 0), measured on a drawing."""
    im = Image.new('L', (f.size * (len(text) + 3), f.size * 3), 0)
    ImageDraw.Draw(im).text((f.size, f.size), text, font=f, fill=255)
    b = im.getbbox()
    if b is None:                        # (a space: nothing drawn)
        return (0, 0, f.getlength(text), 0)
    return (b[0] - f.size, b[1] - f.size, b[2] - f.size, b[3] - f.size)


def layout(f, text, x, track):
    """[(char, x)] with the first letter's ink at x; returns it and the right edge of the ink."""
    out = []
    pos = x - ink(f, text[0])[0]
    right = x
    for ch in text:
        out.append((ch, pos))
        if ch != " ":
            right = pos + ink(f, ch)[2]
        pos += f.getlength(ch) + track * f.size
    return out, right


def draw(mask_img, f, placed, cap_top):
    d = ImageDraw.Draw(mask_img)
    top = ink(f, "H")[1]
    for ch, x in placed:
        d.text((x, cap_top - top), ch, font=f, fill=255)


def render(scale, transparent):
    """Both logos at scale (1 or 2), opaque or with a transparent background:
    {word: image}."""
    K = SS * scale                       # drawing units per layout px
    WO, HO = W * scale, H * scale

    def paint(base, mask_img, top_rgb, bottom_rgb, y0, y1):
        m = np.asarray(mask_img.resize((WO, HO), Image.LANCZOS)).astype(float)[..., None] / 255
        t = np.clip((np.arange(HO) / scale - y0) / float(y1 - y0), 0, 1)[:, None, None]
        col = np.array(top_rgb, float) + (np.array(bottom_rgb, float) - np.array(top_rgb, float)) * t
        return base * (1 - m) + col * m, m[..., 0]

    kan = font("RobotoCondensed[wght].ttf", CAP * K, Weight=500)
    word = font("SairaCondensed-SemiBold.ttf", CAP * K)
    tagf = font("Inter[opsz,wght].ttf", 15 * K, Weight=450)
    k_placed, k_right = layout(kan, "Kanzonas", X0 * K, -0.02)
    GAP = 16 * K                            # from "Kanzonas" to the colored word, as before
    # a round first letter (C) sits optically further away than a straight one (P): 3 px in
    starts = {"PDF": k_right + GAP, "CAD": k_right + GAP - 3 * K, "SVG": k_right + GAP - 3 * K}
    # Every word ends where the farther of "PDF" and "CAD" ends (as it always has: a word
    # added later is fitted to it and never moves the others).
    ends = {w: layout(word, w, starts[w], -0.02)[1] for w in ("PDF", "CAD")}
    R = max(ends.values())
    ref = "VIEW • EDIT • ANNOTATE • REVIEW"
    tag_track = (399 * K - tagf.getlength(ref)) / (len(ref) - 1) / tagf.size


    mark = Image.open(MARK).convert('RGB').resize((W, H)).resize((WO, HO), Image.LANCZOS)
    out = {}
    for w, spec in WORDS.items():
        # the spacing that makes this word end at R
        lo, hi = -0.1, 0.3
        for _i in range(30):
            mid = (lo + hi) / 2
            if layout(word, w, starts[w], mid)[1] > R:
                hi = mid
            else:
                lo = mid
        w_placed, w_right = layout(word, w, starts[w], lo)
        base = Image.new('RGB', (WO, HO), BG)
        base.paste(mark.crop((0, 0, 296 * scale, HO)), (0, 0))
        arr = np.asarray(base).astype(float)
        # what isn't background: the mark (by how far from the background it is), then each drawing
        alpha = np.clip(np.abs(arr - np.array(BG, float)).max(2) / 24.0, 0, 1)
        alpha[:, 296 * scale:] = 0
        m = Image.new('L', (W * K, H * K), 0)
        draw(m, kan, k_placed, CAP_TOP * K)
        arr, a_ = paint(arr, m, INK, INK, 0, 1)
        alpha = np.maximum(alpha, a_)
        m = Image.new('L', (W * K, H * K), 0)
        draw(m, word, w_placed, CAP_TOP * K)
        arr, a_ = paint(arr, m, spec["top"], spec["bottom"], CAP_TOP, CAP_TOP + CAP)
        alpha = np.maximum(alpha, a_)
        # the rule: a dot and a line in the word's color fading to grey, ending with the word
        m = Image.new('L', (W * K, H * K), 0)
        d = ImageDraw.Draw(m)
        y = 261 * K
        d.ellipse((X0 * K - 1 * K, y - 4 * K, X0 * K + 7 * K, y + 4 * K), fill=255)
        d.rectangle((X0 * K + 3 * K, y - 1.25 * K, R, y + 1.25 * K), fill=255)
        mr = np.asarray(m.resize((WO, HO), Image.LANCZOS)).astype(float)[..., None] / 255
        xs = np.clip((np.arange(WO) / scale - X0) / float(R / K - X0), 0, 1)[None, :, None]
        c0 = (np.array(spec["top"], float) + np.array(spec["bottom"], float)) / 2
        c1 = np.array((178, 178, 178), float)
        col = c0 + (c1 - c0) * xs ** 0.8
        arr = arr * (1 - mr) + col * mr
        alpha = np.maximum(alpha, mr[..., 0])
        # the tagline
        t_placed, _r = layout(tagf, spec["tag"], 308 * K, tag_track)
        grey = Image.new('L', (W * K, H * K), 0)
        dots = Image.new('L', (W * K, H * K), 0)
        top = ink(tagf, "H")[1]
        for ch, x in t_placed:
            ImageDraw.Draw(dots if ch == "•" else grey).text((x, 284 * K - top), ch, font=tagf, fill=255)
        arr, a_ = paint(arr, grey, (100, 100, 104), (100, 100, 104), 0, 1)
        alpha = np.maximum(alpha, a_)
        arr, a_ = paint(arr, dots, spec["top"], spec["top"], 0, 1)
        alpha = np.maximum(alpha, a_)
        if transparent:
            # the colors as they'd be with no background under them, and how solid each pixel is
            a = np.clip(alpha, 1e-6, 1)[..., None]
            rgb = np.clip((arr - np.array(BG, float) * (1 - a)) / a, 0, 255)
            img = Image.fromarray(np.dstack([rgb, alpha[..., None] * 255]).round().astype(np.uint8), 'RGBA')
        else:
            img = Image.fromarray(arr.round().astype(np.uint8))
        out[w] = (img, w_placed, w_right, lo)
    return out


def render_home(scale, transparent):
    """kanzonas.com's logo at scale (1 or 2): the mark and "Kanzonas", the word's capitals
    centered on the logo's height, drawn exactly as in the apps' logos (same font, size, place
    from the mark)."""
    K = SS * scale
    HO = H * scale
    kan = font("RobotoCondensed[wght].ttf", CAP * K, Weight=500)
    k_placed, k_right = layout(kan, "Kanzonas", X0 * K, -0.02)
    w1 = int(np.ceil(k_right / K)) + 8           # the word's right edge and a margin, at 1x
    WO = w1 * scale
    cap_top = (H - CAP) / 2.0
    mark = Image.open(MARK).convert('RGB').resize((W, H)).resize((W * scale, HO), Image.LANCZOS)
    base = Image.new('RGB', (WO, HO), BG)
    base.paste(mark.crop((0, 0, 296 * scale, HO)), (0, 0))
    arr = np.asarray(base).astype(float)
    alpha = np.clip(np.abs(arr - np.array(BG, float)).max(2) / 24.0, 0, 1)
    alpha[:, 296 * scale:] = 0
    m = Image.new('L', (w1 * K, H * K), 0)
    draw(m, kan, k_placed, cap_top * K)
    mm = np.asarray(m.resize((WO, HO), Image.LANCZOS)).astype(float)[..., None] / 255
    arr = arr * (1 - mm) + np.array(INK, float) * mm
    alpha = np.maximum(alpha, mm[..., 0])
    if transparent:
        a = np.clip(alpha, 1e-6, 1)[..., None]
        rgb = np.clip((arr - np.array(BG, float) * (1 - a)) / a, 0, 255)
        return Image.fromarray(np.dstack([rgb, alpha[..., None] * 255]).round().astype(np.uint8), 'RGBA')
    return Image.fromarray(arr.round().astype(np.uint8))


for w, (img, placed, right, track) in render(1, False).items():
    img.save(os.path.join(OUT, WORDS[w]["out"]))
    print(w, "letters from", round(placed[0][1] / SS), "to", round(right / SS), "spacing %.3f" % track)
web = os.path.join(OUT, "web")
os.makedirs(web, exist_ok=True)
names = {"PDF": "kanzonaspdf-logo", "CAD": "kanzonascad-logo", "SVG": "kanzonassvg-logo"}
for scale, transparent, suffix in ((1, False, ""), (2, False, "@2x"), (1, True, "-transparent"),
                                   (2, True, "-transparent@2x")):
    for w, (img, *_rest) in render(scale, transparent).items():
        img.save(os.path.join(web, names[w] + suffix + ".png"))
    render_home(scale, transparent).save(os.path.join(web, "kanzonas-logo" + suffix + ".png"))
print("files in", OUT)

# the website's own copies (each Cloudflare Pages project sees only its folder)
for src, dst in (("kanzonas-logo-transparent@2x.png", "home/kanzonas-logo.png"),
                 ("kanzonaspdf-logo-transparent@2x.png", "pdf/kanzonaspdf-logo.png"),
                 ("kanzonascad-logo-transparent@2x.png", "cad/kanzonascad-logo.png")):
    shutil.copyfile(os.path.join(web, src), os.path.join(SITE, dst))
    print("copied to", dst)
