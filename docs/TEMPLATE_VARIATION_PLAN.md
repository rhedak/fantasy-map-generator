# Template Variation Plan

How to make start-from world templates feel like distinct map *styles* and *geographies*, not recolored copies of one bowl valley.

Based on visual study of `ref-local/` (local only; not shipped) and the current `worlds/*` + `render.py` pipeline.

---

## 1. What the references teach

| File | Style family | Layout | Signature techniques |
|------|--------------|--------|----------------------|
| **ref01** | Hand-ink atlas (parchment) | Continental coast + inland biomes | Double coastline, biome fills (forest/plain/desert/swamp), snow-capped peaks, walled city icons, dashed roads, compass, scale, frame |
| **ref02** | Soft painted political map | Large labeled regions + coast | Watercolor washes, region-scale labels (`THE NORTH`), cool/warm zones, soft massifs, sparse settlements |
| **ref03** | Modern procedural vector | Archipelago + hypsometric bands | Contour elevation rings, ocean depth rings, dense tree stamps, star capitals / dot towns, thin branching rivers |
| **ref04** | Dense Inkscape land map | Irregular landmass | Heavy path terrain, warm earth fills, water **wave pattern**, blur/contrast filters, high path count |
| **ref05** | Layered island build | Single island in sea | Explicit layer stack: `waves → sea_shadow → island_base → mt_L1–L3 → rivers` |
| **ref06** | Classic RPG clipart map | Kingdom interior | Repeated mountain **symbols**, named features (“Mountains of Doom”), forest blobs, path labels, `use` symbol library |
| **ref07** | Dark fantasy cartography | Highland basin + passes | Ornate double border, parchment grain, compass, conifer forests, jagged ridgelines, castle/ruin/tower icons, title cartouche |

### Cross-cutting patterns (all strong refs)

1. **Land shape is primary identity** — coast / island / bowl / interior kingdom; not just colors.
2. **Layered depth** — water texture under land; land under vegetation; peaks stacked; labels on top.
3. **Biomes are regions**, not one global forest scatter.
4. **Settlements are typed icons** (village / town / capital / ruin / castle), not identical huts.
5. **Decoration sells the genre** — border, compass, scale, title banner.
6. **Texture beats flat fill** — waves, hatch, stipple, paper grain, contour bands.
7. **Typography hierarchy** — world title ≫ region ≫ place name.

---

## 2. Gap analysis (current templates)

Today every preset mostly shares one recipe:

```
background rect → mist ellipse → mountain RING (fixed mouth) →
uniform forest ellipse → routes → tiny rect settlements → labels → title
```

| Axis | Current | References need |
|------|---------|-----------------|
| Land topology | One elliptical bowl + south-west mouth | Island, archipelago, coast, interior plain, ridge wall, river valley |
| Water | Polyline river only | Ocean, lakes, depth bands, wave fill, coastline stroke |
| Mountains | One peak style, ring layout | Stacked ridges, snow caps, symbol stamps, multi-level masses |
| Forest | One triangle clump style | Conifers, broadleaf canopy blobs, density maps, biome masks |
| Settlements | 2–4 rects | Dots, stars, walls, towers, ruins, size by tier |
| Biomes | Palette only | Region polygons (desert, swamp, plain, ice) |
| Decoration | None | Border, compass, scale, cartouche |
| Seed effect | Jitters peaks/trees | Should also reshape coasts, branch rivers, place secondary POIs |
| Template difference | Palette + ~4 points | **Archetype + biome plan + icon set + decor kit** |

**Conclusion:** Variation must be driven by a **template archetype** (layout + feature kit), with palette as one layer—not the only layer.

---

## 3. Design goal

> Each start-from template is a **MapArchetype**: fixed story geography + style kit, with seed-controlled secondary variation that never destroys the archetype’s silhouette.

Examples:

