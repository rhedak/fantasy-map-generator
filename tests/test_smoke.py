"""Smoke tests for the map generator.

Verify that basic functionality works: SVG renders, is valid, and is deterministic.
"""

import xml.etree.ElementTree as ET

from fantasy_map_generator.render import render_map


def test_svg_renders():
    """A map renders without crashing."""
    svg = render_map()
    assert svg
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")


def test_svg_is_valid_xml():
    """The generated SVG parses as valid XML."""
    svg = render_map()
    ET.fromstring(svg)


def test_deterministic_output():
    """Maps generated with the same seed are identical."""
    svg1 = render_map(seed=42)
    svg2 = render_map(seed=42)
    assert svg1 == svg2


def test_different_seeds_produce_different_maps():
    """Different seeds produce different SVG documents."""
    svg1 = render_map(seed=1)
    svg2 = render_map(seed=2)
    assert svg1 != svg2, "Mountains and terrain should vary based on seed"


def test_canvas_dimensions():
    """Canvas dimensions are reflected in the SVG."""
    svg = render_map(width=800, height=600)
    assert 'width="800"' in svg
    assert 'height="600"' in svg
    assert 'viewBox="0 0 800 600"' in svg
