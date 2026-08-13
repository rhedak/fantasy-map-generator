"""Autumn Kingdoms — inland kingdom archetype."""

from fantasy_map_generator.config import (
    BiomeRegion,
    Decor,
    ForestStand,
    LandBody,
    MapConfig,
    MountainRange,
    Palette,
    Place,
    Route,
)

AUTUMN_PALETTE = Palette(
    background="#1f1410",
    land="#3a2818",
    mountain="#8b4513",
    mountain_stroke="#5c2c0a",
    water="#9b7f5c",
    water_tributary="#8a6d4a",
    water_deep="#2a1a10",
    paddy="#6b5c3d",
    forest="#6b4423",
    plain="#8a6a3a",
    desert="#a08040",
    settlement="#d4a574",
    settlement_roof="#a0682a",
    road="#e8b854",
    road_dim="#c89838",
    text="#f5e6d3",
    text_dim="#d4a574",
    text_faint="#b8956d",
    mist_wall="#f5e6d3",
    gold="#e8b854",
    ink="#1a1008",
    paper="#e8dcc8",
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
    layout="interior",
    style_kit="rpg_symbols",
    canvas_width=1000,
    canvas_height=700,
    landmass=[
        LandBody(
            kind="ellipse",
            center=(500.0, 360.0),
            radii=(470.0, 310.0),
            rough=0.08,
            fill="#3a2818",
        )
    ],
    biome_regions=[
        BiomeRegion("Forest of Greenstones", "forest", (550.0, 300.0), (160.0, 110.0), 0.7),
        BiomeRegion("Harvest Plain", "plain", (320.0, 420.0), (130.0, 90.0), 0.65),
        BiomeRegion("Orchards", "plain", (450.0, 520.0), (80.0, 45.0), 0.5),
    ],
    mountain_ranges={
        "northern_spine": MountainRange(
            kind="ridge",
            points=[
                (60.0, 200.0),
                (140.0, 140.0),
                (240.0, 120.0),
                (360.0, 100.0),
                (480.0, 90.0),
                (600.0, 110.0),
                (720.0, 100.0),
                (860.0, 140.0),
                (960.0, 180.0),
            ],
            density=0.9,
        ),
    },
    forest_stands=[
        ForestStand((560.0, 300.0), (140.0, 100.0), "canopy", 0.85, 12),
        ForestStand((450.0, 520.0), (70.0, 40.0), "stamp", 0.6, 5),
        ForestStand((200.0, 400.0), (50.0, 40.0), "conifer", 0.45, 4),
    ],
    places={
        "Harvest City": Place(300.0, 280.0, tier="capital"),
        "Wood Village": Place(650.0, 320.0, tier="village"),
        "Orchard Hold": Place(450.0, 500.0, tier="town"),
        "Stone Keep": Place(200.0, 450.0, tier="castle"),
    },
    routes={
        "harvest_road": Route(
            [(200.0, 450.0), (300.0, 350.0), (450.0, 400.0), (650.0, 320.0)],
            kind="road",
        ),
        "river": Route(
            [(480.0, 80.0), (460.0, 250.0), (430.0, 400.0), (380.0, 550.0)],
            kind="river",
        ),
        "wood_trail": Route(
            [(650.0, 320.0), (560.0, 380.0), (450.0, 500.0)],
            kind="trail",
        ),
    },
    palette=AUTUMN_PALETTE,
    decor=Decor(border=True, compass=True, scale=True, cartouche=True, paper_texture=True),
    detail=0.6,
    coast_roughness=0.1,
)
