# Interactive Editor TODO

Vision: palette of placeable elements → click-to-place on the map → select/move features → inspector edits properties.  
Source of truth is a mutable **world document** (`MapConfig` JSON), not the SVG alone. Seed only drives procedural garnish.

Related: `docs/TODO.md` (template variation), `docs/ARCHITECTURE.md`.

**Success bar (v1):** place a capital, rename it, drag it, re-render, download SVG/JSON — **done**.

---

## Principles (lock these)

- [x] **Config is source of truth** — browser holds working `MapConfig`; SVG is a projection
- [x] **Modes:** `select` | `place` (Esc → select)
- [x] **Stable IDs** — places/routes carry `id`; SVG emits `data-id` / `data-kind`
- [x] **Drag UX** — ghost while moving; commit coords → re-render on pointerup
- [x] **Hit targets** — place groups pickable; labels `pointer-events: none`
- [x] **Locked flag** on Place/Route (for future seed regen policy)
- [x] **Undo** — config snapshot stack (+ redo)

---

## Phase 0 — Foundations

- [x] World document = MapConfig JSON (`to_dict` / `from_dict`)
- [x] `Place` / `Route` / features carry stable `id`
- [x] Renderer emits `data-id`, `data-kind` on places (and routes)
- [x] Labels non-interactive
- [x] API: `POST /api/render` accepts full `config` JSON
- [x] API: `POST /api/world/normalize`
- [x] GUI holds `workingConfig`; preset load clones into it
- [x] Tests: `data-id` present; config roundtrip

---

## Phase 1 — v1 editor (places only)

### Palette & modes
- [x] Right rail **Elements** palette (settlement tiers)
- [x] Mode toggle Select / Place; Esc clears place tool
- [x] Active tool + hint text

### Click-to-place
- [x] Map click in place mode → create Place at SVG coords
- [x] Default name from tier + counter
- [x] Stable id; undo snapshot; re-render

### Select & move
- [x] Click place → selection + highlight ring
- [x] Drag ghost; commit x/y on release
- [x] Click empty → deselect
- [x] Delete key / button

### Inspector
- [x] Name + tier fields
- [x] Empty state when nothing selected

### Persist / export
- [x] Download world JSON
- [x] Download SVG/PNG from working config
- [x] Open / upload world JSON
- [x] Open SVG (extracts embedded `fmg-world` metadata → restores world)
- [x] Undo / Redo
- [x] sessionStorage snapshot of working config (write)

### Tests
- [x] data-id / selected highlight / API config render / JSON download / normalize

---

## Phase 2 — Routes (roads / rivers)

- [x] Palette: road, trail, river, ferry
- [x] Draw mode: click waypoints; double-click / Enter to finish
- [ ] Select route: drag individual vertices (select + highlight done)
- [x] Inspector: kind, label
- [x] Delete route
- [x] Route `data-kind` hit targets + selection highlight

---

## Phase 3 — Regions & stands

- [ ] Palette: forest stand, biome region
- [ ] Place stand; inspector radii / tree_style / density
- [ ] Biome center + type + name
- [ ] Optional resize handles
- [ ] Mountain ridge polyline tool

---

## Phase 4 — UX polish

- [x] Undo/redo keyboard (Ctrl/Cmd+Z / Shift+Z)
- [ ] Snap to grid
- [ ] Zoom/pan preview
- [ ] Multi-select
- [ ] Dirty flag + revert to preset
- [ ] Share URL for full world (server draft id) — currently preset+seed only
- [x] sessionStorage write (restore optional)
- [ ] Mobile long-press
- [x] Ghost-only while dragging (no per-move full re-render)

---

## Phase 5 — Advanced (later)

- [ ] Server-side world drafts
- [ ] Seed regen vs locked features UI
- [ ] Style kit / decor in inspector
- [ ] Constraint tools

---

## How to try v1

```bash
./gui.sh restart
# open http://localhost:3000
# pick a world → Elements → capital → click map
# Select mode → drag place → edit name/tier → World JSON
```
