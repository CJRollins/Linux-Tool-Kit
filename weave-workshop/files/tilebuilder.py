"""TileBuilder — exploring the world, one tile at a time.

The TileBuilder lets you explore the world map, move around, and discover landmarks.
It's the interface between the player and the generated world.

v1.5: Basic exploration, movement, landmarks, fast travel to Monastery.
"""
import json
import math
from pathlib import Path
from typing import Optional, Dict, Any

from state import WORLDS_DIR, read_state, write_state, append_event


class TileBuilder:
    def __init__(self):
        self.state = read_state()
        self.world_seed = self.state.get("current_world_seed")
        if not self.world_seed:
            raise ValueError("No world has been born yet")
        
        self.world_dir = WORLDS_DIR / str(self.world_seed)
        self.world_data = self.load_world_data()
        self.player_pos = self.get_player_position()
        
    def load_world_data(self) -> Dict[str, Any]:
        """Load the world data from disk."""
        world_file = self.world_dir / "world.json"
        if not world_file.exists():
            # Fallback for old worlds without world.json
            map_file = self.world_dir / "map.txt"
            if map_file.exists():
                ascii_map = map_file.read_text()
                return {
                    "seed": self.world_seed,
                    "ascii_map": ascii_map,
                    "landmarks": {}
                }
            else:
                raise FileNotFoundError(f"World data not found for seed {self.world_seed}")
        
        return json.loads(world_file.read_text())
    
    def get_player_position(self) -> Dict[str, int]:
        """Get the player's current position, defaulting to Monastery if not set."""
        pos = self.state.get("player_position", {})
        if not pos and "monastery" in self.world_data.get("landmarks", {}):
            # Start at Monastery
            monastery = self.world_data["landmarks"]["monastery"]
            pos = {"x": monastery["x"], "y": monastery["y"]}
            self.state["player_position"] = pos
            write_state(self.state)
            append_event("you awaken at the Monastery of the Weave.")
        return pos
    
    def get_map_view(self, radius: int = 10) -> str:
        """Get a view of the map centered on the player position."""
        if not self.player_pos:
            return "You are nowhere. The world hasn't found you yet."
        
        lines = self.world_data["ascii_map"].splitlines()
        height, width = len(lines), len(lines[0]) if lines else 0
        
        x, y = self.player_pos["x"], self.player_pos["y"]
        
        # Create a view window
        view_lines = []
        for dy in range(-radius, radius + 1):
            line = ""
            for dx in range(-radius, radius + 1):
                px, py = x + dx, y + dy
                if 0 <= px < width and 0 <= py < height:
                    char = lines[py][px]
                    # Mark player position
                    if dx == 0 and dy == 0:
                        char = "@"
                    line += char
                else:
                    line += " "
            view_lines.append(line)
        
        return "\n".join(view_lines)
    
    def move_player(self, direction: str, distance: int = 1) -> str:
        """Move the player in a direction."""
        if not self.player_pos:
            return "You cannot move. You are nowhere."
        
        directions = {
            "north": (0, -1),
            "south": (0, 1),
            "east": (1, 0),
            "west": (-1, 0),
            "northeast": (1, -1),
            "northwest": (-1, -1),
            "southeast": (1, 1),
            "southwest": (-1, 1)
        }
        
        if direction not in directions:
            return f"Unknown direction: {direction}. Try: north, south, east, west, or diagonals."
        
        dx, dy = directions[direction]
        new_x = self.player_pos["x"] + dx * distance
        new_y = self.player_pos["y"] + dy * distance
        
        lines = self.world_data["ascii_map"].splitlines()
        height, width = len(lines), len(lines[0]) if lines else 0
        
        if not (0 <= new_x < width and 0 <= new_y < height):
            return "You cannot go that way. The edge of the world blocks your path."
        
        self.player_pos["x"] = new_x
        self.player_pos["y"] = new_y
        self.state["player_position"] = self.player_pos
        write_state(self.state)
        
        # Check for landmarks
        landmark_here = self.get_landmark_at_position(new_x, new_y)
        if landmark_here:
            append_event(f"you arrive at {landmark_here['name']}.")
            return f"You move {direction} and arrive at {landmark_here['name']}.\n{landmark_here['description']}"
        else:
            append_event(f"you travel {direction}.")
            return f"You move {direction}."
    
    def get_landmark_at_position(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """Check if there's a landmark at the given position."""
        landmarks = self.world_data.get("landmarks", {})
        for landmark_key, landmark in landmarks.items():
            if landmark["x"] == x and landmark["y"] == y:
                return landmark
        return None
    
    def fast_travel_to_landmark(self, landmark_name: str) -> str:
        """Fast travel to a known landmark."""
        landmarks = self.world_data.get("landmarks", {})
        
        # Find landmark by name (case-insensitive partial match)
        target = None
        for key, landmark in landmarks.items():
            if landmark_name.lower() in landmark["name"].lower():
                target = landmark
                break
        
        if not target:
            return f"Unknown landmark: {landmark_name}"
        
        if not self.player_pos:
            return "You cannot travel. You are nowhere."
        
        # Calculate distance
        dx = target["x"] - self.player_pos["x"]
        dy = target["y"] - self.player_pos["y"]
        distance = math.sqrt(dx*dx + dy*dy)
        
        self.player_pos["x"] = target["x"]
        self.player_pos["y"] = target["y"]
        self.state["player_position"] = self.player_pos
        write_state(self.state)
        
        append_event(f"you fast travel to {target['name']}.")
        return f"You journey through the weave and arrive at {target['name']}.\n{target['description']}"
    
    def look_around(self) -> str:
        """Describe the current location and nearby landmarks."""
        if not self.player_pos:
            return "You are nowhere."
        
        description = "You stand "
        
        # Get elevation info
        lines = self.world_data["ascii_map"].splitlines()
        if self.player_pos["y"] < len(lines) and self.player_pos["x"] < len(lines[self.player_pos["y"]]):
            terrain = lines[self.player_pos["y"]][self.player_pos["x"]]
            terrain_desc = {
                " ": "in empty void",
                ".": "on flat ground",
                ",": "on low ground", 
                ":": "on rolling hills",
                "-": "on foothills",
                "~": "near water",
                "*": "on highlands",
                "+": "on mountains",
                "=": "on peaks",
                "#": "on the highest peaks"
            }.get(terrain, f"on {terrain} terrain")
            description += terrain_desc
        else:
            description += "somewhere unknown"
        
        # Check for landmarks
        landmark_here = self.get_landmark_at_position(self.player_pos["x"], self.player_pos["y"])
        if landmark_here:
            description += f", at {landmark_here['name']}."
        else:
            description += "."
        
        # Look for nearby landmarks
        nearby = []
        landmarks = self.world_data.get("landmarks", {})
        for key, landmark in landmarks.items():
            if landmark["x"] == self.player_pos["x"] and landmark["y"] == self.player_pos["y"]:
                continue  # Already mentioned
            dx = landmark["x"] - self.player_pos["x"]
            dy = landmark["y"] - self.player_pos["y"]
            distance = math.sqrt(dx*dx + dy*dy)
            if distance <= 20:  # Within view distance
                direction = self.get_direction_name(dx, dy)
                nearby.append(f"{landmark['name']} {direction} ({int(distance)} tiles)")
        
        if nearby:
            description += "\n\nNearby: " + ", ".join(nearby)
        
        return description
    
    def get_direction_name(self, dx: float, dy: float) -> str:
        """Get a directional description from dx, dy."""
        if abs(dx) < 0.5 and abs(dy) < 0.5:
            return "here"
        
        angle = math.degrees(math.atan2(dy, dx))
        directions = [
            ("north", 0),
            ("northeast", 45),
            ("east", 90),
            ("southeast", 135),
            ("south", 180),
            ("southwest", 225),
            ("west", 270),
            ("northwest", 315)
        ]
        
        # Find closest direction
        closest = min(directions, key=lambda d: min(abs(angle - d[1]), 360 - abs(angle - d[1])))
        return closest[0]