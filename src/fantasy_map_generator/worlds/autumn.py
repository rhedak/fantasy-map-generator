"""Autumn Kingdoms example world."""

from fantasy_map_generator.config import MapConfig, Palette

AUTUMN_PALETTE = Palette(
    background="#1f1410",
    mountain="#8b4513",
    mountain_stroke="#5c2c0a",
    water="#9b7f5c",
    water_tributary="#8a6d4a",
    paddy="#6b5c3d",
    forest="#6b4423",
    settlement="#d4a574",
    settlement_roof="#a0682a",
    road="#e8b854",
    road_dim="#c89838",
    text="#f5e6d3",
    text_dim="#d4a574",
    text_faint="#b8956d",
    mist_wall="#f5e6d3",
    mist_wall_stroke="#d4a574",
    passage="#c89a4e",
    zone="#5c3a1f",
    old_wall="#8b4513",
    palace_roof="#a0522d",
    palace_roof_light="#b8734b",
    palace_trim="#d4a574",
    gradient_stops=[
        (0.00, "#f5e6d3"),
        (0.28, "#e8b854"),
        (0.55, "#d4a574"),
        (0.80, "#8b4513"),
        (1.00, "#5c2c0a"),
    ],
)

AUTUMN_CONFIG = MapConfig(
    name="Autumn Kingdoms",
    canvas_width=1000,
    canvas_height=700,
    locations={
        "Harvest City": (300.0, 280.0),
        "Wood Village": (650.0, 320.0),
        "Orchard Hold": (450.0, 500.0),
        "Stone Keep": (200.0, 450.0),
    },
    routes={
        "harvest_road": [(200.0, 450.0), (300.0, 350.0), (450.0, 400.0), (650.0, 320.0)],
        "river": [(480.0, 80.0), (460.0, 250.0), (430.0, 400.0), (380.0, 550.0)],
    },
    palette=AUTUMN_PALETTE,
)
