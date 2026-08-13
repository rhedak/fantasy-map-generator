"""Editor / world-document tests."""

import json
import sys
from pathlib import Path

from fantasy_map_generator.config import MapConfig, Place
from fantasy_map_generator.render import render_map
from fantasy_map_generator.worlds import VALLEY_CONFIG

WEB = Path(__file__).resolve().parents[1] / "web"
sys.path.insert(0, str(WEB))

import bridge  # noqa: E402


def test_place_data_id_in_svg():
    cfg = MapConfig(
        name="Edit",
        places={"p1": Place(400, 300, name="Alpha", tier="town", id="p1")},
    ).normalize()
    svg = render_map(config=cfg, seed=1)
    assert 'data-id="p1"' in svg
    assert 'data-kind="place"' in svg
    assert 'pointer-events="none"' in svg or "pointer-events='none'" in svg
    assert "Alpha" in svg


def test_selected_id_highlight():
    cfg = MapConfig(
        name="Edit",
        places={"p1": Place(400, 300, name="Alpha", tier="capital", id="p1")},
    )
    a = render_map(config=cfg, seed=1, selected_id=None)
    b = render_map(config=cfg, seed=1, selected_id="p1")
    assert a != b
    assert "#ffcc33" in b


def test_config_roundtrip_json():
    raw = VALLEY_CONFIG.to_dict()
    blob = json.dumps(raw)
    cfg = MapConfig.from_dict(json.loads(blob))
    assert cfg.name == VALLEY_CONFIG.name
    assert len(cfg.places) == len(VALLEY_CONFIG.normalize().places)
    svg = render_map(config=cfg, seed=42)
    assert "Kiriguchi" in svg or "Basin" in svg


def test_from_dict_accepts_legacy_locations():
    cfg = MapConfig.from_dict(
        {
            "name": "Legacy",
            "locations": {"Town A": [100, 200], "Town B": [300, 400]},
            "routes": {"river": [[100, 100], [200, 200], [300, 400]]},
        }
    )
    assert len(cfg.places) == 2
    assert any(p.name == "Town A" for p in cfg.places.values())
    assert any(r.kind == "river" for r in cfg.routes.values())


def test_api_render_with_config():
    cfg = MapConfig(
        name="API World",
        places={"x": Place(500, 350, name="Spot", tier="village", id="x")},
    ).to_dict()
    data = json.loads(
        bridge.bridge_render(json.dumps({"config": cfg, "seed": 3, "selected_id": "x"}))
    )
    assert data["svg"].startswith("<svg")
    assert 'data-id="x"' in data["svg"]
    assert data["config"]["places"]["x"]["name"] == "Spot"


def test_api_normalize():
    data = json.loads(
        bridge.bridge_normalize(
            json.dumps({"config": {"name": "N", "places": {"a": {"x": 10, "y": 20, "name": "A"}}}})
        )
    )
    assert "error" not in data
    places = data["config"]["places"]
    assert len(places) == 1


def test_api_download_json():
    data = json.loads(
        bridge.bridge_download(json.dumps({"preset": "valley", "seed": 1, "format": "json"}))
    )
    assert data["mime"] == "application/json"
    world = json.loads(data["data"])
    assert "places" in world


def test_mutate_place_coords():
    cfg = VALLEY_CONFIG.normalize()
    pid = next(iter(cfg.places))
    cfg.places[pid].x = 111.0
    cfg.places[pid].y = 222.0
    svg = render_map(config=cfg, seed=7)
    assert cfg.places[pid].name.split()[0] in svg or cfg.places[pid].name in svg
