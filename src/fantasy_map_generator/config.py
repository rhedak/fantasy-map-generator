"""Map configuration models.

MapConfig separates world data from rendering. Templates differ by layout,
style kit, landmass, biomes, and typed places—not only palette.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import asdict, dataclass, field, fields, is_dataclass
from typing import Any, Literal

Layout = Literal["bowl", "island", "archipelago", "coast", "interior", "ridge"]
StyleKit = Literal[
    "mist_bowl",
    "layered_island",
    "ink_parchment",
    "watercolor",
    "hypsometric",
    "rpg_symbols",
    "valley_parity",
]
Biome = Literal["forest", "desert", "swamp", "ice", "plain", "coast", "tundra"]
TreeStyle = Literal["triangle", "conifer", "canopy", "stamp"]
MountainKind = Literal["ring", "ridge", "stacked", "single"]
RouteKind = Literal["road", "trail", "river", "ferry"]
PlaceTier = Literal["hamlet", "village", "town", "city", "capital", "ruin", "castle", "camp"]

PLACE_TIERS: tuple[PlaceTier, ...] = (
    "hamlet",
    "village",
    "town",
    "city",
    "capital",
    "ruin",
    "castle",
    # A tent glyph rather than a building -- for a temporary/nomadic
    # settlement, not a smaller permanent one (see the Tumen's own doctrine
    # against shaping/settling the land, design.md's "Other powers").
    "camp",
)


def _slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return s or "feature"


def new_id(prefix: str = "id") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def make_meander_border(
    x_nominal: float,
    y_start: float,
    y_end: float,
    seed: int,
    amplitude: float = 70.0,
    step: float = 18.0,
    reversal_chance: float = 0.7,
) -> list[tuple[float, float]]:
    """A jagged, single-valued-in-y border line zigzagging around x_nominal --
    for a political border that reads as organic (think Europe's borders:
    frequent sharp back-and-forth, not a smooth drift) rather than a ruler-
    straight seam. Biases toward flipping direction each step so short runs
    in the same direction (which read as a diagonal line at map scale) stay
    rare. Deterministic per seed so it can be baked into a static world
    config and shared by the two BiomeRegions it separates (same points on
    both sides, so their territories always meet exactly with no gap or
    overlap)."""
    import random as _random

    rng = _random.Random(seed)
    pts: list[tuple[float, float]] = [(x_nominal, y_start)]
    x, y = x_nominal, y_start
    direction = rng.choice([-1, 1])
    while y < y_end:
        y = min(y + step, y_end)
        if rng.random() < reversal_chance:
            direction *= -1
        x += direction * rng.uniform(amplitude * 0.35, amplitude * 0.85)
        x = max(x_nominal - amplitude, min(x_nominal + amplitude, x))
        pts.append((x, y))
    return pts


@dataclass
class LandBody:
    """A landmass silhouette (ellipse or polygon)."""

    kind: Literal["ellipse", "polygon"] = "ellipse"
    center: tuple[float, float] = (500.0, 350.0)
    radii: tuple[float, float] = (200.0, 150.0)
    rough: float = 0.0
    points: list[tuple[float, float]] = field(default_factory=list)
    fill: str | None = None
    id: str = ""


@dataclass
class BiomeRegion:
    """Soft biome underlay inside the map."""

    name: str
    biome: Biome
    center: tuple[float, float]
    radii: tuple[float, float]
    density: float = 0.5
    fill: str | None = None
    # When either is set, this region renders as a territory following the
    # actual landmass coastline (clipped against these west/east border
    # curves, see make_meander_border) instead of a freestanding ellipse --
    # for political/kingdom color zones that should match the land they
    # occupy. Pass the *same* border object to the two regions it separates
    # so their territories meet exactly, no gap or overlap. None on a side
    # means "no clip there" (the region runs to the coast/canvas edge).
    # center/radii are still used for texture scatter (dune hatch etc.) and
    # as the anchor for this region's own small subtitle label.
    left_border: list[tuple[float, float]] | None = None
    right_border: list[tuple[float, float]] | None = None
    # When True (and left_border/right_border are unset), this region's
    # ellipse is clipped against the actual landmass coastline instead of
    # drawn as a freestanding ellipse -- for corner/local dressing (a frost
    # tint, a hot-sand tint) that shouldn't spill out over the ocean.
    clip_to_land: bool = False
    id: str = ""


@dataclass
class RegionLabel:
    """A large political/kingdom name spanning its own territory, distinct
    from BiomeRegion's smaller, density-gated biome label (e.g. a kingdom
    name like "WODENSREICH" versus a biome note like "Scorched Wastes"
    inside it -- both can appear on the same map)."""

    name: str
    center: tuple[float, float]
    font_size: float = 30.0
    rotation: float = 0.0
    id: str = ""


@dataclass
class MountainRange:
    """Mountain generator descriptor."""

    kind: MountainKind = "ring"
    center: tuple[float, float] | None = None
    radii: tuple[float, float] | None = None
    points: list[tuple[float, float]] = field(default_factory=list)
    levels: int = 1
    density: float = 1.0
    mouth_start_deg: float = 0.0
    mouth_end_deg: float = 0.0
    num_peaks: int = 54
    # For kind="ring": radii is the ring's footprint (always literal); size
    # scales only the peak glyphs (height + base width) drawn around that
    # footprint, so footprint and peak height/size are independently
    # adjustable rather than both riding on one shared radii*size product.
    size: float = 50.0
    rotation: float = 0.0
    id: str = ""


@dataclass
class ForestStand:
    """Vegetation cluster."""

    center: tuple[float, float]
    radii: tuple[float, float]
    tree_style: TreeStyle = "triangle"
    density: float = 0.5
    num_clumps: int = 8
    id: str = ""


@dataclass
class WaterBody:
    """A standalone inland lake (as opposed to Route(kind="river"), a
    flowing line feature). Small and simple by design -- an ellipse, filled
    with the palette's water color."""

    center: tuple[float, float]
    radii: tuple[float, float]
    fill: str | None = None
    id: str = ""


