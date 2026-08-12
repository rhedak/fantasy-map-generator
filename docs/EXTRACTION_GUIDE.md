# Extraction Guide: Migrating Valley Mapgen to Fantasy Generator

This document is a step-by-step walkthrough for extracting and generalizing the Valley of Mists map generation code (`../valley_of_mist/valley_of_mist_tools/mapgen.py`) into the Fantasy Map Generator framework.

---

## Overview

**Source:** `/Users/henrik/git/valley_of_mist/valley_of_mist_tools/mapgen.py`

**Target:** `/Users/henrik/git/fantasy-map-generator/src/fantasy_map_generator/`

**Process:**
1. Copy SVG primitives (no changes needed)
2. Extract Palette constants → Palette dataclass
3. Extract LAYOUT constants → MapConfig
4. Generalize terrain functions
5. Refactor render_map() → MapRenderer class
6. Test against Valley reference

---

## Step 1: Copy SVG Primitives

**Source file:** Lines 284–410 in `mapgen.py`

**What to extract:**
- `_polygon()` (284–297)
- `_path()` (300–308)
- `_circle()` (311–324)
- `_ellipse()` (327–335)
- `_rect()` (338–349)
- `_title_case()` (358–361)
- `_text()` (364–385)
- `_line()` (388–396)
- `_leader_label()` (399–410)

**Action:**
1. Copy these functions as-is into `render.py`.
2. Add module-level docstring explaining they're SVG primitives.
3. No changes needed; these have no Valley-specific dependencies.

**Validation:**
```bash
python -c "from fantasy_map_generator.render import _polygon, _circle; print('OK')"
```

---

## Step 2: Extract Palette Constants

**Source:** Lines 39–72 in `mapgen.py`

**What to extract:**
```python
BG = "#202634"
MTN = "#343e54"
MTN_STROKE = "#1c2333"
# ... 24+ more color constants
```

**Action:**
1. Create `Palette` dataclass in `config.py` with fields for each color.
2. Set default values to match Valley colors.
3. Replace global constants in render code with `config.palette.background`, etc.

**Template:**
```python
# config.py
@dataclass
class Palette:
    background: str = "#202634"  # Valley: outside the valley, highlands at night
    mountain: str = "#343e54"    # Valley: the ring that walls the bowl in
    mountain_stroke: str = "#1c2333"
    # ... all 24+ colors
```

**Testing:**
```python
palette = Palette()
assert palette.background == "#202634"
assert palette.mountain == "#343e54"
```

---

## Step 3: Extract LAYOUT Constants

**Source:** Lines 73–279 in `mapgen.py`

**What to extract:**
All the geography data:
- Bowl geometry: `BOWL_CX`, `BOWL_CY`, `BOWL_RX`, `BOWL_RY`, `MOUTH_START`, `MOUTH_END`
- Locations: `KIRIGUCHI`, `KIRI_NO_SATO`, `INN`, `CAPITAL`, etc. (20+ points)
- Routes: `CAPITAL_ROAD`, `RIVER`, `TRIBUTARY`, `SECRET_PASSAGE`, etc. (6+ routes)
- Water features: `LAKE_KIRI_NO_SATO`, `LAKE_KASUMIKYO` (lakes + their dimensions)
- Terrain: `PADDIES`, `MILLS`, `PINE_STAND` (terrain clusters)
- Walls/buildings: `PALACE_*`, `WALL_*`, `BASIN_RING_*` (architectural elements)

**Action:**
1. Create a "world config" for Valley:
```python
# worlds/valley.py
from fantasy_map_generator.config import MapConfig, Palette

VALLEY_PALETTE = Palette(
    background="#202634",
    mountain="#343e54",
    # ... all Valley colors
)

VALLEY_CONFIG = MapConfig(
    name="Valley of Mists",
    canvas_width=1000,
    canvas_height=700,
    
    # Locations: Dict[str, Tuple[float, float]]
    locations={
        "kiriguchi": (180.0, 600.0),
        "kiri_no_sato": (267.5, 473.7),
        "inn": (520.0, 460.0),
        "capital": (660.0, 345.0),
        # ... 15+ more
    },
    
    # Routes: Dict[str, List[Tuple[float, float]]]
    routes={
        "capital_road": [(180.0, 600.0), (230.0, 565.0), (262.0, 542.0), ...],
        "river": [(480.0, 88.0), (460.0, 190.0), ...],
        "tributary": [...],
        # ... more routes
    },
    
    # Geometry (add to MapConfig if needed)
    # If you want Bowl parameters in config:
    geometry={
        "bowl_cx": 500.0,
        "bowl_cy": 350.0,
        "bowl_rx": 390.0,
        "bowl_ry": 265.0,
        "mouth_start": 92.0,
        "mouth_end": 178.0,
    },
    
    palette=VALLEY_PALETTE,
)
```

