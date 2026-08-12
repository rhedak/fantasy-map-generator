"""Command-line interface for fantasy map generation.

Usage:
    fantasy-map-generator --out map.svg --seed 42
    fantasy-map-generator --help
"""

import argparse
import sys
from pathlib import Path

from fantasy_map_generator.render import write_map


def main() -> None:
    """Parse arguments and generate a map."""
    ap = argparse.ArgumentParser(
        description="Generate a procedural fantasy world map as SVG"
    )
    ap.add_argument(
        "--out",
        default="map",
        help="output path prefix (default: map; produces map.svg and map.png)",
    )
    ap.add_argument(
        "--seed",
        type=int,
        default=7,
        help="random seed for deterministic output (default: 7)",
    )
    ap.add_argument(
        "--no-png",
        action="store_true",
        help="skip PNG export (only write SVG)",
    )
    args = ap.parse_args()

    try:
        write_map(Path(args.out), seed=args.seed, want_png=not args.no_png)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
