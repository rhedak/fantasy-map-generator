# Template Variation TODO

Derived from `docs/TEMPLATE_VARIATION_PLAN.md`.  
Check items off as they land; keep presets distinct by silhouette, not only palette.

**Success bar:** at seed 42, each preset is recognizable from silhouette alone; seed changes detail without moving locked capitals.

---

## Phase A — Foundation

- [x] Add `layout` to `MapConfig` (`bowl` | `island` | `archipelago` | `coast` | `interior` | `ridge`)
- [x] Add `style_kit` string to `MapConfig`
- [x] Add settlement tiers (`hamlet` | `village` | `town` | `city` | `capital` | `ruin` | `castle`)
- [x] Replace route name heuristics with explicit route `kind` (`road` | `trail` | `river` | `ferry`)
- [x] Add `decor` flags (`border`, `compass`, `scale`, `cartouche`, `paper_texture`)
- [x] Add optional `landmass`, `biome_regions`, `mountain_ranges`, `forest_stands` config structures
- [x] Introduce style-kit-aware pipeline in renderer (`mist_bowl`, `layered_island`, `ink_parchment`, `rpg_symbols`, …)
- [x] Keep bowl path as default for `layout=bowl` / `mist_bowl`
- [x] Add SVG `<defs>` helpers (wave pattern, mist gradient, paper grain filter)
- [x] Smoke tests: every world still renders valid SVG
- [x] Update `docs/ARCHITECTURE.md` with layer order + kit model

## Phase B — Silhouette divergence

- [x] Sea/ocean background when `layout` is `island` | `archipelago` | `coast`
- [x] Landmass fill from config shapes (ellipse + polygon)
- [x] Coastline stroke (outer water band)
- [x] `layered_island` style kit signals (waves + stacked peaks)
- [x] Rework `tropical` preset into multi-island archipelago data
- [x] Mountain **ranges** (polyline ridge) + stacked + ring
- [x] Bowl ring generator for `valley` / `layout=bowl`
- [x] Rework `desert`: broken ridge + oasis discs + arid biomes
- [x] Rework `arctic`: ice shelf / fjord silhouette + cold sea
- [x] Rework `autumn`: `interior` layout, edge range, inland forests
- [x] Test: presets produce distinct silhouettes at seed=42
- [ ] Manual GUI gallery check: five clearly different thumbnails

## Phase C — Biomes & icons

- [x] Biome region fills (plain, desert, swamp, ice, forest underlay)
- [x] Tree drawers: `triangle` | `conifer` | `canopy` | `stamp`
- [x] Wire `forest_stands` + density into vegetation pass
- [x] Desert dune hatch in desert biomes
- [x] Swamp stipple optional
- [x] Settlement icon drawers by tier (capital star/walls, town dot, ruin, castle keep)
- [x] River multi-stroke / width scale by detail
- [x] Road style variants (solid/dashed road, trail, ferry)
- [x] Region-scale labels
- [x] Expand each `worlds/*.py` with biomes/stands/tiers
- [x] Tests: tier icons differ; locked labels stable across seeds

## Phase D — Decor & seed UX

- [x] Frame / double border
- [x] Compass rose
- [x] Scale bar
- [x] Title cartouche / banner
- [x] Optional paper grain
- [x] Enable decor per template defaults
- [x] Seed knobs: `detail`, `coast_roughness` (config + render + CLI)
- [x] GUI controls for detail/roughness (debounced)
- [x] Share URL includes world, seed, knobs
- [x] README preset blurbs (archetype one-liners)

## Phase E — Polish

- [x] Label micro-offsets (seeded)
- [ ] Optional hypsometric contour bands style kit (ref03) — deeper pass
- [x] `rpg_symbols` mountain stamps style kit (ref06) — ridge symbol mode
- [x] `ink_parchment` kit used by desert/autumn
- [ ] Performance profiling / budgets
- [ ] Optional small SVG baselines under `tests/baselines/`
- [ ] Future presets (optional): `coastal_realm`, `rpg_handout`, `parchment_ornate`

---

## First build slice

1. [x] Config: `layout` + `style_kit` + settlement `tier`
2. [x] Render: sea background + land ellipse + coastline for non-bowl layouts
3. [x] Rework `tropical` → multi-island archipelago + wave pattern + stacked peaks
4. [x] Rework `desert` → broken ridge + oases (no full mountain ring)
5. [x] Settlement icons by tier
6. [x] Tests for silhouette distinctness + determinism
7. [ ] GUI gallery sanity check at seed=42 (manual)

---

## Preset checklist

### `valley` — mist bowl
- [x] Bowl + mouth retained
- [x] Story locations locked
- [x] Cool mist palette identity
- [x] Conifer/triangle stands, capital at Kasumikyo
- [x] Style kit: `mist_bowl`

### `desert` — arid corridor
- [x] No full mountain ring
- [x] Broken ridge + sand majority
- [x] Oasis canopy + sparse vegetation
- [x] Fortress / capital / ruin icons
- [x] Trade-road spine locked

### `tropical` — archipelago
- [x] Sea dominant + wave texture
- [x] Multiple islands
- [x] Stacked peaks on main island
- [x] Dense stamp vegetation
- [x] Harbor capital marked

### `arctic` — ice + fjord
- [x] Cold sea / ice shelf read
- [x] Sharp ridgelines
- [x] Sparse conifer scrub
- [x] Citadel + frozen path locked

### `autumn` — inland kingdom
- [x] No ocean (interior)
- [x] Large forest/orchard stands
- [x] Edge mountain range (symbol style)
- [x] Harvest road + keeps
- [x] Frame / scale / cartouche decor

---

## Remaining (optional / later)

- [ ] Deeper hypsometric contours (ref03)
- [ ] Label collision solver beyond jitter
- [ ] Performance budgets + baselines
- [ ] Extra presets: coastal_realm, rpg_handout, parchment_ornate
- [ ] Manual GUI visual QA pass