2. **Granularity trade-off:**
   - **Simple approach:** Store all Valley data in one VALLEY_CONFIG dict. Easy to migrate, but mixing location names with water features.
   - **Structured approach:** Add more MapConfig fields (locations, water_features, terrain, walls) for better organization.

   **Recommendation:** Use structured approach for clarity and future expansion.

3. **Update MapConfig:**
```python
# config.py
@dataclass
class MapConfig:
    # ... existing fields ...
    
    # Geography (add these if not already present)
    water_features: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # e.g., {"lake_kiri": {"center": (300, 504), "rx": 17, "ry": 12, "type": "lake"}}
    
    terrain_clusters: Dict[str, List[Tuple[float, float]]] = field(default_factory=dict)
    # e.g., {"paddies": (585, 432), "mills": [(565, 442), (605, 428)]}
    
    architecture: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # e.g., {"palace": {"x0": 614, "y0": 273, "x1": 696, "y1": 340}}
```

4. **Test migration:**
```python
# test_valley_config.py
from worlds.valley import VALLEY_CONFIG

def test_valley_config_has_all_locations():
    expected = ["kiriguchi", "kiri_no_sato", "inn", "capital", ...]
    for loc in expected:
        assert loc in VALLEY_CONFIG.locations

def test_valley_config_has_all_routes():
    expected = ["capital_road", "river", "tributary", ...]
    for route in expected:
        assert route in VALLEY_CONFIG.routes
```

---

## Step 4: Generalize Terrain Functions

**Source:** Lines 425–813 in `mapgen.py` (terrain generators)

**What to extract and how to generalize:**

### Example 1: _mountains()

**Before:**
```python
def _mountains(rng: random.Random) -> list[str]:
    """A ring of jagged peaks around the bowl."""
    out: list[str] = []
    n = 54
    for i in range(n):
        a_deg = 360.0 * i / n
        if MOUTH_START <= a_deg <= MOUTH_END:
            continue
        # ... uses BOWL_CX, BOWL_CY, BOWL_RX, BOWL_RY globally
```

**After:**
```python
def _mountains(rng: random.Random, config: MapConfig) -> list[str]:
    """A ring of jagged peaks around the bowl."""
    out: list[str] = []
    
    # Extract geometry from config
    bowl_cx = config.geometry.get("bowl_cx", 500.0)
    bowl_cy = config.geometry.get("bowl_cy", 350.0)
    bowl_rx = config.geometry.get("bowl_rx", 390.0)
    bowl_ry = config.geometry.get("bowl_ry", 265.0)
    mouth_start = config.geometry.get("mouth_start", 92.0)
    mouth_end = config.geometry.get("mouth_end", 178.0)
    
    # Use palette from config
    mtn_color = config.palette.mountain
    mtn_stroke_color = config.palette.mountain_stroke
    
    n = 54
    for i in range(n):
        a_deg = 360.0 * i / n
        if mouth_start <= a_deg <= mouth_end:
            continue
        # ... rest of function, using config values
        out.append(_polygon([...], fill=mtn_color, stroke=mtn_stroke_color, sw=1))
    
    return out
```

**Pattern:** Replace all global `CONSTANT` references with `config.field_name` or `config.geometry["key"]`.

### Example 2: _forest()

**Before:**
```python
def _forest(rng: random.Random, n_clumps: int) -> list[str]:
    """Dense forest cover."""
    # ... uses CAPITAL_ROAD, RIVER, KIRIGUCHI, LAKE_KIRI_NO_SATO, etc.
    # Hard-coded collision checks:
    if any(_dist_to_polyline(cx, cy, route) < 30 for route in routes):
        continue
```

