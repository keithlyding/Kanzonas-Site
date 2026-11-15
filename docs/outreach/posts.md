# Posts to share the apps (drafts for Keith to edit and post)

Drafts, written Nov 2026, in Keith's voice. **Edit them into your own words before posting**:
communities can tell a pasted ad from a person, and your own story (20 years in controls, the
frustration with AutoCAD Electrical, having AI write the apps you needed) is what makes people
listen. Say up front that the apps are made with AI: people respect it when you say so and
turn on you if they find out later. Check each community's rules on AI-made projects too;
some restrict them.

How to post (from the Nov 2026 plan in docs/ROADMAP.md):
- One community at a time, a few days apart, so you can answer every comment and see in the
  Monday summary's "Came from" line which post brought people.
- Read each community's rules first (many have a self-promotion rule or a weekly thread for it).
- Ask for feedback rather than announcing; reply to everything, including criticism.
- Best time: a weekday morning, US Eastern time.

Facts in these drafts come from the apps' READMEs and release notes (Nov 2026). If an app has
changed since, check the numbers before posting.

---

## 1. Hacker News: Show HN (KanzonasSVG)

Rules: https://news.ycombinator.com/showhn.html (it must be something people can try; link the
GitHub repo or the site; be there to answer questions).

**Title** (HN keeps titles short and plain):

    Show HN: KanzonasSVG – Inkscape's bitmap tracing, fixed and made into an app

**URL:** https://github.com/keithlyding/KanzonasSVG

**Text** (first comment, posted right after):

> I needed to turn logos and scanned drawings into SVGs and kept fixing Inkscape's Trace Bitmap
> output by hand: colors a step off, rings of in-between shades around letters, Autotrace filling
> in the holes of an O (or turning a smiley into a black disc). So I had AI coding assistants
> take the tracing code (Potrace and Autotrace, as Inkscape uses them) out of Inkscape and fix
> those, with me testing every change on real pictures.
>
> Measured against Inkscape's own code (its development version, whose tracing is the same as
> 1.4.4's), same pictures, every SVG rendered by rsvg-convert and compared with the picture,
> pixels clearly the wrong color: a two-color logo 1.6% -> 0.26%, a flat illustration 1.7% ->
> 0.29%, a floor plan of thin lines 0.87% -> 0.002%. The full tables, including where it's slower
> and makes bigger files, are in the README.
>
> It picks settings per picture (exact colors for flat art up to 64, smoothing for photos,
> background, line art), shows the SVG beside the picture, and has a command line for batches.
> Windows and Linux, GPL, nothing uploaded. The fixes were offered back to Inkscape as
> inkscape!8302.
>
> It doesn't edit SVGs and doesn't do pixel art (Depixelize). I'd love to hear where it falls
> down: send me a picture that traces badly.

---

## 2. Reddit r/cricut (KanzonasSVG)

Check the sub's rules on self-promotion first; some crafting subs only allow it in a weekly
thread.

**Title:**

    I had AI write me a free image-to-SVG converter that runs on your computer (no upload, no watermark)

**Text:**

> Every free PNG-to-SVG converter I tried either wanted a subscription to download, added a
> watermark, or uploaded my picture to who-knows-where. So I had AI write one for me, KanzonasSVG,
> and it turned out good enough to share. Open a picture,
> it picks the settings, and the SVG appears next to it. Logos and flat designs come out with
> their exact colors and clean edges, and it can remove the background. Then save the SVG and
> open it in Design Space.
>
> Free, open source, Windows and Linux (sorry, no Mac yet): https://svg.kanzonas.com
>
> Before/after: [attach the sunflower screenshot]
>
> If you have a design that traces badly, I'd really like to see it: that's how I'm improving it.

Other places for the same post (adapt the wording): r/silhouettecutters, r/lasercutting,
r/vinyl, r/Inkscape, r/svg.

---

## 3. Reddit r/PLC (KanzonasCAD)

r/PLC is controls engineers and techs: talk to them as one of them.

**Title:**

    After 20 years in controls and plenty of AutoCAD Electrical frustration, I had AI write me an alternative. It's good enough to share (free, open source)

**Text:**

> I've spent 20 years in industrial electrical and controls, a lot of it drawing schematics
> and panel layouts in AutoCAD Electrical. It does the job, but the subscription, the 30-day
> sign-in and the number of ways it can surprise you finally got to me. With how advanced AI
> has gotten, I decided to see if it could write one for me: KanzonasCAD, an electrical CAD
> program that works the AutoCAD way (command line, snaps, grips) with a much shorter list of
> commands. It ended up doing everything I needed and more, so I'm sharing it.
>
> What it does today: JIC/NFPA symbols, device tags by page (CR601), contacts linked to their
> coil with cross-references that update themselves, wire numbers by page (6001) with
> distribution blocks, terminal strips, PLC I/O points, panel layouts at scale with DIN rail and
> duct, a bill of materials and cable pull lists. It opens DWG and DXF, and AutoCAD Electrical's
> attributes come in as tags and parts.
>
> What it doesn't do yet: wire lists, terminal strip reports, multi-user check-out. It's
> version 0.x, US practice only (no IEC).
>
> Free, MIT, Windows and Linux: https://cad.kanzonas.com
>
> I'd value honest feedback from people who do this every day: what would stop you using it on
> a real job?

Other places: PLCtalk.net (Industrial Automation forum: introduce yourself first, then a thread),
eng-tips.com (electrical engineering forums), r/electricians, r/AskEngineers (only as an answer
to a relevant question, not a post).

---

## 4. Reddit r/estimators or r/Construction (KanzonasPDF)

**Title:**

    Free alternative to Bluebeam for takeoffs and markups (open source, no subscription)

**Text:**

> I use PDFs of drawings every day and wanted Bluebeam-style tools without the subscription, so I
> had AI write them for me: KanzonasPDF. It does everything I needed, so I'm sharing it. Calibrate from the title block or a known dimension, then length, area,
> perimeter, volume and counts with snapping, exported to CSV. Named spaces (Room 101) so the
> markups list filters room by room, revision clouds, stamps with your name and date, a tool
> chest, legends, and compare two revisions with the changes clouded.
>
> Markups are standard PDF annotations, so people on Bluebeam or Acrobat see them. It's fast on
> big sheets, runs offline with no account, and runs from a USB stick.
>
> Free, Windows, Mac (Apple silicon) and Linux: https://pdf.kanzonas.com/bluebeam-alternative
>
> What it doesn't have: cloud collaboration (Studio-style live sessions). If you try it on a real
> set, I'd like to hear what's missing for your work.

Other places: r/architecture, r/civilengineering (as an answer where someone asks for a free
Bluebeam alternative), r/software, r/opensource, r/linux (lead with "it runs on Linux").

---

## 5. One-line answers (for "is there a free X?" questions)

Reply only where someone is actually asking; say it's your app.

- PDF: "I make a free, open-source one, KanzonasPDF (Windows, Mac, Linux): calibrated
  measuring, revision clouds, compare, no subscription. https://pdf.kanzonas.com/bluebeam-alternative
  (disclosure: it's mine, made with AI)"
- CAD: "I had AI write me a free AutoCAD Electrical alternative, KanzonasCAD: wire numbers,
  cross-references, JIC symbols, opens DWG. https://cad.kanzonas.com (disclosure: it's mine, made with AI)"
- SVG: "KanzonasSVG is free and runs offline, so nothing gets uploaded: it keeps a logo's exact
  colors. https://svg.kanzonas.com (disclosure: it's mine, made with AI)"
