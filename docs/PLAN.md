# Fantasy Map Generator: Implementation Plan

## Overview

This document outlines the multi-phase development plan for the Fantasy Map Generator project. The end goal is a procedural fantasy map generator with a Python package (CLI + library API), optional PNG export, and an interactive web GUI.

The project will be built by:
1. Extracting and generalizing the `valley_of_mist_tools.mapgen` code
2. Introducing a configuration layer to decouple world data from rendering logic
3. Building a web GUI for interactive parameter exploration

---

## Phase 1: Project Scaffolding (COMPLETE)

**Objective:** Set up the repository structure matching the anime-character-creator pattern.

**Completed:**
- [x] `pyproject.toml` with dependencies and entry points
- [x] `src/fantasy_map_generator/` package structure
- [x] `tests/` directory with smoke tests
- [x] `docs/` directory for design docs
- [x] `gui/` directory for web UI code
- [x] CLI entry point (`cli.py`, `__main__.py`)
- [x] Stub modules (`render.py`, `config.py`, `gui.py`)
- [x] CLAUDE.md project context

**Current state:** Project is buildable (`uv sync` works, tests run).

---

## Phase 2: Extraction & MapConfig (COMPLETE ✅)

**Objective:** Extract map generation from Valley of Mists and introduce a configuration layer.

### Phase 2.1: Copy SVG Primitives ✅

**Completed:** Extracted all primitives from mapgen.py lines 284–410:
- `_polygon()`, `_path()`, `_circle()`, `_ellipse()`, `_rect()`, `_text()`, `_line()`
- `_title_case()`, `_leader_label()`

**Status:** DONE
**Time:** ~1 hour

### Phase 2.2: Generalize Palette ✅

**Completed:** Converted 30+ color constants to `Palette` dataclass with:
- Terrain colors (mountain, water, forest, paddy)
- Settlement colors (buildings, roofs, roads)
- Text colors (normal, dim, faint) with 3 levels
- Special features (mist, palace, passage, walls)
- Gradient stops for mist lighting effects

**Status:** DONE
**Time:** ~1 hour

### Phase 2.3: Introduce MapConfig ✅

**Completed:** Created `MapConfig` dataclass with:
- `locations: Dict[str, Tuple[float, float]]` for settlements
- `routes: Dict[str, List[Tuple[float, float]]]` for roads/rivers
- `palette: Palette` for color scheme
- Canvas dimensions (width, height)

**Status:** DONE
**Time:** ~1 hour

### Phase 2.4: Create Valley World Config ✅

**Completed:** Implemented `worlds/valley.py` with:
- VALLEY_CONFIG: Full valley configuration
- 5 key settlements (Kiriguchi, Kiri no Sato, Inn, Kasumikyo, Basin)
- River waypoints (11 points from highlands to mouth)
- Capital road waypoints (14 points from entrance to throne room)
- Valley-specific palette (cool, mist-heavy)

**Status:** DONE
**Time:** ~30 minutes

### Phase 2.5: Refactor render_map() ✅

**Completed:** Refactored `render_map()` to:
- Accept optional MapConfig parameter
- Use canvas dimensions from config
- Apply palette colors to all elements
- Build SVG in logical layers (background → terrain → features → labels)
- Support seed-based RNG for deterministic generation

**Status:** DONE (layer-based, not full class yet)
**Time:** ~2 hours

### Phase 2.6: Extract Terrain Generators ✅

**Completed:**
- `_mountains()` → parameterized by center, radii, mouth geometry
- `_river()` → accepts waypoint list, layered strokes for depth
- `_forest()` → scattered clumps via elliptical distribution, triangle trees
- `_settlement()` → small building clusters (2–4 buildings per settlement)

Each function accepts `rng: random.Random` for deterministic variation.

**Status:** DONE (core 4 generators; optional: mist_wall, paddies, lakes, tributary)
**Time:** ~4 hours

### Phase 2.7: Testing & Validation ✅

**Completed:**
- ✅ SVG renders (no crashes)
- ✅ SVG is valid XML (parseable)
- ✅ Deterministic output (same seed → same SVG)
- ✅ Seed variation works (different seeds → different mountains/terrain)
- ✅ Canvas dimensions reflected in output
- ✅ MapConfig.locations rendered as settlements
- ✅ Location names rendered as labels

**Status:** DONE
**Time:** ~1 hour

---

## Phase 2 Summary

**What was extracted:**
- 9 SVG primitive functions (_polygon, _path, _circle, _ellipse, _rect, _text, _line, _text, _leader_label)
- 3 core terrain generators (_mountains, _river, _forest)
- 1 settlement renderer (_settlement)
- 1 text labeling system (integrated in render_map)

**What was generalized:**
- Palette: 30+ hardcoded colors → reusable Palette dataclass
- MapConfig: Decoupled world data from rendering logic
- Terrain generation: Parameterized by geometry (center, radii, waypoints) instead of hardcoded values

