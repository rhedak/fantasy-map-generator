"""Staged static-site tests.

./web-stage.sh assembles out/web-stage/ — the exact directory GitHub Pages
serves. These tests re-run the staging script and verify the layout web/
index.html expects (bridge.py, the package copy, and the fetch manifest), and
that the staged copy behaves like the installed package when importable, the
way Pyodide will make it.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "out" / "web-stage"
PKG = "fantasy_map_generator"


def run_stage() -> None:
    subprocess.run([str(ROOT / "web-stage.sh")], cwd=ROOT, check=True, capture_output=True, text=True)


@pytest.fixture(scope="module")
def staged():
    run_stage()
    return STAGE


def test_layout(staged):
    assert (staged / "index.html").is_file()
    assert (staged / "app.js").is_file()
    assert (staged / "style.css").is_file()
    assert (staged / "bridge.py").is_file()
    assert (staged / "src" / PKG).is_dir()
    assert (staged / "src" / PKG / "config.py").is_file()
    assert (staged / "src" / PKG / "valley" / "mapgen.py").is_file()
    assert (staged / "src" / PKG / "worlds" / "__init__.py").is_file()
    assert not any(p.suffix == ".pyc" for p in (staged / "src" / PKG).rglob("*"))


def test_no_server_endpoints_in_page(staged):
    html = (staged / "index.html").read_text()
    js = (staged / "app.js").read_text()
    for text in (html, js):
        assert "/api/" not in text
        assert "fetch('/" not in text


def test_index_has_no_inline_style_or_script(staged):
    """index.html/app.js/style.css split (later session, matching
    ../anime-character-creator's own layout): index.html should link the
    other two, not carry their content inline again."""
    html = (staged / "index.html").read_text()
    assert "<style>" not in html
    assert '<script src="app.js">' in html
    assert '<link rel="stylesheet" href="style.css">' in html
    # The only inline <script> left should be nothing but whitespace between
    # its tags (i.e. no <script>...code...</script>, only <script src=...>).
    import re

    for block in re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S):
        assert block.strip() == ""


def test_manifest_matches_staged_files(staged):
    manifest = json.loads((staged / "src" / f"{PKG}-files.json").read_text())
    staged_files = sorted(
        p.relative_to(staged / "src" / PKG).as_posix()
        for p in (staged / "src" / PKG).rglob("*.py")
        if p.is_file()
    )
    assert manifest == staged_files
    assert manifest


def test_staged_package_works_like_installed(staged):
    import importlib.util

    sys.path.insert(0, str(staged / "src"))
    try:
        import fantasy_map_generator.render as render_mod
        from fantasy_map_generator.worlds import WORLDS

        svg = render_mod.render_map(config=WORLDS["valley"], seed=7)
        assert svg.startswith("<svg")

        spec = importlib.util.spec_from_file_location("staged_bridge", staged / "bridge.py")
        staged_bridge = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(staged_bridge)
        data = json.loads(staged_bridge.bridge_render(json.dumps({"preset": "valley", "seed": 7})))
        assert data["seed"] == 7
        assert data["svg"].startswith("<svg")
    finally:
        sys.path.remove(str(staged / "src"))
