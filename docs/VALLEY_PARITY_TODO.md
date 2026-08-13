# Valley of Mists parity + round-trip TODO

**Goal:** Reproduce the sister-repo Valley map **exactly** (byte-stable for a fixed seed/variant), and support **edit → save → re-open → edit** without losing authored data.

**Canonical reference:** SVG you pasted (and `valley_of_mist/valley_of_mist_tools/mapgen.py`, ~1195 lines).  
**Current FMG valley:** simplified ring + places + routes — missing mist wall, capital complex, lakes, paddies, closed routes, leader labels, basin glyph, etc.

---

## Product decisions (locked unless you change them)

1. **Source of truth for editing = World JSON** (`MapConfig` / extended schema), not reverse-engineering freeform SVG paths.  
2. **SVG is a projection** for display/export; optional **embedded metadata** makes a single `.svg` file round-trip capable.  
3. **Valley “exact” mode** is a first-class kit: procedural layers match sister `mapgen` RNG order + constants; hand-edit layers override/add.  
4. **Round-trip file formats:**
   - Primary: `world.json` (already partly there)
   - Also: `map.svg` containing `<metadata type="application/fmg+json">…</metadata>` (or `<!--fmg:…-->`) so “Open SVG” restores the world

---

## Gap analysis (reference SVG vs current FMG)

| Feature in reference | Sister mapgen | FMG today |
|---------------------|---------------|-----------|
| Mist radial fill ellipse | yes | partial |
| Outer mountain ring + mouth gap | yes (seeded) | yes (simpler) |
| Distant peaks / ground texture | yes | no |
| Rim edge path | yes | no |
| Mist wall band + poles + label | yes | no |
| Main river + opacity layers | yes | polyline only |
| Lakes + capital lake + tributary | yes | no |
| Paddies + mills | yes | no |
| Pine stands / forest clumps w/ road avoidance | yes | simple stands |
| Closed / dashed routes | yes | trails only |
| Hamlets scatter | yes | editor places only |
| Ridge highlands, basin ring | yes | no |
| Kiriguchi / Kiri no Sato / Inn villages | yes | generic tier icons |
| Capital: old wall, gates, streets, palace, shrine, treasury, leader labels | yes | capital star only |
| Basin center glyph + labels | yes | ruin tier |
| Zones / legend / compass | yes | decor partial |
| Title “the Valley Of Mists” | yes | config name |
| Fixed seed=7 style determinism | yes | different pipeline |

**Implication:** “Exact” means **port or wrap sister render pipeline**, not tweak parameters on the generic kit.

---

## Architecture

```
WorldDocument (JSON)
  meta: { generator, version, seed, variant, source: "valley_parity" }
  config: MapConfig-like
  valley: {   # parity-specific locked layout constants + overrides
    variant: "settled" | ...
    label_overrides: {...}
    extra_places / hidden_layers: [...]
  }
  edits: {    # editor mutations on top of base
    places, routes, ...
  }
        │
        ▼
ValleyParityRenderer  ←── port of mapgen.render_map (same RNG call order)
        │
        ▼
SVG (+ optional <metadata> world blob)
```

### Round-trip flows

**A. JSON (recommended default)**  
Save World JSON → Open JSON → `workingConfig` → render → edit → save.

**B. SVG with metadata**  
Export SVG includes:

```xml
<svg …>
  <metadata id="fmg-world" data-format="fmg-world/v1">
    { … full world json … }
  </metadata>
  …drawn content…
</svg>
```

Open SVG → parse metadata → if present, load world; else fail soft (“no FMG metadata; import as flat art not supported”).

**C. Not in v1:** pure geometric reverse-SVG → MapConfig (too lossy for forests/peaks).

---

## Phase V0 — Baseline & harness

- [x] Vendor or path-reference sister `mapgen.py` → vendored into `src/fantasy_map_generator/valley/mapgen.py`
- [x] Capture **golden SVG** from sister for `variant=settled` (seed 7) into `tests/baselines/valley_settled.svg`
- [x] Script: `python -m fantasy_map_generator.valley_baseline` regenerate golden
- [x] Test: FMG parity renderer output **equals** golden (`tests/test_valley_parity.py`)
- [x] Do **not** commit huge binaries; golden SVG text is OK if &lt; ~few hundred KB (90 KB)

## Phase V1 — Port Valley renderer into FMG

- [x] Add package module `src/fantasy_map_generator/valley/`  
  - Port primitives + terrain functions from mapgen (RNG order identical)  
  - `render_valley(variant="settled", seed=…)`  
