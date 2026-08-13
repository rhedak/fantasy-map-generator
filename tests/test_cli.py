"""CLI smoke tests."""

from pathlib import Path

from fantasy_map_generator.cli import main
from fantasy_map_generator.config import MapConfig
from fantasy_map_generator.render import render_map, write_map
from fantasy_map_generator.worlds import DESERT_CONFIG, VALLEY_CONFIG


def test_write_map_uses_config(tmp_path: Path):
    out = tmp_path / "desert"
    write_map(out, seed=3, want_png=False, config=DESERT_CONFIG)
    svg = out.with_suffix(".svg").read_text(encoding="utf-8")
    assert "Desert" in svg or "Oasis" in svg or "Temple" in svg


def test_write_map_default_is_valley(tmp_path: Path):
    out = tmp_path / "default"
    write_map(out, seed=7, want_png=False)
    svg = out.with_suffix(".svg").read_text(encoding="utf-8")
    assert "Valley" in svg or "Mists" in svg or "Kiriguchi" in svg or "Basin" in svg
    empty = len(render_map(config=MapConfig(name="Empty"), seed=7))
    assert len(svg) > empty * 0.5


def test_cli_main(tmp_path: Path, monkeypatch):
    out = tmp_path / "cli_map"
    monkeypatch.setattr(
        "sys.argv",
        [
            "fantasy-map-generator",
            "--out",
            str(out),
            "--seed",
            "9",
            "--world",
            "arctic",
            "--no-png",
            "--detail",
            "0.4",
        ],
    )
    assert main() is None
    svg = out.with_suffix(".svg").read_text(encoding="utf-8")
    assert "Arctic" in svg or "Ice" in svg or "Frost" in svg


def test_valley_config_identity():
    assert VALLEY_CONFIG.name == "Valley of Mists"
    assert VALLEY_CONFIG.layout == "bowl"
    assert VALLEY_CONFIG.style_kit == "valley_parity"
    assert "kasumikyo" in VALLEY_CONFIG.places
    assert "capital_road" in VALLEY_CONFIG.routes


def test_cli_valley_matches_golden(tmp_path: Path):
    baseline = Path(__file__).parent / "baselines" / "valley_settled.svg"
    assert baseline.is_file()
    out = tmp_path / "valley_cli"
    write_map(out, seed=7, want_png=False, config=VALLEY_CONFIG)
    svg = out.with_suffix(".svg").read_text(encoding="utf-8")
    assert svg == baseline.read_text(encoding="utf-8")
