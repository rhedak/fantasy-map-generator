"""Valley of Mists geography map — parity port of sister mapgen.

Vendored from valley_of_mist_tools.mapgen for exact SVG parity (seed=7).
Do not reorder RNG calls; golden tests depend on call order.
"""

from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

# --- palette ----------------------------------------------------------------

BG = "#202634"  # outside the valley: highlands at night
MTN = "#343e54"  # the ring that walls the bowl in
MTN_STROKE = "#1c2333"
ROAD = "#d9c9a3"  # sand, the capital road
ROAD_DIM = "#a99670"  # the dotted ford over the washed-out bridge
WATER = "#6f9ec4"
PADDY = "#5d7f62"
PINE = "#3d5c46"
BUILDING = "#b9a888"
BUILDING_ROOF = "#7a6a4f"
INK = "#e8e2d2"  # label cream
INK_DIM = "#b2a992"
INK_FAINT = "#8f8777"
MIST_WALL = "#dfe6ee"
MIST_WALL_STROKE = "#c3ccd8"
PASSAGE = "#aeb9cc"
ZONE = "#333c4c"
OLD_WALL = "#8b93a6"  # cool worked stone, distinct from the sand road/buildings
PALACE_ROOF = "#33456e"  # Okiri court blue (Tenno's pre-cataclysm "layered silk in Okiri blue")
PALACE_ROOF_LIGHT = "#4d6395"  # upper tier: a lighter step of the same blue
PALACE_TRIM = "#c7ceda"  # crane-and-mist crest, "silver thread" -- ridge accents only

# The valley's own light: densest at the true center, thinning toward the rim
# (geography_reference "Map-drawing constraints", mist rendering).
GRAD_STOPS = (
    (0.00, "#f3f6fa"),
    (0.28, "#cdd6e0"),
    (0.55, "#96a6ba"),
    (0.80, "#5c6a80"),
    (1.00, "#3a4254"),
)

SERIF = "Georgia, 'Times New Roman', serif"

# --- layout: the geography census, drawn ------------------------------------

# The working model from geography_reference.md: a circular bowl sunk below a
# mountain ring, the mouth at the south-west, Kasumikyo off the true center,
# the Basin at the true center.
BOWL_CX, BOWL_CY = 500.0, 350.0  # the true center, where the Basin sits
BOWL_RX, BOWL_RY = 390.0, 265.0  # stylized valley bowl
# The ring is cut for the mouth across this arc of screen degrees (y-down,
# 0 = east, 90 = south): a south-west opening. A margin keeps the mouth wide.
MOUTH_START, MOUTH_END = 92.0, 178.0

# The single maintained entrance: Kiriguchi on the high ground at the rim,
# the mist wall ridge-to-ridge just inside the mouth (Ch1:5, Ch9:129-131).
KIRIGUCHI = (180.0, 600.0)
KIRI_NO_SATO = (267.5, 473.7)  # just inside the mist wall, mirrored ~Kiriguchi's
                               # distance from it, on the valley side (Kyoko's home
                               # village, near the valley's edge, design.md)
INN = (520.0, 460.0)  # the only roofed building between village and capital (Ch15:5), slightly SW of the terraced fields (Ch6:49).
                       # Close enough to the capital that its "broken towers were visible from the inn's upper window...
                       # close enough now that a full day's march would carry us into whatever ruins still stood beneath
                       # them" (Ch15:114) -- the same one-day order as every other leg of the route, not the longest hop on the map.

