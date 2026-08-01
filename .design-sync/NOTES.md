# design-sync notes — aivi-website

## Why this repo is off the standard path

`aivi-website` is a static Jekyll site: no `package.json`, no lockfile, no
`dist/`, no Storybook, no JSX/TSX, and no `.css` files (every page carries its
own inline `<style>` block). The skill's converter (`package-build.mjs`) needs a
compiled component package and does not apply here.

So this sync is **brand-kit-only**: tokens, guidelines and brand assets, no
components. `.design-sync/build.mjs` replaces the converter. Consequence to be
honest about: the design agent gets the palette, type and marks, but has no AIVI
components to compose with — it falls back to generic components wearing the
brand's colours. Closing that gap means building a real component package
(see "If a component library ever lands" below).

## Policy this build enforces

The brand is **extracted from live surfaces, never authored**. `build.mjs`
therefore *parses* values rather than embedding them:

- Dark palette (primary) ← the `:root` block of `index.html`
- Light palette (print/secondary) ← the `@media print { :root }` block of
  `reports/a61CGcll1t.html`
- Font request ← the Google Fonts `<link>` in `index.html`
- Masthead lockup CSS ← `.logo-mark` / `.wordmark` in `index.html`

Changing a colour in those files and re-running the build changes the bundle.
Nothing needs hand-editing. `brand/brand.md` ships verbatim as
`guidelines/brand.md` and remains the canonical prose.

## Findings / gotchas

- **No fonts are vendored.** The repo loads IBM Plex Sans/Mono and Source
  Serif 4 from the Google Fonts CDN. `tokens/fonts.css` carries the same remote
  `@import` rather than inventing local copies. If the design renderer blocks
  external font requests, type falls back to the system stacks in `--sans` /
  `--mono` / `--serif`. Fixing that properly means vendoring the SIL OFL / OFL
  font files into the repo — a real decision, not a sync-time one.
- **The light palette does not live in `report-template.html`.** That file has
  only the dark `:root`. The `@media print` block is in the shipped reports
  under `reports/`. `brand.md` names `Product/aivi-report-standard-template.html`
  as canonical, which is outside this repo — hence sourcing from a shipped
  report, which is a live surface and satisfies the extraction policy.
- **`reports/` is git-ignored build output**, so no report filename is stable
  across clones. `build.mjs` globs `reports/*.html` for the first file carrying
  a print block instead of pinning one, and fails with an explicit message if
  the directory is empty (fresh clone before a report build). Verified the print
  palette is byte-identical across reports, so which one it picks does not
  affect the output — only the source named in the file's banner comment.
- The shipped print block defines 18 properties — more than `brand.md`'s table
  documents. The build takes all 18; the doc's table is a readable subset.
- **Excluded from the upload:** `brand/avatar-comparison-sheet.png` and
  `brand/avatar-40px-circle-magnified.png`. These are analysis artefacts from
  the avatar bake-off, not brand assets.
- **No `_ds_sync.json` anchor.** Its hash recipe is defined for the package and
  storybook shapes; this shape has neither. Omitting it is the honest choice —
  the next sync simply rebuilds and re-uploads everything, which is cheap here.
- `ds-bundle/` is generated and git-ignored. Rebuild with
  `node .design-sync/build.mjs`.

## Brand rules the conventions header encodes

Recorded here because they are policy, not derivable from the CSS:

- Dark theme is primary; light is print/secondary.
- IBM Plex Mono is the accent/label face — figures, data, platform codes.
- `avatar-a-monogram` for avatars/favicons/circular crops/≤64px; the `AI` square
  + wordmark lockup is the masthead form. The `AIVI` four-glyph tile fails at
  40px and must not be used at avatar sizes.
- Never `--pos` green (`#7EE2BC`) as text on white — 1.56:1, fails every floor.
- **"SEZC" never appears in brand surfaces** — footers, About and contracts only.
- Do not invent or "improve" colours or type. The brand is what ships.

## If a component library ever lands

Build it as a proper package with a bundlable `dist/`, then re-run
`/design-sync`: it will detect the package shape and take the standard converter
path. Remove `"shape": "brand-only"` from `.design-sync/config.json` so shape
detection runs again, and keep `conventions.md` — it stays true, but its "there
are no importable components" opening would need rewriting at that point.