| Preset | Archetype | Seed varies | Seed must not break |
|--------|-----------|-------------|---------------------|
| `valley` | Mist bowl + mouth gate | Peak jaggedness, tree clumps, mist opacity | Kiriguchi–Basin axis, river corridor |
| `desert` | Arid basin / oasis chain | Dune hatch, oasis size | Trade-road spine, fortress sites |
| `tropical` | Archipelago + lagoon | Island count/noise, reef dots | Main harbor + temple island |
| `arctic` | Ice shelf + fjord | Crevasse hatch, aurora wash | Citadel + frozen path |
| `autumn` | Inland kingdom forest | Leaf clumps, orchard patches | Harvest road + keeps |

Optional new presets later: `coastal_realm` (ref01/02), `rpg_kingdom` (ref06), `parchment_atlas` (ref07 style kit on any archetype).

---

## 4. Config model extensions

Extend data, keep renderer world-agnostic.

### 4.1 `MapArchetype` (or fields on `MapConfig`)

```text
layout: bowl | island | archipelago | coast | interior | ridge
landmass: list of polygons / ellipses / noise params   # silhouette
water_bodies: oceans, lakes (polygons + style)
biome_regions: [{name, polygon|ellipse, biome}]
elevation_bands: optional contour params (ref03)
mountain_ranges: [{ridge polyline or arc, style, levels}]
forest_stands: [{center, radii, tree_style, density}]
locations: name → {xy, tier, icon}   # tier: hamlet|village|town|city|capital|ruin|castle
routes: name → {waypoints, kind: road|trail|river|ferry}
decor: {border, compass, scale, cartouche, paper_texture}
style_kit: {mountain_draw, tree_draw, settlement_draw, water_fill, label_mode}
palette: existing Palette (+ paper, ink, gold, depth stops)
density: {forest, peaks, waves, settlements}  # 0–1 multipliers for seed detail
```

### 4.2 Route / feature kind (replace name heuristics)

Today: `"river" in key`.  
Target: explicit `kind` on each route/feature so templates stay clear.

### 4.3 Style kits (swapable drawers)

| Kit id | Inspired by | Look |
|--------|-------------|------|
| `ink_parchment` | ref01, ref07 | Cream/dark paper, ink lines, conifers, ornate border |
| `watercolor` | ref02 | Soft fills, low stroke, large region labels |
| `hypsometric` | ref03 | Contour bands, depth rings, stamp trees, star capitals |
| `layered_island` | ref05 | Sea pattern, stacked mountain levels, wave layer |
| `rpg_symbols` | ref06 | Repeated mountain glyphs, bold named ranges |
| `mist_bowl` | current valley | Ring peaks, cool mist gradient (keep as default) |

Renderer selects primitive implementations via `style_kit`, not via world name.

---

## 5. Visual feature backlog (mapped to refs)

Priority = impact on “templates feel different” ÷ effort.

### P0 — Silhouette & water (highest identity)

| Feature | Refs | Implementation sketch |
|---------|------|------------------------|
| Landmass polygon(s) | 01–05, 07 | `landmass` shapes; clip terrain to land; sea = background or inverse |
| Coastline double-stroke | 01, 02, 07 | Outer water band + inner land edge |
| Ocean / sea fill | 03, 05 | Full-canvas water when layout ≠ interior |
| Wave / hatch water texture | 01, 04, 05 | SVG `<pattern>` (wavy white / lines); tile under land |
| Lakes | 07, 03 | Closed polygons + soft edge |
| Layered mountain levels | 05 | 2–3 ridge passes with rising apex offset |
| Explicit mountain ranges | 06, 07 | Polyline ridges, not only bowl ring |

### P1 — Biomes & vegetation

| Feature | Refs | Sketch |
|---------|------|--------|
| Biome region fills | 01, 02 | Soft polygons under icons (plain/desert/swamp/ice) |
| Tree style variants | 01, 03, 07 | `triangle` / `conifer` / `canopy_blob` / `stamp_grid` |
| Desert dunes | 01 | Parallel arc strokes or hatch in desert biome |
| Swamp stipple | 01 | Dots + dashed channels |
| Elevation contours | 03 | Nested offset curves or banded fills from simple height field |

### P2 — Settlements & routes

