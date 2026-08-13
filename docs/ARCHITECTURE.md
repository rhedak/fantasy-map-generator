# Fantasy Map Generator: Architecture

## System Overview

```
MapConfig (layout, style_kit, landmass, biomes, places, routes, decor, palette)
    ↓
render_map() layer pipeline (seeded RNG)
    ↓
SVG Document (+ defs: mist gradient, wave pattern, paper grain)
    ↓ (optional)
PNG (via cairosvg)
```

### Layer order

1. Background (paper / sea + waves)
2. Landmass fills + coastline
3. Biome underlays (+ dune/swamp/ice hatch)
4. Mountains (ring | ridge | stacked)
5. Vegetation stands (triangle / conifer / canopy / stamp)
6. Routes (river / road / trail / ferry)
7. Place icons by tier
8. Labels + region names
9. Title / cartouche
10. Decor (border, compass, scale)

### Style kits

`mist_bowl`, `layered_island`, `ink_parchment`, `watercolor`, `hypsometric`, `rpg_symbols`  
(Kits influence mountain stamp style, paper grain, and sea treatment together with `layout`.)

---

## Components

### MapConfig (`config.py`)

Defines a fantasy world's geography and appearance.

**Structure:**
```python
@dataclass
class MapConfig:
    name: str                                    # "Valley of Mists"
    canvas_width: int                           # 1000
    canvas_height: int                          # 700
    locations: Dict[str, Tuple[float, float]]  # {"kiriguchi": (180, 600)}
    routes: Dict[str, List[Tuple[float, float]]] # {"capital_road": [...]}
    palette: Palette                            # colors
```

**Purpose:** Separate world data from rendering code. Same renderer can produce maps of different worlds by swapping MapConfig.

**Extensibility:** Add new fields as needed (elevation, climate zones, faction territories, etc.) without changing render code.

---

### Palette (`config.py`)

Color scheme for a map.

```python
@dataclass
class Palette:
    background: str         # Dark highlands
    mountain: str          # Mountain color
    water: str            # River / lake blue
    forest: str           # Tree green
    settlement: str       # Building tan
    text: str             # Label cream
    # ... 15+ more colors
```

**Benefit:** Swap palettes to render the same world in different color schemes (e.g., winter vs. summer, light vs. dark mode).

---

### SVG Primitives (`render.py`)

Helper functions that emit SVG elements as text.

```python
def _polygon(points, *, fill, stroke=None, sw=1.0, ...): ...
def _path(points, *, stroke, sw, ...): ...
def _circle(cx, cy, r, *, fill=None, stroke=None, ...): ...
def _text(x, y, s, *, size=13, fill=INK, ...): ...
# ... etc
```

**Design:** Pure functions, no side effects. Emit SVG fragments.

**Pattern:** Each function handles SVG attribute normalization (opacity, stroke-width, dash patterns, etc.) so callers don't need XML knowledge.

**Example:**
```python
# Caller doesn't write SVG; it writes Python
_circle(500, 350, 20, fill=INK_DIM, stroke=INK, sw=1.5)
# Outputs:
# <circle cx="500.0" cy="350.0" r="20" fill="#b2a992" stroke="#e8e2d2" stroke-width="1.5"/>
```

---

### Terrain Generators

Functions that produce clusters of SVG elements for geographic features.

**Pattern:** Each terrain function accepts:
- `rng: random.Random` — seeded RNG for deterministic variation
- `config: MapConfig` — world data (locations, palette, canvas)
- Feature-specific parameters (density, scale, etc.)

**Returns:** List of SVG element strings.

**Examples:**
```python
def _mountains(rng: random.Random, config: MapConfig) -> List[str]:
    """Jagged mountain ring around the bowl."""
    # Uses config.palette.mountain for color
    # Uses seeded rng for peak variation
    return [_polygon(...), _polygon(...), ...]

def _forest(rng, config) -> List[str]:
    """Forest clumps with collision detection."""
    # Avoids roads (config.routes)
    # Avoids settlements (config.locations)
    # Uses rng for tree placement and scale
    return [_polygon(...), ...]
```

---

### MapRenderer Class

Orchestrates the rendering pipeline.

**Design (planned for Phase 2.5):**

```python
class MapRenderer:
    def __init__(self, config: MapConfig, seed: int = 7):
        self.config = config
        self.rng = random.Random(seed)
        self.elements: List[str] = []

    def add_background(self) -> None:
        # Background rect, gradient, atmosphere
        self.elements.extend(_background_elements(...))

    def add_terrain(self) -> None:
        # Mountains, hills, forests
        self.elements.extend(_mountains(self.rng, self.config))
        self.elements.extend(_forest(self.rng, self.config))

    def add_water(self) -> None:
        # Rivers, lakes, tributaries
        for route_name, points in self.config.routes.items():
            if route_name.startswith("river_"):
                self.elements.extend(_path(points, stroke=self.config.palette.water, ...))

    def add_routes(self) -> None:
        # Roads, trails, passages
        self.elements.extend(_path(self.config.routes["capital_road"], ...))

    def add_settlements(self) -> None:
        # Cities, villages
        for name, (cx, cy) in self.config.locations.items():
            self.elements.extend(_village(cx, cy, ..., label=name))

    def add_labels(self) -> None:
        # Text markers
        self.elements.append(_text(500, 44, "the valley of mists"))

    def render(self) -> str:
        """Assemble all layers into a single SVG document."""
        svg_start = f'<svg xmlns="..." width="{self.config.canvas_width}" ...>'
        svg_end = '</svg>'
        return svg_start + '\n'.join(self.elements) + svg_end
```

