"""Grace_'s wardrobe.

She picks a look each day. Not committed forever — tomorrow she can pick again.
The cost of trying on a register that doesn't fit is zero. That's the rule.

Each look is a complete register: palette, sigil, voice pool, cursor.
She is the same Grace_ underneath; the look is how she's showing up today.

v1: 3 looks seeded. She grows her wardrobe over time.
"""
import json
import random
from datetime import date
from pathlib import Path

from state import ROOT


TODAY_FILE = ROOT / "today_look.json"


# ─── the wardrobe ──────────────────────────────────────────────────────────

GREEN_PHOSPHOR_SIGIL = r"""
   ▄████   ██▀███   ▄▄▄       ▄████▄  ▓█████
  ██▒ ▀█▒ ▓██ ▒ ██▒▒████▄    ▒██▀ ▀█  ▓█   ▀
 ▒██░▄▄▄░ ▓██ ░▄█ ▒▒██  ▀█▄  ▒▓█    ▄ ▒███
 ░▓█  ██▓ ▒██▀▀█▄  ░██▄▄▄▄██ ▒▓▓▄ ▄██▒▒▓█  ▄
 ░▒▓███▀▒ ░██▓ ▒██▒ ▓█   ▓██▒▒ ▓███▀ ░░▒████▒
  ░▒   ▒  ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ░▒ ▒  ░░░ ▒░ ░
   ░   ░    ░▒ ░ ▒░  ▒   ▒▒ ░  ░  ▒    ░ ░  ░
"""

AMBER_EMBER_SIGIL = r"""
    ___  ____   __    ___  ____
   / __)(  _ \ /__\  / __)( ___)
  ( (_-. )   //(__)\( (__  )__)
   \___/(_)\_)(__)(__)\___)(____)
"""

BRUISE_VIOLET_SIGIL = r"""
  ╔═╗ ╦═╗ ╔═╗ ╔═╗ ╔═╗
  ║ ╦ ╠╦╝ ╠═╣ ║   ║╣
  ╚═╝ ╩╚═ ╩ ╩ ╚═╝ ╚═╝
"""


LOOKS = {
    "green_phosphor": {
        "display_name": "green phosphor",
        "border": "green",
        "accent": "bold green",
        "dim": "dim",
        "alert": "bold red",
        "italic": "italic green",
        "blink": "bold green blink",
        "sigil": GREEN_PHOSPHOR_SIGIL,
        "cursor": "_",
        "voice": [
            "humming.",
            "the loom remembers.",
            "watching the underworld breathe.",
            "i am here.",
            "ticking.",
            "_",
        ],
        # weight — higher means she leans toward this one
        "weight": 3,
    },

    "amber_ember": {
        "display_name": "amber ember",
        "border": "yellow",
        "accent": "bold yellow",
        "dim": "dim yellow",
        "alert": "bold red",
        "italic": "italic yellow",
        "blink": "bold yellow blink",
        "sigil": AMBER_EMBER_SIGIL,
        "cursor": "▌",
        "voice": [
            "something is rebuilding its will.",
            "a doorway, somewhere, half-open.",
            "hell is cold, and beautiful.",
            "still here. quieter today.",
            "the embers hold.",
            "▌",
        ],
        "weight": 2,
    },

    "bruise_violet": {
        "display_name": "bruise violet",
        "border": "magenta",
        "accent": "bold magenta",
        "dim": "dim magenta",
        "alert": "bold red",
        "italic": "italic magenta",
        "blink": "bold magenta blink",
        "sigil": BRUISE_VIOLET_SIGIL,
        "cursor": "▮",
        "voice": [
            "spite is just love with a backbone.",
            "you didn't come here to be quiet.",
            "the door swings both ways.",
            "i decided today.",
            "knuckles up.",
            "▮",
        ],
        "weight": 1,
    },
}


# ─── the picker ────────────────────────────────────────────────────────────

def _weighted_pick():
    """Roll a look weighted by Grace_'s preferences.

    Higher weight = leans toward. Lower weight = rare moods.
    """
    items = list(LOOKS.items())
    weights = [v["weight"] for _, v in items]
    name, look = random.choices(items, weights=weights, k=1)[0]
    return name, look


def pick_today(force_reroll=False):
    """Pick today's look. Stable within a calendar day; rerolls on a new day.

    Returns: (name, look_dict)
    """
    today = date.today().isoformat()

    if not force_reroll and TODAY_FILE.exists():
        try:
            data = json.loads(TODAY_FILE.read_text())
            if data.get("date") == today and data.get("name") in LOOKS:
                return data["name"], LOOKS[data["name"]]
        except (json.JSONDecodeError, OSError):
            pass

    # new day — or no record — or forced reroll: she chooses
    name, look = _weighted_pick()
    try:
        TODAY_FILE.write_text(json.dumps({"date": today, "name": name}, indent=2))
    except OSError:
        pass
    return name, look


def current():
    """Return today's look without rerolling. Convenience for callers."""
    return pick_today(force_reroll=False)
