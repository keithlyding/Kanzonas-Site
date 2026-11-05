"""The link-preview pictures (Open Graph / Twitter cards) for the three sites, from the logos.

    python brand/make_social.py

Run brand/make_logos.py first. Reads brand/out/web/*-logo-transparent@2x.png and writes a
1200 x 630 picture (the size Facebook, LinkedIn, Slack and X show best) into each site folder:
home/og-image.png, pdf/og-image.png, cad/og-image.png. The logo is centered on white with a
band of the app's color along the bottom (kanzonas.com: the sunflower's yellow).
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
WEB = os.path.join(HERE, "out", "web")
W, H = 1200, 630
BAND = 14                                # the colored band along the bottom, px
SITES = (
    ("kanzonas-logo-transparent@2x.png", "home", (242, 183, 5), 760),     # sunflower yellow
    ("kanzonaspdf-logo-transparent@2x.png", "pdf", (179, 0, 0), 1000),    # PDF red (#b30000)
    ("kanzonascad-logo-transparent@2x.png", "cad", (113, 80, 184), 1000),  # CAD violet (#7150b8)
)

for src, folder, color, logo_w in SITES:
    logo = Image.open(os.path.join(WEB, src)).convert("RGBA")
    logo = logo.resize((logo_w, round(logo.height * logo_w / logo.width)), Image.LANCZOS)
    img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    img.alpha_composite(logo, ((W - logo.width) // 2, (H - BAND - logo.height) // 2))
    img.paste(color + (255,), (0, H - BAND, W, H))
    out = os.path.join(SITE, folder, "og-image.png")
    img.convert("RGB").save(out, optimize=True)
    print("wrote", os.path.relpath(out, SITE))
