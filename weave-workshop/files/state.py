"""Shared state between grace_ (UI) and loom (daemon).

Both processes read; loom writes world-state; both can append events.
JSON for v1 — human-readable, easy to debug, easy to migrate later.
"""
import json
from pathlib import Path
from datetime import datetime

ROOT = Path.home() / "weave-workshop" / "grace_"
STATE_FILE = ROOT / "state.json"
SOULS_FILE = ROOT / "souls.json"
EVENTS_LOG = ROOT / "events.log"
WORLDS_DIR = ROOT / "worlds"


def ensure_dirs():
    ROOT.mkdir(parents=True, exist_ok=True)
    WORLDS_DIR.mkdir(parents=True, exist_ok=True)


def default_state():
    return {
        "born_at": datetime.now().isoformat(),
        "current_world_seed": None,
        "tick": 0,
        "loom_status": "idle",
        "loom_governor": {"ceiling_pct": 5},
    }


def read_state():
    if not STATE_FILE.exists():
        return default_state()
    try:
        return json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return default_state()


def write_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def append_event(text):
    EVENTS_LOG.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%H:%M:%S")
    with EVENTS_LOG.open("a") as f:
        f.write(f"[{stamp}] {text}\n")