**After:**
```python
def _forest(rng: random.Random, config: MapConfig, n_clumps: int) -> list[str]:
    """Dense forest cover, avoiding configured routes and locations."""
    # Build list of collision constraints from config
    routes = list(config.routes.values())  # All routes as polylines
    locations = list(config.locations.values())  # All locations as points
    
    # Geometry from config
    bowl_cx = config.geometry.get("bowl_cx", 500.0)
    bowl_cy = config.geometry.get("bowl_cy", 350.0)
    bowl_rx = config.geometry.get("bowl_rx", 390.0)
    bowl_ry = config.geometry.get("bowl_ry", 265.0)
    
    forest_color = config.palette.forest
    
    out: list[str] = []
    placed = 0
    while placed < n_clumps:
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0, 1) ** 0.5
        cx = bowl_cx + math.cos(a) * bowl_rx * 0.88 * r
        cy = bowl_cy + math.sin(a) * bowl_ry * 0.88 * r
        
        # Skip constraints from config
        if any(_dist_to_polyline(cx, cy, route) < 30 for route in routes):
            continue
        if any(math.hypot(cx - px, cy - py) < 38 for px, py in locations):
            continue
        
        placed += 1
        for _ in range(rng.randint(9, 15)):
            # ... render trees
            out.append(_polygon([...], fill=forest_color, ...))
    
    return out
```

**Key change:** Pass `config` instead of relying on globals. Derive constraints from config data.

### All Terrain Functions to Extract

1. `_mist_gradient()` → Keep as-is (purely mathematical)
2. `_mountains()` → Generalize with config geometry + palette
3. `_rim_edge()` → Generalize with config geometry
4. `_mist_wall_band()` → Generalize; may become optional feature
5. `_basin()` → Generalize (depends on bowl center from config)
6. `_river()` → Generalize to use routes from config
7. `_lake()`, `_capital_lake()`, `_tributary()` → Generalize to use water features from config
8. `_paddies_and_mills()` → Generalize to use terrain clusters from config
9. `_pine_stand()` → Generalize to use terrain from config
10. `_closed_routes()` → Generalize to use routes from config
11. `_hamlets()` → Generalize; may use locations from config or be hardcoded
12. `_ridge_highlands()` → Generalize; may be optional per-world
13. `_basin_ring()` → Generalize (specific to Valley; may not apply to all worlds)
14. `_distant_peaks()` → Generalize; optional texture
15. `_ground_texture()` → Generalize; optional texture
16. `_old_city_wall()` → Generalize to use architecture from config
17. `_capital()` → Generalize to use locations + architecture from config
18. `_zones()` → Generalize; optional legend
19. `_legend()` → Generalize; optional UI
20. `_compass()` → Generalize; optional UI

**Effort:** ~12–16 hours to update all functions.

---

## Step 5: Refactor render_map() → MapRenderer

**Source:** Lines 1072–1153 in `mapgen.py`

**Before (monolithic function):**
```python
def render_map(variant: str = "settled") -> str:
    rng = random.Random(7)
    el: list[str] = [
        f'<svg ...>',
        "<defs>",
        _mist_gradient(),
        "</defs>",
        _rect(0, 0, 1000, 700, fill=BG),
    ]
    # ... 60+ more el.extend(...) calls
    el.append("</svg>")
    return "\n".join(el)
```

**After (layer-based MapRenderer):**
```python
class MapRenderer:
    def __init__(self, config: MapConfig, seed: int = 7):
        self.config = config
        self.rng = random.Random(seed)
        self.elements: list[str] = []
    
    def add_background(self) -> None:
        """Background and gradient."""
        self.elements.append(f'<svg xmlns="..." width="{self.config.canvas_width}" ...>')
        self.elements.append("<defs>")
        self.elements.append(_mist_gradient())
        self.elements.append("</defs>")
        palette = self.config.palette
        self.elements.append(_rect(0, 0, self.config.canvas_width, self.config.canvas_height, 
                                   fill=palette.background))
    
    def add_terrain(self) -> None:
        """Mountains, forests, etc."""
        self.elements.extend(_mountains(self.rng, self.config))
        self.elements.extend(_distant_peaks(self.rng, self.config, n=30))
        self.elements.extend(_forest(self.rng, self.config, n_clumps=42))
    
    def add_water(self) -> None:
        """Rivers, lakes, tributaries."""
        if "river" in self.config.routes:
            self.elements.extend(_river(self.rng, self.config))
        if "lake_kiri_no_sato" in self.config.water_features:
            self.elements.extend(_lake(self.rng, self.config))
    
    def add_routes(self) -> None:
        """Roads, passages."""
        if "capital_road" in self.config.routes:
            route = self.config.routes["capital_road"]
            self.elements.append(_path(route, stroke=self.config.palette.road, sw=2.8))
    
    def add_settlements(self) -> None:
        """Villages, cities."""
        for name, (cx, cy) in self.config.locations.items():
            self.elements.extend(_village(cx, cy, ..., label=_title_case(name)))
    
    def add_labels(self) -> None:
        """Text markers."""
        self.elements.append(_text(500, 44, self.config.name))
    
    def render(self) -> str:
        """Assemble all layers."""
        self.add_background()
        self.add_terrain()
        self.add_water()
        self.add_routes()
        self.add_settlements()
        self.add_labels()
        self.elements.append("</svg>")
        return "\n".join(self.elements)


def render_map(config: MapConfig, seed: int = 7) -> str:
    """Convenience function."""
    return MapRenderer(config, seed).render()
```