@dataclass
class Place:
    """Named settlement / POI. Dict key in MapConfig.places is stable id."""

    x: float
    y: float
    name: str = "Unnamed"
    tier: PlaceTier = "village"
    id: str = ""
    icon: str | None = None
    locked: bool = True

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)


@dataclass
class Route:
    """Path between places (road, trail, river, ferry)."""

    points: list[tuple[float, float]]
    kind: RouteKind = "road"
    id: str = ""
    label: str = ""
    locked: bool = True


@dataclass
class Decor:
    """Optional cartographic chrome."""

    border: bool = False
    compass: bool = False
    scale: bool = False
    cartouche: bool = False
    paper_texture: bool = False


@dataclass
class Palette:
    """Color scheme for a map."""

    background: str = "#202634"
    land: str = "#2a3344"
    mountain: str = "#343e54"
    mountain_stroke: str = "#1c2333"
    water: str = "#6f9ec4"
    water_tributary: str = "#5a8fb5"
    water_deep: str = "#3a6a8a"
    paddy: str = "#5d7f62"
    forest: str = "#3d5c46"
    desert: str = "#c4a574"
    swamp: str = "#4a5c3a"
    ice: str = "#d8e4f0"
    plain: str = "#6a7a5a"
    coast: str = "#4a7a6a"
    settlement: str = "#b9a888"
    settlement_roof: str = "#7a6a4f"
    road: str = "#d9c9a3"
    road_dim: str = "#a99670"
    text: str = "#e8e2d2"
    text_dim: str = "#b2a992"
    text_faint: str = "#8f8777"
    mist_wall: str = "#dfe6ee"
    mist_wall_stroke: str = "#c3ccd8"
    passage: str = "#aeb9cc"
    zone: str = "#333c4c"
    old_wall: str = "#8b93a6"
    palace_roof: str = "#33456e"
    palace_roof_light: str = "#4d6395"
    palace_trim: str = "#c7ceda"
    ink: str = "#1a1510"
    paper: str = "#e8dcc8"
    gold: str = "#c9a227"
    gradient_stops: list[tuple[float, str]] = field(
        default_factory=lambda: [
            (0.00, "#f3f6fa"),
            (0.28, "#cdd6e0"),
            (0.55, "#96a6ba"),
            (0.80, "#5c6a80"),
            (1.00, "#3a4254"),
        ]
    )


