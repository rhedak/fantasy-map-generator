"""Inkwell — hand-drawn cartography style in black ink on white parchment."""

from fantasy_map_generator.config import (
    Decor,
    LandBody,
    MapConfig,
    MountainRange,
    Palette,
    Place,
    Route,
)

INKWELL_PALETTE = Palette(
    background="#ffffff",
    land="#ffffff",
    mountain="#000000",
    mountain_stroke="#000000",
    water="#ffffff",
    water_tributary="#ffffff",
    water_deep="#ffffff",
    paddy="#ffffff",
    forest="#000000",
    desert="#ffffff",
    swamp="#ffffff",
    ice="#ffffff",
    plain="#ffffff",
    coast="#ffffff",
    settlement="#000000",
    settlement_roof="#000000",
    road="#000000",
    road_dim="#333333",
    text="#ffffff",
    text_dim="#ffffff",
    text_faint="#cccccc",
    mist_wall="#cccccc",
    mist_wall_stroke="#999999",
    passage="#999999",
    zone="#cccccc",
    old_wall="#666666",
    palace_roof="#000000",
    palace_roof_light="#333333",
    palace_trim="#000000",
    ink="#000000",
    paper="#ffffff",
    gold="#000000",
    gradient_stops=[
        (0.00, "#ffffff"),
        (0.28, "#e6e6e6"),
        (0.55, "#cccccc"),
        (0.80, "#999999"),
        (1.00, "#000000"),
    ],
)

INKWELL_CONFIG = MapConfig(
    name="Inkwell Realm",
    layout="interior",
    style_kit="ink_parchment",
    canvas_width=1400,
    canvas_height=787,
    landmass=[
        LandBody(
            kind="polygon",
            center=(700.0, 393.0),
            radii=(660.0, 360.0),
            rough=0.08,
            points=[
                (50.0, 50.0),
                (1350.0, 50.0),
                (1350.0, 737.0),
                (50.0, 737.0),
            ],
        )
    ],
    mountain_ranges={
        "northern": MountainRange(
            kind="ridge",
            points=[
                (200.0, 200.0),
                (400.0, 150.0),
                (700.0, 170.0),
                (1000.0, 140.0),
                (1200.0, 200.0),
            ],
            density=0.6,
        ),
        "southern": MountainRange(
            kind="ridge",
            points=[
                (250.0, 500.0),
                (500.0, 530.0),
                (800.0, 510.0),
                (1100.0, 550.0),
            ],
            density=0.4,
        ),
    },
    forest_stands=[],
    places={
        "Capital": Place(700.0, 390.0, name="Capital", tier="capital"),
        "Settlement A": Place(350.0, 280.0, name="Settlement A", tier="town"),
        "Settlement B": Place(1050.0, 320.0, name="Settlement B", tier="town"),
    },
    routes={
        "main_road": Route(
            [(350.0, 280.0), (500.0, 330.0), (700.0, 390.0), (900.0, 350.0), (1050.0, 320.0)],
            kind="road",
        ),
    },
    palette=INKWELL_PALETTE,
    decor=Decor(border=True, compass=True, scale=False, cartouche=False, paper_texture=False),
    detail=0.4,
    coast_roughness=0.12,
)
