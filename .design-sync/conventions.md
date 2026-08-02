# AIVI Labs — brand kit

**This is a brand kit, not a component library.** There are no importable
components. Build UI with plain HTML/JSX and style it with the CSS custom
properties below. Do not reach for a third-party component kit and recolour it —
the tokens *are* the system.

## Setup

No provider, no wrapper. `styles.css` imports everything (fonts, dark tokens,
light tokens) and sets the page defaults, so a design is correct as soon as that
stylesheet is loaded.

**Dark is the default and the primary theme** — `--bg: #0B1220` with
`--text-2` body text is the shipping look, and the report aesthetic *is* the
brand. Do not build a light-first design unless asked. The light palette is the
**print/secondary** theme: it applies automatically under `@media print`, or opt
in explicitly with `<html data-theme="light">`.

## The idiom: CSS custom properties

Every value comes from `var(--*)`. Never hardcode a hex; never invent a token
name. The complete vocabulary:

| family | tokens |
|---|---|
| Surfaces | `--bg` `--surface` `--elevated` |
| Borders | `--border` `--border-em` |
| Text | `--text-1` (headings) `--text-2` (body) `--text-3` `--text-4` `--text-5` (labels, "not measured") |
| Status | `--pos` `--pos-deep` `--warn` `--neg` |
| Status tints | `--pos-tint` `--pos-tint-strong` `--warn-tint` `--neg-tint` |
| Radii | `--radius` (16px) `--radius-sm` (10px) `--radius-pill` (999px) |
| Type stacks | `--sans` `--mono` `--serif` |
| Layout | `--maxw` (1100px) `--pad-x` |

`--pos` (AIVI Green `#7EE2BC`) is the single accent: positive states, emphasis,
the "Labs" in the wordmark. Use `--pos-deep` for hover/pressed. Use the `-tint`
variants for filled status backgrounds, not the solid colour.

**Never put `--pos` green text on a white background** — `#7EE2BC` on `#FFFFFF`
is 1.56:1 and fails every accessibility floor. The light theme already
substitutes `#0F7A52` (5.35:1, AA); that substitution is why you use the token
instead of the hex.

## Typography

- `--sans` (IBM Plex Sans) — UI, body, headings, the wordmark.
- `--mono` (IBM Plex Mono) — **accents and labels**: figures, data, platform
  codes, metric values, small-caps-ish eyebrow labels, and the mark's "AI".
  Reach for mono whenever a number or a label needs to read as measured data.
- `--serif` (Source Serif 4) — long editorial passages in reports only.

Weights that ship: Plex Sans 400/500/600/700, Plex Mono 400/500.

## The logo

Two forms, and they are not interchangeable:

- **Masthead / header / report lockup** — the `AI` square plus the wordmark.
  `styles.css` ships both classes; this is the exact shipping markup:

  ```html
  <span class="logo-mark">AI</span>
  <span class="wordmark">AIVI <span>Labs</span></span>
  ```

- **Avatar, favicon, any circular crop, anything ≤64px** — the single-letter
  `A` monogram, `assets/brand/avatar-a-monogram.svg`. The four-glyph `AIVI`
  tile fails at 40px (1px stems) and must not be used at avatar sizes.

Don't recolour, outline, rotate or add effects to either. Clear space on all
sides is at least 0.235 × mark height.

**"SEZC" never appears in brand surfaces.** The legal entity name belongs in
footers, About sections and contracts — never in a wordmark, header or cover.

## Tagline

Two canonical forms — use one verbatim, never a paraphrase:

- **Short**, for sign-offs, footers and meta labels: `We measure AI responses`
- **Long**, for heroes and About-style copy: `We measure the answers AI gives your customers`

`We measure AI search visibility` is **retired** (2026-08-02). Do not use it,
even though it still appears on the social-cover artwork.

## Copy is never yours to invent

Numbers in this brand are **measured claims**, not decoration. Never invent a
metric, sample size, platform count, price, guarantee or timeframe to make a
mockup look finished — a fabricated number read as approved copy is the single
most expensive mistake you can make here. Use obvious placeholders
(`XX%`, `[practice name]`) and let a human supply the real value.

The same applies to legal and contact surfaces: don't author expiry terms,
refund promises or addresses. Footer contact details come from the approved
delivery copy, never from memory.

## Where the truth lives

- `styles.css` and its imports under `tokens/` — the real, current values.
- `guidelines/brand.md` — the full brand kit: measured contrast ratios, the
  mark's geometry (0.235 tile radius ratio, 0.382 font-to-tile ratio), the
  asset file index, and the print-safe stack for physical mail.

Read those before styling. Values were extracted from live shipping pages, not
authored — so if this file and `tokens/` ever disagree, `tokens/` wins.

## Example

```jsx
<section style={{ background: 'var(--surface)', border: '1px solid var(--border)',
                  borderRadius: 'var(--radius)', padding: '24px', maxWidth: 'var(--maxw)' }}>
  <div style={{ font: '500 12px var(--mono)', letterSpacing: '0.05em', color: 'var(--text-5)' }}>
    AI SEARCH VISIBILITY
  </div>
  <div style={{ fontFamily: 'var(--mono)', fontSize: '40px', color: 'var(--pos)' }}>34%</div>
  <p style={{ color: 'var(--text-3)', margin: 0 }}>Mention rate across measured answers.</p>
</section>
```
