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
    """Color scheme for a map.

    All colors are hex strings. Most are required for basic terrain rendering;
    some are specialized (palace, mist) for specific feature types.
    """

    # Terrain
    background: str = "#202634"
    mountain: str = "#343e54"
    mountain_stroke: str = "#1c2333"
    water: str = "#6f9ec4"
    water_tributary: str = "#5a8fb5"
    paddy: str = "#5d7f62"
    forest: str = "#3d5c46"

    # Settlements & features
    settlement: str = "#b9a888"
    settlement_roof: str = "#7a6a4f"
    road: str = "#d9c9a3"
    road_dim: str = "#a99670"

    # Text (requires outline for readability)
    text: str = "#e8e2d2"
    text_dim: str = "#b2a992"
    text_faint: str = "#8f8777"

    # Mist wall and special features
    mist_wall: str = "#dfe6ee"
    mist_wall_stroke: str = "#c3ccd8"
    passage: str = "#aeb9cc"
    zone: str = "#333c4c"
    old_wall: str = "#8b93a6"

    # Palace (for capital structures)
    palace_roof: str = "#33456e"
    palace_roof_light: str = "#4d6395"
    palace_trim: str = "#c7ceda"

    # Gradient for mist lighting (used in radial gradient)
    gradient_stops: List[tuple[float, str]] = field(
        default_factory=lambda: [
            (0.00, "#f3f6fa"),
            (0.28, "#cdd6e0"),
            (0.55, "#96a6ba"),
            (0.80, "#5c6a80"),
            (1.00, "#3a4254"),
        ]
    )


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
