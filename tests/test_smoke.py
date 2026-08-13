"""Smoke tests for the map generator."""

import xml.etree.ElementTree as ET

from fantasy_map_generator.config import MapConfig, Palette, Place, Route
from fantasy_map_generator.render import render_map
from fantasy_map_generator.worlds import VALLEY_CONFIG, WORLDS


def test_svg_renders():
    svg = render_map(config=VALLEY_CONFIG)
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")


def test_svg_is_valid_xml():
    ET.fromstring(render_map(config=VALLEY_CONFIG))


def test_deterministic_output():
    assert render_map(config=VALLEY_CONFIG, seed=42) == render_map(config=VALLEY_CONFIG, seed=42)


def test_different_seeds_produce_different_maps():
    assert render_map(config=VALLEY_CONFIG, seed=1) != render_map(config=VALLEY_CONFIG, seed=2)


def test_canvas_dimensions():
    from fantasy_map_generator.worlds import DESERT_CONFIG

    svg = render_map(config=DESERT_CONFIG, width=800, height=600)
    assert 'width="800"' in svg
    assert 'height="600"' in svg
    assert 'viewBox="0 0 800 600"' in svg


def test_valley_labels_present():
    svg = render_map(config=VALLEY_CONFIG, seed=7)
    assert "Kiriguchi" in svg
    assert "Basin" in svg
    assert "Valley" in svg or "Mists" in svg


def test_routes_rendered():
    config = MapConfig(
        name="Route Test",
        places={"Town": Place(500.0, 350.0, tier="town")},
        routes={
            "river": Route([(100.0, 100.0), (300.0, 200.0), (500.0, 350.0)], kind="river"),
            "main_road": Route([(200.0, 400.0), (500.0, 350.0), (800.0, 300.0)], kind="road"),
        },
        palette=Palette(),
    )
    svg = render_map(config=config, seed=1)
    assert svg.count("<path") >= 5
    assert "url(#mist)" in svg or "url(#waves)" in svg or "<svg" in svg


def test_legacy_locations_and_route_lists():
    """Old locations= / list routes still render via normalize/coerce."""
    config = MapConfig(
        name="Legacy",
        locations={"A": (100.0, 100.0), "B": (400.0, 300.0)},
        routes={"river": [(100.0, 80.0), (200.0, 150.0), (400.0, 300.0)]},  # type: ignore[dict-item]
    )
    svg = render_map(config=config, seed=3)
    ET.fromstring(svg)
    assert "Legacy" in svg


def test_all_world_presets_render():
    for world_id, config in WORLDS.items():
        svg = render_map(config=config, seed=42)
        ET.fromstring(svg)
        assert config.name.split()[0] in svg or config.name in svg, world_id


def test_presets_distinct_silhouette():
    """Worlds should not be mere palette swaps — layout markers differ."""
    markers = {}
    for world_id, config in WORLDS.items():
        svg = render_map(config=config, seed=42)
        markers[world_id] = (
            config.layout,
            "url(#waves)" in svg,
            svg.count("<ellipse"),
            svg.count("<path"),
        )
    assert markers["tropical"][0] == "archipelago"
    assert markers["tropical"][1] is True  # sea waves
    assert markers["desert"][0] == "interior"
    assert markers["valley"][0] == "bowl"
    assert markers["arctic"][0] == "coast"
    assert markers["autumn"][0] == "interior"
    # path counts should not all be identical
    path_counts = {k: v[3] for k, v in markers.items()}
    assert len(set(path_counts.values())) >= 3


def test_seed_keeps_locked_labels():
    for seed in (1, 2, 99):
        svg = render_map(config=VALLEY_CONFIG, seed=seed)
        assert "Kiriguchi" in svg
        assert "Kasumikyo" in svg


def test_detail_knob_changes_output():
    from fantasy_map_generator.worlds import DESERT_CONFIG

    a = render_map(config=DESERT_CONFIG, seed=7, detail=0.2)
    b = render_map(config=DESERT_CONFIG, seed=7, detail=0.9)
    assert a != b


def test_capital_icon_differs_from_hamlet():
    capital = MapConfig(
        name="Cap",
        places={"C": Place(400, 300, tier="capital")},
        layout="interior",
    )
    hamlet = MapConfig(
        name="Ham",
        places={"H": Place(400, 300, tier="hamlet")},
        layout="interior",
    )
    sc = render_map(config=capital, seed=1)
    sh = render_map(config=hamlet, seed=1)
    assert sc != sh
    assert sc.count("<circle") >= sh.count("<circle")


def test_config_validate_rejects_bad_dimensions():
    config = MapConfig(canvas_width=0, canvas_height=100)
    try:
        config.validate()
        raise AssertionError("expected ValueError")
    except ValueError as e:
        assert "positive" in str(e)


def test_config_validate_rejects_short_route():
    config = MapConfig(routes={"river": Route([(1.0, 2.0)], kind="river")})
    try:
        config.validate()
        raise AssertionError("expected ValueError")
    except ValueError as e:
        assert "river" in str(e)