@dataclass
class MapConfig:
    """Configuration for map generation."""

    name: str = "Untitled Fantasy World"
    canvas_width: int = 1000
    canvas_height: int = 700
    layout: Layout = "bowl"
    style_kit: StyleKit = "mist_bowl"

    landmass: list[LandBody] = field(default_factory=list)
    biome_regions: list[BiomeRegion] = field(default_factory=list)
    region_labels: list[RegionLabel] = field(default_factory=list)
    mountain_ranges: dict[str, MountainRange] = field(default_factory=dict)
    forest_stands: list[ForestStand] = field(default_factory=list)
    lakes: list[WaterBody] = field(default_factory=list)
    places: dict[str, Place] = field(default_factory=dict)
    routes: dict[str, Route] = field(default_factory=dict)

    # Ocean ship glyphs (position-only; world authors place them by hand,
    # same as every other manually-authored map element here) and a legend
    # box (kind, label) pairs; both render only if non-empty.
    ships: list[tuple[float, float]] = field(default_factory=list)
    volcanoes: list[tuple[float, float]] = field(default_factory=list)
    # Sleeping Gods sacred-site landmarks (design.md's "Sleeping Gods"): each
    # a (x, y, kind) tuple, kind one of "temple" (a still-standing built
    # monument) or "kurgan" (an unbuilt natural site -- mound and standing
    # stones, no structure, for a culture whose doctrine forbids building
    # one, e.g. the Tumen).
    sacred_sites: list[tuple[float, float, str]] = field(default_factory=list)
    legend_entries: list[tuple[str, str]] = field(default_factory=list)
    legend_pos: tuple[float, float] | None = None

    # Backward-compatible aliases filled by normalize() if places empty
    locations: dict[str, tuple[float, float]] = field(default_factory=dict)

    palette: Palette = field(default_factory=Palette)
    decor: Decor = field(default_factory=Decor)
    detail: float = 0.55
    coast_roughness: float = 0.15
    title_x: float | None = None
    title_y: float | None = None
    title_font_size: float = 26.0
    title_bold: bool = False
    title_italic: bool = False

    def normalize(self) -> MapConfig:
        """Return a config with places/routes filled and stable ids assigned."""
        places: dict[str, Place] = {}
        if self.places:
            for key, place in self.places.items():
                if not isinstance(place, Place):
                    continue
                pid = place.id or key or new_id("place")
                name = place.name if place.name and place.name != "Unnamed" else key
                places[pid] = Place(
                    x=float(place.x),
                    y=float(place.y),
                    name=name,
                    tier=place.tier,
                    id=pid,
                    icon=place.icon,
                    locked=place.locked,
                )
        elif self.locations:
            for name, xy in self.locations.items():
                pid = _slug(name)
                places[pid] = Place(
                    x=float(xy[0]),
                    y=float(xy[1]),
                    name=name,
                    tier="village",
                    id=pid,
                    locked=True,
                )

        routes: dict[str, Route] = {}
        for key, route in self.routes.items():
            if isinstance(route, Route):
                rid = route.id or key or new_id("route")
                pts = [(float(x), float(y)) for x, y in route.points]
                routes[rid] = Route(
                    points=pts,
                    kind=route.kind,
                    id=rid,
                    label=route.label or key,
                    locked=route.locked,
                )
            else:
                pts = [(float(x), float(y)) for x, y in route]  # type: ignore[union-attr]
                kind: RouteKind = "river" if _legacy_river_name(str(key)) else "road"
                rid = _slug(str(key))
                routes[rid] = Route(points=pts, kind=kind, id=rid, label=str(key), locked=True)

        def _with_ids_land(items: list[LandBody]) -> list[LandBody]:
            out = []
            for i, b in enumerate(items):
                bid = b.id or f"land_{i}"
                out.append(
                    LandBody(
                        kind=b.kind,
                        center=(float(b.center[0]), float(b.center[1])),
                        radii=(float(b.radii[0]), float(b.radii[1])),
                        rough=b.rough,
                        points=[(float(x), float(y)) for x, y in b.points],
                        fill=b.fill,
                        id=bid,
                    )
                )
            return out

        def _with_ids_biome(items: list[BiomeRegion]) -> list[BiomeRegion]:
            out = []
            for i, b in enumerate(items):
                out.append(
                    BiomeRegion(
                        name=b.name,
                        biome=b.biome,
                        center=(float(b.center[0]), float(b.center[1])),
                        radii=(float(b.radii[0]), float(b.radii[1])),
                        density=b.density,
                        fill=b.fill,
                        left_border=[(float(x), float(y)) for x, y in b.left_border] if b.left_border else None,
                        right_border=[(float(x), float(y)) for x, y in b.right_border] if b.right_border else None,
                        clip_to_land=b.clip_to_land,
                        id=b.id or f"biome_{i}",
                    )
                )
            return out

        def _with_ids_mtn(items: dict[str, MountainRange] | list[MountainRange]) -> dict[str, MountainRange]:
            out: dict[str, MountainRange] = {}
            if isinstance(items, list):
                for i, m in enumerate(items):
                    mid = m.id or f"mountain_{i}"
                    out[mid] = MountainRange(
                        kind=m.kind,
                        center=m.center,
                        radii=m.radii,
                        points=[(float(x), float(y)) for x, y in m.points],
                        levels=m.levels,
                        density=m.density,
                        mouth_start_deg=m.mouth_start_deg,
                        mouth_end_deg=m.mouth_end_deg,
                        num_peaks=m.num_peaks,
                        size=m.size if hasattr(m, 'size') else 50.0,
                        rotation=m.rotation if hasattr(m, 'rotation') else 0.0,
                        id=mid,
                    )
            else:
                for k, m in items.items():
                    mid = m.id or k or new_id("mountain")
                    out[mid] = MountainRange(
                        kind=m.kind,
                        center=m.center,
                        radii=m.radii,
                        points=[(float(x), float(y)) for x, y in m.points],
                        levels=m.levels,
                        density=m.density,
                        mouth_start_deg=m.mouth_start_deg,
                        mouth_end_deg=m.mouth_end_deg,
                        num_peaks=m.num_peaks,
                        size=m.size if hasattr(m, 'size') else 50.0,
                        rotation=m.rotation if hasattr(m, 'rotation') else 0.0,
                        id=mid,
                    )
            return out

        def _with_ids_region_labels(items: list[RegionLabel]) -> list[RegionLabel]:
            out = []
            for i, r in enumerate(items):
                out.append(
                    RegionLabel(
                        name=r.name,
                        center=(float(r.center[0]), float(r.center[1])),
                        font_size=r.font_size,
                        rotation=r.rotation,
                        id=r.id or f"region_label_{i}",
                    )
                )
            return out

        def _with_ids_lakes(items: list[WaterBody]) -> list[WaterBody]:
            out = []
            for i, w in enumerate(items):
                out.append(
                    WaterBody(
                        center=(float(w.center[0]), float(w.center[1])),
                        radii=(float(w.radii[0]), float(w.radii[1])),
                        fill=w.fill,
                        id=w.id or f"lake_{i}",
                    )
                )
            return out

        def _with_ids_forest(items: list[ForestStand]) -> list[ForestStand]:
            out = []
            for i, f in enumerate(items):
                out.append(
                    ForestStand(
                        center=(float(f.center[0]), float(f.center[1])),
                        radii=(float(f.radii[0]), float(f.radii[1])),
                        tree_style=f.tree_style,
                        density=f.density,
                        num_clumps=f.num_clumps,
                        id=f.id or f"forest_{i}",
                    )
                )
            return out

        return MapConfig(
            name=self.name,
            canvas_width=self.canvas_width,
            canvas_height=self.canvas_height,
            layout=self.layout,
            style_kit=self.style_kit,
            landmass=_with_ids_land(list(self.landmass)),
            biome_regions=_with_ids_biome(list(self.biome_regions)),
            region_labels=_with_ids_region_labels(list(self.region_labels)),
            mountain_ranges=_with_ids_mtn(self.mountain_ranges),
            forest_stands=_with_ids_forest(list(self.forest_stands)),
            lakes=_with_ids_lakes(list(self.lakes)),
            places=places,
            routes=routes,
            locations={p.name: p.pos for p in places.values()},
            ships=[(float(x), float(y)) for x, y in self.ships],
            volcanoes=[(float(x), float(y)) for x, y in self.volcanoes],
            sacred_sites=[(float(x), float(y), str(k)) for x, y, k in self.sacred_sites],
            legend_entries=list(self.legend_entries),
            legend_pos=self.legend_pos,
            palette=self.palette,
            decor=self.decor,
            detail=self.detail,
            coast_roughness=self.coast_roughness,
            title_x=self.title_x,
            title_y=self.title_y,
            title_font_size=self.title_font_size,
            title_bold=self.title_bold,
            title_italic=self.title_italic,
        )

    def validate(self) -> None:
        """Validate the configuration."""
        if self.canvas_width <= 0 or self.canvas_height <= 0:
            raise ValueError("canvas dimensions must be positive")
        if not (0.0 <= self.detail <= 1.0):
            raise ValueError("detail must be between 0 and 1")
        if not (0.0 <= self.coast_roughness <= 1.0):
            raise ValueError("coast_roughness must be between 0 and 1")

        cfg = self.normalize()
        for pid, place in cfg.places.items():
            x, y = place.x, place.y
            if not (0 <= x <= cfg.canvas_width and 0 <= y <= cfg.canvas_height):
                raise ValueError(f"location {place.name!r} ({pid}) is outside the canvas")
        for rid, route in cfg.routes.items():
            if len(route.points) < 2:
                raise ValueError(f"route {rid!r} needs at least two waypoints")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-friendly dict."""
        return _to_plain(self.normalize())

    @staticmethod
    def from_dict(data: dict[str, Any]) -> MapConfig:
        """Deserialize from JSON dict (editor / file load)."""
        if not isinstance(data, dict):
            raise TypeError("config must be an object")
        return _mapconfig_from_dict(data).normalize()


def place(name: str, x: float, y: float, tier: PlaceTier = "village", **kwargs: Any) -> Place:
    """Helper to build a Place with id derived from name."""
    pid = kwargs.pop("id", None) or _slug(name)
    return Place(x=x, y=y, name=name, tier=tier, id=pid, **kwargs)


def route(
    points: list[tuple[float, float]],
    kind: RouteKind = "road",
    label: str = "",
    **kwargs: Any,
) -> Route:
    rid = kwargs.pop("id", None) or new_id("route")
    return Route(points=points, kind=kind, id=rid, label=label, **kwargs)


def _legacy_river_name(name: str) -> bool:
    key = name.lower()
    return "river" in key or key.startswith("water")


def _to_plain(obj: Any) -> Any:
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: _to_plain(getattr(obj, f.name)) for f in fields(obj)}
    if isinstance(obj, dict):
        return {str(k): _to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_plain(v) for v in obj]
    return obj


def _as_tuple2(value: Any) -> tuple[float, float]:
    if value is None:
        return (0.0, 0.0)
    return (float(value[0]), float(value[1]))


def _as_points(value: Any) -> list[tuple[float, float]]:
    if not value:
        return []
    return [_as_tuple2(p) for p in value]


def _place_from_dict(key: str, data: Any) -> Place:
    if isinstance(data, Place):
        return data
    if isinstance(data, (list, tuple)) and len(data) >= 2:
        return Place(x=float(data[0]), y=float(data[1]), name=key, id=_slug(key))
    if not isinstance(data, dict):
        raise TypeError(f"invalid place for {key!r}")
    pid = str(data.get("id") or key or new_id("place"))
    name = str(data.get("name") or key)
    tier = data.get("tier") or "village"
    if tier not in PLACE_TIERS:
        tier = "village"
    return Place(
        x=float(data.get("x", 0)),
        y=float(data.get("y", 0)),
        name=name,
        tier=tier,
        id=pid,
        icon=data.get("icon"),
        locked=bool(data.get("locked", True)),
    )


def _route_from_dict(key: str, data: Any) -> Route:
    if isinstance(data, Route):
        return data
    if isinstance(data, list):
        kind: RouteKind = "river" if _legacy_river_name(key) else "road"
        return Route(points=_as_points(data), kind=kind, id=_slug(key), label=key)
    if not isinstance(data, dict):
        raise TypeError(f"invalid route for {key!r}")
    kind_s = data.get("kind") or ("river" if _legacy_river_name(key) else "road")
    if kind_s not in ("road", "trail", "river", "ferry"):
        kind_s = "road"
    rid = str(data.get("id") or key or new_id("route"))
    return Route(
        points=_as_points(data.get("points")),
        kind=kind_s,
        id=rid,
        label=str(data.get("label") or key),
        locked=bool(data.get("locked", True)),
    )


def _mapconfig_from_dict(data: dict[str, Any]) -> MapConfig:
    places_in = data.get("places") or {}
    places: dict[str, Place] = {}
    if isinstance(places_in, dict):
        for k, v in places_in.items():
            p = _place_from_dict(str(k), v)
            places[p.id or str(k)] = p

    # legacy locations
    locations = data.get("locations") or {}
    if not places and isinstance(locations, dict):
        for name, xy in locations.items():
            p = _place_from_dict(str(name), xy)
            places[p.id] = p

    routes_in = data.get("routes") or {}
    routes: dict[str, Route] = {}
    if isinstance(routes_in, dict):
        for k, v in routes_in.items():
            r = _route_from_dict(str(k), v)
            routes[r.id or str(k)] = r

    def land_list(raw: Any) -> list[LandBody]:
        out: list[LandBody] = []
        for i, item in enumerate(raw or []):
            if not isinstance(item, dict):
                continue
            out.append(
                LandBody(
                    kind=item.get("kind") or "ellipse",
                    center=_as_tuple2(item.get("center") or (500, 350)),
                    radii=_as_tuple2(item.get("radii") or (200, 150)),
                    rough=float(item.get("rough") or 0),
                    points=_as_points(item.get("points")),
                    fill=item.get("fill"),
                    id=str(item.get("id") or f"land_{i}"),
                )
            )
        return out

    def biome_list(raw: Any) -> list[BiomeRegion]:
        out: list[BiomeRegion] = []
        for i, item in enumerate(raw or []):
            if not isinstance(item, dict):
                continue
            out.append(
                BiomeRegion(
                    name=str(item["name"]) if item.get("name") is not None else f"Biome {i}",
                    biome=item.get("biome") or "plain",
                    center=_as_tuple2(item.get("center") or (500, 350)),
                    radii=_as_tuple2(item.get("radii") or (80, 60)),
                    density=float(item.get("density") or 0.5),
                    fill=item.get("fill"),
                    left_border=_as_points(item["left_border"]) if item.get("left_border") else None,
                    right_border=_as_points(item["right_border"]) if item.get("right_border") else None,
                    clip_to_land=bool(item.get("clip_to_land", False)),
                    id=str(item.get("id") or f"biome_{i}"),
                )
            )
        return out

    def region_label_list(raw: Any) -> list[RegionLabel]:
        out: list[RegionLabel] = []
        for i, item in enumerate(raw or []):
            if not isinstance(item, dict):
                continue
            out.append(
                RegionLabel(
                    name=str(item.get("name") or f"Region {i}"),
                    center=_as_tuple2(item.get("center") or (500, 350)),
                    font_size=float(item.get("font_size") or 30.0),
                    rotation=float(item.get("rotation") or 0.0),
                    id=str(item.get("id") or f"region_label_{i}"),
                )
            )
        return out

    def lake_list(raw: Any) -> list[WaterBody]:
        out: list[WaterBody] = []
        for i, item in enumerate(raw or []):
            if not isinstance(item, dict):
                continue
            out.append(
                WaterBody(
                    center=_as_tuple2(item.get("center") or (500, 350)),
                    radii=_as_tuple2(item.get("radii") or (20, 15)),
                    fill=item.get("fill"),
                    id=str(item.get("id") or f"lake_{i}"),
                )
            )
        return out

    def mtn_list(raw: Any) -> dict[str, MountainRange]:
        out: dict[str, MountainRange] = {}
        if isinstance(raw, dict):
            for k, item in raw.items():
                if not isinstance(item, dict):
                    continue
                mid = str(item.get("id") or k or new_id("mountain"))
                center = item.get("center")
                radii = item.get("radii")
                out[mid] = MountainRange(
                    kind=item.get("kind") or "ring",
                    center=_as_tuple2(center) if center else None,
                    radii=_as_tuple2(radii) if radii else None,
                    points=_as_points(item.get("points")),
                    levels=int(item.get("levels") or 1),
                    density=float(item.get("density") or 1.0),
                    mouth_start_deg=float(item.get("mouth_start_deg") or 0),
                    mouth_end_deg=float(item.get("mouth_end_deg") or 0),
                    num_peaks=int(item.get("num_peaks") or 54),
                    size=float(item.get("size") or 50.0),
                    rotation=float(item.get("rotation") or 0.0),
                    id=mid,
                )
        else:
            for i, item in enumerate(raw or []):
                if not isinstance(item, dict):
                    continue
                mid = str(item.get("id") or f"mountain_{i}")
                center = item.get("center")
                radii = item.get("radii")
                out[mid] = MountainRange(
                    kind=item.get("kind") or "ring",
                    center=_as_tuple2(center) if center else None,
                    radii=_as_tuple2(radii) if radii else None,
                    points=_as_points(item.get("points")),
                    levels=int(item.get("levels") or 1),
                    density=float(item.get("density") or 1.0),
                    mouth_start_deg=float(item.get("mouth_start_deg") or 0),
                    mouth_end_deg=float(item.get("mouth_end_deg") or 0),
                    num_peaks=int(item.get("num_peaks") or 54),
                    size=float(item.get("size") or 50.0),
                    rotation=float(item.get("rotation") or 0.0),
                    id=mid,
                )
        return out

    def forest_list(raw: Any) -> list[ForestStand]:
        out: list[ForestStand] = []
        for i, item in enumerate(raw or []):
            if not isinstance(item, dict):
                continue
            out.append(
                ForestStand(
                    center=_as_tuple2(item.get("center") or (500, 350)),
                    radii=_as_tuple2(item.get("radii") or (60, 40)),
                    tree_style=item.get("tree_style") or "triangle",
                    density=float(item.get("density") or 0.5),
                    num_clumps=int(item.get("num_clumps") or 8),
                    id=str(item.get("id") or f"forest_{i}"),
                )
            )
        return out

    palette = Palette()
    if isinstance(data.get("palette"), dict):
        p_in = data["palette"]
        kwargs = {}
        for f in fields(Palette):
            if f.name in p_in:
                val = p_in[f.name]
                if f.name == "gradient_stops" and val is not None:
                    kwargs[f.name] = [(float(a), str(b)) for a, b in val]
                else:
                    kwargs[f.name] = val
        palette = Palette(**kwargs)

    decor = Decor()
    if isinstance(data.get("decor"), dict):
        d_in = data["decor"]
        decor = Decor(
            border=bool(d_in.get("border", False)),
            compass=bool(d_in.get("compass", False)),
            scale=bool(d_in.get("scale", False)),
            cartouche=bool(d_in.get("cartouche", False)),
            paper_texture=bool(d_in.get("paper_texture", False)),
        )

    return MapConfig(
        name=str(data.get("name") or "Untitled Fantasy World"),
        canvas_width=int(data.get("canvas_width") or 1000),
        canvas_height=int(data.get("canvas_height") or 700),
        layout=data.get("layout") or "bowl",
        style_kit=data.get("style_kit") or "mist_bowl",
        landmass=land_list(data.get("landmass")),
        biome_regions=biome_list(data.get("biome_regions")),
        region_labels=region_label_list(data.get("region_labels")),
        mountain_ranges=mtn_list(data.get("mountain_ranges")),
        forest_stands=forest_list(data.get("forest_stands")),
        lakes=lake_list(data.get("lakes")),
        places=places,
        routes=routes,
        ships=[_as_tuple2(p) for p in (data.get("ships") or [])],
        volcanoes=[_as_tuple2(p) for p in (data.get("volcanoes") or [])],
        sacred_sites=[
            (float(x), float(y), str(k)) for x, y, k in (data.get("sacred_sites") or [])
        ],
        legend_entries=[(str(a), str(b)) for a, b in (data.get("legend_entries") or [])],
        legend_pos=_as_tuple2(data["legend_pos"]) if data.get("legend_pos") else None,
        palette=palette,
        decor=decor,
        detail=float(data.get("detail") if data.get("detail") is not None else 0.55),
        coast_roughness=float(
            data.get("coast_roughness") if data.get("coast_roughness") is not None else 0.15
        ),
        title_x=float(data.get("title_x")) if data.get("title_x") is not None else None,
        title_y=float(data.get("title_y")) if data.get("title_y") is not None else None,
        title_font_size=float(data.get("title_font_size") if data.get("title_font_size") is not None else 26.0),
        title_bold=bool(data.get("title_bold", False)),
        title_italic=bool(data.get("title_italic", False)),
    )


# silence unused import warning if asdict unused
_ = asdict
