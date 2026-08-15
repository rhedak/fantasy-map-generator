"""The continent around the Valley of Mists — first draft, not yet canon.

Four powers, west to east: Wodensreich, Okiri (home of the Valley of Mists
itself), the Tumen plains, and the Sultanate of Devran. See the sister
valley_of_mist repo's docs/geography_reference.md ("The wider continent")
and docs/design.md ("World") for the settled facts this draws from.

Placeholder pending author sign-off: the map's own title, and Devran's
capital name (three candidates considered -- Sarayonu, Kadirabad,
Devrankale -- "Sarayonu" used here as the working default).
"""

from fantasy_map_generator.config import (
    BiomeRegion,
    Decor,
    ForestStand,
    LandBody,
    MapConfig,
    MountainRange,
    Palette,
    Place,
    RegionLabel,
    Route,
    make_meander_border,
)

# Shared political borders (west to east): each is a single meandering line,
# reused by both flanking BiomeRegions so their territories meet exactly with
# no gap or overlap. Nominal x lands on that border's mountain-pass gap;
# mountain ranges get repositioned to track these once the border shape is
# picked (see continent_map_scratch notes -- borders first, mountains after).
_BORDER_WODENSREICH_OKIRI = make_meander_border(615.0, 240.0, 680.0, seed=101)
_BORDER_OKIRI_TUMEN = make_meander_border(905.0, 240.0, 680.0, seed=102)
_BORDER_TUMEN_DEVRAN = make_meander_border(1160.0, 240.0, 680.0, seed=103)

CONTINENT_PALETTE = Palette(
    background="#1c2a3a",
    land="#cbb98c",
    mountain="#8a7960",
    mountain_stroke="#5c4f3d",
    water="#5f8fb4",
    water_tributary="#4f7ea3",
    water_deep="#2c4a63",
    paddy="#7a9463",
    forest="#4b6b45",
    desert="#d1b57a",
    swamp="#5c6b45",
    plain="#a8a86a",
    settlement="#c9a86a",
    settlement_roof="#8a5f3d",
    road="#e8d9ab",
    road_dim="#bfa876",
    # Labels are white fill / black outline (the outline pass is automatic in
    # _text()) rather than dark ink-on-parchment, per author feedback on draft 1.
    text="#ffffff",
    text_dim="#ffffff",
    text_faint="#7a6748",
    gold="#b8860b",
    ink="#2a1f14",
    paper="#efe3c4",
    gradient_stops=[
        (0.00, "#f3ecd6"),
        (0.30, "#e3d3a3"),
        (0.60, "#c9b177"),
        (1.00, "#8a7451"),
    ],
)

# Per-kingdom visual identity (BiomeRegion.fill overrides), each a distinct hue.
# Okiri's color is not invented here -- it's pulled straight from the Valley's
# own established, already-approved palette (fantasy_map_generator/valley/mapgen.py's
# PINE, the valley floor's forest color) so the two maps read as the same world.
WODENSREICH_COLOR = "#556270"  # industrial steel-blue-grey
OKIRI_COLOR = "#3d5c46"  # == valley/mapgen.py PINE
TUMEN_COLOR = "#b3974f"  # steppe tan-gold
DEVRAN_COLOR = "#c17a3d"  # Ottoman-coded warm terracotta

