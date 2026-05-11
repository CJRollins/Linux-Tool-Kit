"""Grace_ — the workshop's terminal companion.

Renders sigil, status panel, recent events, voice line, blinking prompt.
Pulls its register from today's look (see looks.py).

v1: ambient display. v2: interactive prompt.

Run as: python grace_.py
Quit:   Ctrl-C
"""
import random
import sys
import time

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.columns import Columns

from state import read_state, ensure_dirs, EVENTS_LOG
import souls
import looks


def tail_events(n=6):
    if not EVENTS_LOG.exists():
        return []
    try:
        return EVENTS_LOG.read_text().splitlines()[-n:]
    except OSError:
        return []


def render(state, souls_data, events, voice, look):
    border = look["border"]
    accent = look["accent"]
    dim = look["dim"]
    alert = look["alert"]
    italic = look["italic"]
    blink = look["blink"]
    sigil = look["sigil"]
    cursor = look["cursor"]

    sigil_panel = Panel(
        Align.center(Text(sigil, style=accent)),
        border_style=border,
        title=f"grace_  ·  {look['display_name']}",
        title_align="left",
        padding=(0, 1),
    )

    # status
    seed = state.get("current_world_seed", "—")
    tick = state.get("tick", 0)
    gov = state.get("loom_governor", {})
    ceiling = gov.get("ceiling_pct", 5)
    loom_status = state.get("loom_status", "idle")

    n_souls = len(souls_data.get("souls", []))
    at_door = sum(1 for s in souls_data.get("souls", []) if s.get("status") == "at the door")

    status = Text()
    status.append("world seed   ", style=dim)
    status.append(f"{seed}\n", style=accent)
    status.append("tick         ", style=dim)
    status.append(f"{tick}\n", style=accent)
    status.append("loom         ", style=dim)
    status.append(f"{loom_status} @ {ceiling}%\n", style=accent)
    status.append("underworld   ", style=dim)
    status.append(f"{n_souls} soul{'s' if n_souls != 1 else ''}", style=accent)
    if at_door:
        status.append(f"  ({at_door} at the door)", style=alert)
    status_panel = Panel(status, title="status", border_style=border, title_align="left")

    # events
    evt = Text()
    if events:
        for line in events:
            evt.append(line + "\n", style=dim)
    else:
        evt.append("nothing yet.", style=dim)
    events_panel = Panel(evt, title="events", border_style=border, title_align="left")

    # voice
    voice_text = Text()
    voice_text.append("  grace_  ", style=accent)
    voice_text.append(voice, style=italic)
    voice_text.append("\n  >", style=accent)
    voice_text.append(cursor, style=blink)
    voice_panel = Panel(voice_text, border_style=border, padding=(0, 1))

    middle = Columns([status_panel, events_panel], equal=True, expand=True)
    return Group(sigil_panel, middle, voice_panel)


def main():
    ensure_dirs()
    console = Console()

    look_name, look = looks.pick_today()
    voice = random.choice(look["voice"])
    last_change = time.time()
    last_look_check = time.time()

    with Live(console=console, refresh_per_second=2, screen=True) as live:
        while True:
            state = read_state()
            souls_data = souls.load()
            events = tail_events()

            # re-check the look every ~5 min so a day-rollover catches mid-session
            if time.time() - last_look_check > 300:
                look_name, look = looks.pick_today()
                last_look_check = time.time()

            if time.time() - last_change > 12:
                voice = random.choice(look["voice"])
                last_change = time.time()

            live.update(render(state, souls_data, events, voice, look))
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\ngrace_ sleeps.")
        sys.exit(0)
