"""Map rendering engine: MapConfig → SVG.

Layer pipeline + style kits. Deterministic via seeded RNG.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from fantasy_map_generator.config import (
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

# --- SVG primitives ---------------------------------------------------------


def _polygon(
    points: list[tuple[float, float]],
    *,
    fill: str,
    stroke: str | None = None,
    sw: float = 1.0,
    opacity: float = 1.0,
    dash: str | None = None,
    rule: str | None = None,
) -> str:
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


def _path(
    points: list[tuple[float, float]],
    *,
    stroke: str,
    sw: float,
    opacity: float = 1.0,
    dash: str | None = None,
    fill: str = "none",
    linecap: str = "round",
    linejoin: str = "round",
) -> str:
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in points)
    attrs = [
        f'fill="{fill}"',
        f'stroke="{stroke}" stroke-width="{sw}"',
        f'stroke-linecap="{linecap}" stroke-linejoin="{linejoin}"',
    ]
    if opacity < 1.0:
        attrs.append(f'stroke-opacity="{opacity}"')
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    return f'<path d="{d}" {" ".join(attrs)}/>'


def _circle(
    cx: float,
    cy: float,
    r: float,
    *,
    fill: str | None = None,
    stroke: str | None = None,
    sw: float = 1.0,
    opacity: float = 1.0,
) -> str:
    attrs = [f'fill="{fill}"' if fill else 'fill="none"']
    if stroke:
        attrs.append(f'stroke="{stroke}" stroke-width="{sw}"')
    if opacity < 1.0:
        attrs.append(f'opacity="{opacity}"')
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.2f}" {" ".join(attrs)}/>'


def _ellipse_fill(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    *,
    fill: str,
    stroke: str | None = None,
    sw: float = 1.0,
    opacity: float = 1.0,
) -> str:
    attrs = [
        f'cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}"',
        f'fill="{fill}"',
    ]
    if stroke:
        attrs.append(f'stroke="{stroke}" stroke-width="{sw}"')
    if opacity < 1.0:
        attrs.append(f'opacity="{opacity}"')
    return f"<ellipse {' '.join(attrs)}/>"


def _rect(
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fill: str | None = None,
    stroke: str | None = None,
    sw: float = 1.0,
    opacity: float = 1.0,
) -> str:
    attrs = [f'fill="{fill}"' if fill else 'fill="none"']
    if stroke:
        attrs.append(f'stroke="{stroke}" stroke-width="{sw}"')
    if opacity < 1.0:
        attrs.append(f'opacity="{opacity}"')
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" {" ".join(attrs)}/>'


_FILLER_WORDS = {"the", "no"}


def _title_case(s: str) -> str:
    return " ".join(w if w.lower() in _FILLER_WORDS else w[:1].upper() + w[1:] for w in s.split())


def _text(
    x: float,
    y: float,
    s: str,
    *,
    size: float = 13.0,
    anchor: str = "middle",
    fill: str = "#e8e2d2",
    italic: bool = False,
    weight: str | None = None,
    spacing: float | None = None,
    outline: bool = True,
) -> str:
    label = _title_case(s)
    attrs = [
        f'x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}"',
        "font-family=\"Georgia, 'Times New Roman', serif\"",
        'pointer-events="none"',
    ]
    if italic:
        attrs.append('font-style="italic"')
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if spacing is not None:
        attrs.append(f'letter-spacing="{spacing}"')
    base = " ".join(attrs)
    escaped = xml_escape(label)
    if not outline:
        return f'<text {base} fill="{fill}">{escaped}</text>'
    sw = max(1.4, round(size * 0.22, 1))
    return (
        f'<text {base} fill="none" stroke="#000000" stroke-width="{sw}" '
        f'stroke-linejoin="round">{escaped}</text>'
        f'<text {base} fill="{fill}">{escaped}</text>'
    )


def _group(children: list[str], *, data_id: str, data_kind: str, extra: str = "") -> str:
    """Wrap elements in a pickable group."""
    body = "".join(children)
    return (
        f'<g data-id="{xml_escape(data_id)}" data-kind="{xml_escape(data_kind)}" '
        f'style="cursor:pointer" {extra}>{body}</g>'
    )


def _line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    stroke: str,
    sw: float,
    opacity: float = 1.0,
    dash: str | None = None,
) -> str:
    attrs = [
        f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"',
        f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"',
    ]
    if opacity < 1.0:
        attrs.append(f'stroke-opacity="{opacity}"')
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    return f"<line {' '.join(attrs)}/>"


# --- Geometry helpers -------------------------------------------------------


def _rough_ellipse(
    rng: random.Random,
    center: tuple[float, float],
    radii: tuple[float, float],
    rough: float,
    n: int = 48,
) -> list[tuple[float, float]]:
    cx, cy = center
    rx, ry = radii
    amp = max(rough, 0.0)
    pts: list[tuple[float, float]] = []
    for i in range(n):
        a = (math.tau * i) / n
        jitter = 1.0 + amp * rng.uniform(-0.35, 0.45)
        pts.append((cx + math.cos(a) * rx * jitter, cy + math.sin(a) * ry * jitter))
    return pts


def _land_points(
    rng: random.Random, body: LandBody, coast_roughness: float
) -> list[tuple[float, float]]:
    if body.kind == "polygon" and len(body.points) >= 3:
        if coast_roughness <= 0 and body.rough <= 0:
            return list(body.points)
        # light midpoint displacement
        pts = list(body.points)
        out: list[tuple[float, float]] = []
        amp = (body.rough + coast_roughness) * 8
        for i, p in enumerate(pts):
            out.append(p)
            q = pts[(i + 1) % len(pts)]
            mx = (p[0] + q[0]) / 2 + rng.uniform(-amp, amp)
            my = (p[1] + q[1]) / 2 + rng.uniform(-amp, amp)
            out.append((mx, my))
        return out
    rough = max(body.rough, coast_roughness)
    return _rough_ellipse(rng, body.center, body.radii, rough)


def _border_x_at(border: list[tuple[float, float]], y: float) -> float:
    """Interpolate a y-monotonic border polyline's x at a given y (clamped
    to the endpoints outside its range)."""
    if y <= border[0][1]:
        return border[0][0]
    for i in range(1, len(border)):
        x0, y0 = border[i - 1]
        x1, y1 = border[i]
        if y <= y1:
            if y1 == y0:
                return x1
            t = (y - y0) / (y1 - y0)
            return x0 + t * (x1 - x0)
    return border[-1][0]


def _border_crossing(
    p0: tuple[float, float], p1: tuple[float, float], border: list[tuple[float, float]]
) -> tuple[float, float]:
    bx0, bx1 = _border_x_at(border, p0[1]), _border_x_at(border, p1[1])
    denom = (p1[0] - p0[0]) - (bx1 - bx0)
    if abs(denom) < 1e-9:
        return p1
    t = max(0.0, min(1.0, (bx0 - p0[0]) / denom))
    return (p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1]))


def _clip_polygon_by_border(
    points: list[tuple[float, float]], border: list[tuple[float, float]], keep_right: bool
) -> list[tuple[float, float]]:
    """Split a landmass polygon along a jagged, y-monotonic border curve
    (see make_meander_border), keeping the x >= border_x(y) side if
    keep_right else the x <= side. Unlike straight-line Sutherland-Hodgman
    clipping, the kept side's boundary must actually trace the border's own
    zigzag vertices, not just a straight line between where the coastline
    enters and exits the border band -- so this finds the single contiguous
    run of "inside" coastline vertices (there are exactly two crossings:
    where the border meets the top coast and the bottom coast, since the
    border spans the landmass's full vertical extent) and splices in the
    matching slice of the border polyline to close the shape."""
    n = len(points)

    def is_in(p: tuple[float, float]) -> bool:
        bx = _border_x_at(border, p[1])
        return (p[0] >= bx) if keep_right else (p[0] <= bx)

    flags = [is_in(p) for p in points]
    if all(flags):
        return list(points)
    if not any(flags):
        return []

    start = next(i for i in range(n) if flags[i] and not flags[i - 1])
    inside_pts: list[tuple[float, float]] = []
    i = start
    while flags[i % n]:
        inside_pts.append(points[i % n])
        i += 1
    end = i % n

    enter_pt = _border_crossing(points[(start - 1) % n], points[start % n], border)
    exit_pt = _border_crossing(points[(end - 1) % n], points[end % n], border)

    y_lo, y_hi = sorted((enter_pt[1], exit_pt[1]))
    border_seg = [pt for pt in border if y_lo <= pt[1] <= y_hi]
    if exit_pt[1] > enter_pt[1]:
        border_seg = border_seg[::-1]

    return [enter_pt, *inside_pts, exit_pt, *border_seg]


def _lake(lake: WaterBody, palette: Palette) -> str:
    cx, cy = lake.center
    rx, ry = lake.radii
    fill = lake.fill or palette.water
    return (
        f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
        f'fill="{fill}" fill-opacity="0.75" stroke="{palette.water_deep}" '
        f'stroke-width="1" stroke-opacity="0.6"/>'
    )


def _ellipse_polygon(
    center: tuple[float, float], radii: tuple[float, float], n: int = 48
) -> list[tuple[float, float]]:
    cx, cy = center
    rx, ry = radii
    return [
        (cx + rx * math.cos(math.tau * i / n), cy + ry * math.sin(math.tau * i / n)) for i in range(n)
    ]


def _clip_polygon_convex(
    subject: list[tuple[float, float]], clip: list[tuple[float, float]]
) -> list[tuple[float, float]]:
    """Standard Sutherland-Hodgman clip of `subject` against a *convex*
    `clip` polygon (an ellipse approximation, in practice) -- used to
    intersect the landmass coastline with a decorative overlay region so it
    reads as "part of the land" rather than a freestanding shape spilling
    past the shore. Unlike _clip_polygon_by_border, this clips against a
    full closed polygon on every side at once, which only works because the
    clip shape is convex (each edge is a valid infinite half-plane test)."""
    output = subject
    n = len(clip)
    for i in range(n):
        cx1, cy1 = clip[i]
        cx2, cy2 = clip[(i + 1) % n]
        edge_x, edge_y = cx2 - cx1, cy2 - cy1

        def is_inside(p: tuple[float, float], cx1: float = cx1, cy1: float = cy1, edge_x: float = edge_x, edge_y: float = edge_y) -> bool:
            # >= 0 matches a CCW-wound clip polygon (true for _ellipse_polygon's
            # cos/sin construction); verified against a known CCW test square.
            return edge_x * (p[1] - cy1) - edge_y * (p[0] - cx1) >= 0

        input_list, output = output, []
        if not input_list:
            break
        for j in range(len(input_list)):
            cur = input_list[j]
            prev = input_list[j - 1]
            cur_in, prev_in = is_inside(cur), is_inside(prev)
            if cur_in:
                if not prev_in:
                    output.append(_segment_intersect(prev, cur, cx1, cy1, edge_x, edge_y))
                output.append(cur)
            elif prev_in:
                output.append(_segment_intersect(prev, cur, cx1, cy1, edge_x, edge_y))
    return output


def _segment_intersect(
    p0: tuple[float, float], p1: tuple[float, float], ex: float, ey: float, dx: float, dy: float
) -> tuple[float, float]:
    """Intersection of segment p0->p1 with the infinite line through (ex,ey)
    with direction (dx,dy). Used by _clip_polygon_convex."""
    sx, sy = p1[0] - p0[0], p1[1] - p0[1]
    denom = sx * dy - sy * dx
    if abs(denom) < 1e-9:
        return p1
    t = ((ex - p0[0]) * dy - (ey - p0[1]) * dx) / denom
    return (p0[0] + t * sx, p0[1] + t * sy)


def _biome_color(palette: Palette, biome: str) -> str:
    return {
        "forest": palette.forest,
        "desert": palette.desert,
        "swamp": palette.swamp,
        "ice": palette.ice,
        "plain": palette.plain,
        "coast": palette.land,
        "tundra": palette.ice,
    }.get(biome, palette.plain)


# --- Terrain drawers --------------------------------------------------------


def _mountains_ring(
    rng: random.Random,
    center: tuple[float, float],
    radii: tuple[float, float],
    mountain_color: str,
    mountain_stroke: str,
    mouth_start_deg: float = 0.0,
    mouth_end_deg: float = 0.0,
    num_peaks: int = 54,
    density: float = 1.0,
    size: float = 50.0,
    rotation: float = 0.0,
) -> list[str]:
    out: list[str] = []
    cx, cy = center
    rx, ry = radii  # the ring's footprint -- always literal, independent of `size`
    peak_scale = size / 50.0  # scales only the peak glyphs (height + base width), not the footprint
    n = max(8, int(num_peaks * density))
    rot_rad = math.radians(rotation)
    for i in range(n):
        a_deg = 360.0 * i / n + rotation
        if mouth_start_deg <= a_deg <= mouth_end_deg:
            continue
        a = math.radians(a_deg)
        base_offset = (8 + rng.uniform(-3, 3)) * peak_scale
        bx = cx + (rx + base_offset) * math.cos(a)
        by = cy + (ry + base_offset) * math.sin(a)
        tx, ty = -math.sin(a), math.cos(a)
        w = (16 + rng.uniform(-3, 5)) * peak_scale
        peak_reach = (42 + rng.uniform(-6, 14)) * peak_scale
        apex_x = cx + (rx + peak_reach) * math.cos(a) + tx * rng.uniform(-6, 6)
        apex_y = cy + (ry + peak_reach) * math.sin(a) + ty * rng.uniform(-6, 6)
        p1 = (bx + tx * w, by + ty * w)
        p2 = (bx - tx * w, by - ty * w)
        out.append(
            _polygon([p1, (apex_x, apex_y), p2], fill=mountain_color, stroke=mountain_stroke, sw=1)
        )
    return out


def _mountains_ridge(
    rng: random.Random,
    points: list[tuple[float, float]],
    mountain_color: str,
    mountain_stroke: str,
    density: float = 1.0,
    style: str = "jagged",
    size: float = 50.0,
) -> list[str]:
    if len(points) < 2:
        return []
    out: list[str] = []
    # densify polyline
    samples: list[tuple[float, float]] = []
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        seg = math.hypot(x1 - x0, y1 - y0)
        steps = max(1, int(seg / max(14.0 / max(density, 0.2), 8)))
        for s in range(steps):
            t = s / steps
            samples.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    samples.append(points[-1])

    for i, (bx, by) in enumerate(samples):
        if i + 1 < len(samples):
            dx = samples[i + 1][0] - bx
            dy = samples[i + 1][1] - by
        else:
            dx = bx - samples[i - 1][0]
            dy = by - samples[i - 1][1]
        ln = math.hypot(dx, dy) or 1.0
        tx, ty = -dy / ln, dx / ln
        size_scale = size / 50.0  # normalize to default size of 50
        w = (10 + rng.uniform(-2, 6)) * size_scale
        h = (22 + rng.uniform(-4, 12)) * size_scale
        if style == "symbol":
            # simple grey triangle stamp
            apex = (bx + tx * rng.uniform(-2, 2), by - h)
            out.append(
                _polygon(
                    [(bx - w, by), apex, (bx + w, by)],
                    fill=mountain_color,
                    stroke=mountain_stroke,
                    sw=0.8,
                )
            )
        else:
            apex = (bx + tx * rng.uniform(-4, 4), by - h + ty * rng.uniform(-3, 3))
            out.append(
                _polygon(
                    [(bx + tx * w, by + ty * w * 0.2), apex, (bx - tx * w, by - ty * w * 0.2)],
                    fill=mountain_color,
                    stroke=mountain_stroke,
                    sw=1,
                )
            )
            # snow cap tip
            if rng.random() < 0.35:
                out.append(
                    _polygon(
                        [
                            (apex[0], apex[1]),
                            (apex[0] - 3, apex[1] + 7),
                            (apex[0] + 3, apex[1] + 7),
                        ],
                        fill="#e8eef5",
                        opacity=0.75,
                    )
                )
    return out


def _mountains_stacked(
    rng: random.Random,
    center: tuple[float, float],
    radii: tuple[float, float],
    mountain_color: str,
    mountain_stroke: str,
    levels: int = 3,
    density: float = 0.8,
    size: float = 50.0,
    rotation: float = 0.0,
) -> list[str]:
    out: list[str] = []
    cx, cy = center
    size_scale = size / 50.0  # normalize to default size of 50
    for level in range(levels):
        t = (level + 1) / levels
        rx = radii[0] * (0.35 + 0.55 * t) * size_scale
        ry = radii[1] * (0.3 + 0.5 * t) * size_scale
        n = max(5, int(12 * density * (level + 1)))
        for _i in range(n):
            a = rng.uniform(0, math.tau)
            r = rng.uniform(0.2, 1.0) ** 0.7
            bx = cx + math.cos(a) * rx * r
            by = cy + math.sin(a) * ry * r * 0.85
            w = 8 + 6 * t + rng.uniform(-2, 3)
            h = 12 + 14 * t + rng.uniform(-3, 5)
            out.append(
                _polygon(
                    [(bx - w, by), (bx, by - h), (bx + w, by)],
                    fill=mountain_color,
                    stroke=mountain_stroke,
                    sw=0.8,
                    opacity=0.55 + 0.15 * level,
                )
            )
    return out


def _mountains_single(
    center: tuple[float, float],
    size: float,
    rotation: float,
    mountain_color: str,
    mountain_stroke: str,
) -> list[str]:
    """Render a single mountain peak with rotation."""
    cx, cy = center
    rot_rad = math.radians(rotation)
    cos_r = math.cos(rot_rad)
    sin_r = math.sin(rot_rad)

    # Create a single mountain peak (triangle)
    # Base points
    base_width = size * 1.2
    peak_height = size * 1.5

    # Triangle points before rotation: apex at (cx, cy - peak_height), base at cy
    apex = (0, -peak_height)
    left = (-base_width / 2, peak_height / 2)
    right = (base_width / 2, peak_height / 2)

    # Rotate and translate
    def rotate_point(p: tuple[float, float]) -> tuple[float, float]:
        x, y = p
        rx = x * cos_r - y * sin_r
        ry = x * sin_r + y * cos_r
        return (cx + rx, cy + ry)

    p_apex = rotate_point(apex)
    p_left = rotate_point(left)
    p_right = rotate_point(right)

    return [
        _polygon(
            [p_left, p_apex, p_right],
            fill=mountain_color,
            stroke=mountain_stroke,
            sw=1.2,
        )
    ]


def _river(
    rng: random.Random,
    waypoints: list[tuple[float, float]],
    water_color: str,
    tributary_color: str | None = None,
    width_scale: float = 1.0,
) -> list[str]:
    if len(waypoints) < 2:
        return []
    pts = [(x + rng.uniform(-2, 2), y + rng.uniform(-2, 2)) for x, y in waypoints]
    # multi-stroke with growing width downstream
    out = [
        _path(pts, stroke=water_color, sw=3.6 * width_scale, opacity=0.55),
        _path(pts, stroke=water_color, sw=1.4 * width_scale, opacity=0.45),
    ]
    if tributary_color:
        out.append(_path(pts, stroke=tributary_color, sw=0.9 * width_scale, opacity=0.35))
    # highlight taper: short segments with increasing width
    if len(pts) >= 3:
        mid = pts[len(pts) // 2 :]
        out.append(_path(mid, stroke=water_color, sw=2.2 * width_scale, opacity=0.35))
    return out


def _road_draw(
    waypoints: list[tuple[float, float]],
    road_color: str,
    road_dim: str,
    kind: str = "road",
) -> list[str]:
    if len(waypoints) < 2:
        return []
    if kind == "trail":
        return [_path(waypoints, stroke=road_dim, sw=1.2, opacity=0.7, dash="3 5")]
    if kind == "ferry":
        return [_path(waypoints, stroke=road_color, sw=1.4, opacity=0.6, dash="8 6")]
    # road: double-ish
    return [
        _path(waypoints, stroke=road_dim, sw=3.4, opacity=0.55),
        _path(waypoints, stroke=road_color, sw=1.6, opacity=0.85, dash="6 4"),
    ]


def _tree_triangle(ox: float, oy: float, s: float, color: str, opacity: float) -> str:
    return _polygon(
        [(ox, oy - s), (ox - 2.8, oy + s * 0.6), (ox + 2.8, oy + s * 0.6)],
        fill=color,
        opacity=opacity,
    )


def _tree_conifer(ox: float, oy: float, s: float, color: str, opacity: float) -> list[str]:
    return [
        _polygon(
            [(ox, oy - s * 1.4), (ox - s * 0.7, oy - s * 0.2), (ox + s * 0.7, oy - s * 0.2)],
            fill=color,
            opacity=opacity,
        ),
        _polygon(
            [(ox, oy - s * 0.7), (ox - s * 0.95, oy + s * 0.5), (ox + s * 0.95, oy + s * 0.5)],
            fill=color,
            opacity=opacity * 0.95,
        ),
        _rect(ox - 0.7, oy + s * 0.45, 1.4, s * 0.45, fill="#3a2a1a", opacity=opacity * 0.8),
    ]


def _tree_canopy(ox: float, oy: float, s: float, color: str, opacity: float) -> str:
    return _ellipse_fill(ox, oy, s * 1.2, s * 0.85, fill=color, opacity=opacity)


def _forest_stand(
    rng: random.Random,
    stand: ForestStand,
    forest_color: str,
    detail: float,
) -> list[str]:
    out: list[str] = []
    cx, cy = stand.center
    rx, ry = stand.radii
    n_clumps = max(1, int(stand.num_clumps * stand.density * (0.45 + detail)))
    placed = 0
    tries = 0
    while placed < n_clumps and tries < n_clumps * 10:
        tries += 1
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0, 1) ** 0.5
        cluster_x = cx + math.cos(a) * rx * 0.85 * r
        cluster_y = cy + math.sin(a) * ry * 0.85 * r
        placed += 1
        trees = rng.randint(6, 14)
        if stand.tree_style == "stamp":
            trees = rng.randint(10, 18)
        for _ in range(trees):
            ox = cluster_x + rng.uniform(-16, 16)
            oy = cluster_y + rng.uniform(-12, 12)
            s = 3.5 + rng.uniform(-1, 2.5)
            op = rng.uniform(0.5, 0.88)
            if stand.tree_style == "conifer":
                out.extend(_tree_conifer(ox, oy, s, forest_color, op))
            elif stand.tree_style == "canopy":
                out.append(_tree_canopy(ox, oy, s * 1.3, forest_color, op))
            elif stand.tree_style == "stamp":
                out.append(_tree_triangle(ox, oy, s * 0.75, forest_color, op))
            else:
                out.append(_tree_triangle(ox, oy, s, forest_color, op))
    return out


def _dune_hatch(
    rng: random.Random,
    center: tuple[float, float],
    radii: tuple[float, float],
    color: str,
    density: float,
) -> list[str]:
    out: list[str] = []
    cx, cy = center
    rx, ry = radii
    n = int(14 * density)
    for _ in range(n):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0.15, 0.9)
        x = cx + math.cos(a) * rx * r
        y = cy + math.sin(a) * ry * r
        w = rng.uniform(18, 40)
        pts = [
            (x - w * 0.5, y),
            (x - w * 0.15, y - rng.uniform(2, 6)),
            (x + w * 0.15, y - rng.uniform(1, 4)),
            (x + w * 0.5, y + rng.uniform(0, 3)),
        ]
        out.append(_path(pts, stroke=color, sw=1.1, opacity=0.35))
    return out


def _swamp_stipple(
    rng: random.Random,
    center: tuple[float, float],
    radii: tuple[float, float],
    color: str,
    density: float,
) -> list[str]:
    out: list[str] = []
    cx, cy = center
    rx, ry = radii
    for _ in range(int(40 * density)):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0, 1) ** 0.5
        x = cx + math.cos(a) * rx * r
        y = cy + math.sin(a) * ry * r
        out.append(_circle(x, y, rng.uniform(0.8, 2.0), fill=color, opacity=0.4))
    return out


# --- Settlements ------------------------------------------------------------


def _settlement_buildings(
    rng: random.Random,
    cx: float,
    cy: float,
    building_color: str,
    roof_color: str,
    scale: float = 1.0,
    count: int | None = None,
) -> list[str]:
    out: list[str] = []
    n = count if count is not None else rng.randint(2, 4)
    for _ in range(n):
        ox = cx + rng.uniform(-9, 9) * scale
        oy = cy + rng.uniform(-7, 7) * scale
        w = rng.uniform(2.8, 4.2) * scale
        h = 2.6 * scale
        out.append(_rect(ox, oy, w, h, fill=building_color, opacity=0.9))
        out.append(
            _rect(
                ox - 0.3 * scale,
                oy - 1.3 * scale,
                w + 0.6 * scale,
                1.6 * scale,
                fill=roof_color,
                opacity=0.9,
            )
        )
    return out


def _place_icon(
    rng: random.Random,
    place: Place,
    palette: Palette,
    *,
    selected: bool = False,
) -> list[str]:
    x, y = place.x, place.y
    tier = place.tier
    out: list[str] = []

    # Invisible hit disc for easier picking
    out.append(_circle(x, y, 16, fill="#ffffff", opacity=0.001))

    if tier == "capital":
        out.append(_circle(x, y, 10, fill="none", stroke=palette.gold, sw=1.6))
        out.append(_circle(x, y, 6, fill=palette.settlement, stroke=palette.ink, sw=1.0))
        star: list[tuple[float, float]] = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            r = 5.5 if i % 2 == 0 else 2.4
            star.append((x + math.cos(a) * r, y + math.sin(a) * r))
        out.append(_polygon(star, fill=palette.gold, stroke=palette.ink, sw=0.6))
        out.extend(
            _settlement_buildings(
                rng, x, y + 10, palette.settlement, palette.settlement_roof, 1.15, 5
            )
        )
    elif tier == "castle":
        out.append(_rect(x - 7, y - 4, 14, 10, fill=palette.settlement, stroke=palette.ink, sw=0.8))
        out.append(
            _rect(x - 8, y - 10, 5, 8, fill=palette.settlement_roof, stroke=palette.ink, sw=0.6)
        )
        out.append(
            _rect(x + 3, y - 10, 5, 8, fill=palette.settlement_roof, stroke=palette.ink, sw=0.6)
        )
        out.append(_rect(x - 2, y - 14, 4, 6, fill=palette.palace_roof, stroke=palette.ink, sw=0.6))
    elif tier == "ruin":
        out.append(_rect(x - 6, y - 2, 5, 7, fill=palette.old_wall, opacity=0.75))
        out.append(_rect(x + 1, y, 6, 5, fill=palette.old_wall, opacity=0.55))
        out.append(_path([(x - 8, y + 6), (x + 8, y + 7)], stroke=palette.ink, sw=0.8, opacity=0.5))
    elif tier == "city":
        out.append(_circle(x, y, 9, fill="none", stroke=palette.road, sw=1.4))
        out.extend(
            _settlement_buildings(rng, x, y, palette.settlement, palette.settlement_roof, 1.1, 6)
        )
    elif tier == "town":
        out.append(_circle(x, y, 4.5, fill=palette.settlement, stroke=palette.ink, sw=0.9))
        out.extend(
            _settlement_buildings(
                rng, x, y + 6, palette.settlement, palette.settlement_roof, 0.95, 3
            )
        )
    elif tier == "hamlet":
        out.extend(
            _settlement_buildings(rng, x, y, palette.settlement, palette.settlement_roof, 0.75, 2)
        )
    elif tier == "camp":
        # A tent, not a building -- deliberately distinct from "hamlet"
        # (see PlaceTier's own comment): a temporary/nomadic site reads
        # differently even at the smallest permanent-settlement scale.
        out.append(
            _polygon(
                [(x - 5, y + 4), (x, y - 5), (x + 5, y + 4)],
                fill=palette.settlement,
                stroke=palette.ink,
                sw=0.8,
            )
        )
        out.append(_path([(x, y - 5), (x, y + 4)], stroke=palette.ink, sw=0.6, opacity=0.6))
    else:  # village
        out.append(_circle(x, y, 3.2, fill=palette.settlement, stroke=palette.ink, sw=0.7))
        out.extend(
            _settlement_buildings(
                rng, x, y + 5, palette.settlement, palette.settlement_roof, 0.9, 3
            )
        )

    if selected:
        out.append(_circle(x, y, 18, fill="none", stroke="#ffcc33", sw=2.2))
        out.append(_circle(x, y, 18, fill="none", stroke="#ffffff", sw=0.8, opacity=0.9))

    pid = place.id or "place"
    return [_group(out, data_id=pid, data_kind="place")]


# --- Decor ------------------------------------------------------------------


def _decor_border(w: float, h: float, palette: Palette) -> list[str]:
    m = 14.0
    return [
        _rect(0, 0, w, h, fill="none", stroke=palette.ink, sw=2.5),
        _rect(m, m, w - 2 * m, h - 2 * m, fill="none", stroke=palette.gold, sw=1.2),
        _rect(m + 4, m + 4, w - 2 * m - 8, h - 2 * m - 8, fill="none", stroke=palette.ink, sw=0.6),
    ]


def _decor_compass(cx: float, cy: float, palette: Palette, scale: float = 1.0) -> list[str]:
    s = 28 * scale
    out = [
        _circle(cx, cy, s * 0.55, fill="none", stroke=palette.ink, sw=1.2),
        _circle(cx, cy, s * 0.12, fill=palette.gold, stroke=palette.ink, sw=0.6),
    ]
    # N tip
    out.append(
        _polygon(
            [(cx, cy - s), (cx - s * 0.18, cy), (cx + s * 0.18, cy)],
            fill=palette.ink,
        )
    )
    out.append(
        _polygon(
            [(cx, cy + s * 0.7), (cx - s * 0.14, cy), (cx + s * 0.14, cy)],
            fill=palette.text_faint,
            opacity=0.8,
        )
    )
    out.append(_text(cx, cy - s - 6, "N", size=11, fill=palette.text, weight="bold"))
    return out


def _decor_scale(x: float, y: float, palette: Palette) -> list[str]:
    out = [_text(x + 40, y - 6, "1 day", size=9, fill=palette.text_faint, outline=False)]
    for i in range(4):
        fill = palette.ink if i % 2 == 0 else palette.paper
        out.append(_rect(x + i * 20, y, 20, 6, fill=fill, stroke=palette.ink, sw=0.6))
    return out


def _decor_cartouche(cx: float, cy: float, title: str, palette: Palette) -> list[str]:
    w, h = 200.0, 36.0
    x, y = cx - w / 2, cy - h / 2
    return [
        _rect(x, y, w, h, fill=palette.paper, stroke=palette.ink, sw=1.2, opacity=0.92),
        _rect(x + 3, y + 3, w - 6, h - 6, fill="none", stroke=palette.gold, sw=0.8),
        _text(cx, cy + 5, title, size=14, fill=palette.ink, weight="bold", outline=False),
    ]


def _region_label(label: RegionLabel, palette: Palette) -> str:
    """A large political/kingdom name spanning its own territory (see
    RegionLabel's own docstring for how this differs from a BiomeRegion's
    smaller, density-gated label)."""
    cx, cy = label.center
    txt = _text(
        cx,
        cy,
        label.name.upper(),
        size=label.font_size,
        weight="bold",
        fill=palette.text,
        spacing=3.0,
    )
    if not label.rotation:
        return txt
    return f'<g transform="rotate({label.rotation:.1f} {cx:.1f} {cy:.1f})">{txt}</g>'


_LEGEND_GLYPHS: dict[str, str] = {
    "mountain": "mountain",
    "forest": "forest",
    "desert": "desert",
    "swamp": "swamp",
    "capital": "capital",
    "city": "city",
    "town": "town",
    "village": "village",
    "hamlet": "village",
    "castle": "capital",
    "ruin": "village",
    "camp": "camp",
    "road": "road",
    "trail": "trail",
    "river": "river",
}


def _legend_glyph(kind: str, cx: float, cy: float, palette: Palette) -> list[str]:
    """A small (~12px) symbol matching one row of the legend box. Reuses the
    same simple shapes as the full-size map features rather than inventing
    new icon art (a scaled-down triangle for a mountain, a dot for a
    settlement, a short dash for a route), so the legend key actually
    resembles what's drawn on the map itself."""
    kind = _LEGEND_GLYPHS.get(kind, kind)
    if kind == "mountain":
        return [_polygon([(cx, cy - 5), (cx - 5, cy + 5), (cx + 5, cy + 5)], fill=palette.mountain, stroke=palette.mountain_stroke, sw=0.6)]
    if kind == "forest":
        return [_polygon([(cx, cy - 6), (cx - 4, cy + 4), (cx + 4, cy + 4)], fill=palette.forest)]
    if kind == "desert":
        return [_circle(cx + dx, cy, 1.1, fill=palette.text_faint) for dx in (-4, 0, 4)]
    if kind == "swamp":
        return [_path([(cx - 5, cy), (cx - 2, cy - 3), (cx + 1, cy), (cx + 4, cy - 3)], stroke=palette.water, sw=1.2)]
    if kind in {"capital", "city", "town", "village"}:
        r = {"capital": 4.0, "city": 3.2, "town": 2.6, "village": 2.0}[kind]
        return [_circle(cx, cy, r, fill=palette.settlement, stroke=palette.ink, sw=0.6)]
    if kind == "camp":
        return [_polygon([(cx, cy - 4), (cx - 4, cy + 4), (cx + 4, cy + 4)], fill=palette.settlement, stroke=palette.ink, sw=0.6)]
    if kind in {"road", "trail"}:
        dash = ' stroke-dasharray="2 3"' if kind == "trail" else ""
        return [f'<line x1="{cx - 6:.1f}" y1="{cy:.1f}" x2="{cx + 6:.1f}" y2="{cy:.1f}" stroke="{palette.road}" stroke-width="1.6"{dash}/>']
    if kind == "river":
        return [f'<line x1="{cx - 6:.1f}" y1="{cy:.1f}" x2="{cx + 6:.1f}" y2="{cy:.1f}" stroke="{palette.water}" stroke-width="2"/>']
    return []


def _decor_legend(x: float, y: float, entries: list[tuple[str, str]], palette: Palette) -> list[str]:
    """A bordered key box listing (kind, label) pairs, e.g. [("capital",
    "Capital"), ("mountain", "Mountains"), ("trail", "Trade Route")]."""
    row_h = 16.0
    w = 130.0
    h = 14.0 + row_h * len(entries)
    out = [
        _rect(x, y, w, h, fill=palette.paper, stroke=palette.ink, sw=1.2, opacity=0.92),
        _rect(x + 3, y + 3, w - 6, h - 6, fill="none", stroke=palette.gold, sw=0.8),
        _text(x + w / 2, y + 12, "Legend", size=11, fill=palette.ink, weight="bold", outline=False),
    ]
    for i, (kind, label) in enumerate(entries):
        row_y = y + 24 + i * row_h
        out.extend(_legend_glyph(kind, x + 14, row_y - 3, palette))
        out.append(_text(x + 26, row_y, label, size=10, anchor="start", fill=palette.ink, outline=False))
    return out


def _decor_ship(cx: float, cy: float, palette: Palette, scale: float = 1.0) -> list[str]:
    """A small sailing-ship glyph for open ocean; positions are hand-picked
    per world (see MapConfig.ships), not auto-placed/collision-avoided."""
    s = 9.0 * scale
    hull = _path(
        [(cx - s, cy), (cx - s * 0.6, cy + s * 0.5), (cx + s * 0.6, cy + s * 0.5), (cx + s, cy)],
        stroke=palette.ink,
        sw=1.0,
        opacity=0.85,
    )
    mast = f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx:.1f}" y2="{cy - s * 1.6:.1f}" stroke="{palette.ink}" stroke-width="1"/>'
    sail = _polygon(
        [(cx, cy - s * 1.6), (cx, cy - s * 0.2), (cx + s * 0.9, cy - s * 0.3)],
        fill=palette.paper,
        stroke=palette.ink,
        sw=0.6,
        opacity=0.9,
    )
    return [hull, mast, sail]


