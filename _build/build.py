#!/usr/bin/env python3
"""Assemble the committed pages from _src/pages + _src/partials.

    python _build/build.py            # write every page listed in _build/pages.json
    python _build/build.py --check    # write nothing; exit 1 if any page is stale

GitHub Pages serves the committed output as plain HTML; the underscore
directories (_build, _src) are not published. Each page = shared <head>
(title, description, canonical, Open Graph, fonts, /assets/site.css) + shared
header partial (the nav link matching the page URL gets aria-current) + the
page body + shared footer partial. Typefaces are self-hosted (assets/fonts,
declared in assets/fonts.css); nothing in <head> points off-site.

Both modes end with the tracker guard (see TRACKER_MARKERS below) and exit 1
if any served HTML/JS file contains a tracking, analytics or Google Fonts
marker.

report.html is special: build_coverage.py (aivi-delivery-state) rewrites its
<script id="aivi-coverage"> island in place from coverage.json. The island in
the committed report.html is therefore the source of truth, and this build
carries it over from the existing output rather than from _src. The data-cov
text slots are left to build_coverage.py too; after a build, run it with
--check if the city roster may have changed.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
SITE = "https://aivilabs.io"

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{description_tag}
<link rel="canonical" href="{site}{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AIVI Labs">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{site}{url}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/site.css">
{extra_head}</head>
<body>
"""

ISLAND_RE = re.compile(r'<script id="aivi-coverage" type="application/json">.*?</script>', re.S)


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def header_for(url, header):
    """Mark the plain nav link whose href is this page as the current page."""
    def mark(m):
        href = m.group(1)
        if href == url and "btn--nav" not in m.group(0):
            return m.group(0).replace(f'href="{href}"', f'href="{href}" aria-current="page"', 1)
        return m.group(0)
    return re.sub(r'<a href="([^"]+)"[^>]*>', mark, header)


def render(page, header, footer):
    body = (SRC / "pages" / page["source"]).read_text(encoding="utf-8")
    out_path = ROOT / page["out"]
    if page.get("coverage_island"):
        if not out_path.is_file():
            raise SystemExit(f"{page['out']}: coverage island source missing (the committed file)")
        current = ISLAND_RE.search(out_path.read_text(encoding="utf-8"))
        if not current:
            raise SystemExit(f"{page['out']}: no <script id=\"aivi-coverage\"> island in the committed file")
        body, n = ISLAND_RE.subn(lambda _: current.group(0), body, count=1)
        if n != 1:
            raise SystemExit(f"{page['source']}: no island placeholder to fill")
    description_tag = page.get("description_tag") or f'<meta name="description" content="{esc(page["description"])}">'
    extra = page.get("extra_head", "")
    head = HEAD.format(title=esc(page["title"]), description=esc(page["description"]),
                       description_tag=description_tag, url=page["url"], site=SITE,
                       extra_head=(extra + "\n") if extra else "")
    scripts = "".join(f'<script src="{s}"></script>\n' for s in page.get("scripts", []))
    return head + header_for(page["url"], header) + "<main>\n" + body + "</main>\n" + footer + scripts + "</body>\n</html>\n"


def main(argv):
    check = "--check" in argv
    cfg = json.loads((ROOT / "_build" / "pages.json").read_text(encoding="utf-8"))
    header = (SRC / "partials" / "header.html").read_text(encoding="utf-8")
    footer = (SRC / "partials" / "footer.html").read_text(encoding="utf-8")
    stale = []
    for page in cfg["pages"]:
        html = render(page, header, footer)
        out = ROOT / page["out"]
        before = out.read_text(encoding="utf-8") if out.is_file() else None
        if before == html:
            print(f"unchanged : {page['out']}")
            continue
        stale.append(page["out"])
        if check:
            print(f"STALE     : {page['out']}")
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8", newline="\n")
        print(f"wrote     : {page['out']}")
    if check:
        print("check: up to date" if not stale else f"check: {len(stale)} page(s) stale")
    hits = guard()
    if hits:
        return 1
    return 1 if (check and stale) else 0


# --- Tracker guard -----------------------------------------------------------
# aivilabs.io's privacy policy promises no tracking pixels, tags or analytics,
# and that its typefaces are served from its own site. A pixel that slips in
# (an AI tool, a copied snippet, a CDN "feature") is a legal risk, so the build
# refuses to pass while any served HTML or JS file contains one of these.
# The list is documented in _build/README.md; keep the two in step.
TRACKER_MARKERS = [
    "connect.facebook.net", "facebook.com/tr", "fbq(",
    "googletagmanager.com", "google-analytics.com", "gtag(",
    "doubleclick.net", "googleadservices.com",
    "analytics.tiktok.com",
    "snap.licdn.com", "px.ads.linkedin.com",
    "static.hotjar.com", "clarity.ms",
    "cloudflareinsights.com",
    "plausible.io", "cdn.segment.com", "mixpanel", "heapanalytics",
]
# Google Fonts send every visitor's IP address to Google. The site self-hosts
# its typefaces; only report-template.html (served from get.aivilabs.io and
# reports.aivilabs.io, and described as such in the policy) may still use them.
FONT_MARKERS = ["fonts.googleapis.com", "fonts.gstatic.com"]
FONT_EXEMPT = {"report-template.html"}
# Not served by GitHub Pages: underscore and dot directories, and the
# gitignored generated report folders.
SKIP_DIRS = {"r", "reports", "ds-bundle", "node_modules"}


def served_files():
    for path in sorted(ROOT.rglob("*")):
        if path.suffix.lower() not in (".html", ".js"):
            continue
        rel = path.relative_to(ROOT)
        if any(part.startswith((".", "_")) or part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        yield path, rel.as_posix()


def guard():
    """Print every (file, marker) hit in the served tree; return the list."""
    hits = []
    for path, rel in served_files():
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        markers = list(TRACKER_MARKERS)
        if rel not in FONT_EXEMPT:
            markers += FONT_MARKERS
        for marker in markers:
            if marker.lower() in text:
                hits.append((rel, marker))
                print(f"GUARD     : {rel}: contains {marker}")
    if hits:
        print(f"guard: FAIL, {len(hits)} tracker/font marker(s) in {len({h[0] for h in hits})} served file(s)")
    else:
        print("guard: pass, no tracker or Google Fonts markers in served HTML/JS")
    return hits


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
