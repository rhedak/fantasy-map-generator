"""GUI API smoke tests."""

import pytest

flask = pytest.importorskip("flask")

from fantasy_map_generator.gui import create_app  # noqa: E402


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_presets_endpoint(client):
    res = client.get("/api/presets")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    ids = {p["id"] for p in data}
    assert "valley" in ids
    assert "random" in ids
    valley = next(p for p in data if p["id"] == "valley")
    assert valley["preview"] and valley["preview"].startswith("<svg")


def test_render_endpoint(client):
    res = client.post("/api/render", json={"preset": "valley", "seed": 42})
    assert res.status_code == 200
    data = res.get_json()
    assert data["seed"] == 42
    assert data["svg"].startswith("<svg")
    assert "Kiriguchi" in data["svg"] or "Basin" in data["svg"]


def test_render_unknown_preset(client):
    res = client.post("/api/render", json={"preset": "nope", "seed": 1})
    assert res.status_code == 400


def test_download_svg(client):
    res = client.post(
        "/api/download",
        json={"preset": "desert", "seed": 7, "format": "svg"},
    )
    assert res.status_code == 200
    assert res.mimetype == "image/svg+xml"
    assert res.data.startswith(b"<svg")


def test_index_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Fantasy Map Generator" in res.data
