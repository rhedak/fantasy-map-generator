"""Editor / world-document tests."""

import json

import pytest

from fantasy_map_generator.config import MapConfig, Place
from fantasy_map_generator.render import render_map
from fantasy_map_generator.worlds import VALLEY_CONFIG

flask = pytest.importorskip("flask")


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
    from fantasy_map_generator.gui import create_app

    app = create_app()
    client = app.test_client()
    cfg = MapConfig(
        name="API World",
        places={"x": Place(500, 350, name="Spot", tier="village", id="x")},
    ).to_dict()
    res = client.post("/api/render", json={"config": cfg, "seed": 3, "selected_id": "x"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["svg"].startswith("<svg")
    assert 'data-id="x"' in data["svg"]
    assert data["config"]["places"]["x"]["name"] == "Spot"


def test_api_normalize():
    from fantasy_map_generator.gui import create_app

    client = create_app().test_client()
    res = client.post(
        "/api/world/normalize",
        json={"config": {"name": "N", "places": {"a": {"x": 10, "y": 20, "name": "A"}}}},
    )
    assert res.status_code == 200
    places = res.get_json()["config"]["places"]
    assert len(places) == 1


def test_api_download_json():
    from fantasy_map_generator.gui import create_app

    client = create_app().test_client()
    res = client.post(
        "/api/download",
        json={"preset": "valley", "seed": 1, "format": "json"},
    )
    assert res.status_code == 200
    assert res.mimetype == "application/json"
    data = json.loads(res.data)
    assert "places" in data


def test_mutate_place_coords():
    cfg = VALLEY_CONFIG.normalize()
    pid = next(iter(cfg.places))
    cfg.places[pid].x = 111.0
    cfg.places[pid].y = 222.0
    svg = render_map(config=cfg, seed=7)
    assert cfg.places[pid].name.split()[0] in svg or cfg.places[pid].name in svg