# The route spine (geography_reference "Route"): one main road from Kiriguchi
# through the checkpoints, the plank bridge, Kiri no Sato, the inn, into the
# capital and down the secret passage to the Basin.
CAPITAL_ROAD = [
    (180.0, 600.0),  # Kiriguchi
    (230.0, 565.0),  # into the mouth
    (262.0, 542.0),  # just inside the mist wall (the road crosses it at ~246, 553)
    (267.5, 473.7),  # Kiri no Sato
    (370.0, 495.0),  # bending toward the inn
    (520.0, 460.0),  # the inn (Ch15:5), close enough now for the capital's broken towers to show (Ch15:114)
    (595.0, 438.0),  # alongside the fields' far side (Ch6:49) / checkpoint 3
    (640.0, 414.0),  # Kasumikyo, outer district (kept clear of the old wall's south gate)
    (655.0, 392.0),  # through the old city wall's own south gate
    (660.0, 378.0),  # treasury district / lower city, close by the gate
    (648.0, 355.0),  # shrine terrace gate
    (666.0, 340.0),  # through the palace's own south gate
    (676.0, 332.0),  # the annex, found before the throne room (Ch24:18)
    (655.0, 312.0),  # the throne room, deepest in (Ch24:144)
]
# River, flowing from the north highlands down toward the mouth, kept well
# west of Kasumikyo's wall throughout (the wall spans roughly x583-727,
# y259-391) so it never crosses the capital, and routed around the Basin's
# own small mountain ring (BASIN_RING_* below) so it never runs near the
# true center either -- the Basin should read as isolated, not something
# a river casually passes through. Curves east well south of both to reach
# the fields, then bends west again for the two crossings of the road
# (geography_reference "Bridges and fords"): PLANK_BRIDGE, the maintained
# crossing (Ch9:122), near Kiri no Sato; and THIRD_BRIDGE, washed out, where
# the road now fords instead ("fords held in spring flood are interview
# material," geography_reference).
RIVER = [
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
# Both crossings sit close together right at Kiri no Sato, one on each road
# segment meeting at the village (village-to-bend, and mistwall-to-village),
# so the river passes just south of it between the two -- checked clear of
# every other road segment (nothing else in RIVER's path comes within 90
# units of the road anywhere else).
PLANK_BRIDGE = (280.0, 477.0)  # maintained crossing, on the village-to-bend leg
THIRD_BRIDGE = (265.0, 508.0)  # washed out but still a bridge (broken deck), on the mistwall-to-village leg

# A small lake inside the V the road actually forms at Kiri no Sato (map
# addition, author's request): the road climbs from the mist-wall crossing
# up to the village, then back down toward the bend -- that apex-at-the-
# village shape is the V, and the lake sits in the pocket it encloses, near
# the triangle's incenter for maximum clearance from all three road legs
# (~20 units at (300,504); sized well inside that). Gives the "bending
# toward the inn" waypoint an actual reason to exist. Connected to the
# river by a short outlet stream near THIRD_BRIDGE.
LAKE_KIRI_NO_SATO = (300.0, 504.0)
LAKE_RX, LAKE_RY = 17.0, 12.0

# A large lake north-east of Kasumikyo, between the palace and the mountain
# rim (map addition, author's request): the capital's own source of
# drinking water, explaining why a city could sustain a population there at
# all. This pocket is tighter than it looks -- the old ridge road cuts
# diagonally through it from the north-west and the east tributary starts
# at y=233 -- so it sits just above where the tributary begins. Wide rather
# than tall (rx well past ry, at the author's request -- an elongated lake
# isn't a contradiction), since the pocket has more room east-west than
# north-south; checked clear of the ridge road, the city wall, and the
# mountain ring's bases in both dimensions.
LAKE_KASUMIKYO = (766.0, 250.0)
LAKE_KASUMIKYO_RX, LAKE_KASUMIKYO_RY = 50.0, 40.0

# A second, smaller tributary down the valley's east side (map texture, not
# named in prose): the east side is otherwise the emptiest part of the
# valley floor, well clear of the road and Kasumikyo's wall throughout.
# Both ends sit right at the valley bowl's own boundary (BOWL_CX/CY/RX/RY),
# just inside where the mountain ring's bases start, rather than crossing
# over the peaks or trailing off in open ground: the river reads as
# emerging from the northern mountains and running back into the southern
# ones, entirely inside the valley in between.
TRIBUTARY = [
    (850.0, 233.0),
    (845.0, 260.0),
    (815.0, 335.0),
    (775.0, 410.0),
    (740.0, 460.0),
    (690.0, 530.0),
    (642.0, 597.0),
]

# True-center geometry (geography_reference "Center geometry"): the secret
# passage slopes "down and away from the capital's old foundations" (Ch31:9);
# the old ridge road is the surface "long approach" (Ch34:134). Both reach the
# Basin at the true center, and both are sealed after Ch34 ("Same wall,
# different door", Ch34:135).
SECRET_PASSAGE = [(655.0, 312.0), (565.0, 300.0), (510.0, 335.0), (500.0, 350.0)]
RIDGE_ROAD = [(800.0, 150.0), (720.0, 200.0), (630.0, 250.0), (545.0, 305.0), (505.0, 340.0), (500.0, 350.0)]
RIDGE_PATH_OVERLOOK = (545.0, 305.0)  # where the day-0 witnesses stood (Ch0:18, Ch29:108)

# A small mountain range walling the Basin off from the rest of the valley
# (map-planning session, author's request): the true center should read as
# isolated, not casually reachable, so no river runs near it and no forest
# grows inside the ring. Gapped only on the north-east face, where the
# secret passage and the old ridge road both actually converge and arrive
# (checked against both routes' final approach bearings) -- "Same wall,
# different door" (Ch34:135) reads literally here.
BASIN_RING_RX, BASIN_RING_RY = 60.0, 48.0
BASIN_RING_GAP_START, BASIN_RING_GAP_END = 270.0, 335.0

# Closed historical routes (geography_reference): the pilgrim path north of
# the mouth (Ch3:33), and the engineers' track to the old boundary stones
# (Ch9:119).
PILGRIM_PATH = [(150.0, 470.0), (150.0, 430.0), (168.0, 385.0), (200.0, 340.0), (240.0, 300.0)]
BOUNDARY_TRACK = [(350.0, 488.0), (300.0, 458.0), (255.0, 428.0)]
BOUNDARY_STONES = (250.0, 420.0)

# Terrain (geography_reference "Terrain to include"): terraced paddies and
# mist-mills past the second checkpoint (Ch6:49, Ch12:21); the pine stand an
# hour out of Kiriguchi (Ch9:116).
PADDIES = (585.0, 432.0)
MILLS = [(565.0, 442.0), (605.0, 428.0)]
PINE_STAND = (222.0, 585.0)

# Off-valley bearings, the only fixed ones in the book (geography_reference
# "Compass bearings inventory"): Eisenhort east of Kiriguchi (Ch34:189), the
# northern border pass (Ch23:86).
EISENHORT_ROAD = [(180.0, 600.0), (340.0, 645.0), (560.0, 680.0), (900.0, 700.0)]

# Unnamed hamlets (background texture, not settled canon): the census notes
# "the capital's near villages" (Ch6:40) and implies far-rim villages exist
# without naming them (Open item 3). Left unlabeled on the map for exactly
# that reason -- texture filling a gap the prose deliberately left open, not
# an invented place name. Checked clear of the road, the rim mountains, and
# every other drawn route.
HAMLETS = [
    (330.0, 200.0),
    (800.0, 340.0),
    (280.0, 250.0),
    (420.0, 570.0),
    (600.0, 180.0),
    (720.0, 480.0),
]

# Kasumikyo, directly east of the Basin at the true center (geography_reference
# "Kasumikyo"): outer district, treasury district, walled shrine terrace, dead heart.
#
# Layout rebalance (map-planning session): the shrine terrace and treasury/
# lower city are waypoints on the road, not the destination, so they're kept
# small and close to the old city wall's own south gate; the palace, holding
# the throne room the whole route is climbing toward, gets the spacious
# northern interior instead. This matches the existing road order (gate,
# treasury, terrace, palace) while fixing the earlier draft's proportions,
# where the terrace (a waypoint) was visually the biggest thing in the
# capital and the palace (the destination) was squeezed into a corner.
CAPITAL = (660.0, 345.0)
OUTER_DISTRICT = (640.0, 414.0)  # south of the old wall's gate, with clearance so its streets don't overlap the wall line
TREASURY = (660.0, 378.0)  # close by the old city wall's gate, the first thing reached inside it
TERRACE = (648.0, 355.0)  # shrunk and pulled south toward the gate, to free the interior for the palace
TERRACE_NORTH_TOWER = (648.0, 345.0)  # on the terrace's own north wall, not floating above it
DEAD_HEART = (655.0, 312.0)  # the throne room, deepest in the palace; the annex sits nearer the palace gate

# The palace: its own walled footprint predating the old city wall, with an
# eastern courtyard (Mist Guiding Ritual, Ch6:5, "before the sun had properly
# cleared the palace wall") and a south-facing outer gate onto a palace
# square (Ch23:99, Ch23:127). Holds the annex and the throne room (the pre-
# cataclysm "audience hall" Tenno kept, Ch23:99, "Tenno stayed seated on the
# throne" in that same scene) -- given the whole freed northern interior
# now, sized and colored to read as the capital's dominant structure rather
# than a corner afterthought.
PALACE_X0, PALACE_Y0, PALACE_X1, PALACE_Y1 = 614.0, 273.0, 696.0, 340.0
PALACE_GATE_CX = 666.0  # where CAPITAL_ROAD's terrace-to-annex leg crosses the south wall

# The old city wall (map-driven addition, not yet locked in geography_reference):
# a pre-cataclysm fortification around the historic core (treasury, terrace,
# dead heart) only. The outer district grew up outside it during the valley's
# long peace, which is why the road drifts into "outskirts without a clear
# boundary" (Ch17:5) well before reaching this wall -- that phrase describes
# the outer sprawl, not the old wall line. Breached at the south point, where
# the road passes from the outer district into the treasury district, and
# along the west face from age and the cataclysm.
WALL_CX, WALL_CY = 655.0, 325.0
WALL_RX, WALL_RY = 72.0, 76.0


# --- svg element helpers -----------------------------------------------------


def _polygon(points: list[tuple[float, float]], *, fill: str, stroke: str | None = None,
             sw: float = 1.0, opacity: float = 1.0, dash: str | None = None,
             rule: str | None = None) -> str:
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in points) + " Z"
    attrs = [f'fill="{fill}"']
    if stroke:
        attrs.append(f'stroke="{stroke}" stroke-width="{sw}"')
    if opacity < 1.0:
        attrs.append(f'fill-opacity="{opacity}"')
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    if rule:
        attrs.append(f'fill-rule="{rule}"')
    return f'<path d="{d}" {" ".join(attrs)}/>'


def _path(points: list[tuple[float, float]], *, stroke: str, sw: float, opacity: float = 1.0,
          dash: str | None = None, fill: str = "none", linecap: str = "round") -> str:
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in points)
    attrs = [f'fill="{fill}"', f'stroke="{stroke}" stroke-width="{sw}"', f'stroke-linecap="{linecap}"']
    if opacity < 1.0:
        attrs.append(f'stroke-opacity="{opacity}"')
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    return f'<path d="{d}" {" ".join(attrs)}/>'


def _circle(cx: float, cy: float, r: float, *, fill: str | None = None, stroke: str | None = None,
            sw: float = 1.0, opacity: float = 1.0, dash: str | None = None) -> str:
    attrs = []
    if fill:
        attrs.append(f'fill="{fill}"')
    else:
        attrs.append('fill="none"')
    if stroke:
        attrs.append(f'stroke="{stroke}" stroke-width="{sw}"')
    if opacity < 1.0:
        attrs.append(f'fill-opacity="{opacity}"')
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" {" ".join(attrs)}/>'


def _ellipse(cx: float, cy: float, rx: float, ry: float, *, stroke: str, sw: float,
             opacity: float = 1.0, dash: str | None = None) -> str:
    attrs = [f'cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none"',
             f'stroke="{stroke}" stroke-width="{sw}"']
    if opacity < 1.0:
        attrs.append(f'stroke-opacity="{opacity}"')
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    return f'<ellipse {" ".join(attrs)}/>'