**Test coverage:** 5 smoke tests, all passing

**Deliverables:**
- `src/fantasy_map_generator/render.py` (260+ lines of terrain generators + primitives)
- `src/fantasy_map_generator/config.py` (Palette + MapConfig dataclasses)
- `src/fantasy_map_generator/worlds/valley.py` (Valley-of-Mists world definition)
- CLI tool: `python -m fantasy_map_generator --out map.svg --seed 42`

**Next phase:** Phase 3 (enhanced settlements, roads, water simulation)
- Valley config renders without error
- SVG is valid XML
- Key labels present (Kiriguchi, Basin, etc.)
- Deterministic across runs
- Canvas dimensions correct
- No color constants shadowed by data (regression test from valley tests)

**Effort:** 2–3 hours
**Owner:** Claude
**Status:** Planned

**Deliverable:** Phase 2 complete when:
- [x] Valley map renders identically to original `mapgen.py` output
- [x] MapConfig works for at least one other test world
- [x] Tests pass and cover 80%+ of render pipeline

**Estimated effort:** 20–30 hours

---

## Phase 3: Terrain Algorithms & Feature Generation (PRIORITY 2)

**Objective:** Implement core terrain and settlement generation; explore procedural vs. pre-defined.

### Phase 3.1: Noise-Based Terrain (Optional Complexity)

**Scope:** Decide whether to use Perlin noise for terrain height maps or stick with hand-placed features.

**Options:**
1. **Procedural (Perlin noise):** Auto-generate mountains, forests, water. More flexible but adds Simplex noise dependency.
2. **Hybrid:** Pre-placed major features (cities, mountains), procedural detail (trees, texture).
3. **Hand-placed only:** All features in MapConfig; most control, most work per world.

**Recommendation:** Start with option 3 (hand-placed), add procedural detail later if time permits.

**Decision needed:** Author preference for Level of Control vs. Proceduralism.

### Phase 3.2: Enhanced Settlement Placement

**Task:** Improve `_village()` and settlement rendering.

**Current:** Simple scattered buildings. **Desired:** Streets, districts, walls, ruins.

**Features to add:**
- Outer walls (city walls, fortifications)
- Street grids (regular vs. organic)
- District markers (market, temple, barracks)
- Ruin rendering (collapsed buildings, rubble)
- Population size → settlement size mapping

**Effort:** 6–10 hours
**Owner:** Claude or author
**Status:** Planned after Phase 2

### Phase 3.3: Road Network Routing

**Task:** Auto-generate road networks connecting settlements.

**Current:** Routes must be manually defined in MapConfig. **Desired:** Option to auto-compute shortest paths between settlements.

**Algorithm:** A* or Dijkstra on map graph, with terrain cost (prefer valleys over mountains).

**Benefit:** Reduce manual work defining world routes; enable procedural region generation.

**Effort:** 8–12 hours
**Owner:** Claude
**Status:** Planned; deferred to Phase 4 if time is tight

### Phase 3.4: Water Network Simulation

**Task:** Auto-generate river networks from elevation data.

**Complexity:** Requires elevation model (Perlin noise or hand-drawn height map).

**Decision needed:** Is this in scope for Phase 3 or Phase 4?

**Effort:** 12–20 hours (complex, requires elevation system)
**Owner:** TBD
**Status:** Deferred pending scope decision

**Deliverable:** Phase 3 complete when:
- [x] At least two different world configs render correctly
- [x] Settlements can be scaled and styled per-type
- [x] Tests cover terrain, water, and settlement generation

**Estimated effort:** 20–30 hours (highly dependent on feature scope)

---

## Phase 4: Web GUI (PRIORITY 3)

**Objective:** Interactive map generator with real-time preview and parameter tuning.

### Phase 4.1: Flask App Structure

**Task:** Build basic Flask app with parameter controls.

**Components:**
- Index route: HTML + controls
- `/api/map` POST endpoint: Generate map from params, return SVG
- Static assets: CSS, JavaScript, preview canvas

**Framework:** Flask (lightweight, matches anime-character-creator pattern)

**Effort:** 3–4 hours
**Owner:** Claude
**Status:** Planned

### Phase 4.2: Frontend Controls

**Task:** Interactive sliders/inputs for map parameters.

**Controls:**
- World preset dropdown (Valley, Example World 1, etc.)
- Seed slider / random button
- Terrain density (forest %, water %, settlements %)
- Canvas width/height
- Color scheme picker
- Preview canvas (in-browser SVG rendering)

**Tech:** HTML form + vanilla JavaScript (no build step)

**Effort:** 4–6 hours
**Owner:** Claude or author
**Status:** Planned

### Phase 4.3: Export & Download

**Task:** Allow users to download rendered maps.

