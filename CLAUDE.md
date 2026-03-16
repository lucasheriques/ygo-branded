# Pure Branded 2026 — Regional Prep Guide

Interactive single-page study guide for playing pure Branded (no Despia) in the 2026 TCG format after the Burst Protocol booster set. Built for regionals prep.

## Structure

- `index.html` — The entire app (single file: HTML + CSS + JS)
- `images/` — Local card images (JPG, downloaded from YGOPRODeck API)
- `download_images.py` — Script to fetch/refresh card images locally

## How It Works

**index.html** is a self-contained SPA with 7 tabs: How It Works, All Cards, Combos, Hand Traps, Matchups, 2-Week Prep, Card Lookup.

Card data is defined in JS arrays (`C.core`, `C.engine`, `C.ed`, `C.spells`, `MU_CARDS`). Each card entry has: `[apiName, displayName, tags[], goalHTML, whyText, targets]`.

**Image loading strategy:**
1. Try local `images/{slug}.jpg` first (slug = lowercase, non-alphanumeric → hyphens)
2. On error, fall back to YGOPRODeck API (`image_url` for HD)
3. Card JSON is cached in IndexedDB (`ygo-v5` database) to avoid repeat API calls

**Key functions:**
- `loadCardImg(imgEl, name)` — Sets src to local path, onerror falls back to API
- `slugify(name)` — Converts card name to filename slug (must match Python script)
- `fetchCard(name)` — IndexedDB cache → API with rate-limited fetch queue (4 concurrent, 200ms gap)
- `mkCard(el, cardData)` — Renders a card entry with image, tags, goal, why, and target boxes
- `openCard(name)` — Opens modal with full card effect text from API

## Commands

```bash
# Download/refresh card images (requires aiohttp)
uv run --with aiohttp download_images.py
# or: pip install aiohttp && python download_images.py

# Serve locally
python -m http.server 8000
# then open http://localhost:8000
```

## Adding Cards

1. Add the card name to `CARDS` list in `download_images.py`
2. Run the script to download the image
3. Add the card entry to the appropriate array in `index.html` (`C.core`, `C.engine`, `C.ed`, `C.spells`, or `MU_CARDS`)
4. Format: `['API Name','Display Name',['tags'],'<b>Goal:</b> ...','Why text',{label:'Targets',items:[['Card','— reason']]}]`

## Deployment

Hosted on GitHub Pages from `main` branch. Push to deploy.

## Style Notes

- Dark theme with CSS custom properties (`:root` vars)
- Mobile-first responsive (600px breakpoint)
- system-ui font stack, 16px base
- No external dependencies — everything is vanilla JS
