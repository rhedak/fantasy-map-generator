"""Procedurally generates fantasy world maps as parametric SVG.

This package provides the core map generation engine, with optional PNG export
and an interactive web GUI. Maps are defined by a MapConfig object containing
geography, palette, routes, and settlements.

Example usage:
    from fantasy_map_generator.render import render_map
    from fantasy_map_generator.worlds import VALLEY_CONFIG

    svg = render_map(config=VALLEY_CONFIG, seed=42)
    with open("map.svg", "w") as f:
        f.write(svg)
"""

from fantasy_map_generator.render import render_map

__version__ = "0.1.0"
__all__ = ["__version__", "render_map"]