def _decor_volcano(cx: float, cy: float, scale: float = 1.0) -> list[str]:
    """A single dark volcanic cone with a glowing crater and a thin smoke
    wisp -- distinct from an ordinary MountainRange peak (which uses the
    world's plain mountain_color); positions are hand-picked per world (see
    MapConfig.volcanoes)."""
    s = 22.0 * scale
    cone = _polygon(
        [(cx - s * 0.65, cy + s * 0.4), (cx, cy - s), (cx + s * 0.65, cy + s * 0.4)],
        fill="#3c2a24",
        stroke="#241813",
        sw=1.2,
    )
    crater = _circle(cx, cy - s * 0.82, s * 0.16, fill="#e8622c", stroke="#a83a18", sw=0.8)
    glow = _circle(cx, cy - s * 0.82, s * 0.32, fill="#e8622c", opacity=0.25)
    smoke = _path(
        [(cx, cy - s * 1.0), (cx + s * 0.25, cy - s * 1.5), (cx - s * 0.1, cy - s * 2.0), (cx + s * 0.2, cy - s * 2.5)],
        stroke="#8a8a8a",
        sw=2.2,
        opacity=0.35,
    )
    return [smoke, glow, cone, crater]


def _decor_sacred_site(cx: float, cy: float, kind: str, palette: Palette) -> list[str]:
    """A Sleeping Gods landmark (see MapConfig.sacred_sites). "temple" is a
    small stepped/stacked stone monument, still standing; "kurgan" is an
    unbuilt mound ringed by standing stones -- deliberately not a structure,
    for a culture whose doctrine forbids building one (e.g. the Tumen)."""
    if kind == "kurgan":
        out = [_ellipse_fill(cx, cy, 10.0, 6.0, fill=palette.road_dim, opacity=0.5)]
        for i in range(6):
            a = math.tau * i / 6
            sx, sy = cx + math.cos(a) * 13.0, cy + math.sin(a) * 7.0
            out.append(_line(sx, sy - 3.5, sx, sy + 1.5, stroke=palette.ink, sw=1.4, opacity=0.8))
        return out
    # "temple": three stacked, narrowing stone tiers plus a small central spire.
    tiers = [(16.0, 4.0), (11.0, 4.0), (6.0, 4.0)]
    out = []
    y = cy + 6.0
    for w, h in tiers:
        out.append(_rect(cx - w / 2, y - h, w, h, fill=palette.old_wall, stroke=palette.ink, sw=0.7))
        y -= h
    out.append(_line(cx, y, cx, y - 7.0, stroke=palette.gold, sw=1.6))
    return out