| Feature | Refs | Sketch |
|---------|------|--------|
| Settlement tiers + icons | 01, 03, 06, 07 | capital=star/walls, town=dot+ring, ruin=broken rect, castle=keep |
| City walls / towers | 01, 07 | Circle wall + gate notch |
| Road styles | 01, 07 | solid / dashed / double; trails thinner |
| River width along path | 03, 07 | stroke-width lerp by distance downstream |
| Named region labels | 02, 06 | Large faint letter-spacing labels from biome/region list |

### P3 — Decoration & finish

| Feature | Refs | Sketch |
|---------|------|--------|
| Frame / double border | 01, 07 | Rects + corner ornaments |
| Compass rose | 01, 07 | Parametric 8-point rose |
| Scale bar | 01 | Segmented line + unit label |
| Title cartouche | 07 | Banner path + title text |
| Paper grain / vignette | 02, 07 | Noise filter or semi-transparent stipple (keep SVG-light) |
| Label hierarchy | all | size/weight/opacity by tier |

---

## 6. Seed variation strategy

Separate **locked template structure** from **seeded ornament**.

```text
locked (per template):
  landmass silhouette control points (or archetype params)
  major settlements + capital
  primary river corridor + main road
  biome region anchors
  style_kit + palette

seeded (rng):
  coastline fractal displacement (bounded amplitude)
  secondary islands / rocks
  mountain peak jitter and spur count
  forest clump placement inside stands
  minor POIs (shrines, camps) if enabled
  wave phase, hatch offset
  label micro-offsets to reduce collision
```

**Determinism rule (unchanged):** same `(template_id, seed)` → identical SVG.

**Variation rule:** changing seed should be obvious in detail, but gallery thumbnail still reads as the same world.

### Suggested seed knobs (later GUI)

- `detail` (0–1): forest/peak density  
- `coast_roughness`  
- `weathering` (ruin chance, broken roads)  
- `label_density`

---

## 7. Renderer architecture changes

Move from a single linear recipe to **layout pipeline + style drawers**.

```text
render_map(config, seed)
  rng = Random(seed)
  kit = STYLE_KITS[config.style_kit]

  layers = []
  layers += kit.background(config)           # paper / sea / mist
  layers += kit.water_texture(config, rng)
  layers += kit.landmass(config, rng)        # fill + coast
  layers += kit.biomes(config, rng)
  layers += kit.mountains(config, rng)
  layers += kit.vegetation(config, rng)
  layers += kit.watercourses(config, rng)    # rivers/lakes
  layers += kit.routes(config, rng)
  layers += kit.settlements(config, rng)
  layers += kit.labels(config, rng)
  layers += kit.decor(config)                # border, compass, scale, title
  return assemble_svg(layers, defs=kit.defs(config))
```

### Incremental migration

1. Keep current functions as the `mist_bowl` kit.
2. Add `layered_island` kit (ref05 stack) for `tropical`.
3. Add landmass clipping + sea background for island/coast layouts.
4. Introduce settlement tiers without breaking valley labels.
5. Add decor module optional via `config.decor`.

No need for a heavy class hierarchy on day one—**dispatch tables** (`STYLE_KITS`, `TREE_DRAWERS`) are enough.

---

## 8. Per-template rewrite plan

### 8.1 `valley` (keep soul, deepen)

- **Keep:** bowl ring, mouth, story locations, cool mist palette.  
- **Add:** mist wall band near mouth; paddies near river; capital walls at Kasumikyo; conifer stands on slopes; faint zone rings.  
- **Style kit:** `mist_bowl`.  
- **Refs:** current product + ref07 density of forest/river.

### 8.2 `desert` → arid corridor (not green bowl)

- Land: open basin, broken ridge north; sand biome majority.  
- Water: thin wadi (dashed/dry optional) + oasis discs.  
- Mountains: sparse mesa blocks / flat-top polys, not full ring.  
- Forest → oasis palms (few).  
- Settlements: fortress + caravanserai icons.  
- Decor: sun compass optional.  
- **Refs:** ref01 desert quadrant.

