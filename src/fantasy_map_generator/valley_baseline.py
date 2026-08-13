"""Regenerate the Valley golden baseline SVG.

Writes ``tests/baselines/valley_settled.svg`` from the vendored sister
mapgen renderer using the locked ``settled`` variant and seed 7.

Usage:
    python -m fantasy_map_generator.valley_baseline
"""

from __future__ import annotations

from pathlib import Path

from fantasy_map_generator.valley.mapgen import render_map

BASELINE = Path(__file__).resolve().parents[2] / "tests" / "baselines" / "valley_settled.svg"


def main() -> int:
    svg = render_map("settled", seed=7, interactive=False)
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE.write_text(svg, encoding="utf-8")
    print(f"wrote {BASELINE} ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
