# Building the site

The committed HTML is what GitHub Pages serves. It is generated, not hand-written:

```
_src/pages/*.html        page bodies (converted from the design mockups)
_src/partials/*.html     the shared header and footer
_build/pages.json        one entry per page: source, output path, URL, title, description
_build/build.py          assembles head + header + body + footer -> committed pages
_build/convert_mockup.py turns a design-tool mockup export into a _src/pages body
assets/site.css          the shared stylesheet (brand tokens + component classes)
assets/site.js           the /study/ request form and the home-page findings signup
assets/report.css        report.html's two panels
```

Underscore-prefixed folders are not published by GitHub Pages.

## Everyday change

1. Edit the body in `_src/pages/`, a partial, or `pages.json`.
2. `python _build/build.py` (or `--check` to see what is stale without writing).
3. Preview: `python -m http.server 8787` from the repo root, open http://127.0.0.1:8787/.
4. Commit the sources **and** the generated pages together.

## A new or revised mockup from the design tool

Wording lives in the mockup, never here. When a page's copy changes, the new
mockup export arrives (one file per page) and is converted:

```
python _build/convert_mockup.py path/to/handoff/pages/CokePepsi.<mockup-extension>
python _build/build.py
```

The converter strips the tool's wrapper, rewrites links to the live URLs and
replaces the repeated inline styles with classes from `assets/site.css`. Any
style it does not recognise is left inline and listed at the end of the run;
add it to `STYLES` in the converter (and a class to `site.css`) only when it
repeats. The mockup drop folder stays outside the repo.

The home-page and /study/ forms carry a few attributes the mockups do not have
(`id`, `name`, the hidden `website` honeypot, the consent line, the error slot).
After re-converting `Main` or `BrandStudy`, re-apply them; `assets/site.js`
documents what it expects.

## report.html

`report.html` is built like the others, but its `<script id="aivi-coverage">`
island is owned by `build_coverage.py` in aivi-delivery-state, which rewrites
the committed file in place. `build.py` therefore copies the island from the
existing committed `report.html` on every build rather than from `_src`. Its
form script, field names, endpoints and city picker are unchanged from the
July 2026 site.

## Typefaces

IBM Plex Sans, Serif and Mono are self-hosted: the woff2 files are in
`assets/fonts/` (from the official `@ibm/plex-*` npm packages, SIL Open Font
License 1.1, licence file alongside) and declared in `assets/fonts.css`, which
`site.css` imports and the three legal pages link directly. Only the weights
the site uses are shipped (Sans 400/500/600/700, Serif 500/600, Mono 400/500).
No page on aivilabs.io may load fonts from Google: that sends every visitor's
IP address to Google, and the privacy policy says it does not happen.

## Tracker guard

`build.py` (in both modes) ends by scanning every served `.html` and `.js`
file, i.e. everything outside the underscore/dot directories and the ignored
`r/` and `reports/` folders, and exits 1 if any contains one of these markers:

| Marker | What it is |
|---|---|
| `connect.facebook.net`, `facebook.com/tr`, `fbq(` | Meta Pixel |
| `googletagmanager.com`, `google-analytics.com`, `gtag(` | Google Tag Manager / Analytics / Ads |
| `doubleclick.net`, `googleadservices.com` | Google ad tracking |
| `analytics.tiktok.com` | TikTok Pixel |
| `snap.licdn.com`, `px.ads.linkedin.com` | LinkedIn Insight Tag |
| `static.hotjar.com`, `clarity.ms` | Hotjar / Microsoft Clarity session recording |
| `cloudflareinsights.com` | Cloudflare Web Analytics beacon |
| `plausible.io`, `cdn.segment.com`, `mixpanel`, `heapanalytics` | other analytics |
| `fonts.googleapis.com`, `fonts.gstatic.com` | Google Fonts (every served page except `report-template.html`) |

It prints the file and the matched marker. Why: a tracking pixel on the site
is a legal risk, and the privacy policy promises there are none. If the guard
fires, remove the snippet; do not add an exemption. `report-template.html` is
exempt from the fonts check only because it is served from get.aivilabs.io and
reports.aivilabs.io, still uses Google Fonts, and the policy says so.

The guard only sees the repo. Cloudflare can inject scripts on the domains it
serves (Web Analytics beacon, Email Address Obfuscation, Rocket Loader); check
the live pages in a browser with network capture after a deploy.

## Redirects

GitHub Pages cannot redirect server-side. `methodology.html` and `about.html`
are small pages with `<meta http-equiv="refresh">`, a canonical link to the new
URL and a plain link. Keep them.

## Never

- Delete `CNAME`, or the `r/` and `reports/` lines in `.gitignore`.
- Edit `report-template.html` or anything the report generators read.
- Change a word on `privacy/`, `terms/` or `refund/` (Dodo is Merchant of Record).
  They were re-skinned on 2026-10-27 by swapping only their colour and font
  variables.
- Commit a token, place_id or anything from `r/` or `reports/`.
