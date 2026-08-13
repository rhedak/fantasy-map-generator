"""Desert Kingdoms — arid corridor archetype."""

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

DESERT_PALETTE = Palette(
    background="#2a1810",
    land="#6b4423",
    mountain="#6b4423",
    mountain_stroke="#4a2817",
    water="#d4a574",
    water_tributary="#c9945f",
    water_deep="#3a2210",
    paddy="#8b6f47",
    forest="#5d4e2e",
    desert="#c4a574",
    plain="#a08050",
    settlement="#d4a574",
    settlement_roof="#9d7e54",
    road="#e8c9a0",
    road_dim="#c9a878",
    text="#f5e6d3",
    text_dim="#d4a574",
    text_faint="#b8956d",
    mist_wall="#f5e6d3",
    gold="#daa520",
    ink="#1a0c06",
    paper="#3a2818",
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
    layout="interior",
    style_kit="ink_parchment",
    canvas_width=1000,
    canvas_height=700,
    landmass=[
        LandBody(
            kind="ellipse",
            center=(500.0, 380.0),
            radii=(460.0, 300.0),
            rough=0.1,
            fill="#5a3a1a",
        )
    ],
    biome_regions=[
        BiomeRegion("Great Erg", "desert", (520.0, 360.0), (280.0, 180.0), 0.85),
        BiomeRegion("Salt Flats", "plain", (280.0, 480.0), (90.0, 50.0), 0.4),
        BiomeRegion("Northern Dunes", "desert", (650.0, 220.0), (120.0, 70.0), 0.6),
    ],
    mountain_ranges=[
        MountainRange(
            kind="ridge",
            points=[
                (80.0, 160.0),
                (200.0, 120.0),
                (340.0, 100.0),
                (500.0, 130.0),
                (680.0, 110.0),
                (860.0, 150.0),
            ],
            density=0.85,
        ),
        MountainRange(
            kind="ridge",
            points=[(700.0, 480.0), (780.0, 520.0), (880.0, 500.0), (940.0, 540.0)],
            density=0.5,
        ),
    ],
    forest_stands=[
        # oasis palms (sparse canopy)
        ForestStand((200.0, 300.0), (35.0, 25.0), "canopy", 0.9, 3),
        ForestStand((500.0, 500.0), (28.0, 20.0), "canopy", 0.7, 2),
    ],
    places={
        "Oasis City": Place(200.0, 300.0, tier="capital"),
        "Lost Temple": Place(700.0, 250.0, tier="ruin"),
        "Trading Post": Place(500.0, 500.0, tier="town"),
        "Sand Fortress": Place(300.0, 550.0, tier="castle"),
    },
    routes={
        "trade_road": Route(
            [(200.0, 300.0), (350.0, 350.0), (500.0, 400.0), (700.0, 350.0), (700.0, 250.0)],
            kind="road",
        ),
        "wadi": Route(
            [(480.0, 100.0), (450.0, 250.0), (400.0, 400.0), (350.0, 500.0)],
            kind="river",
        ),
        "caravan_trail": Route(
            [(300.0, 550.0), (400.0, 520.0), (500.0, 500.0)],
            kind="trail",
        ),
    },
    palette=DESERT_PALETTE,
    decor=Decor(border=True, compass=True, scale=True, cartouche=False, paper_texture=True),
    detail=0.55,
    coast_roughness=0.12,
)
