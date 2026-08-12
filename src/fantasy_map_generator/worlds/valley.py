"""Valley of Mists example world configuration.

Extracted from the Valley of Mists webnovel geography, showing the bowl-shaped
valley with its settlements, river system, and terrain.
"""

from fantasy_map_generator.config import MapConfig, Palette

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

VALLEY_LOCATIONS = {
    "Kiriguchi": (180.0, 600.0),
    "Kiri no Sato": (267.5, 473.7),
    "The Inn": (520.0, 460.0),
    "Kasumikyo": (640.0, 414.0),
    "The Basin": (500.0, 350.0),
}

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

CAPITAL_ROAD = [
    (180.0, 600.0),
    (230.0, 565.0),
    (262.0, 542.0),
    (267.5, 473.7),
    (370.0, 495.0),
    (520.0, 460.0),
    (595.0, 438.0),
    (640.0, 414.0),
    (655.0, 392.0),
    (660.0, 378.0),
    (648.0, 355.0),
    (666.0, 340.0),
    (676.0, 332.0),
    (655.0, 312.0),
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
