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
    WaterBody,
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
        # Distinct fill from Harvest Plain (same "plain" biome, but the two
        # would tint identically without an override) -- a warmer, redder
        # orchard-row brown. Label center pulled south of the region's own
        # center (which stays at Orchard Hold's texture/tint anchor) so its
        # text doesn't stack on the "Orchard Hold" place label.
        BiomeRegion("Orchards", "plain", (450.0, 545.0), (80.0, 45.0), 0.5, fill="#7a4a28"),
    ],
    mountain_ranges={},
    forest_stands=[
        ForestStand((560.0, 300.0), (140.0, 100.0), "canopy", 0.85, 12),
        ForestStand((450.0, 520.0), (70.0, 40.0), "stamp", 0.6, 5),
        ForestStand((200.0, 400.0), (50.0, 40.0), "conifer", 0.45, 4),
    ],
    lakes=[
        WaterBody(center=(240.0, 220.0), radii=(36.0, 24.0)),
    ],
    places={
        "Harvest City": Place(300.0, 280.0, tier="capital"),
        "Wood Village": Place(650.0, 320.0, tier="village"),
        "Orchard Hold": Place(450.0, 500.0, tier="town"),
        "Stone Keep": Place(200.0, 450.0, tier="castle"),
        "Millbrook": Place(680.0, 530.0, tier="hamlet"),
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
        # A second, shorter tributary feeding the main river near Orchard
        # Hold, breaking up the single straight line down the map.
        "tributary": Route(
            [(280.0, 260.0), (350.0, 330.0), (430.0, 400.0)],
            kind="river",
        ),
        "wood_trail": Route(
            [(650.0, 320.0), (560.0, 380.0), (450.0, 500.0)],
            kind="trail",
        ),
        "mill_trail": Route(
            [(450.0, 500.0), (580.0, 520.0), (680.0, 530.0)],
            kind="trail",
        ),
    },
    legend_entries=[
        ("capital", "Capital"),
        ("town", "Town"),
        ("village", "Village"),
        ("castle", "Castle"),
        ("forest", "Forest"),
        ("road", "Road"),
        ("trail", "Trail"),
        ("river", "River"),
    ],
    palette=AUTUMN_PALETTE,
    decor=Decor(border=True, compass=True, scale=True, cartouche=True, paper_texture=True),
    detail=0.6,
    coast_roughness=0.1,
)
