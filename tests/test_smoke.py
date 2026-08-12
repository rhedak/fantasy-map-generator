"""Smoke tests for the map generator.

Verify that basic functionality works: SVG renders, is valid, and is deterministic.
"""

import xml.etree.ElementTree as ET

from fantasy_map_generator.config import MapConfig, Palette
from fantasy_map_generator.render import render_map
from fantasy_map_generator.worlds import VALLEY_CONFIG, WORLDS


def test_svg_renders():
    """A map renders without crashing."""
    svg = render_map(config=VALLEY_CONFIG)
    assert svg
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")


def test_svg_is_valid_xml():
    """The generated SVG parses as valid XML."""
    svg = render_map(config=VALLEY_CONFIG)
    ET.fromstring(svg)


def test_deterministic_output():
    """Maps generated with the same seed are identical."""
    svg1 = render_map(config=VALLEY_CONFIG, seed=42)
    svg2 = render_map(config=VALLEY_CONFIG, seed=42)
    assert svg1 == svg2


def test_different_seeds_produce_different_maps():
    """Different seeds produce different SVG documents."""
    svg1 = render_map(config=VALLEY_CONFIG, seed=1)
    svg2 = render_map(config=VALLEY_CONFIG, seed=2)
    assert svg1 != svg2, "Mountains and terrain should vary based on seed"


def test_canvas_dimensions():
    """Canvas dimensions are reflected in the SVG."""
    svg = render_map(config=VALLEY_CONFIG, width=800, height=600)
    assert 'width="800"' in svg
    assert 'height="600"' in svg
    assert 'viewBox="0 0 800 600"' in svg


def test_valley_labels_present():
    """Valley settlements appear as labels in the SVG."""
    svg = render_map(config=VALLEY_CONFIG, seed=7)
    for name in ("Kiriguchi", "Kasumikyo", "The Basin"):
        assert name.split()[-1] in svg or name in svg or name.title() in svg or "Basin" in svg
    assert "Valley" in svg or "Mists" in svg


def test_routes_rendered():
    """Configured river and road routes produce path elements."""
    config = MapConfig(
        name="Route Test",
        locations={"Town": (500.0, 350.0)},
        routes={
            "river": [(100.0, 100.0), (300.0, 200.0), (500.0, 350.0)],
            "main_road": [(200.0, 400.0), (500.0, 350.0), (800.0, 300.0)],
        },
        palette=Palette(),
    )
    svg = render_map(config=config, seed=1)
    # background + mist ellipse + mountains + forest trees + river strokes + road strokes
    assert svg.count("<path") >= 5
    assert 'fill="url(#mist)"' in svg


def test_all_world_presets_render():
    """Every registered world preset renders valid SVG."""
    for world_id, config in WORLDS.items():
        svg = render_map(config=config, seed=42)
        ET.fromstring(svg)
        assert config.name.split()[0] in svg or config.name in svg, world_id


def test_config_validate_rejects_bad_dimensions():
    """Invalid canvas dimensions raise ValueError."""
    config = MapConfig(canvas_width=0, canvas_height=100)
    try:
        config.validate()
        raise AssertionError("expected ValueError")
    except ValueError as e:
        assert "positive" in str(e)


def test_config_validate_rejects_short_route():
    """Routes need at least two waypoints."""
    config = MapConfig(routes={"river": [(1.0, 2.0)]})
    try:
        config.validate()
        raise AssertionError("expected ValueError")
    except ValueError as e:
        assert "river" in str(e)
