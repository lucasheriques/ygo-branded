#!/usr/bin/env python3
"""Download all YuGiOh card images used in the Branded guide locally."""

import json
import os
import re
import time
import urllib.request
import urllib.error

API = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

# All card names used in the guide (main cards + target references + matchup cards)
CARDS = [
    # Core starters
    "Branded Fusion",
    "Fallen of the White Dragon",
    "Albion the Shrouded Dragon",
    "Blazing Cartesia, the Virtuous",
    "Branded in High Spirits",
    "The Fallen & The Virtuous",
    "Branded Opening",
    # Engine
    "Fallen of Albaz",
    "Guiding Quem, the Virtuous",
    "Incredible Ecclesia, the Virtuous",
    "The Golden Swordsoul",
    "Tri-Brigade Mercourier",
    "Bystial Lubellion",
    "Comedy",
    # Extra Deck
    "Albion the Branded Dragon",
    "Lubellion the Searing Dragon",
    "Mirrorjade the Iceblade Dragon",
    "Granguignol the Dusk Dragon",
    "Ecclesia and the Dark Dragon",
    "Titaniklad the Ash Dragon",
    "Albion the Sanctifire Dragon",
    "Guardian Chimera",
    # Spells/Traps
    "Branded Lost",
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
    s = s.strip("-")
    return s


def fetch_card(name: str) -> dict | None:
    """Fetch card data from YGOPRODeck API."""
    url = f"{API}?name={urllib.request.quote(name)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "YGO-Branded-Guide/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("data", [None])[0]
    except Exception:
        # Try fuzzy search
        url = f"{API}?fname={urllib.request.quote(name)}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "YGO-Branded-Guide/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                return data.get("data", [None])[0]
        except Exception as e:
            print(f"  ERROR fetching {name}: {e}")
            return None


def download_image(url: str, path: str) -> bool:
    """Download image from URL to path."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "YGO-Branded-Guide/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(path, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"  ERROR downloading: {e}")
        return False


def main():
    os.makedirs(IMG_DIR, exist_ok=True)

    total = len(CARDS)
    success = 0
    skipped = 0

    for i, name in enumerate(CARDS, 1):
        slug = slugify(name)
        small_path = os.path.join(IMG_DIR, f"{slug}.jpg")

        # Skip if already downloaded
        if os.path.exists(small_path) and os.path.getsize(small_path) > 1000:
            print(f"[{i}/{total}] SKIP (exists): {name}")
            skipped += 1
            success += 1
            continue

        print(f"[{i}/{total}] Fetching: {name}")
        card = fetch_card(name)
        if not card:
            print(f"  NOT FOUND in API")
            continue

        images = card.get("card_images", [{}])[0]
        small_url = images.get("image_url_small") or images.get("image_url")

        if not small_url:
            print(f"  NO IMAGE URL")
            continue

        if download_image(small_url, small_path):
            success += 1
            print(f"  OK → {slug}.jpg")
        else:
            print(f"  FAILED")

        # Rate limit: 250ms between requests
        time.sleep(0.25)

    print(f"\nDone: {success}/{total} cards ({skipped} skipped, {success - skipped} downloaded)")


if __name__ == "__main__":
    main()
