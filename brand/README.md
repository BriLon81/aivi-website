# brand/

The AIVI Labs brand kit. **`brand.md` is the document** — tokens, contrast measurements, and the rule that the live files win whenever the kit disagrees with them. Everything else here is an asset it describes.

## `email-skin.html` moved out of this repo

It now lives at **`aivi-delivery-state/email/design-export-raw.html`** (private).

It was the **raw Design export**, not the working skin, and it still carried two strings that `email/render.py` explicitly bans:

- `active measurement subscription` — we sell one-shot reports; nobody has a subscription.
- `https://aivilabs.io/notifications` — that page 404s.

This repo is public and serves `aivilabs.io`. A raw export containing copy that misstates what we sell does not belong in it, even unreferenced — nothing links to it, but it was fetchable, and it reads as current.

The skin that actually ships is `aivi-delivery-state/email/skin.html`, which `render.py` builds the three transactional emails from and which has neither string. The moved file is kept only as a design record of what Design handed over.

> It was briefly committed here (`58c344c`, 2026-08-12) before being moved the same day, so it remains reachable in this repo's public history. Left alone deliberately — it is marketing copy, not a secret, and rewriting published history costs more than it saves.