- [x] Wire preset `valley` to parity renderer (flag `style_kit="valley_parity"`)
- [x] Map sister colors → `Palette` via `_valley_palette()` (no pixel change)
- [x] CLI: `--world valley` produces golden-matching SVG (interactive defaults False on dispatch)
- [x] GUI gallery valley preview = parity map (`/api/presets` renders via dispatch)

## Phase V2 — World document ↔ Valley

- [x] Extend schema: `meta.seed`, `meta.variant`, `meta.renderer: "valley_parity" | "generic"`
- [x] Extract **editable** entities from Valley into places/routes for inspector:
  - Kiriguchi, Kiri no Sato, Valley Inn, Kasumikyo, Basin (place ids)
  - capital_road, secret_passage (route ids); mist wall / capital art stay procedural
- [x] Parity render reads overrides: moved place coords, renamed labels, added editor places (`place_overrides`)
- [x] Layers that stay pure-procedural (forest jitter, mountain jitter) stay seed-locked unless “bake” later

## Phase V3 — Round-trip I/O

- [x] Export SVG: inject `<metadata>` world JSON (compact, `</` → `<\/`)
- [x] Export always also offers World JSON button (already)
- [x] Import SVG: detect FMG metadata → load world (Open SVG button + `/api/world/from-svg`)
- [x] Import JSON: existing normalize path
- [x] Tests:  
  - render → to_dict → from_dict → render (identical)  
  - render → svg+metadata → parse → render (identical)  
  - edit place → save svg → reload → place still moved

## Phase V4 — Editor integration

- [x] Selecting Valley places works on parity SVG (`data-id` on villages/capital/basin when `interactive=True`)
- [x] Moving Kiriguchi updates override; re-render keeps mist wall/capital art
- [x] Adding new settlements draws with generic icons **on top of** parity base
- [ ] Drawing new routes composites after parity layers
- [ ] “Reset Valley layout” discards overrides, keeps seed/variant
- [ ] Document which layers are editable vs cosmetic

## Phase V5 — Polish (optional)

- [ ] Bake procedural forests to editable stands (heavy)
- [ ] Side-by-side diff view vs golden
- [ ] PNG hash regression
- [ ] Variant switcher (`settled` / others from mapgen)

---

## Implementation strategy (recommended order)

1. **Golden harness first** — prove we can match sister output at all.  
2. **Lift mapgen into `valley/` package** with minimal renames (fastest path to exact SVG).  
3. **Only then** peel editable POIs into MapConfig overrides.  
4. **Metadata embed** for single-file round-trip.  
5. **Editor hooks** on parity output.

Avoid rewriting Valley feature-by-feature in the generic pipeline first — you’ll chase pixels for weeks.

---

## Round-trip metadata sketch

```json
{
  "format": "fmg-world/v1",
  "meta": {
    "renderer": "valley_parity",
    "seed": 7,
    "variant": "settled",
    "created_with": "fantasy-map-generator/0.1.0"
  },
  "config": { "...MapConfig..." },
  "overrides": {
    "places": { "kiriguchi": { "x": 180, "y": 600, "name": "Kiriguchi / Nebelmark" } }
  }
}
```

SVG writer appends this under `<metadata>`. Reader: regex/XML parse `metadata#fmg-world` or `data-format="fmg-world/v1"`.

---

## Risks

| Risk | Mitigation |
|------|------------|
| Sister mapgen drifts | Pin path + golden hash; note version in meta |
| RNG order breaks when inserting editor layers | Editor layers drawn **after** parity block; don’t inject into middle of RNG stream |
| Huge SVG in metadata | Compact JSON; or external JSON + svg link |
| Editor expects generic data-id | Parity renderer must emit same data-id scheme |

---

## Success criteria

1. `render_valley(settled)` == sister golden SVG (fixed seed/variant).  
2. Save world JSON / SVG+metadata → reload → identical render.  
3. Move “Kiri no Sato” in GUI → save → reload → still moved; mist wall/capital still present.  
4. Generic worlds (desert/tropical/…) unchanged.

---

## Immediate next coding slice

1. Add `tests/baselines/` + script calling sister mapgen (or vendored copy) to write golden.  
2. Copy `mapgen.py` → `src/fantasy_map_generator/valley/legacy.py` and expose `render_map`.  
3. Point `valley` preset at it; assert equality test.  
4. Then metadata embed + override places.

---

## Open questions (only if you care)

- Pin **seed** to sister’s hard-coded RNG (mapgen uses internal seeds per function)?  
- Support sister **variants** beyond `settled`?  
- Prefer **vendoring** mapgen into this repo vs runtime import from `../valley_of_mist`?