def _rect(x: float, y: float, w: float, h: float, *, fill: str | None = None,
          stroke: str | None = None, sw: float = 1.0, opacity: float = 1.0) -> str:
    attrs = []
    if fill:
        attrs.append(f'fill="{fill}"')
    else:
        attrs.append('fill="none"')
    if stroke:
        attrs.append(f'stroke="{stroke}" stroke-width="{sw}"')
    if opacity < 1.0:
        attrs.append(f'fill-opacity="{opacity}"')
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" {" ".join(attrs)}/>'


# The only words that stay lowercase in map labels ("title style"): the
# article and the Japanese genitive particle (Kiri no Sato). Everything else
# is capitalized, per author direction.
_FILLER_WORDS = {"the", "no"}


def _title_case(s: str) -> str:
    return " ".join(
        w if w.lower() in _FILLER_WORDS else w[:1].upper() + w[1:] for w in s.split()
    )


def _text(x: float, y: float, s: str, *, size: float = 13.0, anchor: str = "middle",
          fill: str = INK, italic: bool = False, weight: str | None = None,
          spacing: float | None = None) -> str:
    # Two passes, outline then fill: cairosvg ignores `paint-order`, so a
    # single element with stroke+fill would paint the stroke over the glyphs.
    # Drawing the black outline as its own fill="none" pass keeps every label
    # readable over both the dark highlands and the bright mist wall.
    label = _title_case(s)
    attrs = [f'x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}"',
             f'font-family="{SERIF}"']
    if italic:
        attrs.append('font-style="italic"')
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if spacing is not None:
        attrs.append(f'letter-spacing="{spacing}"')
    base = " ".join(attrs)
    sw = max(1.4, round(size * 0.22, 1))
    outline = (f'<text {base} fill="none" stroke="#000000" stroke-width="{sw}" '
               f'stroke-linejoin="round">{xml_escape(label)}</text>')
    glyphs = f'<text {base} fill="{fill}">{xml_escape(label)}</text>'
    return outline + glyphs


