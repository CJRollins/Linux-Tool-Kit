"""Grace_ — the workshop's terminal companion.

Renders sigil, status panel, recent events, voice line, interactive prompt.
Pulls its register from today's look (see looks.py).

v1: ambient display. v2: interactive prompt.

Run as: python grace_.py
Quit:   Ctrl-C
"""
import asyncio
import random
import sys
import time

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.columns import Columns

from textual.app import App
from textual.widgets import Static, Input, Header
from textual.containers import Vertical, Horizontal

from state import read_state, ensure_dirs, EVENTS_LOG, append_event
import souls
import looks
import tilebuilder


def tail_events(n=6):
    if not EVENTS_LOG.exists():
        return []
    try:
        return EVENTS_LOG.read_text().splitlines()[-n:]
    except OSError:
        return []


def render_sigil(state, souls_data, events, voice, look):
    border = look["border"]
    accent = look["accent"]
    sigil = look["sigil"]
    sigil_panel = Panel(
        Align.center(Text(sigil, style=accent)),
        border_style=border,
        title=f"grace_  ·  {look['display_name']}",
        title_align="left",
        padding=(0, 1),
    )
    return sigil_panel

def render_status(state, souls_data, events, voice, look, tilebuilder):
    border = look["border"]
    accent = look["accent"]
    dim = look["dim"]
    alert = look["alert"]
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
    
    # Add player position if available
    if tilebuilder and tilebuilder.player_pos:
        pos = tilebuilder.player_pos
        status.append("\nexplorer     ", style=dim)
        status.append(f"({pos['x']}, {pos['y']})", style=accent)
    
    status_panel = Panel(status, title="status", border_style=border, title_align="left")
    return status_panel

def render_events(state, souls_data, events, voice, look):
    border = look["border"]
    dim = look["dim"]
    evt = Text()
    if events:
        for line in events:
            evt.append(line + "\n", style=dim)
    else:
        evt.append("nothing yet.", style=dim)
    events_panel = Panel(evt, title="events", border_style=border, title_align="left")
    return events_panel

def render_voice(state, souls_data, events, voice, look):
    border = look["border"]
    accent = look["accent"]
    italic = look["italic"]
    voice_text = Text()
    voice_text.append("  grace_  ", style=accent)
    voice_text.append(voice, style=italic)
    voice_panel = Panel(voice_text, border_style=border, padding=(0, 1))
    return voice_panel


class GraceApp(App):
    CSS = """
    #sigil {
        height: 5;
    }
    #middle {
        height: 10;
    }
    #voice {
        height: 3;
    }
    #prompt {
        height: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.last_change = time.time()
        self.last_look_check = time.time()
        self.look_name, self.look = looks.pick_today()
        self.voice = random.choice(self.look["voice"])
        self.tilebuilder = None
        self._init_tilebuilder()

    def _init_tilebuilder(self):
        """Initialize TileBuilder if world exists."""
        try:
            self.tilebuilder = tilebuilder.TileBuilder()
        except (ValueError, FileNotFoundError):
            self.tilebuilder = None

    def compose(self):
        yield Header(show_clock=True)
        with Vertical():
            yield Static(id="sigil")
            with Horizontal(id="middle"):
                yield Static(id="status")
                yield Static(id="events")
            yield Static(id="voice")
            yield Input(id="prompt", placeholder="speak, soul")

    async def on_mount(self):
        self.update_display()
        self.set_interval(0.5, self.update_display)

    def update_display(self):
        state = read_state()
        souls_data = souls.load()
        events = tail_events()

        # re-check the look every ~5 min
        if time.time() - self.last_look_check > 300:
            self.look_name, self.look = looks.pick_today()
            self.last_look_check = time.time()

        if time.time() - self.last_change > 12:
            self.voice = random.choice(self.look["voice"])
            self.last_change = time.time()

        self.query_one("#sigil").update(render_sigil(state, souls_data, events, self.voice, self.look))
        self.query_one("#status").update(render_status(state, souls_data, events, self.voice, self.look, self.tilebuilder))
        self.query_one("#events").update(render_events(state, souls_data, events, self.voice, self.look))
        self.query_one("#voice").update(render_voice(state, souls_data, events, self.voice, self.look))

    async def on_input_submitted(self, event):
        command = event.value.strip().lower()
        append_event(f"user said: {event.value}")
        
        response = self.handle_command(command)
        if response:
            append_event(f"grace_ responds: {response}")
        
        self.query_one("#prompt").value = ""

    def handle_command(self, command):
        """Handle user commands for world exploration."""
        if not self.tilebuilder:
            return "The world hasn't been born yet. Wait for the loom to weave."
        
        parts = command.split()
        if not parts:
            return None
        
        cmd = parts[0]
        
        if cmd in ["move", "go", "walk"]:
            if len(parts) < 2:
                return "Move where? Try: move north, move south, etc."
            direction = parts[1]
            distance = 1
            if len(parts) > 2 and parts[2].isdigit():
                distance = int(parts[2])
            return self.tilebuilder.move_player(direction, distance)
        
        elif cmd in ["travel", "fasttravel", "journey"]:
            if len(parts) < 2:
                return "Travel where? Try: travel monastery, travel castle"
            destination = " ".join(parts[1:])
            return self.tilebuilder.fast_travel_to_landmark(destination)
        
        elif cmd in ["look", "see", "view"]:
            return self.tilebuilder.look_around()
        
        elif cmd == "map":
            radius = 10
            if len(parts) > 1 and parts[1].isdigit():
                radius = int(parts[1])
            return f"```\n{self.tilebuilder.get_map_view(radius)}\n```"
        
        elif cmd in ["help", "?"]:
            return """Available commands:
• move/go <direction> [distance] - Move in a direction (north, south, east, west, diagonals)
• travel/journey <landmark> - Fast travel to a landmark
• look/see - Describe your current location
• map [radius] - Show map view centered on you
• help/? - Show this help"""
        
        else:
            return f"Unknown command: {cmd}. Type 'help' for available commands."


def main():
    ensure_dirs()
    app = GraceApp()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\ngrace_ sleeps.")
        sys.exit(0)
