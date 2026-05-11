"""The Loom. Background daemon. Weaves while the workshop is quiet.

Run as: python loom.py
Quit:   Ctrl-C
"""
import random
import sys
import time

from state import (
    ensure_dirs, read_state, write_state, append_event, WORLDS_DIR
)
from governor import Governor
from worldgen import birth_world
import souls


def ensure_world(state):
    """Birth a world on first run."""
    if state.get("current_world_seed") is None:
        seed = random.randint(1, 999_999_999)
        world = birth_world(seed)
        world_dir = WORLDS_DIR / str(seed)
        world_dir.mkdir(parents=True, exist_ok=True)
        (world_dir / "map.txt").write_text(world["ascii_map"])
        state["current_world_seed"] = seed
        state["tick"] = 0
        write_state(state)
        append_event(f"a new world was born. seed: {seed}.")
    return state


def main():
    ensure_dirs()
    souls.seed_first_soul()

    state = read_state()
    write_state(state)               # ensure file exists
    state = ensure_world(state)

    gov = Governor()
    append_event("loom awakens.")
    try:
        while True:
            t0 = time.time()
            ceiling = gov.update()

            # one tick of work
            souls.tick()
            state = read_state()
            state["tick"] = state.get("tick", 0) + 1
            state["loom_status"] = "weaving" if ceiling > 5 else "humming"
            state["loom_governor"] = {"ceiling_pct": ceiling}
            write_state(state)

            work_seconds = time.time() - t0
            gov.sleep_for_duty_cycle(work_seconds)
    except KeyboardInterrupt:
        append_event("loom rests.")
        sys.exit(0)


if __name__ == "__main__":
    main()
