"""Example world configurations and registry."""

from fantasy_map_generator.config import MapConfig
from fantasy_map_generator.worlds.arctic import ARCTIC_CONFIG
from fantasy_map_generator.worlds.autumn import AUTUMN_CONFIG
from fantasy_map_generator.worlds.desert import DESERT_CONFIG
from fantasy_map_generator.worlds.tropical import TROPICAL_CONFIG
from fantasy_map_generator.worlds.valley import VALLEY_CONFIG

WORLDS: dict[str, MapConfig] = {
    "valley": VALLEY_CONFIG,
    "desert": DESERT_CONFIG,
    "tropical": TROPICAL_CONFIG,
    "arctic": ARCTIC_CONFIG,
    "autumn": AUTUMN_CONFIG,
}

__all__ = [
    "ARCTIC_CONFIG",
    "AUTUMN_CONFIG",
    "DESERT_CONFIG",
    "TROPICAL_CONFIG",
    "VALLEY_CONFIG",
    "WORLDS",
]
