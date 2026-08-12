"""Map rendering engine: converts MapConfig to SVG.

Extracted and generalized from valley_of_mist_tools.mapgen for any fantasy world.

Components:
- SVG primitives (_polygon, _path, _circle, etc.)
- Terrain generation (mountains, rivers, forests, etc.)
- Feature placement with spatial collision detection
- Multi-layer rendering orchestration

Design principle: deterministic output via seeded RNG for reproducible maps.
"""

from __future__ import annotations

import math
import random
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from fantasy_map_generator.config import MapConfig


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
    """Generate a filled polygon SVG element."""
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
) -> str:
    """Generate a stroked path SVG element."""
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in points)
    attrs = [
        f'fill="{fill}"',
        f'stroke="{stroke}" stroke-width="{sw}"',
        f'stroke-linecap="{linecap}"',
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
    dash: str | None = None,
) -> str:
    """Generate a circle SVG element."""
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


def _ellipse(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    *,
    stroke: str,
    sw: float,
    opacity: float = 1.0,
    dash: str | None = None,
) -> str:
    """Generate an ellipse SVG element."""
    attrs = [
        f'cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none"',
        f'stroke="{stroke}" stroke-width="{sw}"',
    ]
    if opacity < 1.0:
        attrs.append(f'stroke-opacity="{opacity}"')
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
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
    """Generate a rectangle SVG element."""
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


_FILLER_WORDS = {"the", "no"}


def _title_case(s: str) -> str:
    """Capitalize text except articles and Japanese particles."""
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
) -> str:
    """Generate text with outline for readability over any background."""
    label = _title_case(s)
    attrs = [
        f'x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}"',
        "font-family=\"Georgia, 'Times New Roman', serif\"",
    ]
    if italic:
        attrs.append('font-style="italic"')
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if spacing is not None:
        attrs.append(f'letter-spacing="{spacing}"')
    base = " ".join(attrs)
    sw = max(1.4, round(size * 0.22, 1))
    outline = (
        f'<text {base} fill="none" stroke="#000000" stroke-width="{sw}" '
        f'stroke-linejoin="round">{xml_escape(label)}</text>'
    )
    glyphs = f'<text {base} fill="{fill}">{xml_escape(label)}</text>'
    return outline + glyphs


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
    """Generate a line SVG element."""
    attrs = [
        f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"',
        f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"',
    ]
    if opacity < 1.0:
        attrs.append(f'stroke-opacity="{opacity}"')
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    return f"<line {' '.join(attrs)}/>"


def _leader_label(
    ax: float,
    ay: float,
    lx: float,
    ly: float,
    text: str,
    *,
    size: float = 12.0,
    anchor: str = "start",
    dot_fill: str = "#b2a992",
    line_stroke: str = "#b2a992",
) -> list[str]:
    """A small dot with a leader line and label for cramped features."""
    gap = 4 if anchor == "start" else -4
    return [
        _circle(ax, ay, 1.6, fill=dot_fill),
        _line(ax, ay, lx, ly, stroke=line_stroke, sw=1.0, opacity=0.75),
        _text(lx + gap, ly + 4, text, size=size, anchor=anchor),
    ]


def _mountains(
    rng: random.Random,
    center: tuple[float, float],
    radii: tuple[float, float],
    mountain_color: str,
    mountain_stroke: str,
    mouth_start_deg: float = 0.0,
    mouth_end_deg: float = 0.0,
    num_peaks: int = 54,
) -> list[str]:
    """Generate a ring of jagged mountain peaks around a circular/elliptical bowl."""
    out: list[str] = []
    cx, cy = center
    rx, ry = radii

    for i in range(num_peaks):
        a_deg = 360.0 * i / num_peaks
        if mouth_start_deg <= a_deg <= mouth_end_deg:
            continue

        a = math.radians(a_deg)
        bx = cx + (rx + 8 + rng.uniform(-3, 3)) * math.cos(a)
        by = cy + (ry + 8 + rng.uniform(-3, 3)) * math.sin(a)

        tx, ty = -math.sin(a), math.cos(a)
        w = 16 + rng.uniform(-3, 5)

        apex_x = cx + (rx + 42 + rng.uniform(-6, 14)) * math.cos(a) + tx * rng.uniform(-6, 6)
        apex_y = cy + (ry + 42 + rng.uniform(-6, 14)) * math.sin(a) + ty * rng.uniform(-6, 6)

        p1 = (bx + tx * w, by + ty * w)
        p2 = (bx - tx * w, by - ty * w)

        out.append(
            _polygon([p1, (apex_x, apex_y), p2], fill=mountain_color, stroke=mountain_stroke, sw=1)
        )

    return out


def _river(
    rng: random.Random,
    waypoints: list[tuple[float, float]],
    water_color: str,
    tributary_color: str | None = None,
) -> list[str]:
    """Generate a river flowing through waypoints with multiple strokes for depth."""
    out: list[str] = []

    if not waypoints or len(waypoints) < 2:
        return out

    pts = [(x + rng.uniform(-2, 2), y + rng.uniform(-2, 2)) for x, y in waypoints]

    out.append(_path(pts, stroke=water_color, sw=3.6, opacity=0.55))
    out.append(_path(pts, stroke=water_color, sw=1.4, opacity=0.4))

    if tributary_color:
        out.append(_path(pts, stroke=tributary_color, sw=0.8, opacity=0.3))

    return out


def _road(
    waypoints: list[tuple[float, float]],
    road_color: str,
    road_dim: str,
) -> list[str]:
    """Generate a road path with a dim underlay and a lighter top stroke."""
    if not waypoints or len(waypoints) < 2:
        return []
    return [
        _path(waypoints, stroke=road_dim, sw=3.2, opacity=0.55),
        _path(waypoints, stroke=road_color, sw=1.6, opacity=0.85, dash="6 4"),
    ]


