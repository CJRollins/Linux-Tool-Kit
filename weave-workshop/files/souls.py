"""The Underworld.

Souls don't die. They come here to recharge — and to reckon.

Each soul carries threads: things unfinished, things unsaid, things they
have not yet learned to put down. A thread can be settled, abandoned,
transmuted, or twisted. The arch opens for a soul only when every thread
they carry is in one of the first three states. Will/capacity says whether
they're able to work today. The threads say what work is left.

Each soul who arrives is greeted by the welcome text — the law of the game.
It is not a rule to follow. It is a description of where they are now.

v2a: threads + reckoning + welcome.
v2b: the arch itself, character creator, commitment-binding.
v2c: re-entry with carry-over.
"""
import json
import random
from datetime import datetime
from pathlib import Path

from state import SOULS_FILE, ROOT, append_event


WILL_THRESHOLD = 100      # capacity ceiling — full will means able to work
WORKING_STATES = {"working", "twisted"}    # threads still in motion
RESOLVED_STATES = {"settled", "abandoned", "transmuted"}  # arch-eligible
ALL_STATES = WORKING_STATES | RESOLVED_STATES

WELCOME_FILE = ROOT / "welcome.txt"


# ─── persistence ───────────────────────────────────────────────────────────

def load():
    if not SOULS_FILE.exists():
        return {"souls": []}
    try:
        return json.loads(SOULS_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {"souls": []}


def save(data):
    SOULS_FILE.write_text(json.dumps(data, indent=2))


def welcome_text():
    """Return the welcome text. Souls hear this once, on arrival."""
    if WELCOME_FILE.exists():
        try:
            return WELCOME_FILE.read_text()
        except OSError:
            return ""
    return ""


# ─── thread helpers ────────────────────────────────────────────────────────

def _new_thread(text, kind="unfinished", weight=5):
    """Build a thread. weight is how heavy it sits (1=light, 10=crushing)."""
    return {
        "text": text,
        "kind": kind,
        "weight": weight,
        "tension": 0,            # 0=resting; climbs when twisting
        "state": "working",
        "settled_how": None,
        "history": [],           # micro-log of every move this thread has made
    }


def _log_thread_move(thread, verb, note=None):
    thread["history"].append({
        "at": datetime.now().isoformat(),
        "verb": verb,
        "note": note,
    })


# ─── seeding ───────────────────────────────────────────────────────────────

def seed_first_soul():
    """Mavrin the Underspoken. The first soul. Carries one comfort-thread."""
    data = load()
    if data["souls"]:
        return

    mavrin = {
        "name": "Mavrin the Underspoken",
        "lives": [{
            "world_seed": None,
            "epitaph": "spoke once, was heard forever",
        }],
        "will": 73,
        "status": "recharging",
        "entered": "before history",
        "threads": [
            _new_thread(
                text="the stars went out on a Tuesday. it took him a hundred years to learn he could light one himself.",
                kind="comfort",
                weight=4,
            ),
        ],
        "has_heard_welcome": False,
    }
    data["souls"].append(mavrin)
    save(data)


# ─── arrival ───────────────────────────────────────────────────────────────

def soul_dies(name, life_record, threads=None):
    """A soul arrives in the Underworld. New souls hear the welcome on their first tick."""
    data = load()
    existing = next((s for s in data["souls"] if s["name"] == name), None)
    if existing:
        existing["lives"].append(life_record)
        existing["will"] = 0
        existing["status"] = "recharging"
        existing["entered"] = datetime.now().isoformat()
        # threads from prior visits persist; new threads (if given) get appended
        if threads:
            existing.setdefault("threads", []).extend([_new_thread(**t) for t in threads])
    else:
        data["souls"].append({
            "name": name,
            "lives": [life_record],
            "will": 0,
            "status": "recharging",
            "entered": datetime.now().isoformat(),
            "threads": [_new_thread(**t) for t in (threads or [])],
            "has_heard_welcome": False,
        })
    save(data)


def _greet_if_new(soul):
    """First tick after arrival, deliver the welcome to the events log."""
    if not soul.get("has_heard_welcome"):
        append_event(f"{soul['name']} arrives in the Underworld. they are read the welcome.")
        soul["has_heard_welcome"] = True


# ─── progression ───────────────────────────────────────────────────────────

def _has_unfinished_threads(soul):
    return any(t["state"] in WORKING_STATES for t in soul.get("threads", []))


def _all_threads_resolved(soul):
    threads = soul.get("threads", [])
    if not threads:
        return False        # a soul with no threads is unfinished by default
    return all(t["state"] in RESOLVED_STATES for t in threads)


def _stochastic_thread_step(soul):
    """One tick of automatic thread-work.

    Pick a working thread. Roll against its weight. Outcomes:
      - clean success: tension drops; if tension hits 0, state may shift to settled/abandoned/transmuted
      - partial: tension drifts up or down by 1
      - twist: thread becomes 'twisted' (tension climbs sharply)
    """
    threads = [t for t in soul.get("threads", []) if t["state"] in WORKING_STATES]
    if not threads:
        return

    t = random.choice(threads)
    roll = random.randint(1, 20)

    # heavier threads are harder to move; capacity matters too
    capacity_factor = soul["will"] / WILL_THRESHOLD          # 0..1
    effective = roll + int(capacity_factor * 5) - t["weight"] // 2

    if effective >= 14:
        # clean move toward resolution
        t["tension"] = max(0, t["tension"] - 2)
        if t["tension"] == 0 and t["state"] == "working":
            # 60% settle, 25% abandon, 15% transmute — most resolutions are quiet
            outcome = random.choices(
                ["settled", "abandoned", "transmuted"],
                weights=[60, 25, 15], k=1,
            )[0]
            t["state"] = outcome
            t["settled_how"] = "stochastic"
            _log_thread_move(t, outcome)
            append_event(f"{soul['name']} {_verb_for_resolution(outcome)} a thread.")
        elif t["state"] == "twisted" and t["tension"] <= 1:
            t["state"] = "working"
            _log_thread_move(t, "untwisted")
            append_event(f"a twisted thread in {soul['name']}'s hand eased.")
    elif effective <= 3:
        # twist
        if t["state"] != "twisted":
            t["state"] = "twisted"
            t["tension"] += 3
            _log_thread_move(t, "twisted")
            append_event(f"a thread twisted in {soul['name']}'s hand; they sat with it.")
        else:
            t["tension"] += 1
    else:
        # drift
        t["tension"] += random.choice([-1, 0, 0, 1])
        t["tension"] = max(0, t["tension"])


def _verb_for_resolution(outcome):
    return {
        "settled": "settled",
        "abandoned": "laid down",
        "transmuted": "transmuted",
    }.get(outcome, "moved")


def tick():
    """Each loom-tick: greet new souls, recharge capacity, work threads,
    check for arch-eligibility.
    """
    data = load()
    changed = False
    for soul in data["souls"]:
        # 1. greet on arrival
        if not soul.get("has_heard_welcome"):
            _greet_if_new(soul)
            changed = True

        # 2. recharge will/capacity
        if soul["status"] == "recharging":
            new_will = min(WILL_THRESHOLD, soul.get("will", 0) + 1)
            if new_will != soul["will"]:
                soul["will"] = new_will
                changed = True

        # 3. work threads if there's capacity to do so
        if soul["status"] in {"recharging", "at the door"} and soul["will"] >= 20:
            before = json.dumps(soul.get("threads", []), sort_keys=True)
            _stochastic_thread_step(soul)
            after = json.dumps(soul.get("threads", []), sort_keys=True)
            if before != after:
                changed = True

        # 4. arch-eligibility check
        if _all_threads_resolved(soul) and soul["status"] != "at the door":
            soul["status"] = "at the door"
            _log_status_change = True
            append_event(f"{soul['name']} has settled every thread. the arch is near.")
            changed = True
        elif (not _all_threads_resolved(soul)) and soul["status"] == "at the door":
            # if new threads got added (e.g. re-arrival), they step back from the door
            soul["status"] = "recharging"
            append_event(f"{soul['name']} steps back from the arch. more work to do.")
            changed = True

    if changed:
        save(data)
    return data


# ─── interventions (the human reaches in) ──────────────────────────────────

def intervene(soul_name, thread_index, verb, note=None):
    """The Spinner authors a move on a specific thread.

    verb ∈ {"settle", "abandon", "transmute", "twist", "ease"}
      settle    — clean resolution
      abandon   — laid down without resolving
      transmute — became something else (fuel, teaching, etc.)
      twist     — the soul tried and made it worse
      ease      — partial relief; tension drops by 2 but state unchanged
    """
    data = load()
    soul = next((s for s in data["souls"] if s["name"] == soul_name), None)
    if not soul:
        return False, f"no soul named {soul_name!r}"
    threads = soul.get("threads", [])
    if not (0 <= thread_index < len(threads)):
        return False, f"thread index {thread_index} out of range"
    t = threads[thread_index]

    if verb in {"settle", "abandon", "transmute"}:
        state_map = {"settle": "settled", "abandon": "abandoned", "transmute": "transmuted"}
        t["state"] = state_map[verb]
        t["tension"] = 0
        t["settled_how"] = "authored"
        _log_thread_move(t, verb, note)
        append_event(f"the Spinner reached in. {soul_name} {_verb_for_resolution(state_map[verb])} a thread.")
    elif verb == "twist":
        t["state"] = "twisted"
        t["tension"] += 3
        _log_thread_move(t, "twisted", note)
        append_event(f"a thread of {soul_name}'s twisted by intent.")
    elif verb == "ease":
        t["tension"] = max(0, t["tension"] - 2)
        _log_thread_move(t, "eased", note)
        append_event(f"the Spinner eased a thread in {soul_name}'s hand.")
    else:
        return False, f"unknown verb {verb!r}"

    save(data)
    return True, "ok"


def add_thread(soul_name, text, kind="unfinished", weight=5):
    """Append a new thread to an existing soul."""
    data = load()
    soul = next((s for s in data["souls"] if s["name"] == soul_name), None)
    if not soul:
        return False, f"no soul named {soul_name!r}"
    soul.setdefault("threads", []).append(_new_thread(text, kind, weight))
    append_event(f"{soul_name} picks up a new thread: \u201c{text}\u201d")
    save(data)
    return True, "ok"
