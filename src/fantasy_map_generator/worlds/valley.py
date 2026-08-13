"""Valley of Mists — exact parity with sister mapgen."""

from fantasy_map_generator.valley import default_valley_config

VALLEY_CONFIG = default_valley_config()

# Re-export palette for callers that imported it historically
VALLEY_PALETTE = VALLEY_CONFIG.palette
