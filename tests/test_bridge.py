"""Pyodide bridge tests.

web/bridge.py is the Flask-free core the static GitHub Pages site runs inside
the visitor's browser via Pyodide. It must stay pure stdlib Python and behave
like the /api/* endpoints, so it is exercised directly under CPython here.
"""

import json
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parents[1] / "web"
sys.path.insert(0, str(WEB))

import bridge  # noqa: E402

PAYLOAD = json.dumps({"preset": "valley", "seed": 42})


def _json(fn, payload=PAYLOAD):
    return json.loads(fn(payload))


def _presets():
    return json.loads(bridge.bridge_presets())


def test_presets():
    data = _presets()
    ids = {p["id"] for p in data}
    assert "valley" in ids
    assert "random" in ids
    valley = next(p for p in data if p["id"] == "valley")
    assert valley["preview"].startswith("<svg")
    assert "config" in valley


def test_render():
    data = _json(bridge.bridge_render)
    assert data["seed"] == 42
    assert data["svg"].startswith("<svg")
    assert "Kiriguchi" in data["svg"] or "Basin" in data["svg"]


def test_render_with_explicit_config():
    cfg = next(p for p in _presets() if p["id"] == "desert")["config"]
    data = _json(bridge.bridge_render, json.dumps({"config": cfg, "seed": 7}))
    assert data["svg"].startswith("<svg")


def test_render_unknown_preset():
    data = _json(bridge.bridge_render, json.dumps({"preset": "nope", "seed": 1}))
    assert "error" in data


def test_download_svg():
    data = _json(bridge.bridge_download, json.dumps({"preset": "desert", "seed": 7, "format": "svg"}))
    assert data["mime"] == "image/svg+xml"
    assert data["filename"] == "map-7.svg"
    assert data["data"].startswith("<svg")


def test_download_json():
    data = _json(bridge.bridge_download, json.dumps({"preset": "valley", "seed": 3, "format": "json"}))
    assert data["mime"] == "application/json"
    assert data["filename"] == "world-3.json"
    world = json.loads(data["data"])
    assert world["name"] == "Valley of Mists"


def test_download_png_unavailable():
    data = _json(bridge.bridge_download, json.dumps({"preset": "valley", "seed": 1, "format": "png"}))
    assert "error" in data


def test_normalize():
    cfg = next(p for p in _presets() if p["id"] == "valley")["config"]
    data = _json(bridge.bridge_normalize, json.dumps({"config": cfg}))
    assert "error" not in data
    assert data["config"]["name"] == "Valley of Mists"


def test_from_svg_roundtrip():
    svg = _json(bridge.bridge_download, json.dumps({"preset": "valley", "seed": 42, "format": "svg"}))["data"]
    data = _json(bridge.bridge_from_svg, json.dumps({"svg": svg}))
    assert "error" not in data
    assert data["config"]["name"] == "Valley of Mists"
    assert data["seed"] == 42


def test_from_svg_missing_metadata():
    data = _json(bridge.bridge_from_svg, json.dumps({"svg": "<svg xmlns='x'></svg>"}))
    assert "error" in data
