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

### Launch the Interactive Web Tool

The GUI is a static web app: it runs the real Python in your browser via
[Pyodide](https://pyodide.org/), with no server needed. The same
`out/web-stage/` layout is what GitHub Pages deploys, so local and deployed
behaviour can't drift.

```bash
./web-stage.sh --serve   # assembles out/web-stage/, serves http://localhost:8000
```

First load downloads the Pyodide runtime (~10 MB, cached by the browser after
that).

The GUI features:
- **Map gallery:** Presets (Valley, Desert, Tropical, Arctic, Autumn, Random)
- **Seed slider:** Explore variations (0–10000), debounced live preview
- **Export:** Download SVG, JSON, or PNG (rasterized in the browser off a canvas)
- **Shareable URLs:** `?preset=valley&seed=42`

### Web Tool (GitHub Pages)

The interactive GUI is also published as a static site, at
`https://rhedak.github.io/fantasy-map-generator/`. GitHub Pages serves only
static files, so the visitor's own browser runs the real Python (the same
package, byte for byte) via [Pyodide](https://pyodide.org/), and SVG/JSON
export happens entirely in the tab. PNG export rasterizes in the browser off a
`<canvas>` (cairosvg is server-only and not needed).

To deploy from `main` (push automatically triggers
`.github/workflows/pages.yml`), set this **once** in the repo's web UI:

> Settings → Pages → Build and deployment → Source = **GitHub Actions**

Local preview of the exact deployed layout:

```bash
./web-stage.sh --serve   # assembles out/web-stage/, serves http://localhost:8000
```

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
- `web/` — static interactive web tool (browser runs the package via Pyodide)
- `worlds/` — preset world definitions + `WORLDS` registry

**World presets (distinct archetypes):**

| id | Archetype | Notes |
|----|-----------|--------|
| `valley` | Mist bowl | Story locations, ring peaks, cool mist |
| `desert` | Arid corridor | Broken ridge, dunes, oases, parchment decor |
| `tropical` | Archipelago | Sea + waves, multi-island, stacked peaks |
| `arctic` | Ice coast / fjord | Ice shelf polygon, cold sea, sparse conifers |
| `autumn` | Inland kingdom | Forest stands, edge range, cartouche/border |

CLI knobs: `--detail 0-1`, `--coast-roughness 0-1`. GUI exposes the same + shareable URL params.

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
- *(none for the web tool — it runs in the browser via Pyodide)*

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
