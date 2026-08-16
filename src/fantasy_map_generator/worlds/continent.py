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
    WaterBody,
    make_meander_border,
)

# Shared political borders (west to east): each is a single meandering line,
# reused by both flanking BiomeRegions so their territories meet exactly with
# no gap or overlap. Nominal x lands on that border's mountain-pass gap;
# mountain ranges get repositioned to track these once the border shape is
# picked (see continent_map_scratch notes -- borders first, mountains after).
_BORDER_WODENSREICH_OKIRI = make_meander_border(615.0, 240.0, 680.0, seed=101)
_BORDER_OKIRI_TUMEN = make_meander_border(960.0, 240.0, 680.0, seed=102)
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
    text_faint="#ffffff",
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
    name="Land of the Sleeping Gods",  # design.md's "Sleeping Gods" section
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
        # Climate dressing (geography_reference.md's "Climate" section):
        # overlay regions layered on top of the territory fill above, clipped
        # to the actual coastline (clip_to_land) so they read as part of the
        # land rather than a freestanding ellipse spilling over the ocean.
        # Wodensreich's own coldest corner gets a tundra-fringe tint...
        BiomeRegion("", "ice", (245.0, 370.0), (95.0, 75.0), 0.5, clip_to_land=True),
        # ...and, for contrast within the same kingdom, a scorched-ground
        # tint around the volcanoes in its south-west (dark ash/rock, not a
        # climate-gradient effect -- just local geology, see the volcanoes
        # below).
        BiomeRegion("", "plain", (265.0, 590.0), (85.0, 55.0), 0.6, fill="#4a3428", clip_to_land=True),
        # ...and Devran's own hottest corner gets extra-dense dune texture in
        # a deeper, hotter shade than the rest of the Scorching Wellheads.
        BiomeRegion("", "desert", (1345.0, 565.0), (85.0, 55.0), 1.0, fill="#a85f28", clip_to_land=True),
    ],
    region_labels=[
        RegionLabel("Wodensreich", center=(380.0, 300.0), font_size=36.0),
        RegionLabel("Okiri", center=(770.0, 300.0), font_size=32.0),
        RegionLabel("The Tumen", center=(1040.0, 300.0), font_size=30.0),
        RegionLabel("Devran", center=(1270.0, 300.0), font_size=36.0),
    ],
    mountain_ranges={
        # Okiri's defining feature: the Valley of Mists is a ring of mountains
        # with its capital inside, not a wall on either political border (see
        # style-anchors/map.png, the Valley's own local map). Radii and mouth
        # degrees (92-178) are a direct port of that map's own BOWL_RX/RY and
        # MOUTH_START/END (390x265 at valley-local scale, uniformly scaled by
        # ~0.167 -- the same factor used for every other ported landmark
        # below -- to fit this ring's real elliptical shape at continent
        # scale). The mouth faces south-southwest, toward Kiriguchi and the
        # rest of Okiri's *western* settlements (outside the ring, still
        # Okiri, not Wodensreich).
        "valley_ring": MountainRange(
            kind="ring",
            center=(780.0, 460.0),
            radii=(65.0, 44.0),
            mouth_start_deg=92.0,
            mouth_end_deg=178.0,
            num_peaks=40,
            density=1.0,
        ),
        # The true center: a second, smaller mountain ring around the Basin
        # itself (valley/mapgen.py's BASIN_RING_*, "the true center should
        # read as sealed off" -- same nested-ring structure as the local map,
        # just both rings scaled down together). size=12 shrinks the peak
        # glyphs themselves (not just the ring radius) so they read as a
        # compact inner ring rather than swamping it -- see the size_scale
        # math in render.py's _mountains_ring. Gap continues to face the
        # same 270-335 degree arc as the local map, toward Kasumikyo.
        # radii is the ring's actual footprint; size independently controls
        # how tall/wide the individual peak glyphs are (see MountainRange.size).
        "basin_ring": MountainRange(
            kind="ring",
            center=(780.0, 460.0),
            radii=(14.0, 11.0),
            mouth_start_deg=270.0,
            mouth_end_deg=335.0,
            num_peaks=16,
            size=6.0,
            density=1.0,
        ),
        # East of the ring: broken, low hills with several small rough passes
        # rather than one clean crossing (characters.md's "Warden of the
        # Eastern Veil") -- these lead to Okiri's own eastern villages, still
        # well short of the Okiri/Tumen political border further east.
        "eastern_hills": MountainRange(
            kind="ridge",
            points=[(865.0, 390.0), (888.0, 425.0), (858.0, 460.0), (882.0, 495.0), (855.0, 530.0)],
            density=0.3,
        ),
        # Climate dressing (geography_reference.md's "Climate" section):
        # Wodensreich's own north-west corner is the map's single coldest
        # point -- its highest peaks, snow-capped rather than bare.
        "wodensreich_nw_peaks": MountainRange(
            kind="ridge",
            points=[(210.0, 335.0), (235.0, 365.0), (205.0, 395.0), (240.0, 415.0)],
            density=0.7,
        ),
    },
    forest_stands=[
        ForestStand((738.0, 428.0), (26.0, 18.0), "conifer", 0.6, 3),
        ForestStand((758.0, 495.0), (26.0, 16.0), "conifer", 0.55, 3),
    ],
    lakes=[
        # Both a direct port of the local map's LAKE_KASUMIKYO / LAKE_KIRI_NO_SATO,
        # scaled by the same ~0.167 factor as the mountain ring and slightly
        # exaggerated in size so they stay visible at continent scale.
        WaterBody(center=(824.0, 443.0), radii=(12.0, 9.0)),  # lake near Kasumikyo
        WaterBody(center=(747.0, 486.0), radii=(6.0, 4.5)),  # lake near Kiri no Sato
        # Climate dressing: a frozen lake in Wodensreich's own coldest corner
        # (pale ice-blue fill instead of the ordinary water color).
        WaterBody(center=(270.0, 410.0), radii=(13.0, 9.0), fill="#d8eef5"),
    ],
    places={
        "Eisenhort": Place(320.0, 420.0, tier="capital"),
        # Settlement density, later session ("lived in" pass): Wodensreich
        # and Devran are industrial, city-shaping cultures and should read
        # denser than the Tumen's deliberate sparseness (design.md's
        # "Sleeping Gods"/doctrine notes). A coal-mining town near the
        # north-west peaks, and a river town further south along the same
        # river.
        "Grubenfeld": Place(355.0, 345.0, tier="town"),
        "Kohlbrücke": Place(430.0, 545.0, tier="village"),
        # A disused Woden shrine near the capital -- "ruin" tier's broken-
        # walls icon already reads as exactly the "forgot the charge, went
        # industrial" note in design.md's "Sleeping Gods" section; no new
        # icon needed, unlike Devran's and the Tumen's own sites below.
        "Wodenhalle": Place(280.0, 460.0, tier="ruin"),
        # Ported from the local map's outer-district coordinate (same 0.167
        # scale/anchor as the ring and lakes above), inside the Basin ring's
        # own gap-facing side.
        "Kasumikyo": Place(803.0, 471.0, tier="ruin"),
        # Outside the ring, right against the mouth's own implied arc (as if
        # the ring continued through the gap) -- Okiri's own western
        # settlement, not Wodensreich (style-anchors/map.png's "Kiriguchi /
        # Nebelmark", outside the Mist Wall, hugging it closely).
        "Kiriguchi": Place(698.0, 528.0, tier="village"),
        # East of the ring, through the broken eastern hills, still Okiri --
        # working name pending author sign-off, same as Devran's capital.
        "Higashimura": Place(900.0, 475.0, tier="hamlet"),
        # The Tumen: kept deliberately sparse, per their own doctrine against
        # shaping the land (design.md's "Other powers"/"Sleeping Gods").
        # Boru-Khal stays a real trade-post village (a permanent exception,
        # not a contradiction -- some tribes trade, not all are purely
        # nomadic); Altan-Oyun and the new camp use the "camp" tier (a tent
        # glyph, not a building) to read as temporary rather than a smaller
        # permanent village.
        "Boru-Khal": Place(1000.0, 380.0, tier="village"),
        "Altan-Oyun": Place(1100.0, 480.0, tier="camp"),
        "Sarangerel's Camp": Place(1065.0, 525.0, tier="camp"),
        "Sarayonu": Place(1270.0, 420.0, tier="capital"),
        "Kizil Keep": Place(1360.0, 380.0, tier="castle"),
        # Renamed from "Shirin's Landing" (later session): read too much like
        # a Game of Thrones place name. "Bandar-e-Shirin" ("Port of Shirin",
        # Persian) keeps the name but fits Devran's Ottoman-Persian coding.
        "Bandar-e-Shirin": Place(1220.0, 560.0, tier="city"),
        # A small oasis town at the Devran river's own source, out of the
        # desert (matches its Nile/Tigris-Euphrates coding).
        "Yeşilvaha": Place(1195.0, 305.0, tier="village"),
    },
    routes={
        # The Wodensreich's own "eastern trade roads" (Ch26:17-18): maintained
        # road through to Kiriguchi, then through the ring's mouth to Kasumikyo.
        "western_road": Route(
            [(320.0, 420.0), (500.0, 460.0), (630.0, 505.0), (698.0, 528.0), (745.0, 500.0), (803.0, 471.0)],
            kind="road",
        ),
        # Kasumikyo out through the eastern gap in the hills, on to the
        # Tumen plains and Devran -- unstructured trail the whole way past
        # the ring, matching the Tumen border's own "no clean crossing".
        "eastern_trail": Route(
            [(803.0, 471.0), (855.0, 470.0), (900.0, 475.0), (960.0, 440.0),
             (1000.0, 380.0), (1050.0, 400.0), (1180.0, 410.0), (1270.0, 420.0)],
            kind="trail",
        ),
        # Trade-route texture, later session ("lived in" pass): spurs
        # connecting the settlements added in the density pass, plus
        # Devran's own capital-to-coast connections that had no road at all
        # before. Wodenhalle and the Tumen's camps are deliberately left
        # unconnected -- a disused shrine draws no traffic, and a road to a
        # nomad camp would itself violate the Tumen's doctrine.
        "wodensreich_nw_spur": Route([(320.0, 420.0), (355.0, 345.0)], kind="road"),
        "wodensreich_river_spur": Route([(320.0, 420.0), (430.0, 545.0)], kind="road"),
        "devran_oasis_spur": Route([(1270.0, 420.0), (1195.0, 305.0)], kind="road"),
        "devran_coastal_road": Route(
            [(1270.0, 420.0), (1360.0, 380.0)], kind="road",
        ),
        "devran_south_road": Route(
            [(1270.0, 420.0), (1220.0, 560.0)], kind="road",
        ),
        # Rivers, one per kingdom. Okiri's two are not invented -- they're a
        # simplified port of the local map's own RIVER and TRIBUTARY point
        # arrays (valley/mapgen.py), transformed by the same ~0.167 scale and
        # Basin(500,350)->ring-center(780,460) anchor as the lakes/basin ring/
        # Kasumikyo above, not a fresh design. Fewer points than the local
        # originals (10 and 7) since the ring is tiny at continent scale, but
        # the course shape and endpoints match: the main river still runs
        # north-to-southwest and dies out near the ring's inner west edge,
        # by the lake near Kiri no Sato; the tributary still emerges near the
        # lake by Kasumikyo on the east side and runs south.
        # Both continue past the ring's mouth/gaps to the coast (checked
        # against the landmass polygon, same as the other three kingdoms'
        # rivers below) -- the local map only ever drew the portion inside
        # the valley itself, it was never meant to end there.
        "okiri_river": Route(
            [(777.0, 416.0), (765.0, 455.0), (747.0, 478.0), (741.0, 486.0), (724.0, 500.0),
             (712.0, 545.0), (695.0, 590.0), (675.0, 625.0), (665.0, 640.0)],
            kind="river",
        ),
        "okiri_tributary": Route(
            [(838.0, 441.0), (826.0, 470.0), (812.0, 490.0), (804.0, 501.0),
             (797.0, 535.0), (792.0, 575.0), (787.0, 615.0), (785.0, 656.0)],
            kind="river",
        ),
        # Wodensreich: a Rhine/Volga-like river out of the cold north-west,
        # feeding industry down past Eisenhort (matches the "coal-like solid
        # mana, industrial" coding, design.md's "Sleeping Gods"/"Donarsblut").
        # Source and mouth both checked against the landmass polygon's own
        # coastline so the river starts on land (not in the ocean band) and
        # ends exactly at the shore (not short of it, not past it).
        "wodensreich_river": Route(
            [(260.0, 310.0), (280.0, 330.0), (310.0, 390.0), (320.0, 420.0),
             (360.0, 480.0), (420.0, 540.0), (460.0, 585.0), (478.0, 641.0)],
            kind="river",
        ),
        # The Tumen: one broad, slow steppe river cutting north-south through
        # open plains (Volga/Amu Darya-coded) -- grazing land the tribes
        # pass through, not a settlement spine (geography_reference's
        # doctrine note: no shaping nature, no dense riverside towns).
        "tumen_river": Route(
            [(1025.0, 308.0), (1040.0, 350.0), (1030.0, 430.0), (1060.0, 510.0),
             (1050.0, 590.0), (1065.0, 635.0)],
            kind="river",
        ),
        # Devran: a Nile/Tigris-Euphrates-style river sustaining Sarayonu out
        # of the desert -- oil is Devran's mana, not its water.
        "devran_river": Route(
            [(1185.0, 296.0), (1220.0, 340.0), (1250.0, 390.0), (1270.0, 420.0),
             (1290.0, 470.0), (1310.0, 530.0), (1300.0, 595.0), (1300.0, 624.0)],
            kind="river",
        ),
    },
    # Wodensreich and Devran get extra ships along their own coasts
    # specifically (industrial, naval-trade powers); Okiri's and the Tumen's
    # coastlines stay comparatively quiet.
    ships=[
        (500.0, 150.0), (900.0, 180.0), (700.0, 780.0), (1100.0, 750.0),
        (280.0, 250.0), (200.0, 680.0), (1400.0, 250.0), (1350.0, 680.0),
    ],
    # Wodensreich's south-west: volcanic peaks, deliberate contrast to the
    # frozen lake and tundra in its north-west (same kingdom, two extremes).
    volcanoes=[(240.0, 580.0), (295.0, 600.0)],
    # Sleeping Gods sacred sites (design.md's "Sleeping Gods"). Wodenhalle
    # (above, "ruin" tier) covers Wodensreich; Okiri needs none, already
    # fully covered by the ring/Basin/Kasumikyo detail.
    sacred_sites=[
        # The Great Dev's temple, still standing near the capital -- heritage
        # rather than living faith, but never abandoned or ruined.
        (1300.0, 450.0, "temple"),
        # An unbuilt Tumen sacred site: a mound and standing stones, open
        # plains, no structure -- their doctrine forbids building one.
        (1085.0, 610.0, "kurgan"),
    ],
    legend_entries=[
        ("capital", "Capital"),
        ("city", "City / Town"),
        ("village", "Village"),
        ("camp", "Nomad Camp"),
        ("mountain", "Mountains"),
        ("forest", "Forest"),
        ("desert", "Desert"),
        ("road", "Road"),
        ("trail", "Trail / Trade Route"),
        ("river", "River"),
    ],
    palette=CONTINENT_PALETTE,
    decor=Decor(border=True, compass=True, scale=True, cartouche=True, paper_texture=True),
    detail=0.55,
    coast_roughness=0.12,
)
