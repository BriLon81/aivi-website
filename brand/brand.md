# AIVI Labs — Brand Kit

**Formalization, not redesign.** Every value below was read out of what already
ships. The brand is definitionally what the live report template and site use.

Sources of truth:
- `aivi-website/index.html` — `:root` tokens, `.logo-mark`, `.wordmark`
- `Product/aivi-report-standard-template.html` — the same `:root`, plus the
  `@media print` light palette

If a value here ever disagrees with those files, **those files win** and this
document is stale.

---

## Tokens

### Core

| Token | Value | CSS var | Where it's used |
|---|---|---|---|
| **AIVI Green** | `#7EE2BC` | `--pos` | The mark's tile, "Labs" in the wordmark, positive states, accents |
| AIVI Green Deep | `#5DD0A8` | `--pos-deep` | Hover/pressed states, denser accent fills |
| **Glyph Dark** | `#062418` | *(literal in `.logo-mark`)* | The "AI" letterforms inside the green tile. Not a general text colour — it exists only inside the mark |
| **Ink** | `#0B1220` | `--bg` | Page background, dark-theme surfaces, the inverted mark's tile |
| Surface | `#101A2E` | `--surface` | Cards, panels |
| Elevated | `#16213A` | `--elevated` | Raised panels |

### Text (dark theme)

| Token | Value | CSS var | Use |
|---|---|---|---|
| Text 1 | `#FFFFFF` | `--text-1` | Headings, "AIVI" in the wordmark |
| Text 2 | `#E0E5F0` | `--text-2` | Body |
| Text 3 | `#C8D0E0` | `--text-3` | Secondary body, the social-cover tagline |
| Text 4 | `#B0B8CC` | `--text-4` | Muted |
| Text 5 | `#7B85A0` | `--text-5` | Labels, "not measured" states |

### Light theme (the print palette)

The report's `@media print` block is the canonical light theme — there is no
separate light-mode stylesheet, so print *is* the light palette.

| Token | Value | Dark-theme counterpart |
|---|---|---|
| **Green (light)** | `#0F7A52` | `#7EE2BC` |
| Green Deep (light) | `#0A5C3D` | `#5DD0A8` |
| Background | `#FFFFFF` | `#0B1220` |
| Surface | `#F7F8FB` | `#101A2E` |
| Ink / Text 1 | `#0B0F16` | `#FFFFFF` |
| Text 3 | `#37414F` | `#C8D0E0` |
| Border | `#DFE4EE` | `rgba(255,255,255,0.07)` |

**AIVI Green does not survive on white.** Measured: `#7EE2BC` on `#FFFFFF` is
**1.56:1** — below every accessibility floor and unreadable as text. The light
palette's `#0F7A52` on white is **5.35:1** (AA). Light surfaces use `#0F7A52`.

Measured contrast for the shipping combinations:

| pair | ratio | |
|---|---|---|
| Text 1 `#FFFFFF` on Ink | 18.72:1 | AA |
| Text 3 `#C8D0E0` on Ink (cover tagline) | 12.08:1 | AA |
| AIVI Green on Ink | 12.03:1 | AA |
| Mark glyph `#062418` on green tile | 10.60:1 | AA |
| Green-light `#0F7A52` on white | 5.35:1 | AA |
| **AIVI Green on white** | **1.56:1** | **fails — never do this** |

### Status

| Token | Dark | Light (print) |
|---|---|---|
| Positive | `#7EE2BC` | `#0F7A52` |
| Warning | `#FFD66B` | `#8A6A00` |
| Negative | `#F47B7B` | `#C0392B` |

### Geometry

| Token | Value |
|---|---|
| Radius | `16px` (`--radius`) |
| Radius small | `10px` (`--radius-sm`) |
| Radius pill | `999px` |
| Mark tile radius | `8px` on a `34px` box — **ratio 0.235**, scale proportionally |

### Type

| Role | Stack | Used for |
|---|---|---|
| **Sans** | `"IBM Plex Sans", system-ui, -apple-system, Segoe UI, Roboto, sans-serif` | UI, body, the wordmark |
| **Mono** | `"IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace` | The mark's "AI", data, figures, platform codes |
| Serif | `"Source Serif 4", "Source Serif Pro", Georgia, "Times New Roman", serif` | Report editorial passages |
| **Print-safe sans** | `"Helvetica Neue", Helvetica, Arial, sans-serif` | Direct mail only |

The print-safe stack exists because PostGrid's renderer has neither IBM Plex nor
Georgia — a serif specified there fell back silently and shipped wrong. Physical
mail uses Helvetica/Arial and nothing else.

**Wordmark type spec:** "AIVI" IBM Plex Sans **600**, "Labs" IBM Plex Sans
**400** in AIVI Green, `letter-spacing: -0.005em`.
**Mark type spec:** "AI" IBM Plex Mono **700**, `letter-spacing: 0.05em`,
font-size 0.382 × tile size (13px on a 34px tile).

---

## Tagline

Two canonical forms. Both are current; pick by the space, not by preference.

| Form | Text | Use |
|---|---|---|
| **Short** | `We measure AI responses` | Sign-offs, footers, meta labels, anywhere a one-liner sits beside the wordmark |
| **Long** | `We measure the answers AI gives your customers` | Heroes, About-style copy, title tags — anywhere a full sentence already lives |

Do not invent a third form, and do not mix them in one surface.

**Superseded:** `We measure AI search visibility`. Retired 2026-08-02. It still
appears in two places, both deliberate:

- `social-cover-1640x856.svg` / `.png` — the artwork carries the old line as
  outlined paths. Regenerating it is **visual work, out of scope** until the
  post-launch identity rollout. The Files table below describes the asset as it
  currently is, not as it should read.
