"""Procedurally generates fantasy world maps as parametric SVG.

This package provides the core map generation engine, with optional PNG export
and an interactive web GUI. Maps are defined by a MapConfig object containing
geography, palette, routes, and settlements.

Example usage:
    from fantasy_map_generator import render_map

    svg = render_map(seed=42)
    with open("map.svg", "w") as f:
        f.write(svg)
"""

__version__ = "0.1.0"