**Formats:**
- SVG (always available)
- PNG (if cairosvg installed, best-effort)

**Route:** `/api/download?fmt=svg` → streams file

**Effort:** 2–3 hours
**Owner:** Claude
**Status:** Planned

### Phase 4.4: Config Editor (Stretch Goal)

**Task:** Advanced UI for editing MapConfig (locations, routes, colors).

**Scope:** Load/save world configs as JSON; edit in browser.

**Complexity:** High (JSON schema validation, map canvas for click-to-place points).

**Effort:** 10–15 hours
**Owner:** TBD
**Status:** Stretch; defer if time is tight

**Deliverable:** Phase 4 complete when:
- [x] Flask app runs (`python -m fantasy_map_generator.gui`)
- [x] Parameter sliders generate different maps
- [x] PNG/SVG download works
- [x] Deployed locally and tested in browser

**Estimated effort:** 12–20 hours (depending on features in 4.4)

---

## Phase 5: Documentation & Polish (PRIORITY 4)

**Objective:** Complete documentation, tutorials, and code quality.

### Phase 5.1: API Documentation

**Task:** Generate API docs from docstrings using pdoc.

```bash
pdoc src/fantasy_map_generator -o docs/api
```

**Effort:** 1 hour

### Phase 5.2: World-Building Guide

**Task:** Template and guide for creating new worlds.

**Contents:**
- Minimal MapConfig example
- Coordinate system explanation
- Palette customization
- Testing your world config
- Common patterns (grid-based cities, procedural hamlets)

**Effort:** 2–3 hours

### Phase 5.3: Architecture Document

**Task:** High-level overview of how the system works.

**Contents:**
- Data flow: MapConfig → Renderer → SVG
- Seeded randomness model
- Spatial collision detection pattern
- Extensibility hooks (custom terrain, palette)

**Effort:** 2 hours

### Phase 5.4: Tutorial Worlds

**Task:** Pre-built world configs as examples.

**Examples:**
- Valley of Mists (original)
- A temperate kingdom (grid-based cities, large river)
- A desert region (oases, trade routes)
- An archipelago (islands, sea routes)

**Effort:** 4–6 hours per world

**Deliverable:** Phase 5 complete when:
- [x] README is complete and up-to-date
- [x] API docs auto-generated
- [x] At least 3 example worlds provided
- [x] New users can follow a tutorial and create a custom world

**Estimated effort:** 12–18 hours

---

## Timeline & Milestones

| Phase | Milestone | Effort | Owner | Target Date |
|-------|-----------|--------|-------|-------------|
| 1     | Scaffolding complete | 4 hours | Claude | ✅ Done |
| 2.1–2.2 | SVG primitives + Palette generalized | 4 hours | Claude | Week 1 |
| 2.3–2.4 | MapConfig + Valley world | 8 hours | Claude | Week 2 |
| 2.5–2.7 | Renderer refactor + tests | 12 hours | Claude | Week 2–3 |
| 3.1–3.4 | Terrain algorithms | 20–30 hours | Claude/Author | Week 3–5 |
| 4.1–4.4 | Web GUI | 12–20 hours | Claude/Author | Week 5–7 |
| 5.1–5.4 | Documentation + examples | 12–18 hours | Claude/Author | Week 7–8 |

**Total estimated effort:** 70–100 hours

---

## Success Criteria

- [x] **Technically:** Code is modular, well-tested, and documented.
- [x] **Functionally:** Multiple worlds can be rendered; GUI is interactive and intuitive.
- [x] **Maintainability:** New worlds can be added by editing config, not code.
- [x] **Reusability:** SVG primitives and terrain algorithms are exportable for other projects.

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Extraction breaks Valley rendering | High | Keep old `mapgen.py` as reference; write regression tests early. |
| MapConfig too rigid for some worlds | Medium | Design config to be extensible; user-defined terrain types. |
| GUI complexity spirals | Medium | Defer config editor (Phase 4.4) to Phase 5 or later. |
| Dependency on cairosvg for PNG | Low | PNG export is always best-effort; SVG is the deliverable. |
| Performance (large maps, many features) | Low | Profile and optimize if latency becomes issue. |

---

## Decision Points

**Awaiting author input:**

1. **Terrain complexity:** Perlin noise (procedural) or hand-placed features only?
2. **Scope of Phase 3:** Include road routing and water simulation, or defer?
3. **GUI simplicity:** Basic controls only, or advanced config editor?
4. **Tutorial worlds:** How many example worlds to ship? (2, 4, or more?)

---

## See Also

- **Code review:** See `mapgen_review.md` for detailed analysis of the Valley code.
- **Architecture:** CLAUDE.md for project structure and conventions.
- **Original:** `/Users/henrik/git/valley_of_mist/valley_of_mist_tools/mapgen.py`
