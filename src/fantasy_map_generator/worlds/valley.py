"""Valley of Mists example world configuration.

Extracted from the Valley of Mists webnovel geography_reference,
showing the bowl-shaped valley with its settlements, river system, and terrain.
"""

from fantasy_map_generator.config import MapConfig, Palette

# Valley-specific palette: darker, mist-heavy, with cooler tones
VALLEY_PALETTE = Palette(
    background="#202634",
    mountain="#343e54",
    mountain_stroke="#1c2333",
    water="#6f9ec4",
    water_tributary="#5a8fb5",
    paddy="#5d7f62",
    forest="#3d5c46",
    settlement="#b9a888",
    settlement_roof="#7a6a4f",
    road="#d9c9a3",
    road_dim="#a99670",
    text="#e8e2d2",
    text_dim="#b2a992",
    text_faint="#8f8777",
    mist_wall="#dfe6ee",
    mist_wall_stroke="#c3ccd8",
    passage="#aeb9cc",
    zone="#333c4c",
    old_wall="#8b93a6",
    palace_roof="#33456e",
    palace_roof_light="#4d6395",
    palace_trim="#c7ceda",
)

# Key settlements and points of interest from the story
VALLEY_LOCATIONS = {
    "Kiriguchi": (180.0, 600.0),  # Mountain gate at the mouth
    "Kiri no Sato": (267.5, 473.7),  # Kyoko's village near the mist wall
    "The Inn": (520.0, 460.0),  # Only roofed building between village and capital
    "Kasumikyo": (640.0, 414.0),  # The capital city
    "The Basin": (500.0, 350.0),  # True center, summoning basin
}

# River path from highlands through the valley to the mouth
VALLEY_RIVER = [
    (480.0, 88.0),
    (460.0, 190.0),
    (410.0, 320.0),
    (430.0, 400.0),
    (350.0, 440.0),
    (300.0, 460.0),
    (280.0, 477.0),
    (265.0, 508.0),
    (200.0, 555.0),
    (162.0, 588.0),
]

# Main road from entrance to capital to basin
CAPITAL_ROAD = [
    (180.0, 600.0),  # Kiriguchi
    (230.0, 565.0),
    (262.0, 542.0),
    (267.5, 473.7),  # Kiri no Sato
    (370.0, 495.0),
    (520.0, 460.0),  # The Inn
    (595.0, 438.0),
    (640.0, 414.0),  # Kasumikyo
    (655.0, 392.0),
    (660.0, 378.0),
    (648.0, 355.0),
    (666.0, 340.0),
    (676.0, 332.0),
    (655.0, 312.0),  # Throne room
]

VALLEY_CONFIG = MapConfig(
    name="Valley of Mists",
    canvas_width=1000,
    canvas_height=700,
    locations=VALLEY_LOCATIONS,
    routes={
        "capital_road": CAPITAL_ROAD,
        "river": VALLEY_RIVER,
    },
    palette=VALLEY_PALETTE,
)

# Desert world: warm golds, sandy tones, sparse water
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

# Tropical world: vibrant greens, blues, warm tones
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

# Arctic world: cool blues, whites, silver
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

# Autumn world: warm oranges, deep reds, browns
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
