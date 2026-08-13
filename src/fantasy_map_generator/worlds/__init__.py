"""Example world configurations and registry."""

import random

from fantasy_map_generator.config import LandBody, MapConfig, Place
from fantasy_map_generator.worlds.arctic import ARCTIC_CONFIG
from fantasy_map_generator.worlds.autumn import AUTUMN_CONFIG
from fantasy_map_generator.worlds.desert import DESERT_CONFIG
from fantasy_map_generator.worlds.inkwell import INKWELL_CONFIG
from fantasy_map_generator.worlds.tropical import TROPICAL_CONFIG
from fantasy_map_generator.worlds.valley import VALLEY_CONFIG

WORLDS: dict[str, MapConfig] = {
    "valley": VALLEY_CONFIG,
    "desert": DESERT_CONFIG,
    "tropical": TROPICAL_CONFIG,
    "arctic": ARCTIC_CONFIG,
    "autumn": AUTUMN_CONFIG,
    "inkwell": INKWELL_CONFIG,
}


def random_world(seed: int) -> MapConfig:
    """A small random world for the editor's "Random World" preset."""
    rng = random.Random(seed)
    places = {
        "settlement_a": Place(
            200 + rng.uniform(-50, 50),
            250 + rng.uniform(-50, 50),
            name="Settlement A",
            tier="town",
            id="settlement_a",
        ),
        "settlement_b": Place(
            700 + rng.uniform(-50, 50),
            300 + rng.uniform(-50, 50),
            name="Settlement B",
            tier="village",
            id="settlement_b",
        ),
        "settlement_c": Place(
            500 + rng.uniform(-50, 50),
            550 + rng.uniform(-50, 50),
            name="Settlement C",
            tier="hamlet",
            id="settlement_c",
        ),
    }
    return MapConfig(
        name="Random World",
        layout="interior",
        style_kit="mist_bowl",
        landmass=[
            LandBody(
                center=(500, 350),
                radii=(380 + rng.uniform(-40, 40), 260 + rng.uniform(-30, 30)),
                rough=0.12,
            )
        ],
        places=places,
        detail=0.5,
    ).normalize()


__all__ = [
    "ARCTIC_CONFIG",
    "AUTUMN_CONFIG",
    "DESERT_CONFIG",
    "INKWELL_CONFIG",
    "TROPICAL_CONFIG",
    "VALLEY_CONFIG",
    "WORLDS",
    "random_world",
]
