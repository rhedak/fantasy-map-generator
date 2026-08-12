"""Desert Kingdoms example world."""

from fantasy_map_generator.config import MapConfig, Palette

DESERT_PALETTE = Palette(
    background="#2a1810",
    mountain="#6b4423",
    mountain_stroke="#4a2817",
    water="#d4a574",
    water_tributary="#c9945f",
    paddy="#8b6f47",
    forest="#5d4e2e",
    settlement="#d4a574",
    settlement_roof="#9d7e54",
    road="#e8c9a0",
    road_dim="#c9a878",
    text="#f5e6d3",
    text_dim="#d4a574",
    text_faint="#b8956d",
    mist_wall="#f5e6d3",
    mist_wall_stroke="#d4a574",
    passage="#c9956f",
    zone="#5d3e1f",
    old_wall="#8b6f47",
    palace_roof="#8b4513",
    palace_roof_light="#a0522d",
    palace_trim="#daa520",
    gradient_stops=[
        (0.00, "#f5e6d3"),
        (0.28, "#e8c9a0"),
        (0.55, "#c9a878"),
        (0.80, "#8b6f47"),
        (1.00, "#4a2817"),
    ],
)

DESERT_CONFIG = MapConfig(
    name="Desert Kingdoms",
    canvas_width=1000,
    canvas_height=700,
    locations={
        "Oasis City": (200.0, 300.0),
        "Lost Temple": (700.0, 250.0),
        "Trading Post": (500.0, 500.0),
        "Sand Fortress": (300.0, 550.0),
    },
    routes={
        "trade_road": [(200.0, 300.0), (350.0, 350.0), (500.0, 400.0), (700.0, 350.0)],
        "river": [(480.0, 100.0), (450.0, 250.0), (400.0, 400.0), (350.0, 500.0)],
    },
    palette=DESERT_PALETTE,
)