**Benefits:**
- Easy to add/remove layers
- Reorder rendering for desired depth
- Enable/disable features per world

---

## Data Flow

### User → CLI

```
User runs: python -m fantasy_map_generator --out map.svg --seed 42

↓

cli.py parses args → seed=42, out_prefix="map"

↓

render.write_map(Path("map"), seed=42, want_png=True)

↓

render.py calls MapRenderer(config=valley_config, seed=42).render()

↓

SVG string written to map.svg
```

### User → GUI

```
User opens: http://localhost:5000

↓

Browser loads HTML + JS controls

↓

User adjusts sliders (seed, terrain density, etc.)

↓

JavaScript POST /api/map with params

↓

gui.py creates MapRenderer, returns SVG

↓

JavaScript renders SVG in browser canvas
```

---

## Determinism & Randomness

**Key principle:** Same seed → same map. Different seed → different map.

**Implementation:** Pass `rng: random.Random` object (seeded once per render) through the call stack.

```python
render_map(seed=42):
    rng = random.Random(42)  # Deterministic
    return MapRenderer(config, seed=42).render()

# Result is deterministic: render_map(seed=42) == render_map(seed=42)
```

**Why:** Allows reproducible maps for testing, version control, and iteration.

---

## Extensibility

### Adding a New Terrain Type

```python
# In render.py
def _swamps(rng: random.Random, config: MapConfig) -> List[str]:
    """Boggy regions with murky water and reeds."""
    out: List[str] = []
    for location in config.swamp_locations:
        # Place swamp patches with collision detection
        out.extend(_polygon(..., fill=config.palette.swamp))
    return out

# In MapRenderer.add_terrain():
def add_terrain(self):
    # ... existing terrain ...
    self.elements.extend(_swamps(self.rng, self.config))
```

### Adding a New World

```python
# In worlds/example.py
EXAMPLE_WORLD = MapConfig(
    name="The Shattered Isles",
    canvas_width=1200,
    canvas_height=800,
    locations={"port_city": (600, 400), ...},
    routes={"trade_route": [(100, 200), (600, 400), ...], ...},
    palette=Palette(background="#1a3a4a", water="#4a9aff", ...),
)

# In GUI or CLI, users select: fantasy-map-generator --world shattered_isles
```

### Adding a New Feature

Any new feature should:
1. Accept `config: MapConfig` and `rng: random.Random`
2. Return `List[str]` (SVG elements)
3. Use `config.palette` for colors
4. Use `rng` for variation
5. Respect spatial constraints (check collision against routes/locations)

---

## Testing Strategy

### Unit Tests

Test individual functions in isolation.

```python
def test_mountains_generates_valid_svg():
    config = MapConfig(...)
    rng = random.Random(7)
    elements = _mountains(rng, config)
    assert all("<polygon" in el for el in elements)

def test_mountains_are_deterministic():
    rng1 = random.Random(7)
    rng2 = random.Random(7)
    assert _mountains(rng1, config) == _mountains(rng2, config)
```

### Integration Tests

Test that full render pipeline works.

```python
def test_valley_config_renders_without_error():
    svg = MapRenderer(VALLEY_CONFIG, seed=42).render()
    ET.fromstring(svg)  # Verify it's valid XML

def test_different_seeds_produce_different_svgs():
    svg1 = render_map(seed=1)
    svg2 = render_map(seed=2)
    assert svg1 != svg2
```

### Regression Tests

Verify that refactoring doesn't break Valley rendering.

```python
def test_valley_output_unchanged():
    """Generated SVG matches the original valley_of_mist_tools output."""
    # Compare against reference SVG generated from original mapgen.py
    reference = Path("docs/reference_valley.svg").read_text()
    actual = render_map(seed=7, config=VALLEY_CONFIG)
    assert actual == reference
```

---

## Performance Considerations

**Current:** Single-threaded, ~100ms per render on modern hardware.

**Bottlenecks:**
- `_forest()` collision detection (O(n²) placement attempts)
- PNG export via cairosvg (network I/O, subprocess spawn)

**Optimizations (if needed):**
- Parallel forest placement (already uses spatial grid, not RNG)
- Caching cairosvg subprocess
- Lazy PNG generation (render SVG immediately, cache PNG async)

**No optimization needed yet:** Maps render fast enough for interactive GUI (200ms per update is acceptable).

---

## Security

**Threat model:** GUI accepts user parameters (seed, world name, palette colors).

**Mitigations:**
- Seed is integer; reject non-numeric input
- World names are from a whitelist (WORLDS dict)
- Palette colors are validated as hex codes before use
- SVG output is sanitized (no `<script>` tags possible from parameter input)
- PNG export runs in subprocess with `--help` flags, no shell injection

**No SQL/database, no file uploads, no remote API calls → low risk.**

---

## Dependencies

**Core (no dependencies):** Standard library only.

**Optional:**
- `cairosvg` (PNG export; fails gracefully if missing)
- `flask` (GUI; fails gracefully if missing)

**Development:**
- `pytest` (testing)
- `ruff` (linting)
- `pdoc` (docs generation)

**Rationale:** Keep core dependencies minimal so the package is lightweight and portable.

---

## See Also

- **PLAN.md:** Implementation roadmap and milestones.
- **CLAUDE.md:** Project context and conventions.
- **mapgen_review.md:** Detailed analysis of the Valley code being extracted.