### 8.3 `tropical` → archipelago

- Layout: `archipelago`; sea background + wave pattern (ref05).  
- 3–6 islands from seeded ellipses around anchors.  
- Mountains: stacked levels on largest island only (ref05 L1–L3).  
- Dense stamp trees (ref03).  
- Reef dots / shoals near coast.  
- Capital star on harbor island.  
- **Refs:** ref03, ref05.

### 8.4 `arctic` → ice + fjord

- Land: pale ice shelf + dark rock ridges.  
- Biomes: ice pack hatch, tundra scrub (sparse).  
- Water: deep cold sea + frozen river (lighter stroke, ice edge).  
- Mountains: sharp monochrome ridgelines.  
- Settlements: citadel heavy walls; harbor ice-free notch.  
- **Refs:** ref02 cool north + ref07 ink ridges.

### 8.5 `autumn` → inland kingdom

- Layout: `interior` (no ocean); parchment or dark paper.  
- Forest stands as large canopy blobs + orchard grid near towns (ref06/07).  
- Mountains: one named range along edge (rpg_symbols or jagged ridge).  
- Roads: harvest road double-line; labeled mid-path.  
- Decor: simple frame + scale.  
- **Refs:** ref06 names/symbols, ref01 plains/forest mix.

### 8.6 Future presets (optional)

| id | Pitch | Primary refs |
|----|-------|--------------|
| `coastal_realm` | Big coastline + political regions | ref01, ref02 |
| `rpg_handout` | Grey peak stamps + bold labels | ref06 |
| `parchment_ornate` | Style kit only (wrap any layout) | ref07 |

---

## 9. Implementation phases

### Phase A — Foundation (≈1–2 days)

- [ ] Extend `MapConfig` with `layout`, `style_kit`, `landmass`, `biome_regions`, settlement tiers, explicit route kinds, `decor` flags.
- [ ] Introduce `STYLE_KITS` dispatch; move current render path to `mist_bowl`.
- [ ] Add SVG `<defs>` helpers: wave pattern, simple paper filter (optional).
- [ ] Tests: each world still renders; golden smoke per preset name/labels.
- [ ] Docs: update ARCHITECTURE with layer order.

### Phase B — Silhouette divergence (≈2–3 days)

- [ ] Landmass + sea background + coastline stroke.
- [ ] `layered_island` kit; rework `tropical` preset data.
- [ ] Mountain **ranges** (polyline) + keep bowl generator for valley.
- [ ] Desert/arctic layouts stop using full mountain ring (template-specific ranges).
- [ ] GUI gallery should show clearly different silhouettes at seed=42.

### Phase C — Biomes & icons (≈2–3 days)

- [ ] Biome fills + tree drawers (conifer, canopy, stamp).
- [ ] Settlement tier icons (capital/town/ruin/castle).
- [ ] River width gradient; road style variants.
- [ ] Region labels (watercolor / rpg mode).
- [ ] Expand world modules with real biome/stand data (not only points).

### Phase D — Decor & seed UX (≈1–2 days)

- [ ] Border, compass, scale, cartouche (toggle per template).
- [ ] Seed knobs in GUI: detail, roughness (optional).
- [ ] Share URL includes `world` + `seed` + knobs.
- [ ] README screenshots / preset blurbs describing archetype.

### Phase E — Polish (ongoing)

- [ ] Label collision avoidance.
- [ ] Optional light height-field contours (ref03) behind `hypsometric` kit.
- [ ] Performance budget: gallery preview &lt; ~150ms/target; full detail &lt; ~400ms.
- [ ] Optional regression SVGs under `tests/baselines/` (small, not ref-local binaries).

---

## 10. Concrete data shape (target example)

