"""Tropical Islands example world."""

from fantasy_map_generator.config import MapConfig, Palette

TROPICAL_PALETTE = Palette(
    background="#0a1f2e",
    mountain="#1e5d4d",
    mountain_stroke="#0d3b33",
    water="#2db3a8",
    water_tributary="#1fa399",
    paddy="#2d7a6b",
    forest="#0d6b5c",
    settlement="#d4a574",
    settlement_roof="#a0823d",
    road="#d4c5a8",
    road_dim="#b8a885",
    text="#e8f4f0",
    text_dim="#a8d4c8",
    text_faint="#7ba89d",
    mist_wall="#b8f0ed",
    mist_wall_stroke="#80d4cc",
    passage="#5fa89f",
    zone="#0d3b33",
    old_wall="#1e5d4d",
    palace_roof="#0d6b5c",
    palace_roof_light="#2d8a7a",
    palace_trim="#80d4cc",
    gradient_stops=[
        (0.00, "#b8f0ed"),
        (0.28, "#80d4cc"),
        (0.55, "#2db3a8"),
        (0.80, "#1e5d4d"),
        (1.00, "#0d3b33"),
    ],
)

TROPICAL_CONFIG = MapConfig(
    name="Tropical Islands",
    canvas_width=1000,
    canvas_height=700,
    locations={
        "Jungle Temple": (350.0, 300.0),
        "Coastal Town": (650.0, 350.0),
        "Island Village": (200.0, 550.0),
        "Lagoon Harbor": (750.0, 500.0),
    },
    routes={
        "reef_path": [(200.0, 550.0), (400.0, 450.0), (650.0, 350.0), (750.0, 300.0)],
        "river": [(500.0, 80.0), (480.0, 200.0), (450.0, 350.0), (400.0, 500.0)],
    },
    palette=TROPICAL_PALETTE,
)
