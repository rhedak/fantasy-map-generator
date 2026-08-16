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


# New selectable kinds (later session, exposing the continent map's own new
# elements to the GUI): biome region, region label, lake, ship, volcano,
# sacred site. Each gets the same data-id/data-kind + bridge CRUD coverage
# place/route/mountain already had.


def test_new_kinds_have_data_id_in_svg():
    from fantasy_map_generator.config import BiomeRegion, RegionLabel, WaterBody

    cfg = MapConfig(
        name="Edit",
        biome_regions=[BiomeRegion("Region", "plain", (400, 300), (80, 60), 0.5, id="b1")],
        region_labels=[RegionLabel("Label", center=(400, 200), id="rl1")],
        lakes=[WaterBody(center=(300, 300), radii=(20, 15), id="lk1")],
        ships=[(100.0, 100.0)],
        volcanoes=[(150.0, 150.0)],
        sacred_sites=[(200.0, 200.0, "kurgan")],
    ).normalize()
    svg = render_map(config=cfg, seed=1)
    assert 'data-id="b1" data-kind="biome"' in svg
    assert 'data-id="rl1" data-kind="region_label"' in svg
    assert 'data-id="lk1" data-kind="lake"' in svg
    assert 'data-id="ship_0" data-kind="ship"' in svg
    assert 'data-id="volcano_0" data-kind="volcano"' in svg
    assert 'data-id="sacred_0" data-kind="sacred_site"' in svg


def test_new_kinds_selected_highlight():
    from fantasy_map_generator.config import RegionLabel

    cfg = MapConfig(name="Edit", region_labels=[RegionLabel("Label", center=(400, 200), id="rl1")])
    a = render_map(config=cfg, seed=1, selected_id=None)
    b = render_map(config=cfg, seed=1, selected_id="rl1")
    assert a != b
    assert "#ffcc33" in b


def test_gui_flow_select_highlight_for_every_new_kind():
    """End-to-end through bridge.render_json (the exact call renderMap() in
    index.html makes): load a preset, client-side-append one of each new
    kind (mirrors placeLandmarkAt), re-render with it selected, and check
    both the data-id/data-kind pick target and the #ffcc33 highlight ring
    are present. This is the check that would have caught render.py's lake
    branch missing its highlight entirely (copy-pasted the other five,
    forgot the highlight block) -- data-id alone isn't enough coverage."""
    out1 = json.loads(bridge.render_json(json.dumps({"preset": "continent", "seed": 7})))
    assert "error" not in out1
    cfg = out1["config"]

    cfg["biome_regions"].append(
        {"name": "", "biome": "plain", "center": [900, 300], "radii": [40, 30], "density": 0.5,
         "fill": None, "left_border": None, "right_border": None, "clip_to_land": False, "id": "biome_test"}
    )
    cfg["region_labels"].append({"name": "Test", "center": [900, 320], "font_size": 20, "rotation": 0, "id": "rl_test"})
    cfg["lakes"].append({"center": [900, 340], "radii": [10, 8], "fill": None, "id": "lake_test"})
    cfg["ships"].append([900, 360])
    ship_id = f"ship_{len(cfg['ships']) - 1}"
    cfg["volcanoes"].append([900, 380])
    volcano_id = f"volcano_{len(cfg['volcanoes']) - 1}"
    cfg["sacred_sites"].append([900, 400, "temple"])
    sacred_id = f"sacred_{len(cfg['sacred_sites']) - 1}"

    for selected_id, kind in [
        ("biome_test", "biome"),
        ("rl_test", "region_label"),
        ("lake_test", "lake"),
        (ship_id, "ship"),
        (volcano_id, "volcano"),
        (sacred_id, "sacred_site"),
    ]:
        out = json.loads(bridge.render_json(json.dumps({"config": cfg, "seed": 7, "selected_id": selected_id})))
        assert "error" not in out, (selected_id, out)
        svg = out["svg"]
        assert f'data-id="{selected_id}" data-kind="{kind}"' in svg, f"{selected_id} not pickable"
        assert "#ffcc33" in svg, f"{selected_id} has no selection highlight"


