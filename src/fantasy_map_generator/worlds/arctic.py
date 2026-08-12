"""Arctic Tundra example world."""

from fantasy_map_generator.config import MapConfig, Palette

ARCTIC_PALETTE = Palette(
    background="#1a2332",
    mountain="#4a6a8f",
    mountain_stroke="#2a3f5f",
    water="#5a8fbf",
    water_tributary="#4a7faf",
    paddy="#4a6a8f",
    forest="#3a5a7f",
    settlement="#c8d4e8",
    settlement_roof="#8fa8c8",
    road="#d8e4f0",
    road_dim="#b8c8d8",
    text="#e8f4fc",
    text_dim="#a8c4dc",
    text_faint="#7a94ac",
    mist_wall="#d8e4f0",
    mist_wall_stroke="#b8c8d8",
    passage="#8fa8c8",
    zone="#2a3f5f",
    old_wall="#4a6a8f",
    palace_roof="#2a4a7f",
    palace_roof_light="#4a6a9f",
    palace_trim="#a8c4dc",
    gradient_stops=[
        (0.00, "#e8f4fc"),
        (0.28, "#d8e4f0"),
        (0.55, "#8fa8c8"),
        (0.80, "#4a6a8f"),
        (1.00, "#2a3f5f"),
    ],
)

ARCTIC_CONFIG = MapConfig(
    name="Arctic Tundra",
    canvas_width=1000,
    canvas_height=700,
    locations={
        "Ice Citadel": (350.0, 250.0),
        "Frost Harbor": (700.0, 400.0),
        "Northern Settlement": (200.0, 350.0),
        "Crystal Lake": (500.0, 550.0),
    },
    routes={
        "frozen_path": [(200.0, 350.0), (350.0, 280.0), (500.0, 350.0), (700.0, 400.0)],
        "river": [(480.0, 80.0), (450.0, 200.0), (420.0, 400.0), (450.0, 550.0)],
    },
    palette=ARCTIC_PALETTE,
)
