"""Valley of Mists exact-parity and round-trip tests."""

from __future__ import annotations

import json
from pathlib import Path

from fantasy_map_generator.config import MapConfig, Place
from fantasy_map_generator.render import render_map
from fantasy_map_generator.valley import (
    default_valley_config,
    extract_world_from_svg,
    render_valley,
)
from fantasy_map_generator.valley.mapgen import render_map as valley_raw
from fantasy_map_generator.worlds import VALLEY_CONFIG, WORLDS

BASELINE = Path(__file__).parent / "baselines" / "valley_settled.svg"


def test_valley_config_is_parity_kit():
    assert VALLEY_CONFIG.style_kit == "valley_parity"
    assert WORLDS["valley"].style_kit == "valley_parity"


def test_raw_valley_matches_baseline():
    assert BASELINE.is_file(), "missing golden baseline; generate tests/baselines/valley_settled.svg"
    golden = BASELINE.read_text(encoding="utf-8")
    actual = valley_raw("settled", seed=7, interactive=False)
    assert actual == golden


def test_render_map_dispatches_to_valley():
    svg = render_map(config=VALLEY_CONFIG, seed=7, interactive=False)
    golden = BASELINE.read_text(encoding="utf-8")
    assert svg == golden


def test_valley_has_canonical_features():
    svg = render_map(config=VALLEY_CONFIG, seed=7, interactive=True)
    for needle in (
        "Kiriguchi",
        "Kiri no Sato",
        "Valley Inn",
        "Kasumikyo",
        "Basin",
        "Mist Wall",
        "Palace",
        'data-id="kiriguchi"',
        'data-id="kasumikyo"',
    ):
        assert needle in svg, needle


def test_place_override_moves_village():
    cfg = default_valley_config()
    cfg.places["kiriguchi"].x = 200.0
    cfg.places["kiriguchi"].y = 580.0
    svg = render_valley(cfg, seed=7, interactive=True)
    # village buildings near new x
    assert 'x="200' in svg or "200.0" in svg


def test_roundtrip_svg_metadata():
    cfg = default_valley_config()
    cfg.places["kiri_no_sato"].x = 280.0
    svg = render_map(config=cfg, seed=7, embed_world=True, interactive=True)
    assert "fmg-world" in svg
    world = extract_world_from_svg(svg)
    assert world is not None
    assert world["meta"]["renderer"] == "valley_parity"
    restored = MapConfig.from_dict(world["config"])
    assert abs(restored.places["kiri_no_sato"].x - 280.0) < 0.01
    svg2 = render_map(config=restored, seed=7, interactive=True)
    # both should place sato at override
    assert "280.0" in svg2 or 'x="280' in svg2


def test_roundtrip_json_dict():
    cfg = default_valley_config()
    blob = json.dumps({"format": "fmg-world/v1", "meta": {"seed": 7}, "config": cfg.to_dict()})
    data = json.loads(blob)
    back = MapConfig.from_dict(data["config"])
    assert back.style_kit == "valley_parity"
    assert "kiriguchi" in back.places


def test_api_from_svg(client=None):
    import json
    import sys
    from pathlib import Path

    web = Path(__file__).resolve().parents[1] / "web"
    sys.path.insert(0, str(web))
    try:
        import bridge
    finally:
        sys.path.remove(str(web))
    svg = render_map(config=VALLEY_CONFIG, seed=7, embed_world=True, interactive=True)
    body = json.loads(bridge.bridge_from_svg(json.dumps({"svg": svg})))
    assert "error" not in body
    assert body["config"]["style_kit"] == "valley_parity"
    assert "kiriguchi" in body["config"]["places"]


def test_generic_embed_world_roundtrip():
    from fantasy_map_generator.worlds import DESERT_CONFIG
    from fantasy_map_generator.config import MapConfig

    svg = render_map(config=DESERT_CONFIG, seed=7, embed_world=True)
    world = extract_world_from_svg(svg)
    assert world is not None
    assert world["meta"]["renderer"] == "ink_parchment"
    assert world["meta"]["seed"] == 7
    restored = MapConfig.from_dict(world["config"])
    svg2 = render_map(config=restored, seed=7, embed_world=True)
    assert svg == svg2
    assert "fmg-world" in svg and "<\\/" not in svg



def test_extra_editor_place_composites():
    cfg = default_valley_config()
    cfg.places["camp_1"] = Place(400, 400, name="Scout Camp", tier="hamlet", id="camp_1")
    svg = render_valley(cfg, seed=7, interactive=True)
    assert 'data-id="camp_1"' in svg
    assert "Scout Camp" in svg or "Scout" in svg


def test_valley_palette_override_changes_colors():
    cfg = default_valley_config()
    svg_default = render_valley(cfg, seed=7, interactive=False)
    cfg.palette.background = "#ff00aa"
    cfg.palette.mist_wall = "#00ff88"
    svg = render_valley(cfg, seed=7, interactive=False)
    assert "#ff00aa" in svg
    assert "#00ff88" in svg
    assert "#202634" not in svg
    assert svg_default == BASELINE.read_text(encoding="utf-8")
