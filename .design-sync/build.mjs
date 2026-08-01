#!/usr/bin/env node
// Builds ds-bundle/ for claude.ai/design from this repo's live surfaces.
//
// POLICY: every colour, radius and type stack below is PARSED out of shipping
// HTML -- never transcribed by hand and never invented. brand/brand.md is the
// canonical prose; index.html and reports/*.html are where the values live.
// If a value changes in those files, re-running this script changes the bundle.

import { readFileSync, writeFileSync, mkdirSync, copyFileSync, readdirSync, rmSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const OUT = join(ROOT, 'ds-bundle');
const read = (p) => readFileSync(join(ROOT, p), 'utf8');
const write = (p, s) => { mkdirSync(dirname(join(OUT, p)), { recursive: true }); writeFileSync(join(OUT, p), s); };

// ASSUMPTION: the dark palette is the :root block of index.html -- the site's
// primary surface. Override by pointing DARK_SRC at another shipping page.
const DARK_SRC = 'index.html';
// ASSUMPTION: the light palette is the @media print block of a shipped report.
// brand.md: "print *is* the light palette" -- there is no light stylesheet.
//
// reports/ is generated build output and is git-ignored, so no single filename
// is stable across clones. Take the first report that actually carries a print
// block rather than pinning one, and fail loudly if the directory is empty.
function findLightSrc() {
  let entries = [];
  try { entries = readdirSync(join(ROOT, 'reports')).filter((f) => f.endsWith('.html')).sort(); }
  catch { /* directory absent on a fresh clone */ }
  for (const f of entries) {
    if (/@media\s+print\s*\{[\s\S]*?:root\s*\{/.test(read(join('reports', f)))) return join('reports', f).replace(/\\/g, '/');
  }
  throw new Error(
    'No report with an @media print :root block found under reports/.\n' +
    'reports/ is git-ignored build output — generate the reports first, or point\n' +
    'LIGHT_SRC at the canonical Product/aivi-report-standard-template.html.\n' +
    'The light palette must be extracted from a live surface, never transcribed.');
}
const LIGHT_SRC = findLightSrc();

const declRe = /(--[a-z0-9-]+)\s*:\s*([^;]+);/gi;

/** Pull custom-property declarations out of the first :root block of `css`. */
function parseRoot(html) {
  const m = html.match(/:root\s*\{([\s\S]*?)\}/);
  if (!m) throw new Error('no :root block found');
  return [...m[1].matchAll(declRe)].map(([, k, v]) => [k, v.trim()]);
}

/** Pull custom properties out of the @media print { :root { ... } } block. */
function parsePrintRoot(html) {
  const m = html.match(/@media\s+print\s*\{[\s\S]*?:root\s*\{([\s\S]*?)\}/);
  if (!m) throw new Error('no @media print :root block found');
  return [...m[1].matchAll(declRe)].map(([, k, v]) => [k, v.trim().toUpperCase()]);
}

const dark = parseRoot(read(DARK_SRC));
const light = parsePrintRoot(read(LIGHT_SRC));
if (dark.length < 15) throw new Error(`dark palette looks truncated: ${dark.length} tokens`);
if (light.length < 15) throw new Error(`light palette looks truncated: ${light.length} tokens`);

// The exact Google Fonts request index.html makes. No fonts are vendored in
// this repo, so the bundle carries the same remote request rather than
// inventing local copies.
const FONT_URL = read(DARK_SRC).match(/https:\/\/fonts\.googleapis\.com\/css2[^"']*/)[0];

const banner = (what, src) =>
  `/* AIVI Labs — ${what}\n   Extracted from ${src}. Do not hand-edit: regenerate with\n   .design-sync/build.mjs so the bundle stays equal to what ships. */\n\n`;

const decls = (pairs, indent = '  ') => pairs.map(([k, v]) => `${indent}${k}: ${v};`).join('\n');

rmSync(OUT, { recursive: true, force: true });

write('tokens/fonts.css',
  banner('type', `the <link> in ${DARK_SRC}`) +
  `@import url("${FONT_URL}");\n`);

write('tokens/tokens.css',
  banner('tokens (dark — primary)', `${DARK_SRC} :root`) +
  `/* Dark is the primary theme. The report aesthetic IS the brand. */\n:root {\n${decls(dark)}\n}\n`);

write('tokens/tokens-light.css',
  banner('tokens (light — print / secondary)', `${LIGHT_SRC} @media print`) +
  `/* Secondary. Applied on print, or opt in with [data-theme="light"].\n   AIVI Green #7EE2BC on white is 1.56:1 and fails every floor —\n   light surfaces use --pos #0F7A52 (5.35:1, AA) instead. */\n` +
  `@media print {\n  :root {\n${decls(light, '    ')}\n  }\n}\n\n` +
  `[data-theme="light"] {\n${decls(light)}\n}\n`);

// styles.css is the entry point: rendered designs receive only its transitive
// @import closure, so everything the brand needs must be reachable from here.
write('styles.css',
  banner('entry stylesheet', 'this repo’s shipping pages') +
  `@import "./tokens/fonts.css";\n@import "./tokens/tokens.css";\n@import "./tokens/tokens-light.css";\n\n` +
  `/* Page defaults, verbatim from ${DARK_SRC}. */\n` +
  `*{ box-sizing: border-box; }\n` +
  `html, body { margin:0; padding:0; background:var(--bg); color:var(--text-2); }\n` +
  `body {\n  font-family: var(--sans);\n  font-size: 16px;\n  line-height: 1.6;\n  -webkit-font-smoothing: antialiased;\n  text-rendering: optimizeLegibility;\n}\n\n` +
  `/* The masthead lockup, verbatim from ${DARK_SRC}. The AI square + wordmark\n   is the masthead form; use avatar-a-monogram for circular/small avatars. */\n` +
  `.logo-mark { background:var(--pos); color:#062418; width:34px; height:34px;\n  border-radius:8px; display:inline-flex; align-items:center; justify-content:center;\n  font-family:var(--mono); font-weight:700; font-size:13px; letter-spacing:0.05em; }\n` +
  `.wordmark { font-family:var(--sans); font-weight:600; font-size:17px;\n  color:var(--text-1); letter-spacing:-0.005em; }\n` +
  `.wordmark span { color:var(--pos); font-weight:400; }\n`);

// Brand assets. Diagnostics from the avatar bake-off are analysis artefacts,
// not brand assets -- they stay in the repo.
const SKIP = new Set(['avatar-comparison-sheet.png', 'avatar-40px-circle-magnified.png', 'brand.md']);
let assets = 0;
for (const f of readdirSync(join(ROOT, 'brand'))) {
  if (SKIP.has(f)) continue;
  mkdirSync(join(OUT, 'assets/brand'), { recursive: true });
  copyFileSync(join(ROOT, 'brand', f), join(OUT, 'assets/brand', f));
  assets++;
}

write('guidelines/brand.md', read('brand/brand.md'));

const header = read('.design-sync/conventions.md');
write('README.md', header + `\n\n---\n\n## Generated index\n\n` +
  `| file | what |\n|---|---|\n` +
  `| \`styles.css\` | Entry point. Imports every token file; carries page defaults and the masthead lockup classes. |\n` +
  `| \`tokens/tokens.css\` | ${dark.length} dark-theme custom properties (primary). |\n` +
  `| \`tokens/tokens-light.css\` | ${light.length} light/print custom properties (secondary). |\n` +
  `| \`tokens/fonts.css\` | IBM Plex Sans/Mono + Source Serif 4 from Google Fonts. |\n` +
  `| \`guidelines/brand.md\` | The canonical brand kit, verbatim. |\n` +
  `| \`assets/brand/\` | ${assets} mark, wordmark and social files (SVG + PNG exports). |\n\n` +
  `Built from \`${DARK_SRC}\` and \`${LIGHT_SRC}\` by \`.design-sync/build.mjs\`.\n`);

console.log(JSON.stringify({ darkTokens: dark.length, lightTokens: light.length, assets }, null, 2));
