# Fantasy Map Generator

A procedural fantasy map generator that produces parametric SVG maps of imaginary worlds. The project includes a Python package (with PNG export support) and a planned interactive web GUI.

## Status

**Phase 1 (Scaffolding):** Project structure initialized, CLI and stub GUI in place.

**Phase 2 (Extraction & Refactoring):** Planned. Extract and generalize the map generation code from `../valley_of_mist_tools/mapgen.py`.

**Phase 3 (Features):** Terrain generation, settlement placement, water features, labels, etc.

**Phase 4 (GUI):** Web interface for interactive map parameter tuning.

## Architecture

- **Python Package** (`src/fantasy_map_generator/`): Core rendering engine, deterministic via seeded RNG.
  - `render.py`: SVG generation (will be extracted from Valley of Mists).
  - `config.py`: MapConfig data model for world geography and palette.
  - `cli.py`: Command-line interface.
  - `gui.py`: Flask web app (under development).

- **Tests** (`tests/`): Regression and smoke tests.

- **Docs** (`docs/`): Design documents, architecture notes, world-building templates.

## Design Principles

1. **Configuration-driven:** MapConfig objects define geography and palette; rendering code is world-agnostic.
2. **Deterministic:** Same seed always produces the same map (good for testing and iteration).
3. **Modular terrain:** Mountains, rivers, forests, settlements are independent, reusable functions.
4. **Spatial collision detection:** Features respect constraints (roads, mountains, water) to avoid overlap.
5. **SVG-first:** No image files; purely parametric drawing. PNG export is optional (via cairosvg).

## Extraction Plan

The codebase will be seeded from `../valley_of_mist_tools/mapgen.py` in this phase:

1. **SVG primitives** (lines 284–410 in mapgen.py): Extract `_polygon`, `_path`, `_circle`, `_text`, etc. as-is; these are reusable.
2. **Terrain generators** (lines 425–723): Extract and parameterize `_mountains`, `_river`, `_forest`, `_mist_wall_band`, etc.
3. **Palette abstraction**: Generalize the color constants (lines 39–59) into a `Palette` dataclass.
4. **Geography model**: Generalize the LAYOUT section (lines 73–279) into MapConfig.
5. **Refactor render_map()**: Break into layer-based methods; make seed and canvas size configurable.

See `docs/extraction_plan.md` for detailed steps and phase-wise milestones.

## Working Conventions

- Do NOT commit unless asked.
- When testing, run `uv sync` once before the first test run.
- SVG rendering is the deliverable; PNG is optional and always best-effort (cairosvg may not be available).
- Keep the SVG modular: one function per terrain type makes it easy to add or disable features.

## Building and Running

```bash
# Install dependencies
uv sync

# Generate a map from the command line
python -m fantasy_map_generator --out map.svg --seed 42

# Run tests
pytest

# Start the web GUI (under development)
python -m fantasy_map_generator.gui
```

## See Also

- **Sister project:** `../valley_of_mist_tools/mapgen.py` (the source being extracted).
- **Related:** `../anime-character-creator` (similar architecture: Python package + optional GUI + SVG generation).
