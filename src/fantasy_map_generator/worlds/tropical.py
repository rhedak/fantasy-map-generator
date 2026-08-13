"""Tropical Islands — archipelago archetype."""

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

TROPICAL_PALETTE = Palette(
    background="#0a1f2e",
    land="#1e5d4d",
    mountain="#1e5d4d",
    mountain_stroke="#0d3b33",
    water="#2db3a8",
    water_tributary="#1fa399",
    water_deep="#0a3a48",
    paddy="#2d7a6b",
    forest="#0d6b5c",
    plain="#2d8a6a",
    coast="#3a9a80",
    settlement="#d4a574",
    settlement_roof="#a0823d",
    road="#d4c5a8",
    road_dim="#b8a885",
    text="#e8f4f0",
    text_dim="#a8d4c8",
    text_faint="#7ba89d",
    mist_wall="#b8f0ed",
    gold="#e8c96a",
    ink="#041820",
    paper="#0a1f2e",
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
    layout="archipelago",
    style_kit="layered_island",
    canvas_width=1000,
    canvas_height=700,
    landmass=[
        LandBody(kind="ellipse", center=(420.0, 340.0), radii=(170.0, 120.0), rough=0.16),
        LandBody(kind="ellipse", center=(700.0, 400.0), radii=(100.0, 75.0), rough=0.2),
        LandBody(kind="ellipse", center=(220.0, 520.0), radii=(75.0, 50.0), rough=0.22),
        LandBody(kind="ellipse", center=(780.0, 220.0), radii=(45.0, 32.0), rough=0.25),
    ],
    biome_regions=[
        BiomeRegion("Jungle", "forest", (420.0, 340.0), (120.0, 85.0), 0.8),
        BiomeRegion("Lagoon Shore", "coast", (700.0, 400.0), (70.0, 50.0), 0.5),
    ],
    mountain_ranges={
        "central_peaks": MountainRange(
            kind="stacked",
            center=(420.0, 330.0),
            radii=(110.0, 80.0),
            levels=3,
            density=0.85,
        ),
        "island_peaks": MountainRange(
            kind="stacked",
            center=(700.0, 390.0),
            radii=(50.0, 40.0),
            levels=2,
            density=0.5,
        ),
    },
    forest_stands=[
        ForestStand((400.0, 360.0), (100.0, 70.0), "stamp", 0.95, 10),
        ForestStand((690.0, 410.0), (55.0, 40.0), "stamp", 0.7, 5),
        ForestStand((220.0, 520.0), (40.0, 28.0), "canopy", 0.6, 3),
    ],
    places={
        "Jungle Temple": Place(350.0, 300.0, tier="ruin"),
        "Coastal Town": Place(650.0, 350.0, tier="town"),
        "Island Village": Place(200.0, 550.0, tier="village"),
        "Lagoon Harbor": Place(750.0, 420.0, tier="capital"),
    },
    routes={
        "reef_path": Route(
            [(200.0, 550.0), (400.0, 450.0), (650.0, 350.0), (750.0, 420.0)],
            kind="ferry",
        ),
        "spring_river": Route(
            [(420.0, 280.0), (400.0, 340.0), (380.0, 400.0), (360.0, 440.0)],
            kind="river",
        ),
    },
    palette=TROPICAL_PALETTE,
    decor=Decor(border=False, compass=True, scale=True, cartouche=False),
    detail=0.65,
    coast_roughness=0.2,
)