def _line(x1: float, y1: float, x2: float, y2: float, *, stroke: str, sw: float,
          opacity: float = 1.0, dash: str | None = None) -> str:
    attrs = [f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"',
             f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"']
    if opacity < 1.0:
        attrs.append(f'stroke-opacity="{opacity}"')
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    return f'<line {" ".join(attrs)}/>'


def _leader_label(ax: float, ay: float, lx: float, ly: float, text: str, *,
                   size: float = 12.0, anchor: str = "start") -> list[str]:
    """A small dot at (ax, ay), a thin line out to (lx, ly), and a label
    there -- for naming a feature packed too tightly inside a cluster (like
    Kasumikyo's walls) to hold its own label without colliding with its
    neighbors."""
    gap = 4 if anchor == "start" else -4
    return [
        _circle(ax, ay, 1.6, fill=INK_DIM),
        _line(ax, ay, lx, ly, stroke=INK_DIM, sw=1.0, opacity=0.75),
        _text(lx + gap, ly + 4, text, size=size, anchor=anchor),
    ]


# --- drawn elements -----------------------------------------------------------


def _mist_gradient() -> str:
    stops = "".join(
        f'<stop offset="{p * 100:.0f}%" stop-color="{c}"/>' for p, c in GRAD_STOPS
    )
    return (
        '<radialGradient id="mist" cx="50%" cy="50%" r="50%">' + stops + "</radialGradient>"
    )


def _mountains(rng: random.Random) -> list[str]:
    """A ring of jagged peaks around the bowl, cut for the south-west mouth.

    geography_reference "Working model": the bowl is ringed by mountains/high
    ridges, and the mouth is ridge-bounded (Ch9:131). Deterministic (seeded)
    so regeneration produces the same map.
    """
    out: list[str] = []
    n = 54
    for i in range(n):
        a_deg = 360.0 * i / n
        if MOUTH_START <= a_deg <= MOUTH_END:
            continue
        a = math.radians(a_deg)
        bx = BOWL_CX + (BOWL_RX + 8 + rng.uniform(-3, 3)) * math.cos(a)
        by = BOWL_CY + (BOWL_RY + 8 + rng.uniform(-3, 3)) * math.sin(a)
        tx, ty = -math.sin(a), math.cos(a)  # tangent to the rim
        w = 16 + rng.uniform(-3, 5)
        apex_x = BOWL_CX + (BOWL_RX + 42 + rng.uniform(-6, 14)) * math.cos(a) + tx * rng.uniform(-6, 6)
        apex_y = BOWL_CY + (BOWL_RY + 42 + rng.uniform(-6, 14)) * math.sin(a) + ty * rng.uniform(-6, 6)
        p1 = (bx + tx * w, by + ty * w)
        p2 = (bx - tx * w, by - ty * w)
        out.append(_polygon([p1, (apex_x, apex_y), p2], fill=MTN, stroke=MTN_STROKE, sw=1))
    return out


def _rim_edge(rng: random.Random) -> list[str]:
    """The rim lip between mountain ring and bowl, along the open mouth.

    A wavy polyline at the bowl's edge across exactly the mouth arc, so the
    mouth reads as a bounded gap rather than a flat hole in the ring.
    """
    pts: list[tuple[float, float]] = []
    steps = 22
    for i in range(steps + 1):
        a = math.radians(MOUTH_START + (MOUTH_END - MOUTH_START) * i / steps)
        x = BOWL_CX + (BOWL_RX - 6) * math.cos(a) + rng.uniform(-4, 4)
        y = BOWL_CY + (BOWL_RY - 6) * math.sin(a) + rng.uniform(-4, 4)
        pts.append((x, y))
    return [_path(pts, stroke=MTN_STROKE, sw=4, fill="none")]


def _mist_wall_band(rng: random.Random) -> list[str]:
    """The silver-white wall hugging the rim across the mouth (Ch9:131).

    geography_reference "Mist rendering": the wall shows as a silver-white
    band sitting exactly on the valley's edge, ridge line to ridge line
    across the mouth; the road passes through it. The band follows the
    bowl's elliptical rim along the mouth arc (MOUTH_START..MOUTH_END),
    straddling the edge line.
    """
    half = 7.0
    n = 18
    top: list[tuple[float, float]] = []
    bot: list[tuple[float, float]] = []
    for i in range(n + 1):
        a = math.radians(MOUTH_START + (MOUTH_END - MOUTH_START) * i / n)
        px = BOWL_CX + BOWL_RX * math.cos(a)
        py = BOWL_CY + BOWL_RY * math.sin(a)
        tx, ty = -BOWL_RX * math.sin(a), BOWL_RY * math.cos(a)  # rim tangent
        tl = math.hypot(tx, ty)
        nx, ny = ty / tl, -tx / tl  # outward normal
        wave = math.sin(i / n * math.pi * 3) * 4 + rng.uniform(-2, 2)
        top.append((px + nx * (half + wave), py + ny * (half + wave)))
        bot.append((px - nx * (half + wave), py - ny * (half + wave)))
    band = [*top, *reversed(bot)]
    out = [_polygon(band, fill=MIST_WALL, opacity=0.92)]
    # a couple of fog streaks, faint, just inside the band
    for k in range(2):
        a = math.radians(MOUTH_START + (MOUTH_END - MOUTH_START) * (0.25 + 0.3 * k))
        pts = [
            (BOWL_CX + (BOWL_RX - 26) * math.cos(a) + rng.uniform(-8, 8),
             BOWL_CY + (BOWL_RY - 26) * math.sin(a) + rng.uniform(-8, 8))
            for _ in range(2)
        ]
        out.append(_path(pts, stroke=MIST_WALL_STROKE, sw=1.5, opacity=0.5))
    return out


def _basin() -> list[str]:
    """The true center: the summoning basin in the oldest foundation.

    geography_reference "The Basin": densest mist in the valley, the stone
    basin worn soft by centuries of hands (Ch29:42-43, Ch32:3).
    """
    return [
        _circle(BOWL_CX, BOWL_CY, 34, fill="#ffffff", opacity=0.18),
        _circle(BOWL_CX, BOWL_CY, 20, fill="#ffffff", opacity=0.35),
        _circle(BOWL_CX, BOWL_CY, 26, stroke="#e8edf3", sw=1.5),
        _circle(BOWL_CX, BOWL_CY, 32, stroke="#e8edf3", sw=0.8, opacity=0.6, dash="3,4"),
        _line(BOWL_CX - 4, BOWL_CY, BOWL_CX + 4, BOWL_CY, stroke="#e8edf3", sw=1.2),
        _line(BOWL_CX, BOWL_CY - 4, BOWL_CX, BOWL_CY + 4, stroke="#e8edf3", sw=1.2),
    ]


def _river(rng: random.Random) -> list[str]:
    """The river and its two crossings, both close together at Kiri no Sato.

    geography_reference "Bridges and fords": a maintained plank bridge and a
    washed-out third bridge. Both read as bridges here (the author asked for
    a bridge at each crossing); the third's deck is broken in the middle
    rather than a plain ford, keeping the "washed out" detail visible
    without falling back to unmarked stones.
    """
    out: list[str] = []
    pts = [(x + rng.uniform(-2, 2), y + rng.uniform(-2, 2)) for x, y in RIVER]
    out.append(_path(pts, stroke=WATER, sw=3.6, opacity=0.55))
    out.append(_path(pts, stroke=WATER, sw=1.4, opacity=0.4))
    # the maintained plank bridge (Ch9:122): a short, complete deck
    bx, by = PLANK_BRIDGE
    for k in range(4):
        out.append(_line(bx - 4 + k * 2.6, by - 5, bx - 4 + k * 2.6, by + 5,
                         stroke=BUILDING_ROOF, sw=1.6))
    # the third bridge, washed out (Ch4): a deck with a gap in the middle,
    # a bridge rather than a ford, but visibly broken
    fx, fy = THIRD_BRIDGE
    for k in range(4):
        if k == 2:
            continue  # the washed-out gap
        out.append(_line(fx - 4.5 + k * 3, fy - 5, fx - 4.5 + k * 3, fy + 5,
                         stroke=BUILDING_ROOF, sw=1.6, opacity=0.85))
    return out


def _lake(rng: random.Random) -> list[str]:
    """A small lake south of Kiri no Sato; see the LAKE_* comment. Sits in
    the pocket the road's bend curves around, with a short outlet stream
    back to the river at the midpoint between the two bridges -- PLANK_BRIDGE
    and THIRD_BRIDGE are consecutive RIVER points, so that midpoint sits
    exactly on the river's own line, a proper confluence rather than a
    stream trailing off to nowhere."""
    lx, ly = LAKE_KIRI_NO_SATO
    out = [
        _ellipse(lx, ly, LAKE_RX, LAKE_RY, stroke=WATER, sw=1.2, opacity=0.6),
        f'<ellipse cx="{lx:.1f}" cy="{ly:.1f}" rx="{LAKE_RX:.1f}" ry="{LAKE_RY:.1f}" '
        f'fill="{WATER}" fill-opacity="0.4"/>',
    ]
    mx = (PLANK_BRIDGE[0] + THIRD_BRIDGE[0]) / 2
    my = (PLANK_BRIDGE[1] + THIRD_BRIDGE[1]) / 2
    out.append(_path([(lx - LAKE_RX + 6, ly - 4), (mx, my)], stroke=WATER, sw=1.6, opacity=0.5))
    return out


def _capital_lake() -> list[str]:
    """The large lake north-east of Kasumikyo; see the LAKE_KASUMIKYO
    comment. No outlet drawn -- it's the capital's own water source, not
    part of the river system."""
    lx, ly = LAKE_KASUMIKYO
    return [
        _ellipse(lx, ly, LAKE_KASUMIKYO_RX, LAKE_KASUMIKYO_RY, stroke=WATER, sw=1.4, opacity=0.6),
        f'<ellipse cx="{lx:.1f}" cy="{ly:.1f}" rx="{LAKE_KASUMIKYO_RX:.1f}" ry="{LAKE_KASUMIKYO_RY:.1f}" '
        f'fill="{WATER}" fill-opacity="0.4"/>',
    ]


def _tributary(rng: random.Random) -> list[str]:
    """A second, smaller stream down the valley's otherwise-empty east side
    (see the TRIBUTARY comment) -- lighter and thinner than the main river,
    a minor watercourse rather than the route's own landmark."""
    pts = [(x + rng.uniform(-2, 2), y + rng.uniform(-2, 2)) for x, y in TRIBUTARY]
    return [
        _path(pts, stroke=WATER, sw=2.4, opacity=0.4),
        _path(pts, stroke=WATER, sw=1.0, opacity=0.3),
    ]


def _paddies_and_mills(rng: random.Random) -> list[str]:
    """Terraced paddies and mist-mills past the second checkpoint (Ch6:49,
    Ch12:21). No channel back to the river: the mills are mist-driven, not
    water-driven (design.md), and the river no longer runs anywhere near the
    fields now that both its crossings sit together at Kiri no Sato."""
    out: list[str] = []
    cx, cy = PADDIES
    for r, w, h in ((0, 34, 20), (1, 24, 13), (2, 14, 7)):
        out.append(_rect(cx - w / 2 + r * 2, cy - h / 2 + r * 1, w, h, stroke=PADDY, sw=1.1))
    out.append(_path([(cx - 16, cy + 4), (cx + 16, cy - 2)], stroke=PADDY, sw=1.1))
    # mist-driven wheels, further south of the paddies (Ch12:21)
    for mx, my in MILLS:
        out.append(_circle(mx, my, 3.2, fill="none", stroke=BUILDING, sw=1.2))
        for d in range(4):
            a = math.radians(d * 90 + 45)
            out.append(_line(mx - 5 * math.cos(a), my - 5 * math.sin(a),
                             mx + 5 * math.cos(a), my + 5 * math.sin(a),
                             stroke=BUILDING, sw=0.9))
    return out


def _pine_stand(rng: random.Random) -> list[str]:
    """The pine stand an hour out of Kiriguchi (Ch9:116)."""
    out: list[str] = []
    px, py = PINE_STAND
    for _ in range(6):
        ox = rng.uniform(-13, 13)
        oy = rng.uniform(-8, 8)
        s = 5 + rng.uniform(-1, 2)
        out.append(_polygon(
            [(px + ox, py + oy - s), (px + ox - 3.4, py + oy + s * 0.6),
             (px + ox + 3.4, py + oy + s * 0.6)],
            fill=PINE,
        ))
    return out


def _closed_routes(rng: random.Random) -> list[str]:
    """Historical routes closed before the story opens (geography_reference):
    the pilgrim path north of the mouth (Ch3:33), and the engineers' track
    to the old boundary stones (Ch9:119). Faint and dotted throughout --
    abandoned, not maintained."""
    out: list[str] = []
    out.append(_path(PILGRIM_PATH, stroke=ROAD_DIM, sw=1.3, opacity=0.55, dash="1.5,3"))
    out.append(_path(BOUNDARY_TRACK, stroke=ROAD_DIM, sw=1.3, opacity=0.55, dash="1.5,3"))
    sx, sy = BOUNDARY_STONES
    for _ in range(6):
        a = rng.uniform(0, math.tau)
        out.append(_circle(sx + 7 * math.cos(a), sy + 7 * math.sin(a), 1.6, fill=INK_DIM))
    return out


def _hamlets(rng: random.Random, n: int) -> list[str]:
    """A handful of small, unlabeled building clusters scattered along the
    rim -- background texture for the near/far-rim villages the census
    implies exist without naming (see the HAMLETS comment)."""
    out: list[str] = []
    for cx, cy in HAMLETS[:n]:
        for _ in range(rng.randint(2, 4)):
            ox = rng.uniform(-9, 9)
            oy = rng.uniform(-7, 7)
            w = rng.uniform(2.8, 4.2)
            out.append(_rect(cx + ox, cy + oy, w, 2.6, fill=BUILDING, opacity=0.9))
            out.append(_rect(cx + ox, cy + oy - 1.3, w + 0.6, 1.6, fill=BUILDING_ROOF, opacity=0.9))
    return out


def _ridge_highlands(rng: random.Random) -> list[str]:
    """The old ridge road, the surface 'long approach' to the Basin
    (Ch34:134), crossing the highlands north-east of the bowl -- outside the
    mountain ring, so it doesn't compete with the bowl's own geometry.
    Sealed after Ch34 ("Same wall, different door"), so drawn faint and worn
    like the other closed routes, with a little rocky texture along it."""
    out: list[str] = []
    out.append(_path(RIDGE_ROAD, stroke=PASSAGE, sw=1.6, opacity=0.6, dash="5,4"))
    for x, y in RIDGE_ROAD[:3]:
        for _ in range(3):
            ox = x + rng.uniform(-22, 22)
            oy = y + rng.uniform(-16, 16)
            out.append(_polygon(
                [(ox - 3, oy + 2), (ox, oy - 3), (ox + 3, oy + 2)],
                fill=MTN, stroke=MTN_STROKE, sw=0.8, opacity=0.8,
            ))
    ox, oy = RIDGE_PATH_OVERLOOK
    out.append(_circle(ox, oy, 2.2, stroke=INK_DIM, sw=1.0))
    return out


def _basin_ring(rng: random.Random) -> list[str]:
    """A small mountain range walling the Basin off; see the BASIN_RING_*
    comment. Same jagged-peak technique as the main ring (_mountains), just
    scaled down, with its own gap instead of the valley mouth's."""
    out: list[str] = []
    n = 22
    for i in range(n):
        a_deg = 360.0 * i / n
        if BASIN_RING_GAP_START <= a_deg <= BASIN_RING_GAP_END:
            continue
        a = math.radians(a_deg)
        bx = BOWL_CX + (BASIN_RING_RX + rng.uniform(-3, 3)) * math.cos(a)
        by = BOWL_CY + (BASIN_RING_RY + rng.uniform(-3, 3)) * math.sin(a)
        tx, ty = -math.sin(a), math.cos(a)
        w = 8 + rng.uniform(-2, 3)
        apex_x = BOWL_CX + (BASIN_RING_RX + 16 + rng.uniform(-3, 6)) * math.cos(a) + tx * rng.uniform(-3, 3)
        apex_y = BOWL_CY + (BASIN_RING_RY + 16 + rng.uniform(-3, 6)) * math.sin(a) + ty * rng.uniform(-3, 3)
        p1 = (bx + tx * w, by + ty * w)
        p2 = (bx - tx * w, by - ty * w)
        out.append(_polygon([p1, (apex_x, apex_y), p2], fill=MTN, stroke=MTN_STROKE, sw=0.9))
    return out


def _distant_peaks(rng: random.Random, n: int) -> list[str]:
    """A hazier, receding layer of peaks scattered across the exterior
    highlands (map texture, not geography_reference canon): the mountain
    ring by itself reads as one thin wall, so this gives the valley a
    broader range around it. Skips the mouth's own arc, which already has
    its own established context (Kiriguchi, the mist wall band)."""
    out: list[str] = []
    for _ in range(n):
        a_deg = rng.uniform(0, 360)
        if MOUTH_START - 20 <= a_deg <= MOUTH_END + 20:
            continue
        a = math.radians(a_deg)
        r_mult = rng.uniform(1.12, 1.25)
        cx = BOWL_CX + BOWL_RX * r_mult * math.cos(a)
        cy = BOWL_CY + BOWL_RY * r_mult * math.sin(a)
        w = rng.uniform(14, 26)
        h = rng.uniform(10, 20)
        out.append(_polygon(
            [(cx - w / 2, cy + h / 2), (cx, cy - h / 2), (cx + w / 2, cy + h / 2)],
            fill=MTN, stroke=MTN_STROKE, sw=0.8, opacity=0.5,
        ))
    return out


def _ground_texture(rng: random.Random, n: int) -> list[str]:
    """Faint scattered marks across the empty valley floor -- grass/reed
    texture, purely decorative, so the mist between the road and the rim
    doesn't read as dead space."""
    out: list[str] = []
    tries = 0
    placed = 0
    while placed < n and tries < n * 6:
        tries += 1
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0, 1) ** 0.5
        x = BOWL_CX + math.cos(a) * BOWL_RX * 0.82 * r
        y = BOWL_CY + math.sin(a) * BOWL_RY * 0.82 * r
        # skip the road corridor and the capital cluster, both already busy
        if 590 < x < 730 and 250 < y < 420:
            continue
        # the Basin's own mountain ring: keep the true center clear
        if math.hypot(x - BOWL_CX, y - BOWL_CY) < 95:
            continue
        # the lake south of Kiri no Sato
        if math.hypot(x - LAKE_KIRI_NO_SATO[0], y - LAKE_KIRI_NO_SATO[1]) < 38:
            continue
        # the lake north-east of Kasumikyo
        if math.hypot(x - LAKE_KASUMIKYO[0], y - LAKE_KASUMIKYO[1]) < 62:
            continue
        placed += 1
        ang = rng.uniform(0, math.pi)
        dx, dy = math.cos(ang) * 2.2, math.sin(ang) * 2.2
        out.append(_line(x - dx, y - dy, x + dx, y + dy, stroke=PADDY, sw=0.8, opacity=0.35))
    return out


