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


def birth_world(seed):
    grid = generate_heightmap(seed)
    return {
        "seed": seed,
        "ascii_map": heightmap_to_ascii(grid),
    }