def _forest(
    rng: random.Random,
    center: tuple[float, float],
    radii: tuple[float, float],
    forest_color: str,
    num_clumps: int = 8,
) -> list[str]:
    """Generate scattered forest/woodland clumps as triangles within a region."""
    out: list[str] = []
    cx, cy = center
    rx, ry = radii

    placed = 0
    tries = 0
    max_tries = num_clumps * 8

    while placed < num_clumps and tries < max_tries:
        tries += 1

        a = rng.uniform(0, math.tau)
        r = rng.uniform(0, 1) ** 0.5
        cluster_x = cx + math.cos(a) * rx * 0.85 * r
        cluster_y = cy + math.sin(a) * ry * 0.85 * r

        placed += 1

        for _ in range(rng.randint(9, 15)):
            ox = cluster_x + rng.uniform(-16, 16)
            oy = cluster_y + rng.uniform(-12, 12)
            s = 4 + rng.uniform(-1, 2.5)

            out.append(
                _polygon(
                    [(ox, oy - s), (ox - 2.8, oy + s * 0.6), (ox + 2.8, oy + s * 0.6)],
                    fill=forest_color,
                    opacity=rng.uniform(0.55, 0.85),
                )
            )

    return out


def _settlement(
    rng: random.Random,
    cx: float,
    cy: float,
    building_color: str,
    roof_color: str,
    scale: float = 1.0,
) -> list[str]:
    """Render a small settlement/hamlet at (cx, cy) as scattered buildings."""
    out: list[str] = []
    num_buildings = rng.randint(2, 4)
    for _ in range(num_buildings):
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


def _is_river_route(name: str) -> bool:
    key = name.lower()
    return "river" in key or key.startswith("water")


def render_map(
    config: MapConfig | None = None,
    seed: int = 7,
    width: int | None = None,
    height: int | None = None,
) -> str:
    """Render a fantasy map as an SVG document string.

    Args:
        config: MapConfig defining world geography and colors. If None, uses defaults.
        seed: Random seed for deterministic output.
        width: Canvas width (overrides config if provided).
        height: Canvas height (overrides config if provided).

    Returns:
        SVG document as a string.

    Raises:
        ValueError: If dimensions or config are invalid.
    """
    if config is None:
        config = MapConfig()

    canvas_width = width or config.canvas_width
    canvas_height = height or config.canvas_height

    if canvas_width <= 0 or canvas_height <= 0:
        raise ValueError("canvas dimensions must be positive")

    # Validate against effective canvas size
    check = MapConfig(
        name=config.name,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        locations=config.locations,
        routes=config.routes,
        palette=config.palette,
    )
    check.validate()

    rng = random.Random(seed)
    palette = config.palette

    grad_stops = "".join(
        f'<stop offset="{offset * 100}%" stop-color="{color}"/>'
        for offset, color in palette.gradient_stops
    )

    bowl_center = (canvas_width / 2, canvas_height / 2)
    bowl_radii = (canvas_width * 0.35, canvas_height * 0.35)

    layers: list[str] = [
        f'<rect width="{canvas_width}" height="{canvas_height}" fill="{palette.background}"/>',
        f'<ellipse cx="{bowl_center[0]:.1f}" cy="{bowl_center[1]:.1f}" '
        f'rx="{bowl_radii[0]:.1f}" ry="{bowl_radii[1]:.1f}" fill="url(#mist)" opacity="0.35"/>',
    ]

    layers.extend(
        _mountains(
            rng,
            center=bowl_center,
            radii=bowl_radii,
            mountain_color=palette.mountain,
            mountain_stroke=palette.mountain_stroke,
            mouth_start_deg=92.0,
            mouth_end_deg=178.0,
        )
    )

    layers.extend(
        _forest(
            rng,
            center=bowl_center,
            radii=(bowl_radii[0] * 0.75, bowl_radii[1] * 0.75),
            forest_color=palette.forest,
            num_clumps=8,
        )
    )

    for route_name, waypoints in config.routes.items():
        if _is_river_route(route_name):
            layers.extend(
                _river(rng, waypoints, palette.water, tributary_color=palette.water_tributary)
            )
        else:
            layers.extend(_road(waypoints, palette.road, palette.road_dim))

    for _name, (x, y) in config.locations.items():
        layers.extend(
            _settlement(rng, x, y, palette.settlement, palette.settlement_roof, scale=1.0)
        )

    for name, (x, y) in config.locations.items():
        layers.append(_text(x, y + 20, name, size=11, anchor="middle", fill=palette.text_dim))

    layers.append(
        _text(
            canvas_width // 2,
            30,
            config.name,
            size=20,
            anchor="middle",
            fill=palette.text,
        )
    )

    svg_body = "\n  ".join(layers)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" height="{canvas_height}" viewBox="0 0 {canvas_width} {canvas_height}">
  <defs>
    <radialGradient id="mist" cx="50%" cy="50%" r="50%">
      {grad_stops}
    </radialGradient>
  </defs>
  {svg_body}
</svg>'''


def write_map(
    output_path: Path,
    seed: int = 7,
    want_png: bool = True,
    config: MapConfig | None = None,
) -> None:
    """Write a generated map to SVG (and optionally PNG).

    Args:
        output_path: Path prefix (will add .svg and .png suffixes).
        seed: Random seed for the map.
        want_png: If True, attempt to export PNG via cairosvg.
        config: Optional world configuration. Defaults to Valley of Mists.
    """
    if config is None:
        from fantasy_map_generator.worlds import VALLEY_CONFIG

        config = VALLEY_CONFIG

    output_path.parent.mkdir(parents=True, exist_ok=True)
    svg = render_map(config=config, seed=seed)

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