def _dist_to_polyline(x: float, y: float, pts: list[tuple[float, float]]) -> float:
    best = math.inf
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        dx, dy = x2 - x1, y2 - y1
        seg_len_sq = dx * dx + dy * dy
        t = 0.0 if seg_len_sq == 0 else max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / seg_len_sq))
        px, py = x1 + dx * t, y1 + dy * t
        best = min(best, math.hypot(x - px, y - py))
    return best


def _forest(rng: random.Random, n_clumps: int) -> list[str]:
    """Dense forest cover across the valley floor's otherwise-empty space --
    background texture, not settled canon, the same standing as the second
    tributary, the hamlets, and the distant peaks: filling gaps the story
    leaves open rather than asserting a new fact. Kept clear of the road,
    the river system, Kasumikyo's wall and its leader-line labels, the
    villages, the fields, the hamlets, and the Basin's own isolating ring,
    so nothing already drawn gets buried under it."""
    out: list[str] = []
    routes = [CAPITAL_ROAD, RIVER, TRIBUTARY, SECRET_PASSAGE]
    points = [KIRIGUCHI, KIRI_NO_SATO, INN, PADDIES, *MILLS, *HAMLETS]
    tries = 0
    placed = 0
    while placed < n_clumps and tries < n_clumps * 8:
        tries += 1
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0, 1) ** 0.5
        cx = BOWL_CX + math.cos(a) * BOWL_RX * 0.88 * r
        cy = BOWL_CY + math.sin(a) * BOWL_RY * 0.88 * r
        # Kasumikyo's wall and its leader-line labels, a wide rectangle
        if 585 < cx < 870 and 250 < cy < 400:
            continue
        # the Basin's own mountain ring: keep the true center clear
        if math.hypot(cx - BOWL_CX, cy - BOWL_CY) < 95:
            continue
        # the lake south of Kiri no Sato
        if math.hypot(cx - LAKE_KIRI_NO_SATO[0], cy - LAKE_KIRI_NO_SATO[1]) < 42:
            continue
        # the lake north-east of Kasumikyo
        if math.hypot(cx - LAKE_KASUMIKYO[0], cy - LAKE_KASUMIKYO[1]) < 68:
            continue
        if any(_dist_to_polyline(cx, cy, route) < 30 for route in routes):
            continue
        if any(math.hypot(cx - px, cy - py) < 38 for px, py in points):
            continue
        placed += 1
        for _ in range(rng.randint(9, 15)):
            ox = cx + rng.uniform(-16, 16)
            oy = cy + rng.uniform(-12, 12)
            s = 4 + rng.uniform(-1, 2.5)
            out.append(_polygon(
                [(ox, oy - s), (ox - 2.8, oy + s * 0.6), (ox + 2.8, oy + s * 0.6)],
                fill=PINE, opacity=rng.uniform(0.55, 0.85),
            ))
    return out


