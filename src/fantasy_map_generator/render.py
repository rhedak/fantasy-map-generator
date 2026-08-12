"""Map rendering engine: converts MapConfig to SVG.

This module will contain the refactored SVG generation primitives extracted
from valley_of_mist_tools.mapgen, generalized for any fantasy world.

Planned components:
- SVG helper functions (_polygon, _path, _circle, etc.)
- Terrain generation (mountains, rivers, forests, etc.)
- Feature placement with spatial collision detection
- Multi-layer rendering orchestration

Design principle: deterministic output via seeded RNG for reproducible maps.
"""

import math
import random
from pathlib import Path
from typing import Optional
from xml.sax.saxutils import escape as xml_escape


def render_map(seed: int = 7, width: int = 1000, height: int = 700) -> str:
    """Render a fantasy map as an SVG document string.

    Args:
        seed: Random seed for deterministic output.
        width: Canvas width in units.
        height: Canvas height in units.

    Returns:
        SVG document as a string.

    Raises:
        ValueError: If width or height are invalid.
    """
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")

    rng = random.Random(seed)

    # TODO: Implement full rendering pipeline
    # For now, return a minimal valid SVG
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <radialGradient id="mist" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#f3f6fa"/>
      <stop offset="50%" stop-color="#96a6ba"/>
      <stop offset="100%" stop-color="#3a4254"/>
    </radialGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="#202634"/>
  <ellipse cx="{width//2}" cy="{height//2}" rx="{width*0.39}" ry="{height*0.38}" fill="url(#mist)"/>
  <text x="{width//2}" y="50" text-anchor="middle" font-size="24" fill="#e8e2d2">Fantasy Map Generator</text>
</svg>'''
    return svg


def write_map(output_path: Path, seed: int = 7, want_png: bool = True) -> None:
    """Write a generated map to SVG (and optionally PNG).

    Args:
        output_path: Path prefix (will add .svg and .png suffixes).
        seed: Random seed for the map.
        want_png: If True, attempt to export PNG via cairosvg.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    svg = render_map(seed=seed)

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
