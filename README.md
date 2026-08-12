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
# From the command line (default world: valley)
python -m fantasy_map_generator --out my_map --seed 42 --no-png

# Choose a world preset
python -m fantasy_map_generator --world desert --seed 7 --out desert_map --no-png

# From Python
from fantasy_map_generator.render import render_map
from fantasy_map_generator.worlds import VALLEY_CONFIG

svg = render_map(config=VALLEY_CONFIG, seed=42)
print(svg[:100])
```

### Launch the Interactive GUI

**Option 1: Using the control script (recommended)**
```bash
./gui.sh start
# Opens http://localhost:3000
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

Optional env vars: `FMG_HOST` (default `127.0.0.1`), `FMG_PORT` (default `3000`), `FMG_DEBUG=1`.

The GUI features:
- **Map gallery:** Presets (Valley, Desert, Tropical, Arctic, Autumn, Random)
- **Seed slider:** Explore variations (0–10000), debounced live preview
- **Export:** Download SVG or PNG (if cairosvg installed)
- **Shareable URLs:** `?preset=valley&seed=42`

## Features

- **Procedural generation:** Mountains, rivers, forests, settlements, roads—from a seed.
- **Deterministic:** Same seed produces the same map every time.
- **Configuration-driven:** Define worlds in Python; render without touching core code.
- **SVG-native:** Pure text output, scalable to any resolution.
- **Optional PNG:** Export via cairosvg (best-effort).
- **Interactive GUI:** Gallery, seed control, preview, download.

## Architecture

**Core components:**

- `render.py` — SVG primitives and terrain generators
- `config.py` — `MapConfig` and `Palette` dataclasses
- `cli.py` — command-line interface (`--world`, `--seed`, `--out`)
- `gui.py` — Flask web app
- `worlds/` — preset world definitions + `WORLDS` registry

**World presets:** `valley`, `desert`, `tropical`, `arctic`, `autumn`

## Development Phases

| Phase | Status | Milestone |
|-------|--------|-----------|
| 1. Scaffolding | ✅ Done | Project structure, CLI, tests |
| 2. Extraction & Refactor | ✅ Done | Primitives, Palette, MapConfig, terrain generators |
| 3. Terrain Algorithms | 🔄 In progress | Routes wired; richer settlement/water still open |
| 4. Web GUI | ✅ Core | Gallery, seed slider, preview, download, URL sharing |
| 5. Advanced GUI | 📋 Later | Location editor, density sliders, palette picker |
| 6. Documentation | 📋 Ongoing | Tutorials, API docs, world-building guide |

See `docs/PLAN.md` for the detailed roadmap.

## Usage Examples

### Generate a Valley Map

```python
from fantasy_map_generator.render import render_map
from fantasy_map_generator.worlds import VALLEY_CONFIG

svg = render_map(config=VALLEY_CONFIG, seed=7)
with open("valley.svg", "w") as f:
    f.write(svg)
```

### Create a Custom World

```python
from fantasy_map_generator.config import MapConfig, Palette
from fantasy_map_generator.render import render_map

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

svg = render_map(config=my_world, seed=123)
```

Route keys containing `river` (or starting with `water`) are drawn as water; all other routes are roads.

### Export to PNG

```bash
# Requires cairosvg (included in dev extras via uv sync)
python -m fantasy_map_generator --out my_map --seed 42
# Creates my_map.svg and my_map.png (2x scale)
```

## Testing

```bash
pytest
pytest tests/test_smoke.py -v
ruff check src tests
```

## Dependencies

**Core:** None (pure stdlib).

**Optional:**
- `cairosvg` (PNG export)
- `flask` (GUI)

**Development:** `pytest`, `ruff`, `pdoc`

## License

MIT. See LICENSE file.

## See Also

- **Companion project:** `../anime-character-creator`
- **Source material:** `../valley_of_mist/` (webnovel), `../valley_of_mist_tools/mapgen.py`

## Contributing

Early development; APIs may change.

- Do not commit unless asked.
- Run `pytest` and `ruff check src tests` before submitting.
- Follow `docs/PLAN.md` phase order when adding large features.