def _village(cx: float, cy: float, n: int, rng: random.Random, *, label: str,
             label_y: float) -> list[str]:
    """A scatter of small buildings plus a label."""
    out: list[str] = []
    for _ in range(n):
        ox = rng.uniform(-11, 11)
        oy = rng.uniform(-9, 9)
        w = rng.uniform(3.2, 5.0)
        out.append(_rect(cx + ox, cy + oy, w, 3.2, fill=BUILDING))
        out.append(_rect(cx + ox, cy + oy - 1.6, w + 0.8, 2.0, fill=BUILDING_ROOF))
    out.append(_text(cx, label_y, label, size=13))
    return out


def _old_city_wall(rng: random.Random) -> list[str]:
    """The old wall ringing Kasumikyo's historic core; see the WALL_* comment.

    A flat-top hexagon (built stonework, so straighter than the mountains'
    jitter) with two gaps: a narrow gate at the south (flat) face, where the
    road actually crosses from the outer district into the treasury
    district, and a wider breach on the north-east face from the cataclysm.
    """
    verts = [
        (WALL_CX + WALL_RX * math.cos(a), WALL_CY + WALL_RY * math.sin(a))
        for a in (math.radians(60 * i) for i in range(6))
    ]
    edges = list(zip(verts, verts[1:] + verts[:1]))

    def stone_run(p1: tuple[float, float], p2: tuple[float, float],
                   t0: float = 0.0, t1: float = 1.0) -> list[tuple[float, float]]:
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1]) * (t1 - t0)
        n = max(2, round(length / 14))
        pts = []
        for i in range(n + 1):
            t = t0 + (t1 - t0) * i / n
            x = p1[0] + (p2[0] - p1[0]) * t + rng.uniform(-0.6, 0.6)
            y = p1[1] + (p2[1] - p1[1]) * t + rng.uniform(-0.6, 0.6)
            pts.append((x, y))
        return pts

    def crenellations(pts: list[tuple[float, float]]) -> list[str]:
        # short outward ticks along the run, for a fortification silhouette
        ticks: list[str] = []
        cx_, cy_ = WALL_CX, WALL_CY
        for i in range(0, len(pts) - 1, 2):
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            nx, ny = mx - cx_, my - cy_
            nl = math.hypot(nx, ny) or 1.0
            nx, ny = nx / nl, ny / nl
            ticks.append(_line(mx, my, mx + nx * 3.5, my + ny * 3.5, stroke=OLD_WALL, sw=2))
        return ticks

    out: list[str] = []
    for i, (p1, p2) in enumerate(edges):
        if i == 1:
            # south face (flat): the road's gate, a narrow notch at the
            # middle, between the outer district and the treasury district
            runs = [(0.0, 0.4), (0.6, 1.0)]
        elif i == 5:
            # north-east face: a wider breach from the cataclysm
            runs = [(0.0, 0.3), (0.7, 1.0)]
        else:
            runs = [(0.0, 1.0)]
        for t0, t1 in runs:
            pts = stone_run(p1, p2, t0, t1)
            out.append(_path(pts, stroke=OLD_WALL, sw=3.2))
            out.extend(crenellations(pts))
    # a corner bastion at each vertex, stone-toned rather than the
    # village/capital buildings' tan roofs, so the wall reads as one
    # fortification rather than a string of separate structures
    for vx, vy in verts:
        out.append(_circle(vx, vy, 4.6, fill=OLD_WALL, stroke=MTN_STROKE, sw=1.2))
        out.append(_circle(vx, vy, 1.6, fill=MTN_STROKE))
    return out