def test_api_biome_region_crud():
    added = json.loads(
        bridge.add_biome_region(
            json.dumps({"preset": "valley", "seed": 1, "biome": "forest", "center": [400, 300], "radii": [70, 50]})
        )
    )
    assert "error" not in added
    regions = added["config"]["biome_regions"]
    assert len(regions) >= 1
    rid = regions[-1]["id"]

    updated = json.loads(
        bridge.update_biome_region(
            json.dumps({"config": added["config"], "id": rid, "density": 0.9, "fill": "#123456"})
        )
    )
    assert "error" not in updated
    region = next(r for r in updated["config"]["biome_regions"] if r["id"] == rid)
    assert region["density"] == 0.9
    assert region["fill"] == "#123456"

    deleted = json.loads(bridge.delete_biome_region(json.dumps({"config": updated["config"], "id": rid})))
    assert "error" not in deleted
    assert all(r["id"] != rid for r in deleted["config"]["biome_regions"])


def test_api_region_label_crud():
    added = json.loads(
        bridge.add_region_label(json.dumps({"preset": "valley", "seed": 1, "name": "New Land", "center": [400, 300]}))
    )
    assert "error" not in added
    lid = added["config"]["region_labels"][-1]["id"]

    updated = json.loads(
        bridge.update_region_label(json.dumps({"config": added["config"], "id": lid, "font_size": 40.0}))
    )
    label = next(r for r in updated["config"]["region_labels"] if r["id"] == lid)
    assert label["font_size"] == 40.0

    deleted = json.loads(bridge.delete_region_label(json.dumps({"config": updated["config"], "id": lid})))
    assert all(r["id"] != lid for r in deleted["config"]["region_labels"])


def test_api_lake_crud():
    added = json.loads(bridge.add_lake(json.dumps({"preset": "valley", "seed": 1, "center": [400, 300], "radii": [10, 8]})))
    assert "error" not in added
    wid = added["config"]["lakes"][-1]["id"]

    updated = json.loads(bridge.update_lake(json.dumps({"config": added["config"], "id": wid, "center": [410, 310]})))
    lake = next(w for w in updated["config"]["lakes"] if w["id"] == wid)
    assert lake["center"] == [410.0, 310.0]

    deleted = json.loads(bridge.delete_lake(json.dumps({"config": updated["config"], "id": wid})))
    assert all(w["id"] != wid for w in deleted["config"]["lakes"])


def test_api_ship_volcano_sacred_site_crud():
    added = json.loads(bridge.add_ship(json.dumps({"preset": "valley", "seed": 1, "center": [100, 100]})))
    assert added["config"]["ships"][-1] == [100.0, 100.0]
    moved = json.loads(
        bridge.update_ship(json.dumps({"config": added["config"], "id": "ship_0", "center": [120, 130]}))
    )
    assert moved["config"]["ships"][0] == [120.0, 130.0]
    deleted = json.loads(bridge.delete_ship(json.dumps({"config": moved["config"], "id": "ship_0"})))
    assert deleted["config"]["ships"] == []

    addedv = json.loads(bridge.add_volcano(json.dumps({"preset": "valley", "seed": 1, "center": [50, 60]})))
    assert addedv["config"]["volcanoes"][-1] == [50.0, 60.0]
    deletedv = json.loads(bridge.delete_volcano(json.dumps({"config": addedv["config"], "id": "volcano_0"})))
    assert deletedv["config"]["volcanoes"] == []

    addeds = json.loads(
        bridge.add_sacred_site(json.dumps({"preset": "valley", "seed": 1, "center": [70, 80], "kind": "temple"}))
    )
    assert addeds["config"]["sacred_sites"][-1] == [70.0, 80.0, "temple"]
    updateds = json.loads(
        bridge.update_sacred_site(json.dumps({"config": addeds["config"], "id": "sacred_0", "kind": "kurgan"}))
    )
    assert updateds["config"]["sacred_sites"][0][2] == "kurgan"
    deleteds = json.loads(bridge.delete_sacred_site(json.dumps({"config": updateds["config"], "id": "sacred_0"})))
    assert deleteds["config"]["sacred_sites"] == []
