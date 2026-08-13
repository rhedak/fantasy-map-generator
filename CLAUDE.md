# Fantasy Map Generator

A procedural fantasy map generator that produces parametric SVG maps of imaginary worlds. Python package (CLI + library), optional PNG export, and interactive Flask GUI.

## Status

- **Phase 1–2:** Done (scaffold, extraction, MapConfig/Palette, terrain generators).
- **Phase 3:** Template variation landed (layouts, style kits, biomes, tier icons, decor).
- **Phase 4:** Core GUI done (gallery, seed, detail/roughness, preview, download, share URLs).
- **Phase 5–6:** Advanced GUI and deeper docs later. See `docs/TODO.md`.

## Architecture

- **Package** (`src/fantasy_map_generator/`):
  - `render.py` — SVG primitives + terrain + `render_map` / `write_map`
  - `config.py` — `MapConfig`, `Palette`
  - `cli.py` — `--world`, `--seed`, `--out`, `--no-png`
  - `gui.py` — Flask app on `127.0.0.1:3000` by default
  - `worlds/` — presets + `WORLDS` registry (`valley`, `desert`, `tropical`, `arctic`, `autumn`)

- **Tests** (`tests/`): smoke, CLI, GUI API.

- **Docs** (`docs/`): PLAN, ARCHITECTURE, EXTRACTION_GUIDE.

## Design Principles

1. **Configuration-driven:** MapConfig holds geography and palette; renderer is world-agnostic.
2. **Deterministic:** Same seed → same map.
3. **Modular terrain:** Mountains, rivers, forests, settlements are independent functions.
4. **Routes convention:** keys containing `river` (or starting with `water`) → water; else roads.
5. **SVG-first:** PNG via cairosvg is optional/best-effort.

## Working Conventions

- Do NOT commit unless asked.
- Run `uv sync` once before the first test run.
- Keep one function per terrain type.
- GUI binds to localhost by default; use `FMG_HOST` / `FMG_PORT` / `FMG_DEBUG` to override.

## Building and Running

```bash
uv sync

python -m fantasy_map_generator --out map --seed 42 --world valley --no-png

pytest
ruff check src tests

python -m fantasy_map_generator.gui
# or: ./gui.sh start  → http://localhost:3000
```

## See Also

- Sister project: `../valley_of_mist_tools/mapgen.py`
- Related: `../anime-character-creator`