def _capital(rng: random.Random) -> list[str]:
    """Kasumikyo, slightly off the true center: outer district, treasury,
    walled shrine terrace, dead heart (geography_reference "Kasumikyo")."""
    out: list[str] = []
    ox, oy = OUTER_DISTRICT
    # the outer district's straight paved streets (Ch17:11-12)
    for k in range(4):
        out.append(_line(ox - 26, oy - 8 + k * 5.5, ox + 26, oy - 8 + k * 5.5,
                         stroke=ROAD_DIM, sw=1.0, opacity=0.6))
    for k in range(2):
        out.append(_line(ox - 18 + k * 36, oy - 12, ox - 18 + k * 36, oy + 8,
                         stroke=ROAD_DIM, sw=1.0, opacity=0.6))
    for _ in range(12):
        out.append(_rect(ox + rng.uniform(-24, 24), oy + rng.uniform(-6, 6),
                         rng.uniform(2.6, 4.2), 2.8, fill=BUILDING))
    # the treasury district (Ch18), close by the old city wall's gate, with
    # the lower-city texture around it that a single building can't carry
    # alone: a market-street barricade and a collapsed well-house (both
    # named in Ch18 but previously undrawn), plus an outer-district-style
    # building scatter, so this reads as a district and not a lone archive.
    tx, ty = TREASURY
    for k in range(3):
        out.append(_line(tx - 22, ty - 10 + k * 6, tx - 22, ty + 10,
                         stroke=ROAD_DIM, sw=1.0, opacity=0.5))
    for _ in range(9):
        out.append(_rect(tx + rng.uniform(-20, 18), ty + rng.uniform(-11, 11),
                         rng.uniform(2.4, 3.8), 2.6, fill=BUILDING, opacity=0.9))
    # the barricade spanning the mouth of a wide market street (Ch18:6)
    bx, by = tx - 15, ty + 9
    for i in range(3):
        out.append(_line(bx + i * 2.4, by - 2, bx + i * 2.4, by + 2, stroke=BUILDING_ROOF, sw=1.6))
    # the collapsed well-house (Ch18:3): a broken (dashed) ring rather than
    # a closed circle, plus fallen roof timbers scattered beside it
    wx, wy = tx - 17, ty - 8
    out.append(_circle(wx, wy, 2.6, stroke=INK_DIM, sw=1.2, dash="2,1.6"))
    out.append(_line(wx - 3.5, wy + 2, wx + 1, wy + 4, stroke=BUILDING_ROOF, sw=1.2, opacity=0.8))
    # the treasury building itself: intact and roofed, marked with a vault
    # seal so it doesn't read as an identical twin of the annex
    out.append(_rect(tx - 7, ty - 6, 14, 11, fill="none", stroke=BUILDING, sw=1.2))
    out.append(_rect(tx - 4, ty - 3, 8, 6, fill=BUILDING_ROOF))
    out.append(_polygon([(tx, ty - 2.4), (tx + 2.4, ty), (tx, ty + 2.4), (tx - 2.4, ty)],
                        fill="none", stroke=INK_DIM, sw=0.8))
    # the walled shrine terrace, the one place the Kirijuu do not cluster
    # (Ch20): a moss-softened courtyard with shrine buildings ranged around
    # it (Ch20:7-10), shrunk and pulled toward the gate so it reads as a
    # waypoint rather than the capital's dominant structure
    gx, gy = TERRACE
    out.append(_rect(gx - 17, gy - 11, 34, 22, stroke=INK_DIM, sw=1.3, fill="#3a4436"))
    for dx, dy in ((-12, -6), (12, -6), (-12, 6), (12, 6)):
        out.append(_rect(gx + dx - 2.1, gy + dy - 1.8, 4.2, 1.5, fill=BUILDING_ROOF))
        out.append(_rect(gx + dx - 1.8, gy + dy - 1.1, 3.6, 2.3, fill=BUILDING))
    # the ritual stone basin, courtyard center (Ch20:44)
    out.append(_circle(gx, gy, 2.2, fill=INK_DIM))
    # the north tower, set into the terrace's own wall (Ch21:82), not
    # floating apart from it
    twx, twy = TERRACE_NORTH_TOWER
    out.append(_rect(twx - 2.4, twy - 5.5, 4.8, 5.5, fill=BUILDING_ROOF))
    out.append(_circle(twx, twy, 2.6, fill=BUILDING))
    # the palace wall: its own footprint, older than the outer city wall,
    # around the dead heart's throne room ruin below. South wall carries a
    # gate where the road actually crosses in from the terrace gate; the
    # eastern courtyard (Ch6:5) is a small walled bump on the east face.
    px0, py0, px1, py1 = PALACE_X0, PALACE_Y0, PALACE_X1, PALACE_Y1
    out.append(_line(px0, py0, px1, py0, stroke=OLD_WALL, sw=2.0))
    out.append(_line(px1, py0, px1, py1, stroke=OLD_WALL, sw=2.0))
    out.append(_line(px0, py0, px0, py1, stroke=OLD_WALL, sw=2.0))
    out.append(_line(px0, py1, PALACE_GATE_CX - 5, py1, stroke=OLD_WALL, sw=2.0))
    out.append(_line(PALACE_GATE_CX + 5, py1, px1, py1, stroke=OLD_WALL, sw=2.0))
    out.append(_rect(px1, py0 + 6, 11, 9, fill="none", stroke=OLD_WALL, sw=1.4))
    # the throne room: "the largest room still standing in Kasumikyo"
    # (Ch27:56) and the pre-cataclysm audience hall (Ch23:99) -- given a
    # tiered footprint and its own Okiri-court-blue color (Tenno's "layered
    # silk in Okiri blue," continuity_reference), so it reads as the
    # capital's one deliberately grand structure rather than another roofed
    # shed in BUILDING/BUILDING_ROOF tan. Explicitly still standing (Ch24:10,
    # "the least ruined ground the column had crossed"), so a solid roof
    # fill throughout, no rubble.
    hx, hy = DEAD_HEART
    base_w, base_h = 70.0, 26.0
    out.append(_rect(hx - base_w / 2, hy - base_h / 2, base_w, base_h,
                     fill=PALACE_ROOF, stroke=PALACE_TRIM, sw=1.4))
    upper_w, upper_h = 38.0, 20.0
    upper_top = hy - base_h / 2 - upper_h + 2  # 2 units of overlap onto the base tier
    out.append(_rect(hx - upper_w / 2, upper_top, upper_w, upper_h,
                     fill=PALACE_ROOF_LIGHT, stroke=PALACE_TRIM, sw=1.2))
    # ridge accents, "crane-and-mist crest in silver thread" (Ch6, Tenno's
    # regalia) echoed here rather than repeated verbatim
    out.append(_line(hx - upper_w / 2, upper_top, hx + upper_w / 2, upper_top,
                     stroke=PALACE_TRIM, sw=1.0, opacity=0.85))
    out.append(_circle(hx, upper_top - 3, 2.2, fill=PALACE_TRIM))
    out.append(_line(hx - base_w / 2, hy - base_h / 2, hx - upper_w / 2, hy - base_h / 2,
                     stroke=PALACE_TRIM, sw=0.8, opacity=0.7))
    out.append(_line(hx + upper_w / 2, hy - base_h / 2, hx + base_w / 2, hy - base_h / 2,
                     stroke=PALACE_TRIM, sw=0.8, opacity=0.7))
    # the annex, closer to the palace gate, found before the throne room
    # (Ch24:18) -- a low, humble, windowless building, deliberately kept in
    # the ordinary village/capital BUILDING tan rather than the throne
    # room's blue
    anx, any_ = PALACE_GATE_CX + 10, PALACE_Y1 - 8
    out.append(_rect(anx - 4.5, any_ - 3, 9, 6, fill="none", stroke=BUILDING, sw=1.2))
    out.append(_rect(anx - 3.5, any_ - 2, 7, 4, fill=BUILDING_ROOF))
    # the colonnade between them, "half-collapsed and half-standing"
    # (Ch24:144): alternating standing (tall) and collapsed (short stub)
    # columns along the connecting path
    c1x, c1y = hx + base_w / 2 - 2, hy + base_h / 2 - 4
    c2x, c2y = anx - 4.5, any_ - 3
    for k in range(5):
        t = k / 4
        cxk = c1x + (c2x - c1x) * t
        cyk = c1y + (c2y - c1y) * t
        h = 2.6 if k % 2 == 0 else 1.0
        out.append(_line(cxk, cyk - h / 2, cxk, cyk + h / 2, stroke=BUILDING, sw=1.0, opacity=0.85))
    # the grave just outside the colonnade (Ch27:4-5)
    out.append(_line(anx + 5, any_ + 3, anx + 8, any_ + 3, stroke=INK_DIM, sw=1.2))
    out.append(_line(anx + 6.5, any_ + 1.5, anx + 6.5, any_ + 4.5, stroke=INK_DIM, sw=1.2))
    return out


def _zones() -> list[str]:
    """Faint creature-zone rings, optional legend texture (design.md:201-212)."""
    rings = [
        (330, 225, 0),
        (240, 160, 0),
        (140, 95, 0),
    ]
    return [
        _ellipse(BOWL_CX, BOWL_CY, rx, ry, stroke=ZONE, sw=1, opacity=0.55) for rx, ry, _ in rings
    ]


def _legend() -> list[str]:
    box_x, box_y, box_w, box_h = 762, 480, 220, 172
    rows = [
        ("silver band", "the mist wall (Ch9)"),
        ("dashed line", "the secret passage (sealed)"),
        ("dotted line", "closed routes"),
        ("zone rings", "creature zones, outer to center"),
        ("scale", "scale stylized, not literal"),
    ]
    out = [
        _rect(box_x, box_y, box_w, box_h, fill="#10141c", opacity=0.62),
        _rect(box_x, box_y, box_w, box_h, stroke=INK_DIM, sw=1),
        _text(box_x + 12, box_y + 18, "Legend", size=11, anchor="start", fill=INK, spacing=2),
    ]
    y = box_y + 40
    for key, label in rows:
        if key == "silver band":
            out.append(_rect(box_x + 12, y - 6, 14, 6, fill=MIST_WALL))
        elif key == "dashed line":
            out.append(_line(box_x + 12, y - 2, box_x + 26, y - 2, stroke=PASSAGE, sw=2, dash="4,3"))
        elif key == "dotted line":
            out.append(_line(box_x + 12, y - 2, box_x + 26, y - 2, stroke=ROAD_DIM, sw=2, dash="1.5,3"))
        elif key == "zone rings":
            out.append(_ellipse(box_x + 19, y - 2, 9, 5, stroke=INK_DIM, sw=1))
        else:
            out.append(_text(box_x + 12, y - 4, "~", size=11, anchor="start", fill=INK_DIM))
        out.append(_text(box_x + 36, y, label, size=10, anchor="start", fill=INK_DIM))
        y += 24
    return out