# --- Pipeline ---------------------------------------------------------------


def _defs(palette: Palette) -> str:
    grad_stops = "".join(
        f'<stop offset="{offset * 100}%" stop-color="{color}"/>'
        for offset, color in palette.gradient_stops
    )
    wave = (
        '<pattern id="waves" patternUnits="userSpaceOnUse" width="24" height="8">'
        f'<path d="M0 4 Q6 0 12 4 T24 4" fill="none" stroke="{palette.mist_wall}" '
        'stroke-width="0.8" opacity="0.35"/>'
        "</pattern>"
    )
    paper = (
        '<filter id="paperGrain" x="0" y="0" width="100%" height="100%">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" result="n"/>'
        '<feColorMatrix type="matrix" values="0 0 0 0 0.2  0 0 0 0 0.15  0 0 0 0 0.1  0 0 0 0.08 0"/>'
        "</filter>"
    )
    return f"""<defs>
    <radialGradient id="mist" cx="50%" cy="50%" r="50%">{grad_stops}</radialGradient>
    {wave}
    {paper}
  </defs>"""


def _has_sea(layout: str) -> bool:
    return layout in {"island", "archipelago", "coast"}


def render_map(
    config: MapConfig | None = None,
    seed: int = 7,
    width: int | None = None,
    height: int | None = None,
    detail: float | None = None,
    coast_roughness: float | None = None,
    selected_id: str | None = None,
    *,
    embed_world: bool = False,
    interactive: bool | None = None,
) -> str:
    """Render a fantasy map as an SVG document string."""
    if config is None:
        config = MapConfig()

    # Allow legacy callers that pass locations/routes as plain dicts of tuples/lists
    if config.locations and not config.places:
        pass  # normalize handles it
    # Coerce legacy routes dict[str, list] if someone constructed MapConfig oddly
    raw_routes = config.routes
    coerced_routes: dict[str, Route] = {}
    for k, v in list(raw_routes.items()):
        if isinstance(v, Route):
            coerced_routes[k] = v
        elif isinstance(v, list):
            from fantasy_map_generator.config import _legacy_river_name

            kind = "river" if _legacy_river_name(k) else "road"
            coerced_routes[k] = Route(points=v, kind=kind)  # type: ignore[arg-type]
    if coerced_routes:
        config.routes = coerced_routes  # type: ignore[assignment]

    cfg = config.normalize()

    # Exact Valley of Mists parity renderer (sister mapgen port)
    if cfg.style_kit == "valley_parity":
        from fantasy_map_generator.valley import render_valley

        return render_valley(
            cfg,
            seed=seed,
            variant="settled",
            interactive=False if interactive is None else interactive,
            embed_world=embed_world,
            selected_id=selected_id,
        )
    canvas_width = width or cfg.canvas_width
    canvas_height = height or cfg.canvas_height
    if canvas_width <= 0 or canvas_height <= 0:
        raise ValueError("canvas dimensions must be positive")

    cfg.canvas_width = canvas_width
    cfg.canvas_height = canvas_height
    if detail is not None:
        cfg.detail = detail
    if coast_roughness is not None:
        cfg.coast_roughness = coast_roughness
    cfg.validate()

    rng = random.Random(seed)
    palette = cfg.palette
    detail_v = cfg.detail
    layers: list[str] = []

    # Background
    if _has_sea(cfg.layout):
        layers.append(
            f'<rect width="{canvas_width}" height="{canvas_height}" fill="{palette.water_deep}"/>'
        )
        layers.append(
            f'<rect width="{canvas_width}" height="{canvas_height}" fill="url(#waves)" opacity="0.9"/>'
        )
        # depth vignette
        layers.append(
            f'<ellipse cx="{canvas_width / 2:.1f}" cy="{canvas_height / 2:.1f}" '
            f'rx="{canvas_width * 0.48:.1f}" ry="{canvas_height * 0.45:.1f}" '
            f'fill="{palette.water}" opacity="0.25"/>'
        )
    else:
        bg = (
            palette.paper
            if cfg.style_kit in {"ink_parchment", "watercolor"}
            else palette.background
        )
        layers.append(f'<rect width="{canvas_width}" height="{canvas_height}" fill="{bg}"/>')
        if cfg.decor.paper_texture or cfg.style_kit == "ink_parchment":
            layers.append(
                f'<rect width="{canvas_width}" height="{canvas_height}" filter="url(#paperGrain)"/>'
            )

    # Default landmass for bowl if none provided
    landmass = list(cfg.landmass)
    if not landmass and cfg.layout == "bowl":
        landmass = [
            LandBody(
                kind="ellipse",
                center=(canvas_width / 2, canvas_height / 2),
                radii=(canvas_width * 0.35, canvas_height * 0.35),
                rough=0.04,
            )
        ]
    elif not landmass and cfg.layout == "interior":
        landmass = [
            LandBody(
                kind="ellipse",
                center=(canvas_width / 2, canvas_height / 2),
                radii=(canvas_width * 0.48, canvas_height * 0.46),
                rough=0.06,
            )
        ]

    # Land + coast
    land_polys: list[list[tuple[float, float]]] = []
    for body in landmass:
        pts = _land_points(rng, body, cfg.coast_roughness)
        land_polys.append(pts)
        fill = body.fill or palette.land
        if _has_sea(cfg.layout):
            # outer water band
            layers.append(_polygon(pts, fill=palette.water, opacity=0.55))
            # shrink-ish second stroke via duplicate with land fill
            layers.append(_polygon(pts, fill=fill, stroke=palette.ink, sw=1.4))
            layers.append(_path([*pts, pts[0]], stroke=palette.water_deep, sw=3.5, opacity=0.35))
        elif cfg.layout == "bowl":
            layers.append(
                _ellipse_fill(
                    body.center[0],
                    body.center[1],
                    body.radii[0],
                    body.radii[1],
                    fill="url(#mist)",
                    opacity=0.35,
                )
            )
        else:
            layers.append(_polygon(pts, fill=fill, stroke=palette.ink, sw=0.8, opacity=0.95))

    # Biomes
    for region in cfg.biome_regions:
        color = region.fill or _biome_color(palette, region.biome)
        if (region.left_border or region.right_border) and land_polys:
            territory = land_polys[0]
            if region.left_border:
                territory = _clip_polygon_by_border(territory, region.left_border, keep_right=True)
            if territory and region.right_border:
                territory = _clip_polygon_by_border(territory, region.right_border, keep_right=False)
            if len(territory) >= 3:
                layers.append(_polygon(territory, fill=color, opacity=0.92))
        elif region.clip_to_land and land_polys:
            ellipse_poly = _ellipse_polygon(region.center, region.radii)
            clipped = _clip_polygon_convex(land_polys[0], ellipse_poly)
            if len(clipped) >= 3:
                layers.append(
                    _polygon(clipped, fill=color, opacity=0.22 + 0.25 * region.density)
                )
        else:
            layers.append(
                _ellipse_fill(
                    region.center[0],
                    region.center[1],
                    region.radii[0],
                    region.radii[1],
                    fill=color,
                    opacity=0.22 + 0.25 * region.density,
                )
            )
        if region.biome == "desert":
            layers.extend(
                _dune_hatch(rng, region.center, region.radii, palette.road_dim, region.density)
            )
        elif region.biome == "swamp":
            layers.extend(
                _swamp_stipple(rng, region.center, region.radii, palette.swamp, region.density)
            )
        elif region.biome == "ice":
            # hatch
            cx, cy = region.center
            rx, ry = region.radii
            for i in range(int(8 * region.density)):
                y = cy - ry + (2 * ry) * (i + 1) / (8 * region.density + 1)
                layers.append(
                    _path(
                        [(cx - rx * 0.8, y), (cx + rx * 0.8, y + rng.uniform(-3, 3))],
                        stroke=palette.mist_wall,
                        sw=0.7,
                        opacity=0.3,
                    )
                )

    # Lakes (standalone inland water bodies, see WaterBody)
    for lake in cfg.lakes:
        layers.append(_lake(lake, palette))

    # Mountains
    mountain_ranges = dict(cfg.mountain_ranges)
    if not mountain_ranges and cfg.layout == "bowl":
        mountain_ranges = {
            "ring_0": MountainRange(
                kind="ring",
                center=(canvas_width / 2, canvas_height / 2),
                radii=(canvas_width * 0.35, canvas_height * 0.35),
                mouth_start_deg=92.0,
                mouth_end_deg=178.0,
                num_peaks=54,
            )
        }

    style = cfg.style_kit
    for mrid, mr in mountain_ranges.items():
        dens = mr.density * (0.5 + detail_v)
        elems: list[str] = []
        if mr.kind == "ring":
            center = mr.center or (canvas_width / 2, canvas_height / 2)
            radii = mr.radii or (canvas_width * 0.35, canvas_height * 0.35)
            elems.extend(
                _mountains_ring(
                    rng,
                    center,
                    radii,
                    palette.mountain,
                    palette.mountain_stroke,
                    mr.mouth_start_deg,
                    mr.mouth_end_deg,
                    mr.num_peaks,
                    dens,
                    mr.size or 50.0,
                    mr.rotation or 0.0,
                )
            )
        elif mr.kind == "stacked":
            center = mr.center or (canvas_width / 2, canvas_height / 2)
            radii = mr.radii or (120.0, 90.0)
            elems.extend(
                _mountains_stacked(
                    rng,
                    center,
                    radii,
                    palette.mountain,
                    palette.mountain_stroke,
                    levels=mr.levels,
                    density=dens,
                    size=mr.size or 50.0,
                    rotation=mr.rotation or 0.0,
                )
            )
        elif mr.kind == "single":
            center = mr.center or (canvas_width / 2, canvas_height / 2)
            size = mr.size or 50.0
            rotation = mr.rotation or 0.0
            elems.extend(
                _mountains_single(
                    center,
                    size,
                    rotation,
                    palette.mountain,
                    palette.mountain_stroke,
                )
            )
            if selected_id and selected_id == mrid:
                # Draw a circle around the selected single mountain
                elems.append(
                    _circle(center[0], center[1], size, stroke="#ffcc33", sw=2.0, opacity=0.45)
                )
        else:  # ridge
            ridge_style = "symbol" if style == "rpg_symbols" else "jagged"
            elems.extend(
                _mountains_ridge(
                    rng,
                    mr.points,
                    palette.mountain,
                    palette.mountain_stroke,
                    density=dens,
                    style=ridge_style,
                    size=mr.size or 50.0,
                )
            )
            if selected_id and selected_id == mrid:
                elems.append(
                    _path(mr.points, stroke="#ffcc33", sw=3.0, opacity=0.45)
                )
        layers.append(_group(elems, data_id=mrid, data_kind="mountain"))

    # Volcanoes (hand-placed, see MapConfig.volcanoes)
    for vx, vy in cfg.volcanoes:
        layers.extend(_decor_volcano(vx, vy))

    # Sleeping Gods sacred sites (hand-placed, see MapConfig.sacred_sites)
    for sx, sy, skind in cfg.sacred_sites:
        layers.extend(_decor_sacred_site(sx, sy, skind, palette))

    # Forests
    stands = list(cfg.forest_stands)
    if not stands and cfg.layout == "bowl":
        stands = [
            ForestStand(
                center=(canvas_width / 2, canvas_height / 2),
                radii=(canvas_width * 0.26, canvas_height * 0.26),
                tree_style="triangle",
                density=0.7,
                num_clumps=8,
            )
        ]
    for stand in stands:
        layers.extend(_forest_stand(rng, stand, palette.forest, detail_v))

    # Routes
    for rid, route in cfg.routes.items():
        route_id = route.id or rid
        elems: list[str] = []
        if len(route.points) >= 2:
            # wide invisible stroke for easier picking
            elems.append(
                _path(route.points, stroke="#ffffff", sw=14.0, opacity=0.001)
            )
        if route.kind == "river":
            elems.extend(
                _river(
                    rng,
                    route.points,
                    palette.water,
                    tributary_color=palette.water_tributary,
                    width_scale=0.7 + 0.6 * detail_v,
                )
            )
        else:
            elems.extend(
                _road_draw(route.points, palette.road, palette.road_dim, kind=route.kind)
            )
        if selected_id and selected_id == route_id and route.points:
            elems = [
                *elems,
                _path(route.points, stroke="#ffcc33", sw=5.0, opacity=0.45),
            ]
        layers.append(_group(elems, data_id=route_id, data_kind="route"))

    # Places
    for pid, place in cfg.places.items():
        layers.extend(
            _place_icon(
                rng,
                place,
                palette,
                selected=bool(selected_id and selected_id in {place.id, pid}),
            )
        )

    # Labels (with slight seed jitter for collision)
    for _pid, place in cfg.places.items():
        jx = rng.uniform(-4, 4) * (1.0 - detail_v * 0.3)
        jy = 18 + rng.uniform(0, 6)
        size = 20 if place.tier in {"capital", "city", "castle"} else 16
        layers.append(
            _text(
                place.x + jx,
                place.y + jy,
                place.name,
                size=size,
                anchor="middle",
                fill=palette.text_dim,
            )
        )

    # Region labels
    for region in cfg.biome_regions:
        if region.density >= 0.45 and region.name:
            layers.append(
                _text(
                    region.center[0],
                    region.center[1],
                    region.name.upper(),
                    size=15,
                    fill=palette.text_faint,
                    italic=True,
                    spacing=2.5,
                )
            )

    # Kingdom/political region labels (large, distinct from the biome labels above)
    for region_label in cfg.region_labels:
        layers.append(_region_label(region_label, palette))

    # Ships (hand-placed, see MapConfig.ships)
    for sx, sy in cfg.ships:
        layers.extend(_decor_ship(sx, sy, palette))

    # Title / cartouche
    if cfg.decor.cartouche:
        layers.extend(_decor_cartouche(canvas_width / 2, 40, cfg.name, palette))
    else:
        title_x = cfg.title_x if cfg.title_x is not None else (canvas_width / 2)
        title_y = cfg.title_y if cfg.title_y is not None else 30
        title_elems: list[str] = [
            # Invisible rect for easier picking
            _rect(title_x - 150, title_y - 20, 300, 40, fill="#ffffff", opacity=0.001),
            _text(
                title_x,
                title_y,
                cfg.name,
                size=cfg.title_font_size,
                anchor="middle",
                fill=palette.text,
                italic=cfg.title_italic,
                weight="bold" if cfg.title_bold else None,
            ),
        ]
        if selected_id and selected_id == "map_title":
            # Highlight selected title
            title_elems.append(
                _rect(title_x - 150, title_y - 20, 300, 40, stroke="#ffcc33", sw=2.0, opacity=0.45)
            )
        layers.append(_group(title_elems, data_id="map_title", data_kind="title"))

    # Decor
    if cfg.decor.border:
        layers.extend(_decor_border(canvas_width, canvas_height, palette))
    if cfg.decor.compass:
        layers.extend(_decor_compass(canvas_width - 70, canvas_height - 70, palette, scale=0.9))
    if cfg.decor.scale:
        layers.extend(_decor_scale(40, canvas_height - 40, palette))
    if cfg.legend_entries:
        lx, ly = cfg.legend_pos or (canvas_width - 150, canvas_height - 30 - 14 - 16 * len(cfg.legend_entries))
        layers.extend(_decor_legend(lx, ly, cfg.legend_entries, palette))

    svg_body = "\n  ".join(layers)

    head = f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" height="{canvas_height}" viewBox="0 0 {canvas_width} {canvas_height}">'
    if embed_world:
        world = {
            "format": "fmg-world/v1",
            "meta": {
                "renderer": cfg.style_kit,
                "seed": seed,
            },
            "config": cfg.to_dict(),
        }
        safe = json.dumps(world, separators=(",", ":")).replace("</", "<\\/")
        head += f'\n  <metadata id="fmg-world" data-format="fmg-world/v1">{safe}</metadata>'
    return f"""{head}
  {_defs(palette)}
  {svg_body}
</svg>"""


def write_map(
    output_path: Path,
    seed: int = 7,
    want_png: bool = True,
    config: MapConfig | None = None,
    detail: float | None = None,
    coast_roughness: float | None = None,
) -> None:
    """Write a generated map to SVG (and optionally PNG)."""
    if config is None:
        from fantasy_map_generator.worlds import VALLEY_CONFIG

        config = VALLEY_CONFIG

    output_path.parent.mkdir(parents=True, exist_ok=True)
    svg = render_map(config=config, seed=seed, detail=detail, coast_roughness=coast_roughness)

    svg_path = output_path.with_suffix(".svg")
    svg_path.write_text(svg, encoding="utf-8")
    print(f"wrote {svg_path}")

    if want_png:
        try:
            import cairosvg

            png_path = output_path.with_suffix(".png")
            png_path.write_bytes(cairosvg.svg2png(bytestring=svg.encode(), scale=2))
            print(f"wrote {png_path}")
        except ImportError:
            print("cairosvg not installed; skipping PNG export (SVG is valid)")
        except OSError as e:
            print(f"cairosvg export failed ({e}); SVG was written")
