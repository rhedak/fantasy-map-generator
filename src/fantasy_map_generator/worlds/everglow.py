"""The Everglow kingdom -- map for the short story "The Hunt for the Everglow
Crystals" (../short_stories/stories/everglow_crystals).

Geography is deliberately spare (short story, strict naming policy). Every
fixed fact comes from that story's notes.md "Geography" section:

- One river spine, running roughly NNW to SSE: it rises at the cold northern
  frontier, the everglow cave sits at its headwaters behind the waterfall
  that feeds it, and it runs down through the hill country, past the village,
  on to the capital, which sits on it.
- The capital: south end, on the river, seat of the crown and the vault.
- The village: northwest of the capital, about a day out, on the river.
  Linnea's family, the inn.
- The old country / the cave: far north, the abandoned everglow homeland at
  the cold frontier, "the better part of a month" up the valley from the
  village.
- The picket: where the south road up from the capital meets the northern
  track down from the frontier (ch5).

Nothing here is named that the story does not name: the cave, the village,
the capital, the picket, the old country, the hill country.
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
    WaterBody,
)

# A world lived in near-darkness: cold, always winter, the light rationed.
# Palette sits in the same lifted-but-still-cold blue register as the story
# cover, with the everglow's own low green-gold as the single warm accent.
EVERGLOW_PALETTE = Palette(
    background="#0d121c",
    land="#1b2432",
    mountain="#2c3648",
    mountain_stroke="#141b28",
    water="#3f6f92",
    water_tributary="#37627f",
    water_deep="#24455c",
    paddy="#39503f",
    forest="#2b4536",
    ice="#7f8ea1",
    plain="#39433a",
    settlement="#b7a67f",
    settlement_roof="#7c6a48",
    road="#c2ad7e",
    road_dim="#8a7a55",
    text="#e9e3d2",
    text_dim="#b4ac95",
    text_faint="#877f6a",
    mist_wall="#cdd8e4",
    # The everglow: low, steady green-gold. Used for the map's accent lines.
    gold="#9cb85e",
    ink="#0a0e16",
    paper="#e8dcc8",
    gradient_stops=[
        (0.00, "#cdd8e4"),
        (0.30, "#8ea2b6"),
        (0.58, "#5a6c80"),
        (0.80, "#374254"),
        (1.00, "#212a38"),
    ],
)

EVERGLOW_CONFIG = MapConfig(
    name="The Everglow Crystals",
    layout="interior",
    style_kit="rpg_symbols",
    canvas_width=900,
    canvas_height=1060,
    title_font_size=18.0,
    landmass=[
        LandBody(
            kind="ellipse",
            center=(450.0, 545.0),
            radii=(412.0, 515.0),
            rough=0.10,
            fill="#1b2432",
        )
    ],
    biome_regions=[
        # The old country: the abandoned frontier, always winter, more so than
        # anywhere else in a kingdom that is already cold year round.
        BiomeRegion("", "ice", (450.0, 150.0), (250.0, 80.0), 0.15, clip_to_land=True),
        # The hill country the river runs down through, between frontier and
        # capital: thin cold woods, not lush.
        BiomeRegion("", "forest", (435.0, 700.0), (215.0, 150.0), 0.3, clip_to_land=True),
        # A faint green-gold wash at the cave: the un-mined everglow seams
        # still lighting the rock (story's consistency lock -- the cave is not
        # pitch black).
        BiomeRegion("", "swamp", (500.0, 150.0), (62.0, 46.0), 0.5, fill="#3f5a30", clip_to_land=True),
    ],
    region_labels=[
        RegionLabel("The Old Country", center=(455.0, 250.0), font_size=16.0),
        RegionLabel("The Hill Country", center=(178.0, 640.0), font_size=15.0, rotation=-90.0),
    ],
    mountain_ranges={
        # The northern hills along the cold frontier -- the cave is "in a hill
        # that looked back the way they had come" (ch3). A broken arc, not a
        # wall.
        "frontier_hills": MountainRange(
            kind="ridge",
            points=[(180.0, 250.0), (240.0, 220.0), (300.0, 198.0), (360.0, 185.0),
                    (420.0, 179.0), (480.0, 181.0), (540.0, 193.0), (600.0, 213.0),
                    (660.0, 238.0), (712.0, 266.0)],
            density=0.9,
            size=34.0,
        ),
        # Low hills flanking the valley the river runs down, thinning south.
        "west_hills": MountainRange(
            kind="ridge",
            points=[(285.0, 370.0), (278.0, 425.0), (274.0, 480.0), (278.0, 535.0),
                    (288.0, 590.0), (304.0, 645.0), (322.0, 695.0)],
            density=0.7,
            size=22.0,
        ),
        "east_hills": MountainRange(
            kind="ridge",
            points=[(612.0, 360.0), (620.0, 415.0), (624.0, 470.0), (622.0, 525.0),
                    (628.0, 580.0), (644.0, 635.0), (662.0, 685.0)],
            density=0.7,
            size=22.0,
        ),
    },
    forest_stands=[
        ForestStand((575.0, 320.0), (60.0, 40.0), "conifer", 0.25, 3),
        ForestStand((360.0, 600.0), (55.0, 45.0), "conifer", 0.5, 4),
        ForestStand((520.0, 720.0), (55.0, 40.0), "triangle", 0.4, 3),
    ],
    lakes=[
        # The pool the waterfall drops into at the river's head (ch3), tinted
        # with the everglow's green-gold.
        WaterBody(center=(500.0, 188.0), radii=(30.0, 18.0), fill="#6f8a48"),
    ],
    waterfalls=[(500.0, 172.0)],
    places={
        "everglow_cave": Place(500.0, 142.0, name="The Everglow Cave", tier="ruin"),
        # The picket sits close below the village on the road: the crown men
        # there were watching the village (ch4), not holding open country.
        "the_village": Place(362.0, 650.0, name="The Village", tier="village"),
        "the_picket": Place(432.0, 720.0, name="The Picket", tier="camp"),
        "the_capital": Place(560.0, 955.0, name="The Capital", tier="capital"),
    },
    routes={
        # The river spine: headwaters behind the fall, down past the village,
        # on to the capital. NNW to SSE.
        "river": Route(
            [(498.0, 190.0), (462.0, 300.0), (432.0, 420.0), (412.0, 550.0),
             (418.0, 680.0), (468.0, 810.0), (530.0, 910.0), (560.0, 985.0)],
            kind="river",
        ),
        # The northern track: a month up the valley from the village to the
        # cave, unstructured (ch3). Runs down through the village to the
        # picket, where it meets the road up from the capital (ch5). Kept
        # west of the river through the hill country so the two read apart.
        "north_track": Route(
            [(500.0, 165.0), (466.0, 290.0), (428.0, 410.0), (388.0, 530.0),
             (362.0, 650.0), (432.0, 720.0)],
            kind="trail",
        ),
        # The maintained south road: capital up to the picket, where it meets
        # the northern track (ch5).
        "south_road": Route(
            [(432.0, 720.0), (490.0, 820.0), (560.0, 955.0)],
            kind="road",
        ),
    },
    legend_entries=[
        ("capital", "The Capital"),
        ("village", "The Village"),
        ("ruin", "Abandoned workings"),
        ("camp", "Crown picket"),
        ("mountain", "Hills"),
        ("forest", "Cold woods"),
        ("river", "River"),
        ("road", "Road"),
        ("trail", "Track"),
    ],
    palette=EVERGLOW_PALETTE,
    decor=Decor(border=True, compass=True, scale=True, cartouche=True, paper_texture=False),
    detail=0.5,
    coast_roughness=0.12,
)
