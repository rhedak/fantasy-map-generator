"""Arctic Tundra — ice shelf + fjord archetype."""

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

ARCTIC_PALETTE = Palette(
    background="#1a2332",
    land="#3a4a5f",
    mountain="#4a6a8f",
    mountain_stroke="#2a3f5f",
    water="#5a8fbf",
    water_tributary="#4a7faf",
    water_deep="#152030",
    paddy="#4a6a8f",
    forest="#3a5a7f",
    ice="#d8e4f0",
    plain="#6a7a8f",
    settlement="#c8d4e8",
    settlement_roof="#8fa8c8",
    road="#d8e4f0",
    road_dim="#b8c8d8",
    text="#e8f4fc",
    text_dim="#a8c4dc",
    text_faint="#7a94ac",
    mist_wall="#d8e4f0",
    gold="#a8c4dc",
    ink="#0a1018",
    paper="#1a2332",
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
    layout="coast",
    style_kit="mist_bowl",
    canvas_width=1000,
    canvas_height=700,
    landmass=[
        # main ice shelf / mainland from north
        LandBody(
            kind="polygon",
            points=[
                (0.0, 0.0),
                (1000.0, 0.0),
                (1000.0, 280.0),
                (880.0, 320.0),
                (760.0, 300.0),
                (640.0, 380.0),
                (520.0, 340.0),
                (400.0, 420.0),
                (280.0, 360.0),
                (160.0, 400.0),
                (40.0, 340.0),
                (0.0, 300.0),
            ],
            rough=0.12,
            fill="#3a4a5f",
        ),
        # fjord peninsula
        LandBody(
            kind="ellipse",
            center=(720.0, 480.0),
            radii=(90.0, 55.0),
            rough=0.18,
            fill="#3a4a5f",
        ),
    ],
    biome_regions=[
        BiomeRegion("Ice Pack", "ice", (500.0, 160.0), (300.0, 100.0), 0.75),
        BiomeRegion("Tundra Scrub", "tundra", (400.0, 320.0), (150.0, 80.0), 0.45),
    ],
    mountain_ranges={
        "arctic_spine": MountainRange(
            kind="ridge",
            points=[
                (100.0, 120.0),
                (220.0, 90.0),
                (360.0, 110.0),
                (500.0, 80.0),
                (640.0, 100.0),
                (800.0, 70.0),
                (940.0, 110.0),
            ],
            density=1.0,
        ),
        "fjord_range": MountainRange(
            kind="ridge",
            points=[(280.0, 280.0), (360.0, 250.0), (450.0, 270.0)],
            density=0.55,
        ),
    },
    forest_stands=[
        ForestStand((380.0, 300.0), (50.0, 35.0), "conifer", 0.35, 3),
        ForestStand((700.0, 470.0), (40.0, 25.0), "conifer", 0.3, 2),
    ],
    places={
        "Ice Citadel": Place(350.0, 250.0, tier="castle"),
        "Frost Harbor": Place(700.0, 400.0, tier="capital"),
        "Northern Settlement": Place(200.0, 350.0, tier="village"),
        "Crystal Lake": Place(500.0, 320.0, tier="hamlet"),
    },
    routes={
        "frozen_path": Route(
            [(200.0, 350.0), (350.0, 280.0), (500.0, 320.0), (700.0, 400.0)],
            kind="road",
        ),
        "ice_river": Route(
            [(480.0, 80.0), (470.0, 160.0), (450.0, 240.0), (500.0, 320.0)],
            kind="river",
        ),
    },
    palette=ARCTIC_PALETTE,
    decor=Decor(border=False, compass=True, scale=False, cartouche=False),
    detail=0.5,
    coast_roughness=0.18,
)