CONTINENT_CONFIG = MapConfig(
    name="The Continent",  # working title, not yet a settled in-world name
    layout="island",
    style_kit="ink_parchment",
    canvas_width=1600,
    canvas_height=900,
    landmass=[
        LandBody(
            kind="polygon",
            points=[
                (200.0, 300.0), (350.0, 260.0), (550.0, 290.0), (750.0, 270.0),
                (950.0, 310.0), (1150.0, 280.0), (1350.0, 320.0), (1420.0, 380.0),
                (1440.0, 500.0), (1400.0, 600.0), (1200.0, 650.0), (1000.0, 620.0),
                (800.0, 660.0), (600.0, 630.0), (400.0, 650.0), (250.0, 600.0),
                (180.0, 500.0), (150.0, 400.0),
            ],
            rough=0.12,
            fill=None,
        ),
        # Unexplored islands, decorative and unlabeled (geography_reference.md's
        # own "not yet detailed" note on this).
        LandBody(kind="ellipse", center=(1500.0, 200.0), radii=(40.0, 25.0), rough=0.3),
        LandBody(kind="ellipse", center=(250.0, 750.0), radii=(35.0, 20.0), rough=0.3),
        LandBody(kind="ellipse", center=(1500.0, 750.0), radii=(30.0, 18.0), rough=0.3),
    ],
    biome_regions=[
        # name="" -- no small subtitle; it would just repeat the big RegionLabel
        # below it ("Wodensreich" over "Wodensreich"), unlike the other three
        # kingdoms where the subtitle is a distinct place-name, not a repeat.
        # x_range bands follow the actual coastline (clipped from the landmass
        # polygon at render time) rather than approximating each kingdom with
        # a freestanding ellipse; the cuts land on the mountain-range gaps so
        # the color seam and the mountains coincide.
        BiomeRegion(
            "", "plain", (380.0, 440.0), (210.0, 190.0), 0.5,
            fill=WODENSREICH_COLOR, right_border=_BORDER_WODENSREICH_OKIRI,
        ),
        BiomeRegion(
            "The Valley of Mists", "forest", (770.0, 375.0), (110.0, 210.0), 0.6,
            fill=OKIRI_COLOR, left_border=_BORDER_WODENSREICH_OKIRI, right_border=_BORDER_OKIRI_TUMEN,
        ),
        BiomeRegion(
            "The Tumen Plains", "plain", (1040.0, 345.0), (110.0, 210.0), 0.4,
            fill=TUMEN_COLOR, left_border=_BORDER_OKIRI_TUMEN, right_border=_BORDER_TUMEN_DEVRAN,
        ),
        BiomeRegion(
            "Scorching Wellheads", "desert", (1270.0, 365.0), (130.0, 210.0), 0.75,
            fill=DEVRAN_COLOR, left_border=_BORDER_TUMEN_DEVRAN,
        ),
    ],
    region_labels=[
        RegionLabel("Wodensreich", center=(380.0, 300.0), font_size=36.0),
        RegionLabel("Okiri", center=(770.0, 300.0), font_size=32.0),
        RegionLabel("The Tumen", center=(1040.0, 300.0), font_size=30.0),
        RegionLabel("Devran", center=(1270.0, 300.0), font_size=36.0),
    ],
    mountain_ranges={
        # Wodensreich/Okiri border: one well-defined pass (Ch23:86, Ch34:209/227).
        "western_range": MountainRange(
            kind="ridge",
            points=[(620.0, 290.0), (630.0, 380.0), (600.0, 470.0), (640.0, 560.0)],
            density=0.9,
        ),
        # Okiri/Tumen border: unstructured, several small rough passes rather
        # than one clean crossing (characters.md's "Warden of the Eastern Veil").
        "eastern_range": MountainRange(
            kind="ridge",
            points=[(900.0, 300.0), (920.0, 400.0), (890.0, 500.0), (930.0, 580.0)],
            density=0.35,
        ),
    },
    forest_stands=[
        ForestStand((760.0, 400.0), (60.0, 45.0), "conifer", 0.7, 4),
        ForestStand((850.0, 470.0), (50.0, 35.0), "conifer", 0.6, 3),
    ],
    places={
        "Eisenhort": Place(320.0, 420.0, tier="capital"),
        "Kasumikyo": Place(760.0, 440.0, tier="ruin"),
        "Kiriguchi": Place(700.0, 480.0, tier="village"),
        "Boru-Khal": Place(1000.0, 380.0, tier="village"),
        "Altan-Oyun": Place(1100.0, 480.0, tier="hamlet"),
        "Sarayonu": Place(1270.0, 420.0, tier="capital"),
        "Kizil Keep": Place(1360.0, 380.0, tier="castle"),
        "Shirin's Landing": Place(1220.0, 560.0, tier="city"),
    },
    routes={
        # The Wodensreich's own "eastern trade roads" (Ch26:17-18): maintained
        # road through Wodensreich/Okiri, unstructured trail on past it.
        "western_road": Route(
            [(320.0, 420.0), (500.0, 440.0), (650.0, 460.0), (760.0, 440.0)],
            kind="road",
        ),
        "eastern_trail": Route(
            [(760.0, 440.0), (900.0, 420.0), (1050.0, 400.0), (1180.0, 410.0), (1270.0, 420.0)],
            kind="trail",
        ),
    },
    ships=[(500.0, 150.0), (900.0, 180.0), (700.0, 780.0), (1100.0, 750.0)],
    legend_entries=[
        ("capital", "Capital"),
        ("city", "City / Town"),
        ("village", "Village"),
        ("mountain", "Mountains"),
        ("forest", "Forest"),
        ("desert", "Desert"),
        ("road", "Road"),
        ("trail", "Trail / Trade Route"),
    ],
    palette=CONTINENT_PALETTE,
    decor=Decor(border=True, compass=True, scale=True, cartouche=True, paper_texture=True),
    detail=0.55,
    coast_roughness=0.12,
)