- The three Instantly outreach step cards — hand-maintained in the dashboard,
  inside Andrea-approved copy.

`aivi-delivery-state/email/render.py` bans the retired line outright, so it
cannot return to a delivery email.

---

## Files

Glyphs in every SVG are **outlined to paths** from the real IBM Plex fonts
(SIL OFL), so they render correctly on machines without IBM Plex installed.
Editing the letterforms means regenerating from the font, not nudging paths.

### Square mark — `AI` in a rounded tile

| File | Tile | Glyph | Use |
|---|---|---|---|
| `mark-green-tile.svg` + `-512/-192/-64/-40.png` | `#7EE2BC` | `#062418` | **Primary.** This is what ships in the site header |
| `mark-inverted.svg` + `-512/-192/-64/-40.png` | `#0B1220` | `#7EE2BC` | On green or light backgrounds; when the primary would vibrate |
| `mark-light-theme.svg` + `-512/-192/-64/-40.png` | `#0F7A52` | `#FFFFFF` | Print and white-background documents |

### Wordmark — "AIVI Labs", two-tone

| File | "AIVI" | "Labs" | Background |
|---|---|---|---|
| `wordmark-dark-theme.svg` + `-1200/-480.png` | `#FFFFFF` | `#7EE2BC` | transparent |
| `wordmark-light-theme.svg` + `-1200/-480.png` | `#0B0F16` | `#0F7A52` | transparent |
| `wordmark-on-dark-bg.svg` + `-1200/-480.png` | `#FFFFFF` | `#7EE2BC` | `#0B1220` baked in |

### Social

| File | Size | Contents |
|---|---|---|
| `social-cover-1640x856.svg` / `.png` | 1640×856 | Ink background, mark + wordmark lockup, "We measure AI search visibility" in Text 3 — **the retired tagline**; the artwork is unchanged pending the identity rollout (see Tagline above) |

Facebook page cover. Content is centred so the mobile crop keeps it inside the
safe area.

---

## Legibility

**40px avatar test: both variants pass with no weight tweak.** Rendered and
inspected at 40×40 — IBM Plex Mono Bold at ~15px effective holds its counters,
and the `A`/`I` stay distinct.

- `mark-green-tile-40.png` — dark glyph on mint. The stronger of the two;
  use this as the default avatar.
- `mark-inverted-40.png` — mint glyph on ink. Legible, but light-on-dark always
  reads slightly lighter. Prefer the primary at avatar sizes.

No size required a modified weight, so all exports come from one geometry. If a
future surface needs sub-32px, re-test rather than assuming — the 0.382
font-to-tile ratio is tuned for 34px and up.

---

## Usage

1. **Mark alone** for avatars, favicons and anywhere under ~120px wide.
   **Wordmark or lockup** wherever there is room for the name — the mark is not
   yet recognisable on its own.
2. **Minimum sizes:** mark 40px (tested); wordmark 88px wide, below which "Labs"
   at weight 400 starts to break up.
3. **Dark/light:** default to dark — the report aesthetic *is* the brand. On
   white or print use the light-theme files; never put `#7EE2BC` text on white.
4. **Clear space:** at least the tile's corner radius (0.235 × mark height) on
   all sides. Don't recolour, outline, rotate, or add effects to either asset.
5. **"SEZC" never appears in brand surfaces.** The legal entity name belongs in
   footers, About sections and contracts only — never in the wordmark, the
   social cover, or any header.

---

## Avatar variants

**Avatar-only.** The masthead lockup keeps the shipping `AI` square — nothing
about the site header or the report changes.

Two candidates were rendered and measured at the size that decides it: 40px,
circle-masked, which is Facebook's comment-thread avatar.

| file | glyphs | cap @40px | min stroke @40px | verdict |
|---|---|---|---|---|
| `mark-green-tile.svg` *(shipping)* | `AI` | 10px | 2px | OK |
| `avatar-aivi-tile.svg` | `AIVI` | 8px | **1px** | **fails** |
| `avatar-a-monogram.svg` | `A` | 20px | **4px** | **strongest** |

### The AIVI tile does not hold at 40px in a circle

Four mono glyphs across ~36 visible pixels leaves each stem **1px wide**. A 1px
stem cannot render as a stem — it survives only as anti-aliased grey, so the
letterforms stop resolving as shapes. Cap height falls to 8px, below the
shipping mark's 10px, because four glyphs must be sized down to fit at all.

See `avatar-40px-circle-magnified.png` (each 40px render upscaled 10×,
nearest-neighbour). Read left to right — `AI`, `AIVI`, `A` — the middle one is a
smear that is only readable if you already know what it says. That is not a test
it passes.

It is fine at 512 and acceptable at 80. **The failure is specific to avatar
sizes, which is the only thing it was built for.**

### Recommendation

**Use `avatar-a-monogram` as the standalone social avatar.** At 4px minimum
stroke and 20px cap it is the only one of the three that is unambiguous at 40px,
and it has room to spare as platforms shrink avatars further.

The cost is that a lone `A` carries less brand information than `AI` — but an
illegible mark carries none, and the wordmark does the naming everywhere the
avatar appears (profile name, page title, post attribution).

| context | use |
|---|---|
| Social avatar, favicon, any circular crop, anything ≤64px | `avatar-a-monogram` |
| Site header, report masthead, lockups | `mark-green-tile` *(the `AI` square — unchanged)* |
| Large square placements ≥192px where the full name helps | `avatar-aivi-tile` is viable, but the lockup is better |

### Circle-crop safety

The circle mask removes the tile's corners entirely. All three candidates keep
their glyphs well inside the inscribed circle, so nothing load-bearing is lost —
verified, not assumed. Any future avatar must keep artwork inside a centred
circle of 0.9 × tile width.
