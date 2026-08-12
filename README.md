# Fantasy Map Generator

Procedurally generates fantasy world maps as parametric SVG, with an interactive web GUI. No image files, no AI—purely mathematical rendering of geography, settlements, and terrain.

```
MapConfig (world data)
    ↓
Python package (deterministic SVG generation)
    ↓
PNG export (optional, via cairosvg)
    ↓
Web GUI (interactive parameter tuning)
```

## Quick Start

### Installation

```bash
# Install the package and dependencies
uv sync
```

### Generate a Map

```bash
# From the command line
python -m fantasy_map_generator --out my_map.svg --seed 42

# From Python
from fantasy_map_generator.render import render_map
svg = render_map(seed=42)
print(svg[:100])  # First 100 chars of SVG
```

### Launch the Interactive GUI

**Option 1: Using the control script (recommended)**
```bash
./gui.sh start
# Opens http://localhost:5000
```

**Option 2: Direct Python**
```bash
python -m fantasy_map_generator.gui
```

**Manage the server:**
```bash
./gui.sh status    # Check if server is running
./gui.sh stop      # Stop the server
./gui.sh restart   # Restart the server
./gui.sh logs      # Follow server logs
```

The GUI features:
- **Map gallery:** Choose from presets (Valley of Mists, Random world)
- **Seed slider:** Adjust seed to explore variations (0–10000)
- **Live preview:** Real-time SVG rendering as you adjust parameters
- **Export buttons:** Download as SVG or PNG (if cairosvg installed)
- **Shareable URLs:** Copy links like `?preset=valley&seed=42` to share maps

## Features

- **Procedural generation:** Mountains, rivers, forests, settlements, roads—all from a seed.
- **Deterministic:** Same seed produces the same map, every time.
- **Configuration-driven:** Define worlds in Python; render without touching code.
- **SVG-native:** Pure text output, scalable to any resolution.
- **Optional PNG:** Export to PNG via cairosvg (best-effort).
- **Interactive GUI:** Parameter sliders and preview (in development).

## Architecture

**Core Components:**

- `render.py`: SVG generation engine with primitives and terrain algorithms.
- `config.py`: MapConfig dataclass defining world geography and palette.
- `cli.py`: Command-line interface.
- `gui.py`: Flask web app (under development).

**World Definitions:**

- `worlds/valley.py`: Extracted from the Valley of Mists webnovel.
- More example worlds planned (desert region, archipelago, temperate kingdom, etc.).

## Development Phases

| Phase | Status | Effort | Milestone |
|-------|--------|--------|-----------|
| 1. Scaffolding | ✅ Done | 4h | Project structure, CLI, tests |
| 2. Extraction & Refactor | ✅ Done | ~10h | SVG primitives, Palette, MapConfig, terrain generators (mountains, river, forest, settlements) |
| 3. Terrain Algorithms | 📋 Next | 20–30h | Enhanced settlement placement, road networks, water features, decorative elements |
| 4. Web GUI | ✅ Core | ~8h | Gallery, seed slider, live preview, download, URL sharing (expandable) |
| 5. Advanced GUI | 📋 Later | 20–30h | Location editor, terrain density sliders, palette picker, custom world builder |
| 6. Documentation | 📋 Ongoing | 12–18h | Tutorials, API docs, example worlds, world-building guide |

See `docs/PLAN.md` for detailed roadmap and decision points.

## Usage Examples

### Generate a Valley Map

```python
from fantasy_map_generator.render import render_map
from worlds.valley import VALLEY_CONFIG

svg = render_map(config=VALLEY_CONFIG, seed=7)
with open("valley.svg", "w") as f:
    f.write(svg)
```

### Create a Custom World

```python
from fantasy_map_generator.config import MapConfig, Palette

my_world = MapConfig(
    name="The Shattered Isles",
    canvas_width=1200,
    canvas_height=800,
    locations={
        "port_city": (600, 400),
        "mountain_hold": (200, 300),
        "forest_settlement": (800, 500),
    },
    routes={
        "trade_route": [(600, 400), (200, 300), (800, 500)],
        "river": [(100, 200), (500, 400), (900, 600)],
    },
    palette=Palette(
        background="#1a3a4a",
        mountain="#4a6a8a",
        water="#4a9aff",
        forest="#2d6b3d",
    ),
)

from fantasy_map_generator.render import render_map
svg = render_map(config=my_world, seed=123)
```

### Export to PNG

```bash
# Requires cairosvg: pip install cairosvg
python -m fantasy_map_generator --out my_map.svg
# Creates my_map.svg and my_map.png (2x scale)
```

## Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_smoke.py::test_svg_renders -v

# Test coverage
pytest --cov=src/fantasy_map_generator
```

## Architecture & Design

See `docs/ARCHITECTURE.md` for:
- System overview and data flow
- Component design (MapConfig, Palette, terrain generators)
- Extensibility patterns (adding new terrain types, worlds, features)
- Testing strategy
- Performance considerations

## Extraction from Valley of Mists

The codebase builds on `../valley_of_mist_tools/mapgen.py`, extracting and generalizing its proven map generation algorithms.

**For detailed extraction steps:** See `docs/EXTRACTION_GUIDE.md`

**For code review of the Valley source:** See `mapgen_review.md` in the parent directory

## Dependencies

**Core:** None (pure stdlib).

**Optional:**
- `cairosvg` (PNG export; fails gracefully if missing)
- `flask` (GUI; fails gracefully if missing)

**Development:**
- `pytest`, `ruff` (testing and linting)
- `pdoc` (API documentation)

## Performance

Typical map generation times on modern hardware:

- **SVG generation:** ~100ms
- **PNG export (cairosvg):** ~500ms–1s

Interactive GUI targets 200ms per update (responsive to slider input).

## Roadmap

**Phase 2 (Next):** Extract and generalize the Valley code into MapConfig and terrain algorithms.

**Phase 3:** Enhanced settlement placement, road network routing, water simulation.

**Phase 4:** Web GUI with interactive parameter controls and real-time preview.

**Phase 5:** Tutorials, example worlds, API documentation.

## License

MIT. See LICENSE file.

## See Also

- **Companion project:** `../anime-character-creator` (similar architecture: Python package + GUI + SVG generation)
- **Source material:** `../valley_of_mist/` (the webnovel being illustrated)

## Contributing

This project is in early development. Architecture and APIs may change.

When working on this project:
- **Do not commit** unless asked (use `git status` to track work).
- **Run tests** before submitting changes (`pytest`).
- **Follow the PLAN:** Phases are sequential; check Phase status before starting new work.
- **Update docs:** Every new feature or design decision should be documented.

## Questions?

See `CLAUDE.md` for project context and working conventions.
