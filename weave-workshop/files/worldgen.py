"""DF-inspired worldgen.

v1: heightmap birth — one shot at world creation.
v2: civilizations, tick loop, history events, named figures.
v3: when a figure dies → souls.soul_dies() → enters the Underworld.
"""
import math
import random


# low → high elevation
CHARS = " .,:-~*+=#@"


def generate_heightmap(seed, width=80, height=30):
    rng = random.Random(seed)
    grid = [[0.0] * width for _ in range(height)]
    n_hills = 60
    for _ in range(n_hills):
        cx = rng.uniform(0, width)
        cy = rng.uniform(0, height)
        r = rng.uniform(3, 14)
        amp = rng.uniform(-1.2, 1.6)
        for y in range(height):
            for x in range(width):
                d = math.hypot(x - cx, y - cy)
                if d < r:
                    grid[y][x] += amp * math.cos((d / r) * (math.pi / 2))
    return grid


def heightmap_to_ascii(grid):
    flat = [v for row in grid for v in row]
    lo, hi = min(flat), max(flat)
    span = (hi - lo) or 1
    out = []
    for row in grid:
        line = []
        for v in row:
            idx = int(((v - lo) / span) * (len(CHARS) - 1))
            line.append(CHARS[max(0, min(len(CHARS) - 1, idx))])
        out.append("".join(line))
    return "\n".join(out)


def place_landmarks(grid, seed):
    """Place specific landmarks on the world map."""
    rng = random.Random(seed + 1000)  # Different seed for landmarks
    height, width = len(grid), len(grid[0])
    
    landmarks = {}
    
    # Monastery - place in a valley/mid-elevation area
    monastery_x = rng.randint(width // 4, 3 * width // 4)
    monastery_y = rng.randint(height // 4, 3 * height // 4)
    # Find a suitable spot (not too high, not too low)
    for attempt in range(50):
        x = rng.randint(5, width - 6)
        y = rng.randint(5, height - 6)
        elevation = sum(grid[y + dy][x + dx] for dy in [-1, 0, 1] for dx in [-1, 0, 1]) / 9
        if -0.3 < elevation < 0.3:  # Mid-range elevation
            monastery_x, monastery_y = x, y
            break
    
    landmarks["monastery"] = {
        "x": monastery_x,
        "y": monastery_y,
        "name": "Monastery of the Weave",
        "description": "A hub of learning and contemplation, perched on a hillside overlooking the world."
    }
    
    # Castle of Najkir - place on a high peak
    castle_x = rng.randint(width // 4, 3 * width // 4)
    castle_y = rng.randint(height // 4, 3 * height // 4)
    # Find the highest nearby peak
    max_elevation = -float('inf')
    for attempt in range(50):
        x = rng.randint(5, width - 6)
        y = rng.randint(5, height - 6)
        elevation = sum(grid[y + dy][x + dx] for dy in [-2, -1, 0, 1, 2] for dx in [-2, -1, 0, 1, 2]) / 25
        if elevation > max_elevation:
            max_elevation = elevation
            castle_x, castle_y = x, y
    
    landmarks["castle_najkir"] = {
        "x": castle_x,
        "y": castle_y,
        "name": "Castle of Najkir",
        "description": "A mechanized flying island, defended by dragons crafted in its forges. It hovers above the highest peaks."
    }
    
    return landmarks


def birth_world(seed):
    grid = generate_heightmap(seed)
    landmarks = place_landmarks(grid, seed)
    return {
        "seed": seed,
        "ascii_map": heightmap_to_ascii(grid),
        "landmarks": landmarks,
    }
