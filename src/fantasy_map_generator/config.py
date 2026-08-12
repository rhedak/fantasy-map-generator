"""Map configuration models.

A MapConfig encapsulates all the data needed to render a fantasy world map:
geography (locations, routes, water features), palette (colors), and rendering
parameters (canvas size, density settings).

This separation of data from rendering logic allows different worlds to be
rendered without code changes—just swap the MapConfig.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class Palette:
    """Color scheme for a map."""

    background: str = "#202634"
    mountain: str = "#343e54"
    mountain_stroke: str = "#1c2333"
    water: str = "#6f9ec4"
    water_tributary: str = "#5a8fb5"
    forest: str = "#3d5c46"
    settlement: str = "#b9a888"
    settlement_roof: str = "#7a6a4f"
    text: str = "#e8e2d2"
    text_dim: str = "#b2a992"


@dataclass
class MapConfig:
    """Configuration for map generation.

    Attributes:
        name: Human-readable name of this world/region.
        canvas_width: SVG canvas width in units.
        canvas_height: SVG canvas height in units.
        locations: Named points of interest (villages, cities, etc.)
            key -> (x, y) coordinate.
        routes: Named paths connecting locations.
            key -> list of (x, y) waypoints in order.
        palette: Color scheme.
        seed: Random seed for deterministic output.
    """

    name: str = "Untitled Fantasy World"
    canvas_width: int = 1000
    canvas_height: int = 700

    # Geography
    locations: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    routes: Dict[str, List[Tuple[float, float]]] = field(default_factory=dict)

    # Rendering
    palette: Palette = field(default_factory=Palette)

    def validate(self) -> None:
        """Validate the configuration.

        Raises:
            ValueError: If any required fields are missing or invalid.
        """
        if self.canvas_width <= 0 or self.canvas_height <= 0:
            raise ValueError("canvas dimensions must be positive")
        if not self.locations:
            raise ValueError("at least one location must be defined")
