#!/usr/bin/env python3
"""Download all YuGiOh card images used in the Branded guide locally (HD).

Uses asyncio + aiohttp for concurrent downloads. Run with:
  uv run --with aiohttp download_images.py
  # or: pip install aiohttp && python download_images.py
"""

import asyncio
import json
import os
import re
import sys

try:
    import aiohttp
except ImportError:
    print("aiohttp required. Install with: pip install aiohttp")
    print("Or run with: uv run --with aiohttp download_images.py")
    sys.exit(1)

API = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
MAX_CONCURRENT = 6  # concurrent downloads

# All card names used in the guide
CARDS = [
    # Core starters
    "Branded Fusion",
    "Fallen of the White Dragon",
    "Albion the Shrouded Dragon",
    "Blazing Cartesia, the Virtuous",
    "Branded in High Spirits",
    "The Fallen & The Virtuous",
    "Branded Opening",
    "Aluber the Jester of Despia",
    # Engine
    "Fallen of Albaz",
    "Guiding Quem, the Virtuous",
    "Incredible Ecclesia, the Virtuous",
    "The Golden Swordsoul",
    "Tri-Brigade Mercourier",
    "Bystial Lubellion",
    # Extra Deck
    "Albion the Branded Dragon",
    "Lubellion the Searing Dragon",
    "Mirrorjade the Iceblade Dragon",
    "Granguignol the Dusk Dragon",
    "Ecclesia and the Dark Dragon",
    "Titaniklad the Ash Dragon",
    "Albion the Sanctifire Dragon",
    "Secreterion Dragon",
    "Despian Proskenion",
    "Alba-Lenatus the Abyss Dragon",
    "Rindbrumm the Striking Dragon",
    "The Dragon that Devours the Dogma",
    "Khaos Starsource Dragon",
    # Spells/Traps
    "Branded Lost",
    "Branded in White",
    "Branded in Red",
    "Branded Retribution",
    # Matchup - Sky Striker
    "Sky Striker Mobilize - Engage!",
    "Sky Striker Ace - Raye",
    "Sky Striker Mecha - Widow Anchor",
    "Sky Striker Ace - Zero",
    # Matchup - Fiendsmith
    "Fiendsmith's Requiem",
    "Fiendsmith Engraver",
    "D/D/D Wave High King Caesar",
    # Matchup - Mitsurugi
    "End of the World Ruler",
    # Matchup - Vanquish Soul
    "Vanquish Soul Razen",
    "Dr. Mad Love",
    # Matchup - Maliss
    "Maliss P White Rabbit",
    "Maliss P Dormouse",
    # Matchup - Radiant Typhoon
    "Radiant Typhoon Krosea",
    "Radiant Typhoon Meghala",
    "Radiant Typhoon Mandate",
    # Matchup - Dracotail
    "Dracotail Lukias",
    "Rahu Dracotail",
]


def slugify(name: str) -> str:
    """Convert card name to a safe filename slug."""
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


# Minimum file size for HD images (low-res are ~25-33KB, HD are ~60KB+)
MIN_HD_SIZE = 50_000


async def fetch_card(session: aiohttp.ClientSession, name: str) -> dict | None:
    """Fetch card data from YGOPRODeck API."""
    for query_param in ["name", "fname"]:
        url = f"{API}?{query_param}={name}"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    card = (data.get("data") or [None])[0]
                    if card:
                        return card
        except Exception:
            pass
    return None


async def download_image(session: aiohttp.ClientSession, url: str, path: str) -> bool:
    """Download image from URL to path."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status != 200:
                return False
            data = await resp.read()
            with open(path, "wb") as f:
                f.write(data)
            return True
    except Exception as e:
        print(f"  ERROR downloading: {e}")
        return False


async def process_card(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    name: str,
    index: int,
    total: int,
) -> bool:
    """Process a single card: fetch data + download HD image."""
    async with semaphore:
        slug = slugify(name)
        path = os.path.join(IMG_DIR, f"{slug}.jpg")

        # Skip if already downloaded in HD (>50KB = likely full res)
        if os.path.exists(path) and os.path.getsize(path) > MIN_HD_SIZE:
            print(f"[{index}/{total}] SKIP (HD exists): {name}")
            return True

        print(f"[{index}/{total}] Fetching: {name}")
        card = await fetch_card(session, name)
        if not card:
            print(f"  NOT FOUND in API")
            return False

        images = card.get("card_images", [{}])[0]
        # Prefer full HD image (image_url), NOT image_url_small
        hd_url = images.get("image_url")
        if not hd_url:
            hd_url = images.get("image_url_small")
        if not hd_url:
            print(f"  NO IMAGE URL")
            return False

        if await download_image(session, hd_url, path):
            size_kb = os.path.getsize(path) / 1024
            print(f"  OK → {slug}.jpg ({size_kb:.0f}KB)")
            return True
        else:
            print(f"  FAILED")
            return False


async def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    total = len(CARDS)

    headers = {"User-Agent": "YGO-Branded-Guide/1.0"}
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [
            process_card(session, semaphore, name, i, total)
            for i, name in enumerate(CARDS, 1)
        ]
        results = await asyncio.gather(*tasks)

    success = sum(1 for r in results if r)
    print(f"\nDone: {success}/{total} cards downloaded/verified")


if __name__ == "__main__":
    asyncio.run(main())