def _compass() -> list[str]:
    cx, cy = 88, 84
    out = [
        _circle(cx, cy, 20, fill="#10141c", opacity=0.6),
        _circle(cx, cy, 20, stroke=INK_DIM, sw=1, fill="none"),
        _polygon([(cx, cy - 15), (cx - 4.5, cy + 6), (cx, cy + 3), (cx + 4.5, cy + 6)],
                 fill=INK, stroke="none"),
        _polygon([(cx, cy + 15), (cx - 4.5, cy - 6), (cx, cy - 3), (cx + 4.5, cy - 6)],
                 fill=INK_DIM, stroke="none"),
        _text(cx, cy - 26, "N", size=12, fill=INK),
    ]
    for deg, ch in ((90, "E"), (180, "S"), (270, "W")):
        a = math.radians(deg)
        out.append(_text(cx + 15 * math.cos(a), cy - 15 * math.sin(a) + 4, ch,
                         size=9, fill=INK_DIM))
    return out


def _wrap_group(elems: list[str], *, data_id: str, data_kind: str = "place") -> list[str]:
    """Wrap elements in a pickable group (interactive mode only)."""
    body = "".join(elems)
    return [
        f'<g data-id="{xml_escape(data_id)}" data-kind="{xml_escape(data_kind)}" '
        f'style="cursor:pointer">{body}</g>'
    ]


def render_map(
    variant: str = "settled",
    *,
    seed: int = 7,
    interactive: bool = False,
    place_overrides: dict[str, tuple[float, float]] | None = None,
    metadata_json: str | None = None,
) -> str:
    """Assemble the full SVG document, deterministic for seed+variant.

    Args:
        variant: minimal | settled | textured
        seed: RNG seed (sister default is 7)
        interactive: wrap key POIs with data-id groups for the editor
        place_overrides: map place id -> (x, y) for movable settlements
        metadata_json: optional FMG world JSON embedded in <metadata>
    """
    if variant not in ("minimal", "settled", "textured"):
        raise ValueError(f"unknown variant: {variant!r}")
    ov = place_overrides or {}
    rng = random.Random(seed)
    el: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="700" '
        f'viewBox="0 0 1000 700" font-family="{SERIF}">',
    ]
    if metadata_json:
        # Keep on its own lines; does not affect painting
        safe = metadata_json.replace("</", "<\\/")
        el.append(
            f'<metadata id="fmg-world" data-format="fmg-world/v1">{safe}</metadata>'
        )
    el.extend(
        [
            "<defs>",
            _mist_gradient(),
            "</defs>",
            _rect(0, 0, 1000, 700, fill=BG),
        ]
    )
    # the valley bowl: the mist, densest at the true center
    el.append(
        f'<ellipse cx="{BOWL_CX}" cy="{BOWL_CY}" rx="{BOWL_RX}" ry="{BOWL_RY}" '
        f'fill="url(#mist)"/>'
    )
    el.extend(_mountains(rng))
    el.extend(_distant_peaks(rng, 30))  # a hazier, broader range beyond the ring
    el.extend(_rim_edge(rng))
    el.extend(_ridge_highlands(rng))  # the old ridge road, outside the bowl entirely
    el.extend(_basin_ring(rng))  # walls the Basin off from the rest of the valley
    if variant == "textured":
        el.extend(_ground_texture(rng, 90))
    el.extend(_river(rng))
    el.extend(_lake(rng))
    el.extend(_capital_lake())
    el.extend(_tributary(rng))
    el.extend(_paddies_and_mills(rng))
    el.extend(_pine_stand(rng))
    if variant in ("settled", "textured"):
        el.extend(_closed_routes(rng))
        el.extend(_hamlets(rng, 6))
    el.extend(_forest(rng, 42))
    # the capital road, the journey spine: Kiriguchi through the wall, Kiri
    # no Sato, the inn, into Kasumikyo
    road_pts = list(CAPITAL_ROAD)
    # apply place overrides to known road endpoints if present
    if "kiriguchi" in ov:
        road_pts[0] = ov["kiriguchi"]
    road_el = _path(road_pts, stroke=ROAD, sw=2.8)
    if interactive:
        el.extend(_wrap_group([road_el], data_id="capital_road", data_kind="route"))
    else:
        el.append(road_el)
    # the secret passage, below everything (Ch31:9)
    pass_el = _path(SECRET_PASSAGE, stroke=PASSAGE, sw=2.2, dash="6,6")
    if interactive:
        el.extend(_wrap_group([pass_el], data_id="secret_passage", data_kind="route"))
    else:
        el.append(pass_el)
    # the mist wall at the mouth, over the road it cuts
    el.extend(_mist_wall_band(rng))
    # settlements (overridable positions)
    kiri = ov.get("kiriguchi", KIRIGUCHI)
    sato = ov.get("kiri_no_sato", KIRI_NO_SATO)
    inn = ov.get("valley_inn", INN)
    v_kiri = _village(*kiri, 4, rng, label="Kiriguchi / Nebelmark", label_y=kiri[1] + 34)
    v_sato = _village(*sato, 5, rng, label="Kiri no Sato", label_y=sato[1] - 18.7)
    v_inn = _village(*inn, 1, rng, label="the Valley Inn", label_y=inn[1] - 18)
    if interactive:
        el.extend(_wrap_group(v_kiri, data_id="kiriguchi"))
        el.extend(_wrap_group(v_sato, data_id="kiri_no_sato"))
        el.extend(_wrap_group(v_inn, data_id="valley_inn"))
    else:
        el.extend(v_kiri)
        el.extend(v_sato)
        el.extend(v_inn)
    el.extend(_old_city_wall(rng))
    cap = _capital(rng)
    if interactive:
        el.extend(_wrap_group(cap, data_id="kasumikyo"))
    else:
        el.extend(cap)
    bas = _basin()
    if interactive:
        el.extend(_wrap_group(bas, data_id="basin"))
    else:
        el.extend(bas)
    # --- labels (uniform: same font style as "Kiriguchi / Nebelmark") ---
    el.append(_text(500, 44, "the valley of mists"))
    el.append(_text(BOWL_CX, 334, "Kiri no chuushin"))
    el.append(_text(BOWL_CX, 350, "the Basin"))
    el.append(_text(276, 590, "the mist wall"))
    el.append(_text(660, 231, "Kasumikyo"))
    el.append(_text(660, 246, "the ruined capital"))
    # Kasumikyo's sub-locations, named with leader lines out past the wall
    # rather than packed into the cluster (which is how the in-wall labels
    # collided earlier in this map's iteration)
    el.extend(_leader_label(690, 312, 775, 298, "the palace"))
    el.extend(_leader_label(665, 355, 740, 348, "the shrine terrace"))
    el.extend(_leader_label(667, 378, 745, 380, "the treasury"))
    el.append("</svg>")
    return "\n".join(el)


def write_map(
    out_prefix: Path,
    want_png: bool = True,
    *,
    variant: str = "settled",
    seed: int = 7,
) -> None:
    """Write the SVG (and best-effort PNG)."""
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    svg = render_map(variant=variant, seed=seed)
    svg_path = out_prefix.with_suffix(".svg")
    svg_path.write_text(svg, encoding="utf-8")
    print(f"wrote {svg_path}")

    if want_png:
        try:
            import cairosvg

            png_path = out_prefix.with_suffix(".png")
            png_path.write_bytes(cairosvg.svg2png(bytestring=svg.encode(), scale=2))
            print(f"wrote {png_path}")
        except ImportError:
            print("cairosvg not installed; skipping PNG export (SVG is valid, open it directly)")
        except OSError as e:
            print(
                f"cairosvg needs the system cairo library, which isn't available ({e}); "
                "SVG was still written"
            )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="valley_map", help="output path prefix")
    ap.add_argument("--no-png", action="store_true", help="skip PNG export")
    ap.add_argument("--variant", default="settled", choices=("minimal", "settled", "textured"))
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    write_map(Path(args.out), want_png=not args.no_png, variant=args.variant, seed=args.seed)


if __name__ == "__main__":
    sys.exit(main() or 0)