```python
TROPICAL_CONFIG = MapConfig(
    name="Tropical Islands",
    layout="archipelago",
    style_kit="layered_island",
    landmass=[
        LandBody(kind="ellipse", center=(420, 360), radii=(160, 110), rough=0.12),
        LandBody(kind="ellipse", center=(680, 420), radii=(90, 70), rough=0.18),
        LandBody(kind="ellipse", center=(240, 520), radii=(70, 45), rough=0.2),
    ],
    biome_regions=[
        BiomeRegion("jungle", body=0, biome="forest", density=0.9),
        BiomeRegion("lagoon_shore", body=1, biome="coast", density=0.4),
    ],
    mountain_ranges=[
        MountainRange(body=0, levels=3, density=0.7, style="stacked"),
    ],
    locations={
        "Lagoon Harbor": Place((750, 500), tier="capital", icon="star_port"),
        "Jungle Temple": Place((350, 300), tier="ruin", icon="temple"),
        ...
    },
    routes=[
        Route("reef_path", kind="trail", points=[...]),
        Route("spring_river", kind="river", points=[...]),
    ],
    decor=Decor(border=False, compass=True, scale=True, cartouche=True),
    palette=TROPICAL_PALETTE,
)
```

(Exact dataclasses can be slimmer at first—start with ellipses + tiers, grow polygons later.)

---

## 11. Testing strategy for variation

| Test | Intent |
|------|--------|
| `test_presets_distinct_silhouette` | Hash of landmass path / sea rect presence differs across worlds at seed=42 |
| `test_seed_stability` | same world+seed identical |
| `test_seed_changes_detail` | same world, seeds 1 vs 2 differ but both contain locked labels |
| `test_style_kit_smoke` | each kit id renders valid XML |
| `test_tier_icons` | capital/ruin produce different element counts or markers |
| GUI gallery | manual: five thumbnails readable as five geographies |

Avoid committing large `ref-local` binaries; keep them developer-only (already gitignored).

---

## 12. Non-goals (for this plan)

- Full GIS / real projection math  
- Raster brushes as primary output  
- ML / image-to-map  
- Pixel-perfect clones of ref files (copyright + different medium)  
- Requiring cairosvg for core look  

Refs are **inspiration and acceptance taste**, not assets to embed.

---

## 13. Success criteria

Templates are “done enough” when:

1. At seed 42, a user can name the preset from the silhouette alone (no legend).  
2. Valley still feels like Valley of Mists (story points intact).  
3. Tropical is visibly oceanic; desert is visibly arid; arctic reads cold; autumn reads inland kingdom.  
4. Changing seed alters detail without teleporting capitals.  
5. Style kit can be reused (e.g. `ink_parchment` on `autumn`) without rewriting geography.  
6. Tests guard distinctness + determinism; ruff/pytest clean.

---

## 14. Recommended first build slice

Smallest path to a dramatic gallery upgrade:

1. **Config:** `layout` + `style_kit` + settlement `tier`.  
2. **Render:** sea background when `layout in {island, archipelago, coast}`; land ellipse fill; coastline stroke.  
3. **Tropical** rework as 3-island archipelago + wave pattern + stacked peaks on main island.  
4. **Desert** drop full ring → southern broken ridge + oasis circles.  
5. **Settlement icons** by tier (capital star, others dots).  
6. **Tests** for silhouette distinctness.

Estimate: ~1 focused day for a visible quality jump; Phases B–D as follow-ons.

---

## 15. Reference → checklist cheat sheet

When implementing a feature, skim the matching ref:

- Coast & biomes side-by-side → **ref01**  
- Big political labels / soft paint → **ref02**  
- Contours, archipelago density, capital stars → **ref03**  
- Water patterns / dense fills → **ref04**  
- Layer order for islands → **ref05** (`waves`, `sea_shadow`, `island_base`, `mountains_level*`, `rivers`)  
- Symbol mountains & named ranges → **ref06**  
- Border, compass, conifers, ruins, cartouche → **ref07**

---

## See also

- `docs/ARCHITECTURE.md` — current pipeline  
- `docs/PLAN.md` — overall phases (this doc specializes Phase 3 template work)  
- `src/fantasy_map_generator/worlds/` — presets to rewrite  
- `src/fantasy_map_generator/render.py` — drawers to modularize  
