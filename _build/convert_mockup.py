#!/usr/bin/env python3
"""Convert a design-tool mockup page (*.dc.html) into a page body for build.py.

    python _build/convert_mockup.py <handoff>/pages/Dentists.dc.html
    python _build/convert_mockup.py <handoff>/pages/*.dc.html

For each mockup this strips the design-tool wrapper (support.js, <x-dc>,
<helmet>, the trailing text/x-dc script), drops the mockup's own header and
footer (build.py adds the shared partials), rewrites the mockup links to the
live URLs, and swaps the repeated inline styles for the classes in
assets/site.css. A style that is not in the table below stays inline, so a
one-off layout is never lost; the script lists every style it left inline so
the table can be extended when a new mockup introduces one.

Wording is copied byte for byte. Never edit copy here; a wording change goes
back to the mockup first (brief, section 8).

Output: _src/pages/<slug>.html — the page body only. Run build.py afterwards.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "_src" / "pages"

# mockup file stem -> (page slug, live URL)
PAGES = {
    "Main": ("index", "/"),
    "BrandStudy": ("study", "/study/"),
    "HowWeMeasure": ("how-we-measure", "/how-we-measure/"),
    "Dentists": ("studies-dentists", "/studies/dentists/"),
    "Toronto": ("studies-toronto", "/studies/toronto/"),
    "Sources": ("studies-sources", "/studies/sources/"),
    "PILaw": ("studies-injury-law-ontario", "/studies/injury-law-ontario/"),
    "AskTwice": ("studies-ask-twice", "/studies/ask-twice/"),
    "CokePepsi": ("lab-coke-or-pepsi", "/lab/coke-or-pepsi/"),
    "About": ("about", "/about/"),
}

# href rewrites, applied in order (longest first so "Main.dc.html#x" wins over "Main.dc.html")
LINKS = [
    ("Main.dc.html#lab-notes", "/#lab-finds"),
    ("Main.dc.html#studies", "/#studies"),
    ("Main.dc.html#commission", "/study/#request"),
    ("Main.dc.html", "/"),
    ("#lab-notes", "#lab-finds"),
    ("#commission", "/study/#request"),
] + [(f"{stem}.dc.html", url) for stem, (_, url) in PAGES.items() if stem != "Main"]

# exact inline style -> classes, or (classes, residual inline style)
STYLES = {
    # --- links and inline text
    "color: #5B6478": "c-muted",
    "color: #3D4658; text-decoration: none": "c-ink2",
    "color: #0B1220": "c-ink",
    "color: #0F7A52": "c-green",
    "font-weight: 600": "fw-600",
    "font-weight: 600; font-size: 17px": "b17",
    "font-weight: 600; font-size: 18px": "b18",
    "font-weight: 600; font-size: 19px": "b19",
    "font-weight: 600; color: #0A5C3D": "card-lab__go",
    "font-size: 14px; font-weight: 600; color: #0F7A52": "go-14",
    "font-size: 15px; font-weight: 600; color: #0F7A52": "go-15",
    "font-size: 16px; line-height: 1.6; color: #3D4658": "s16",
    "font-size: 15px; line-height: 1.6; color: #3D4658": "t15",
    "font-size: 17px; line-height: 1.6; color: #3D4658": "s17",
    "font-size: 13px; color: #5B6478; font-family: 'IBM Plex Mono', monospace": "card-study__meta",
    "font-size: 13px; color: #0A5C3D; font-family: 'IBM Plex Mono', monospace": "card-lab__meta",
    "font-family: 'IBM Plex Serif', Georgia, serif; font-size: 27px; font-weight: 600; line-height: 1.2": "card-study__t",
    "font-family: 'IBM Plex Serif', Georgia, serif; font-size: 25px; font-weight: 600; line-height: 1.25": "card-lab__t",
    "margin-top: auto; padding-top: 8px; font-weight: 600; color: #0F7A52": "card-study__go",
    "font-family: 'IBM Plex Mono', monospace; color: #0B1220": "mono c-ink",
    "font-family: 'IBM Plex Mono', monospace; color: #0B1220; white-space: nowrap": "mono c-ink nowrap",
    "font-family: 'IBM Plex Mono', monospace; color: #0F7A52": "mono c-green",
    "font-family: 'IBM Plex Mono', monospace": "mono",
    "font-family: 'IBM Plex Mono', monospace; font-size: 15px; color: #0F7A52; padding-top: 3px": "step__num",
    "font-size: 14px; color: #5B6478": "t14-muted",
    "display: inline-flex; align-items: center; gap: 6px": "legend__item",
    "width: 12px; height: 12px; border-radius: 3px; background: #0F7A52": "swatch",
    "width: 12px; height: 12px; border-radius: 3px; background: #0B1220": "swatch swatch--ink",
    "width: 12px; height: 12px; border-radius: 3px; background: #E1E6EF; border: 1px solid #C9D0DC": "swatch swatch--empty",
    "width: 36px; height: 36px; border-radius: 8px; background: #0F7A52": "ask",
    "width: 36px; height: 36px; border-radius: 8px; background: #FFFFFF; border: 1px solid #D5DBE6": "ask ask--empty",
    "flex: 0 0 auto; width: 40px; height: 40px; border-radius: 999px; background: #0F7A52; color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-family: 'IBM Plex Mono', monospace; font-size: 16px": "step__n",
    "padding: 7px 13px; border-radius: 999px; font-size: 14px; color: #0A5C3D; background: #E7F6EF": "chip",
    "padding: 10px 16px; border-radius: 999px; border: 1px solid #E1E6EF; font-size: 16px; color: #0B1220": "chip--outline",
    "list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 8px": "chips",
    "margin: 0 0 18px; display: inline-block; padding: 6px 12px; border-radius: 999px; background: #E7F6EF; font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: #0A5C3D": "tag",
    # --- headings
    "margin: 0; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: clamp(36px, 5vw, 60px); line-height: 1.08; letter-spacing: -0.02em; color: #0B1220": "h1",
    "margin: 0; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: clamp(40px, 5.6vw, 68px); line-height: 1.06; letter-spacing: -0.02em; color: #0B1220": "h1 h1--home",
    "margin: 0; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: 34px; letter-spacing: -0.01em; color: #0B1220": "h2",
    "margin: 0; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: 34px; line-height: 1.2; letter-spacing: -0.01em; color: #0B1220": "h2 lh-12",
    "margin: 0; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: 40px; letter-spacing: -0.01em; color: #0B1220": "h2-40",
    "margin: 0; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: 38px; letter-spacing: -0.01em; color: #0B1220": "h2-38",
    "margin: 0 0 32px; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: 38px; letter-spacing: -0.01em; color: #0B1220": "h2-38 mb-32",
    "margin: 0; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: 32px; letter-spacing: -0.01em; color: #0B1220": "h2-32",
    "margin: 0; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: 30px; color: #0B1220": "h2-30",
    "margin: 0; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: 30px; line-height: 1.2; color: #0B1220": "h2-30 lh-12",
    "margin: 64px 0 0; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: 30px; color: #0B1220": "h2-30 mt-64",
    "margin: 0; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: 28px; color: #0B1220": "h2-28",
    "margin: 0 0 16px; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: 28px; color: #0B1220": "h2-28 mb-16",
    "margin: 0; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: 26px; color: #0B1220": "h2-26",
    "margin: 0; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: 26px; color: #0A5C3D": "h2-26 c-gd",
    "margin: 0; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: 34px; line-height: 1.15": "cta__h",
    "margin: 0; font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; font-size: clamp(30px, 4vw, 46px); line-height: 1.12; letter-spacing: -0.015em": "cta__h cta__h--home",
    "margin: 14px 0 0; font-size: 18px; line-height: 1.65; color: #D7EFE4": "cta__p",
    "margin: 20px 0 0; font-size: 19px; line-height: 1.65; max-width: 640px; color: #D7EFE4": ("cta__p mt-20 mw-640", "font-size: 19px"),
    "margin: 0; font-size: 24px; font-weight: 600; line-height: 1.3; color: #0B1220": "h3",
    "margin: 10px 0 0; font-size: 22px; font-weight: 600; line-height: 1.3; color: #0B1220": "h3-22 mt-10",
    "margin: 0; font-size: 21px; font-weight: 600; color: #0B1220": "h3-21",
    "margin: 0; font-size: 20px; font-weight: 600; color: #0B1220": "h3-20",
    "margin: 0; font-size: 18px; font-weight: 600; color: #0B1220": "h-18",
    # --- eyebrows, crumbs, meta
    "margin: 0 0 12px; font-size: 14px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: #0F7A52": "eyebrow",
    "margin: 0 0 20px; font-size: 14px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: #0F7A52": "eyebrow mb-20",
    "margin: 40px 0 14px; font-size: 14px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: #0F7A52": "eyebrow mt-40 mb-14",
    "margin: 0 0 20px; font-size: 15px; color: #5B6478": "crumbs",
    "margin: 20px 0 0; font-family: 'IBM Plex Mono', monospace; font-size: 13px; line-height: 1.6; color: #5B6478": "hero-meta",
    "margin: 0 0 10px; font-family: 'IBM Plex Mono', monospace; font-size: 14px; color: #0F7A52": "fnum",
    "margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 14px; color: #0F7A52": "mono-14",
    "margin: 6px 0 0; font-family: 'IBM Plex Mono', monospace; font-size: 14px; color: #0F7A52": "mono-14 mt-6",
    # --- body text
    "margin: 24px 0 0; font-size: 21px; line-height: 1.6; color: #3D4658": "lead mt-24",
    "margin: 20px 0 0; font-size: 19px; line-height: 1.7; color: #3D4658": "t19 mt-20",
    "margin: 18px 0 0; max-width: 760px; font-size: 19px; line-height: 1.7; color: #3D4658": "t19 mt-18 mw-760",
    "margin: 28px 0 0; max-width: 620px; font-size: 20px; line-height: 1.65; color: #3D4658": ("t17-165 mt-28 mw-620", "font-size: 20px"),
    "margin: 16px 0 0; font-size: 18px; line-height: 1.7; color: #3D4658": "t18 mt-16",
    "margin: 14px 0 0; font-size: 18px; line-height: 1.7; color: #3D4658": "t18 mt-14",
    "margin: 16px 0 32px; max-width: 720px; font-size: 18px; line-height: 1.7; color: #3D4658": "t18 mt-16 mb-32 mw-720",
    "margin: 16px 0 0; max-width: 760px; font-size: 18px; line-height: 1.7; color: #3D4658": "t18 mt-16 mw-760",
    "margin: 18px 0 0; font-size: 18px; line-height: 1.75; color: #3D4658": "t18-175 mt-18",
    "margin: 16px 0 0; font-size: 18px; line-height: 1.75; color: #3D4658": "t18-175 mt-16",
    "margin: 18px 0 0; max-width: 720px; font-size: 18px; line-height: 1.75; color: #3D4658": "t18-175 mt-18 mw-720",
    "margin: 14px 0 0; font-size: 17px; line-height: 1.7; color: #3D4658": "t17 mt-14",
    "margin: 14px 0 0; max-width: 720px; font-size: 17px; line-height: 1.7; color: #3D4658": "t17 mt-14 mw-720",
    "margin: 12px 0 0; font-size: 17px; line-height: 1.7; color: #3D4658": "t17 mt-12",
    "margin: 10px 0 0; font-size: 17px; line-height: 1.7; color: #3D4658": "t17 mt-10",
    "margin: 8px 0 0; font-size: 17px; line-height: 1.7; color: #3D4658": "t17 mt-8",
    "margin: 16px 0 0; font-size: 17px; line-height: 1.7; color: #3D4658": "t17 mt-16",
    "margin: 20px 0 0; font-size: 17px; line-height: 1.7; color: #3D4658": "t17 mt-20",
    "margin: 24px 0 0; font-size: 17px; line-height: 1.7; color: #3D4658": "t17 mt-24",
    "margin: 24px 0 0; max-width: 720px; font-size: 17px; line-height: 1.7; color: #3D4658": "t17 mt-24 mw-720",
    "margin: 12px 0 0; font-size: 17px; line-height: 1.7; color: #0A5C3D": "t17 mt-12 c-gd",
    "margin: 8px 0 0; font-size: 17px; line-height: 1.65; color: #3D4658": "t17-165 mt-8",
    "margin: 12px 0 0; font-size: 17px; line-height: 1.65; color: #3D4658": "t17-165 mt-12",
    "margin: 16px 0 0; font-size: 17px; line-height: 1.65; color: #3D4658": "t17-165 mt-16",
    "margin: 0 0 16px; font-size: 17px; line-height: 1.65; color: #3D4658": "t17-165 mb-16",
    "margin: 8px 0 0; font-size: 16px; line-height: 1.65; color: #3D4658": "t16 mt-8",
    "margin: 10px 0 0; font-size: 16px; line-height: 1.65; color: #3D4658": "t16 mt-10",
    "margin: 14px 0 0; font-size: 16px; line-height: 1.65; color: #3D4658": "t16 mt-14",
    "margin: 28px 0 0; max-width: 760px; font-size: 16px; line-height: 1.65; color: #5B6478": "t16 mt-28 mw-760 c-muted",
    "margin: 10px 0 0; font-size: 16px; line-height: 1.7; color: #3D4658": "t16-17 mt-10",
    "margin: 6px 0 0; font-size: 16px; line-height: 1.7; color: #3D4658": "t16-17 mt-6",
    "margin: 10px 0 0; font-size: 16px; line-height: 1.7; color: #5B6478": "note mt-10",
    "margin: 6px 0 0; font-size: 15px; line-height: 1.6; color: #3D4658": "t15 mt-6",
    "margin: 6px 0 0; font-size: 15px; line-height: 1.6; color: #0A5C3D": "t15 mt-6 c-gd",
    "margin: 0; font-size: 15px; line-height: 1.55; color: #3D4658": "t15-155",
    "margin: 0; font-size: 15px; line-height: 1.55; color: #0A5C3D": "t15-155",
    "margin: 10px 0 0; font-size: 15px; line-height: 1.55; color: #0A5C3D": "t15-155 mt-10 c-gd",
    "margin: 8px 0 0; font-size: 15px; line-height: 1.6; color: #5B6478": "t15-muted mt-8",
    "margin: 16px 0 0; font-size: 15px; line-height: 1.6; color: #5B6478": "t15-muted mt-16",
    "margin: 22px 0 0; font-size: 15px; line-height: 1.6; color: #5B6478": "t15-muted mt-22",
    "margin-top: 18px; font-size: 15px; line-height: 1.55; color: #5B6478": ("t15-muted mt-18", "line-height: 1.55"),
    "margin: 12px 0 0; font-size: 14px; color: #5B6478": "t14-muted mt-12",
    "margin: 4px 0 0; font-size: 14px; color: #5B6478": "t14-muted mt-4",
    "margin: 6px 0 24px; font-size: 16px; color: #5B6478": ("t14-muted mt-6 mb-24", "font-size: 16px"),
    "margin: 8px 0 0; font-size: 14px; color: #3D4658": "t14-ink2 mt-8",
    "margin: 0; font-size: 14px; color: #3D4658": "t14-ink2",
    "margin: 2px 0 0; font-size: 14px; color: #3D4658": "t14-ink2 mt-2",
    "margin: 8px 0 0; font-size: 14px; color: #0A5C3D": "t14-gd mt-8",
    "margin: 0; font-weight: 600; font-size: 17px; color: #0B1220": "kicker",
    "margin: 8px 0 0; font-weight: 600; font-size: 17px; color: #0B1220": "kicker mt-8",
    "margin: 0; font-weight: 600; font-size: 17px; color: #0A5C3D": "kicker c-gd",
    "margin: 36px 0 16px; font-size: 15px; font-weight: 600; color: #0B1220": ("kicker mt-36 mb-16", "font-size: 15px"),
    "margin: 0; font-size: 16px; line-height: 1.6; color: #0B1220": "quote__text",
    "margin: 0; font-size: 19px; font-weight: 600; line-height: 1.35; color: #0B1220": "hero-card__t",
    "margin: 0; font-size: 19px; font-weight: 600; line-height: 1.35; color: #0A5C3D": "hero-card__t",
    "margin-top: auto; padding-top: 4px; font-size: 14px; font-weight: 600; color: #0F7A52": "hero-card__go",
    "margin-top: auto; padding-top: 4px; font-size: 14px; font-weight: 600; color: #0A5C3D": "hero-card__go",
    "margin: 16px 0 0": "mt-16",
    "margin: 24px 0 0": "mt-24",
    "margin: 20px 0 0": "mt-20",
    "margin: 32px 0 0": "mt-32",
    # --- figures
    "margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 40px; color: #0A5C3D": "fig fig-40",
    "margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 40px; color: #0B1220": "fig fig-40 c-ink",
    "margin: 12px 0 0; font-family: 'IBM Plex Mono', monospace; font-size: 40px; color: #0B1220": "fig fig-40 c-ink mt-12",
    "margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 40px; white-space: nowrap; color: #0A5C3D": "fig fig-40 nowrap",
    "margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 40px; white-space: nowrap; color: #0B1220": "fig fig-40 nowrap c-ink",
    "margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 34px; color: #0A5C3D": "fig fig-34",
    "margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 34px; color: #0B1220": "fig fig-34 c-ink",
    "margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 34px; white-space: nowrap; color: #0A5C3D": "fig fig-34 nowrap",
    "margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 34px; white-space: nowrap; color: #0B1220": "fig fig-34 nowrap c-ink",
    "margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 32px; white-space: nowrap; color: #0A5C3D": "fig fig-32 nowrap",
    "margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 32px; white-space: nowrap; color: #0B1220": "fig fig-32 nowrap c-ink",
    "margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 28px; white-space: nowrap; color: #0B1220": "fig fig-28 nowrap c-ink",
    "margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 28px; white-space: nowrap; color: #0A5C3D": "fig fig-28 nowrap",
    "margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 28px; color: #0A5C3D": "fig fig-28",
    "margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 48px; font-weight: 500; letter-spacing: -0.02em; color: #0B1220": "fig fig-48 c-ink",
    "margin: 4px 0 0; font-family: 'IBM Plex Mono', monospace; font-size: 34px; line-height: 1.1; white-space: nowrap; color: #0B1220": "fig fig-34 lh-11 nowrap c-ink mt-4",
    "margin: 4px 0 0; font-family: 'IBM Plex Mono', monospace; font-size: 34px; line-height: 1.1; white-space: nowrap; color: #0A5C3D": "fig fig-34 lh-11 nowrap mt-4",
    "margin: 6px 0 0; font-family: 'IBM Plex Mono', monospace; font-size: 26px; color: #0B1220": "stat-tile__v",
    # --- layout: sections and wraps
    "background: #F6F8FB; border-bottom: 1px solid #E1E6EF": "band-alt",
    "background: #F6F8FB; border-top: 1px solid #E1E6EF; border-bottom: 1px solid #E1E6EF": "band-alt band-alt--rules",
    "background: #062418; color: #FFFFFF": "band-forest",
    "background: #062418; color: #FFFFFF; margin-top: 72px": "band-forest mt-72",
    "background: #FFFFFF": "",
    "max-width: 920px; margin: 0 auto; padding: 72px 24px 0": "wrap pt-72 pb-0",
    "max-width: 920px; margin: 0 auto; padding: 72px 24px 24px": "wrap pt-72 pb-24",
    "max-width: 920px; margin: 0 auto; padding: 72px 24px 64px": "wrap pt-72 pb-64",
    "max-width: 920px; margin: 0 auto; padding: 72px 24px 88px": "wrap pt-72 pb-88",
    "max-width: 920px; margin: 0 auto; padding: 64px 24px 0": "wrap pt-64 pb-0",
    "max-width: 920px; margin: 0 auto; padding: 64px 24px 24px": "wrap pt-64 pb-24",
    "max-width: 920px; margin: 0 auto; padding: 56px 24px 0": "wrap pt-56 pb-0",
    "max-width: 920px; margin: 0 auto; padding: 56px 24px 72px": "wrap pt-56 pb-72",
    "max-width: 920px; margin: 0 auto; padding: 48px 24px": "wrap pt-48 pb-48",
    "max-width: 920px; margin: 0 auto; padding: 48px 24px 0": "wrap pt-48 pb-0",
    "max-width: 920px; margin: 0 auto; padding: 80px 24px 72px": "wrap pt-80 pb-72",
    "max-width: 920px; margin: 0 auto; padding: 80px 24px; display: flex; flex-wrap: wrap; gap: 28px; align-items: center; justify-content: space-between": "wrap pt-80 pb-80 cta__in",
    "max-width: 1200px; margin: 0 auto; padding: 96px 24px; display: flex; flex-wrap: wrap; gap: 32px; align-items: center; justify-content: space-between": "wrap wrap--wide pt-96 pb-96 cta__in gap-32",
    "max-width: 1200px; margin: 0 auto; padding: 80px 24px; display: flex; flex-wrap: wrap; gap: 32px; align-items: center; justify-content: space-between": "wrap wrap--wide pt-80 pb-80 cta__in gap-32",
    "max-width: 1200px; margin: 0 auto; padding: 96px 24px 88px; display: flex; flex-wrap: wrap; gap: 56px; align-items: center": "wrap wrap--wide pt-96 pb-88 cols gap-56 ac",
    "max-width: 1200px; margin: 0 auto; padding: 96px 24px; display: flex; flex-wrap: wrap; gap: 56px; align-items: center": "wrap wrap--wide pt-96 pb-96 cols gap-56 ac",
    "max-width: 1200px; margin: 0 auto; padding: 88px 24px; display: flex; flex-wrap: wrap; gap: 32px; align-items: center": "wrap wrap--wide pt-88 pb-88 cols gap-32 ac",
    "max-width: 1200px; margin: 0 auto; padding: 96px 24px 0": "wrap wrap--wide pt-96 pb-0",
    "max-width: 1200px; margin: 0 auto; padding: 96px 24px": "wrap wrap--wide pt-96 pb-96",
    # --- flex rows and columns
    "display: flex; flex-wrap: wrap; gap: 32px; align-items: center": "cols gap-32 ac",
    "display: flex; flex-wrap: wrap; gap: 32px": "cols gap-32",
    "display: flex; flex-wrap: wrap; gap: 40px": "cols gap-40",
    "display: flex; flex-wrap: wrap; gap: 14px": "cols gap-14",
    "display: flex; flex-wrap: wrap; gap: 18px": "cols gap-18",
    "display: flex; flex-wrap: wrap; gap: 8px": "cols gap-8",
    "margin-top: 28px; display: flex; flex-wrap: wrap; gap: 16px": "cols gap-16 mt-28",
    "margin-top: 28px; display: flex; flex-wrap: wrap; gap: 14px": "cols gap-14 mt-28",
    "margin-top: 28px; display: flex; flex-wrap: wrap; gap: 10px": "cols gap-10 mt-28",
    "margin-top: 24px; display: flex; flex-wrap: wrap; gap: 14px": "cols gap-14 mt-24",
    "margin-top: 24px; display: flex; flex-wrap: wrap; gap: 16px": "cols gap-16 mt-24",
    "margin-top: 36px; display: flex; flex-wrap: wrap; gap: 20px": "cols gap-20 mt-36",
    "margin-top: 36px; display: flex; flex-wrap: wrap; gap: 12px": "cols gap-12 mt-36",
    "margin-top: 40px; display: flex; flex-wrap: wrap; gap: 20px": "cols gap-20 mt-40",
    "display: flex; flex-direction: column; gap: 14px": "col gap-14",
    "display: flex; flex-direction: column; gap: 16px": "col gap-16",
    "display: flex; flex-direction: column; gap: 18px": "col gap-18",
    "margin-top: 28px; display: flex; flex-direction: column; gap: 14px": "col gap-14 mt-28",
    "margin-top: 28px; display: flex; flex-direction: column; gap: 18px": "col gap-18 mt-28",
    "list-style: none; margin: 28px 0 0; padding: 0; display: flex; flex-wrap: wrap; gap: 16px": "list cols gap-16 mt-28",
    "list-style: none; margin: 32px 0 0; padding: 0; display: flex; flex-direction: column; gap: 14px": "list col gap-14 mt-32",
    "list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px": "query-list",
    "margin: 0; padding-left: 20px; display: flex; flex-direction: column; gap: 12px; font-size: 17px; line-height: 1.65; color: #3D4658": "how-list",
    "margin: 40px 0 0; display: flex; flex-wrap: wrap; gap: 14px": "stats",
    "flex: 1 1 380px; min-width: 0": "f-380",
    "flex: 1 1 460px; min-width: 0": "f-460",
    "flex: 1 1 440px; min-width: 0": "f-440",
    "flex: 1 1 560px; min-width: 0": "f-560",
    "flex: 1 1 420px; min-width: 0": "f-420",
    "flex: 1 1 340px; min-width: 0": "f-340",
    "flex: 1 1 260px; min-width: 0": "f-260",
    "min-width: 0": "mw0",
    "flex: 1": "f-1",
    "flex: 1 1 320px; min-width: 0; display: flex; gap: 14px": "f-320 cols gap-14",
    "flex: 1 1 320px; min-width: 0; display: flex; flex-wrap: wrap; gap: 14px": "f-320 cols gap-14",
    # --- cards and tiles
    "padding: 36px; border-radius: 20px; background: #FFFFFF; border: 1px solid #E1E6EF; box-shadow: 0 1px 2px rgba(11,18,32,0.04), 0 12px 32px rgba(11,18,32,0.06)": "card-feature",
    "display: flex; flex-wrap: wrap; gap: 32px; align-items: center; padding: 36px; border-radius: 20px; background: #FFFFFF; border: 1px solid #E1E6EF; box-shadow: 0 1px 2px rgba(11,18,32,0.04), 0 12px 32px rgba(11,18,32,0.06)": "card-feature cols gap-32 ac",
    "flex: 1 1 380px; min-width: 0; padding: 32px; border-radius: 20px; background: #FFFFFF; border: 1px solid #E1E6EF; box-shadow: 0 1px 2px rgba(11,18,32,0.04), 0 12px 32px rgba(11,18,32,0.06)": ("f-380 card-feature", "padding: 32px"),
    "padding: 32px; border-radius: 18px; background: #F6F8FB; border: 1px solid #E1E6EF": "card-soft",
    "padding: 32px; border-radius: 18px; background: #F6F8FB; border: 1px solid #E1E6EF; display: flex; flex-wrap: wrap; gap: 24px 48px": ("card-soft cols", "gap: 24px 48px"),
    "padding: 32px; border-radius: 18px; background: #E7F6EF": "card-tint",
    "flex: 1 1 220px; padding: 20px; border-radius: 14px; background: #F6F8FB": "f-220 tile",
    "flex: 1 1 240px; padding: 20px; border-radius: 14px; background: #F6F8FB": "f-240 tile",
    "flex: 1 1 240px; padding: 20px; border-radius: 14px; background: #E7F6EF": "f-240 tile tile--tint",
    "flex: 1 1 260px; padding: 22px; border-radius: 14px; background: #F6F8FB; border: 1px solid #E1E6EF": "f-260 tile-260",
    "flex: 1 1 260px; min-width: 0; padding: 22px; border-radius: 14px; background: #F6F8FB; border: 1px solid #E1E6EF": "f-260 tile-260",
    "flex: 1 1 260px; min-width: 0; padding: 28px; border-radius: 18px; background: #F6F8FB; border: 1px solid #E1E6EF": "f-260 card-num",
    "flex: 1 1 320px; min-width: 0; padding: 28px; border-radius: 18px; background: #FFFFFF; border: 1px solid #E1E6EF": "f-320 card-person",
    "flex: 1 1 380px; min-width: 0; padding: 24px; border-radius: 16px; border: 1px solid #E1E6EF": "f-380 card-rule",
    "flex: 1 1 200px; min-width: 0; padding: 22px; border-radius: 16px; border: 1px solid #E1E6EF": "f-200 card-step",
    "flex: 1 1 320px; min-width: 0; padding: 24px; border-radius: 16px; background: #E7F6EF": "f-320 stat",
    "flex: 1 1 260px; min-width: 0; padding: 24px; border-radius: 16px; background: #E7F6EF": "f-260 stat",
    "flex: 1; padding: 24px; border-radius: 16px; background: #E7F6EF": "f-1 stat",
    "flex: 1; padding: 24px; border-radius: 16px; background: #F6F8FB; border: 1px solid #E1E6EF": "f-1 stat stat--alt",
    "flex: 1 1 150px; padding: 24px; border-radius: 16px; background: #E7F6EF": "f-150 stat",
    "flex: 1 1 150px; padding: 24px; border-radius: 16px; background: #F6F8FB; border: 1px solid #E1E6EF": "f-150 stat stat--alt",
    "flex: 1 1 180px; padding: 18px 20px; border-radius: 14px; background: #FFFFFF; border: 1px solid #E1E6EF": "f-180 stat-tile",
    "flex: 1 1 240px; min-width: 0; display: flex; flex-direction: column; gap: 10px; padding: 22px 24px; border-radius: 16px; background: #FFFFFF; border: 1px solid #E1E6EF": "f-240 hero-card",
    "flex: 1 1 240px; min-width: 0; display: flex; flex-direction: column; gap: 10px; padding: 22px 24px; border-radius: 16px; background: #E7F6EF; border: 1px solid transparent": "f-240 hero-card hero-card--key",
    "flex: 1 1 340px; min-width: 0; display: flex; flex-direction: column; gap: 8px; padding: 24px; border-radius: 16px; border: 1px solid #E1E6EF; text-decoration: none; color: #0B1220": "f-340 card-link",
    "flex: 1 1 380px; min-width: 0; display: flex; flex-direction: column; gap: 8px; padding: 24px; border-radius: 16px; border: 1px solid #E1E6EF; text-decoration: none; color: #0B1220": "f-380 card-link",
    "flex: 1 1 380px; min-width: 0; display: flex; flex-direction: column; gap: 8px; padding: 24px; border-radius: 16px; background: #F6F8FB; border: 1px solid #E1E6EF; color: #0B1220": "f-380 card-link card-link--soft",
    "flex: 1 1 260px; min-width: 0; display: flex; flex-direction: column; gap: 6px; padding: 22px; border-radius: 16px; border: 1px solid #E1E6EF; text-decoration: none; color: #0B1220": "f-260 card-link card-link--s",
    "flex: 1 1 520px; min-width: 0; display: flex; flex-direction: column; gap: 14px; padding: 32px; border-radius: 18px; background: #FFFFFF; border: 1px solid #E1E6EF; box-shadow: 0 1px 2px rgba(11,18,32,0.04); text-decoration: none; color: #0B1220": "f-520 card-study",
    "flex: 2 1 520px; min-width: 0; display: flex; flex-direction: column; gap: 10px; padding: 28px 32px; border-radius: 18px; background: #E7F6EF; text-decoration: none; color: #0B1220": ("card-lab", "flex: 2 1 520px"),
    "display: flex; gap: 20px; padding: 26px; border-radius: 16px; background: #F6F8FB; border: 1px solid #E1E6EF": "step",
    "display: flex; gap: 20px; padding: 24px; border-radius: 16px; background: #F6F8FB; border: 1px solid #E1E6EF": "step step--s",
    "padding: 12px 16px; border-radius: 10px; background: #F6F8FB; border: 1px solid #E1E6EF; font-family: 'IBM Plex Mono', monospace; font-size: 15px; color: #0B1220": "query",
    # --- findings and charts
    "padding: 36px 0; border-top: 1px solid #E1E6EF": "finding",
    "padding: 36px 0; border-top: 1px solid #E1E6EF; border-bottom: 1px solid #E1E6EF": "finding finding--last",
    "flex: 1 1 320px; min-width: 0; margin: 0; padding: 24px; border-radius: 16px; background: #F6F8FB; border: 1px solid #E1E6EF": "f-320 figure",
    "flex: 1 1 440px; min-width: 0; margin: 0; padding: 32px; border-radius: 20px; background: #F6F8FB; border: 1px solid #E1E6EF": ("f-440 figure", "padding: 32px; border-radius: 20px"),
    "margin: 28px 0 0; padding: 24px; border-radius: 16px; background: #F6F8FB; border: 1px solid #E1E6EF": "figure mt-28",
    "font-size: 14px; color: #5B6478; margin-bottom: 18px": "figure__cap",
    "display: flex; flex-wrap: wrap; gap: 8px 20px; font-size: 14px; color: #5B6478; margin-bottom: 20px": "figure__legend",
    "display: flex; justify-content: space-between; font-size: 14px; color: #3D4658; margin-bottom: 6px": "bar__label",
    "display: flex; justify-content: space-between; gap: 12px; font-size: 14px; color: #3D4658; margin-bottom: 6px": "bar__label gap-12",
    "height: 12px; border-radius: 6px; background: #E1E6EF": "bar",
    "display: flex; height: 12px; border-radius: 6px; background: #E1E6EF": "bar",
    "display: flex; justify-content: space-between; font-size: 15px; color: #0B1220; margin-bottom: 6px": "split-label",
    "display: flex; height: 14px; border-radius: 7px; overflow: hidden; background: #E1E6EF": "split",
    # --- quotes
    "flex: 1 1 400px; min-width: 0; margin: 0; padding: 20px 22px; border-radius: 14px; border: 1px solid #E1E6EF; border-left: 4px solid #0F7A52; background: #FFFFFF": "f-400 quote",
    "flex: 1 1 400px; min-width: 0; margin: 0; padding: 20px 22px; border-radius: 14px; border: 1px solid #E1E6EF; border-left: 4px solid #B8C0CE; background: #FFFFFF": "f-400 quote quote--no",
    "margin: 0 0 8px; font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: #0F7A52": "quote__who",
    "margin: 0 0 8px; font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: #5B6478": "quote__who",
    # --- buttons
    "display: inline-flex; align-items: center; min-height: 52px; padding: 0 26px; border-radius: 999px; background: #0F7A52; color: #FFFFFF; text-decoration: none; font-weight: 600; font-size: 17px": "btn btn--primary",
    "display: inline-flex; align-items: center; min-height: 52px; padding: 0 26px; border-radius: 999px; border: 1px solid #C3CBDA; background: #FFFFFF; color: #0B1220; text-decoration: none; font-weight: 600; font-size: 17px": "btn btn--secondary",
    "display: inline-flex; align-items: center; min-height: 54px; padding: 0 30px; border-radius: 999px; background: #7EE2BC; color: #062418; text-decoration: none; font-weight: 600; font-size: 17px": "btn btn--mint",
    "display: inline-flex; align-items: center; min-height: 48px; padding: 0 22px; border-radius: 999px; background: #0F7A52; color: #FFFFFF; text-decoration: none; font-weight: 600": "btn btn--small",
    "display: inline-flex; align-items: center; min-height: 48px; padding: 0 22px; border-radius: 999px; border: 1px solid #0F7A52; background: #FFFFFF; color: #0F7A52; text-decoration: none; font-weight: 600": "btn btn--outline",
    "min-height: 52px; padding: 0 28px; border-radius: 999px; border: none; background: #0F7A52; color: #FFFFFF; font-weight: 600; font-size: 17px; font-family: inherit; cursor: pointer": "btn-submit",
    "min-height: 50px; padding: 0 24px; border-radius: 999px; border: none; background: #0F7A52; color: #FFFFFF; font-weight: 600; font-size: 16px; font-family: inherit; cursor: pointer": "btn-submit btn-submit--s",
    # --- forms
    "font-size: 14px; font-weight: 500; color: #3D4658": "label",
    "min-height: 50px; padding: 0 16px; border-radius: 12px; border: 1px solid #C3CBDA; background: #FFFFFF; color: #0B1220; font-size: 16px; font-family: inherit": "input",
    "padding: 14px 16px; border-radius: 12px; border: 1px solid #C3CBDA; background: #FFFFFF; color: #0B1220; font-size: 16px; line-height: 1.5; font-family: inherit; resize: vertical": "input input--area",
    "display: flex; flex-direction: column; gap: 6px": "field",
    "flex: 1 1 260px; display: flex; flex-direction: column; gap: 6px": "f-260 field",
    "flex: 1 1 240px; display: flex; flex-direction: column; gap: 6px": "f-240 field",
    "margin-top: 28px; display: flex; flex-direction: column; gap: 18px": "col gap-18 mt-28",
    "flex: 1 1 420px; min-width: 0; display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end": ("f-420 cols gap-12", "align-items: flex-end"),
}


BAR_FILL = re.compile(r'^width: ([\d.]+%); height: 12px; border-radius: 6px; background: #0F7A52$')
BAR_FILL_NEUTRAL = re.compile(r'^width: ([\d.]+%); min-width: 4px; height: 12px; border-radius: 6px; background: #8A93A8$')
SPLIT_L = re.compile(r'^width: ([\d.]+%); background: #0F7A52$')
SPLIT_R = re.compile(r'^width: ([\d.]+%); background: #0B1220$')

TAG_RE = re.compile(r'<(\w+)([^>]*?)\sstyle="([^"]*)"([^>]*)>')


def map_style(style):
    """Return (classes, residual_style) for one inline style, or None if unmapped."""
    s = style.strip().rstrip(";").strip()
    s = re.sub(r"\s+", " ", s)
    if s in STYLES:
        v = STYLES[s]
        return (v, "") if isinstance(v, str) else v
    for rx, cls in ((BAR_FILL, "bar__fill"), (BAR_FILL_NEUTRAL, "bar__fill bar__fill--neutral"),
                    (SPLIT_L, "split__l"), (SPLIT_R, "split__r")):
        m = rx.match(s)
        if m:
            return cls, f"width: {m.group(1)}"
    return None


def convert(src: Path, unmapped: dict):
    stem = src.name.replace(".dc.html", "")
    if stem not in PAGES:
        raise SystemExit(f"{src.name}: not a known mockup (known: {', '.join(PAGES)})")
    slug, url = PAGES[stem]
    html = src.read_text(encoding="utf-8")

    # 1. body: inside the page wrapper div, between the mockup header and footer.
    m = re.search(r'<div style="background: #FFFFFF; color: #0B1220;[^"]*min-height: 100vh">(.*)</div>\s*</x-dc>', html, re.S)
    if not m:
        raise SystemExit(f"{src.name}: page wrapper not found")
    body = m.group(1)
    body = re.sub(r"<header\b.*?</header>", "", body, count=1, flags=re.S)
    body = re.sub(r"<footer\b.*?</footer>", "", body, count=1, flags=re.S)
    assert "support.js" not in body and "<x-dc" not in body and "<helmet" not in body and "text/x-dc" not in body

    # 2. links
    for old, new in LINKS:
        body = body.replace(f'href="{old}"', f'href="{new}"')
    if stem == "Dentists":
        # the two "Find your practice's report" buttons go to the report page
        body = re.sub(r'href="/studies/dentists/"(?=[^>]*>Find your practice\'s report<)', 'href="/report.html"', body)
    if stem == "Main":
        body = body.replace('<section id="lab-notes"', '<section id="lab-finds"')
    assert ".dc.html" not in body, f"{src.name}: unrewritten mockup link"

    # 3. inline styles -> classes
    def repl(mt):
        tag, before, style, after = mt.groups()
        mapped = map_style(style)
        if mapped is None:
            unmapped.setdefault(style, []).append(f"{stem}:{tag}")
            return mt.group(0)
        classes, residual = mapped
        attrs = before + after
        if "class=" in attrs:
            raise SystemExit(f"{src.name}: <{tag}> already has a class attribute")
        out = f"<{tag}{before}"
        if classes:
            out += f' class="{classes}"'
        if residual:
            out += f' style="{residual}"'
        return out + f"{after}>"
    body = TAG_RE.sub(repl, body)

    out = OUT_DIR / f"{slug}.html"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out.write_text(body.strip() + "\n", encoding="utf-8", newline="\n")
    return out


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    unmapped = {}
    for arg in argv:
        out = convert(Path(arg), unmapped)
        print(f"wrote {out.relative_to(ROOT)}")
    if unmapped:
        print(f"\n{len(unmapped)} inline style(s) left in place (add to STYLES if they repeat):")
        for style, where in unmapped.items():
            print(f"  [{len(where)}] {', '.join(sorted(set(where)))}: {style}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