**Benefits:**
- Easy to enable/disable layers per-world
- Reorderable for different depth effects
- Testable in isolation

---

## Step 6: Test Against Valley Reference

**Validation strategy:**

1. **Generate reference SVG from original `mapgen.py`:**
```bash
cd /Users/henrik/git/valley_of_mist
python -m valley_of_mist_tools.mapgen --out /tmp/valley_original.svg --no-png
```

2. **Generate SVG from new Fantasy Generator:**
```bash
cd /Users/henrik/git/fantasy-map-generator
uv sync
python -m fantasy_map_generator --out /tmp/valley_extracted.svg --world valley --seed 7
```

3. **Compare outputs:**
```bash
diff /tmp/valley_original.svg /tmp/valley_extracted.svg
```

**Expected:** Outputs should be byte-identical (same seed, same code).

**If they differ:**
- Check for rounding errors (format differences in float precision)
- Verify all constants migrated correctly
- Ensure RNG calls are in the same order

**Regression test:**
```python
# tests/test_extraction.py
def test_valley_extraction_matches_original():
    """Verify extracted Valley code produces same SVG as original."""
    from worlds.valley import VALLEY_CONFIG
    svg = MapRenderer(VALLEY_CONFIG, seed=7).render()
    
    # Load reference (generated from original mapgen.py)
    reference = Path("docs/reference_valley.svg").read_text()
    
    assert svg == reference, "Extracted Valley code differs from original"
```

---

## Checklist

- [ ] SVG primitives copied to `render.py`
- [ ] Palette extracted to `config.py` and validated
- [ ] VALLEY_CONFIG created with all locations, routes, water features, terrain
- [ ] MapConfig dataclass expanded to support all Valley features
- [ ] All terrain functions updated to accept `config: MapConfig` parameter
- [ ] Global color constants replaced with `config.palette.field_name`
- [ ] Global geometry constants replaced with `config.geometry[key]`
- [ ] MapRenderer class implemented and tested in isolation
- [ ] render_map() function signature updated to accept MapConfig
- [ ] Extracted Valley SVG compared to original (byte-identical)
- [ ] All tests pass (`pytest`)
- [ ] CLI works: `python -m fantasy_map_generator --world valley --seed 42`

---

## Timeline

**Estimated effort:** 20–30 hours (depending on terrain function complexity)

**Breakdown:**
- Step 1 (SVG primitives): 1 hour
- Step 2 (Palette): 2 hours
- Step 3 (LAYOUT → MapConfig): 4–6 hours
- Step 4 (Generalize terrain): 8–12 hours
- Step 5 (MapRenderer): 4–5 hours
- Step 6 (Testing): 2–3 hours

---

## Troubleshooting

**Q: Extracted SVG doesn't match the original.**

A: Likely causes:
1. RNG call order changed → re-verify all `rng.uniform()` calls are in the same order
2. Missing config field → check VALLEY_CONFIG has all necessary data
3. Color constant shadowed → verify all references to BG, MTN, etc. are updated
4. Floating-point rounding → unlikely, but check SVG decimal precision

**Q: Some terrain doesn't render.**

A: Check:
1. Terrain function is called in MapRenderer
2. Necessary data is in VALLEY_CONFIG (e.g., if `_forest()` needs bowl geometry, verify it's in config.geometry)
3. Collision detection constraints are correct (e.g., routes and locations are in config)

**Q: CLI argument parsing fails.**

A: Verify:
1. `cli.py` passes `--world` argument to MapRenderer
2. VALLEY_CONFIG is in the WORLDS registry
3. Argument names match (e.g., `--world valley` vs. `--world valley_of_mists`)

---

## See Also

- **PLAN.md:** Phase 2 timeline and deliverables
- **ARCHITECTURE.md:** System design and data flow
- **mapgen_review.md:** Detailed analysis of the original code
