"""Client-side bridge: Flask-free equivalents of the GUI API endpoints.

Loaded into Pyodide by web/index.html. Each function takes plain JSON-able
arguments and returns a JSON string, so the JavaScript side can just
``JSON.parse`` the result without touching proxy objects.

This module is pure stdlib Python and is also exercised by CPython tests.
"""

from __future__ import annotations

import json

from fantasy_map_generator.config import MapConfig
from fantasy_map_generator.render import render_map
from fantasy_map_generator.valley import extract_world_from_svg
from fantasy_map_generator.worlds import WORLDS, random_world

PRESETS: dict[str, tuple[str, MapConfig | None, int | None]] = {
    world_id: (config.name, config, 42) for world_id, config in WORLDS.items()
}
PRESETS["random"] = ("Random World", None, None)


def _clamp01(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, v))


def _resolve_config(data: dict, seed: int) -> MapConfig:
    """Prefer explicit config JSON; else preset id."""
    if data.get("config"):
        return MapConfig.from_dict(data["config"])
    preset_id = data.get("preset", "valley")
    if preset_id not in PRESETS:
        raise KeyError(preset_id)
    _name, config_or_none, _seed = PRESETS[preset_id]
    if config_or_none is None:
        return random_world(seed)
    return MapConfig.from_dict(config_or_none.to_dict())


def presets_json() -> str:
    presets = []
    for preset_id, (name, config, seed) in PRESETS.items():
        preview_svg = None
        cfg_dict = None
        try:
            cfg = config if config is not None else random_world(42)
            cfg = cfg.normalize()
            preview_svg = render_map(config=cfg, seed=seed or 42)
            cfg_dict = cfg.to_dict()
        except Exception:
            pass
        presets.append(
            {
                "id": preset_id,
                "name": name,
                "preview": preview_svg,
                "layout": (config.layout if config else "interior"),
                "config": cfg_dict,
            }
        )
    return json.dumps(presets)


def render_json(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})

    def _parse_knobs(d: dict):
        try:
            seed = int(d.get("seed", 42))
        except (ValueError, TypeError):
            seed = 42
        return seed, _clamp01(d.get("detail")), _clamp01(d.get("coast_roughness"))

    seed, detail, roughness = _parse_knobs(payload)
    selected_id = payload.get("selected_id") or None
    try:
        config = _resolve_config(payload, seed)
    except KeyError:
        return json.dumps({"error": f"Unknown preset: {payload.get('preset')}"})
    except Exception as e:
        return json.dumps({"error": f"Invalid config: {e}"})

    try:
        if detail is not None:
            config.detail = detail
        if roughness is not None:
            config.coast_roughness = roughness
        svg = render_map(
            config=config,
            seed=seed,
            detail=detail,
            coast_roughness=roughness,
            selected_id=selected_id,
            interactive=True,
        )
        return json.dumps(
            {
                "svg": svg,
                "seed": seed,
                "config": config.to_dict(),
                "detail": config.detail,
                "coast_roughness": config.coast_roughness,
            }
        )
    except Exception as e:
        return json.dumps({"error": str(e)})


def download_json(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    format_ = payload.get("format", "svg")
    try:
        seed = int(payload.get("seed", 42))
    except (ValueError, TypeError):
        seed = 42
    detail = _clamp01(payload.get("detail"))
    roughness = _clamp01(payload.get("coast_roughness"))
    try:
        config = _resolve_config(payload, seed)
    except Exception as e:
        return json.dumps({"error": str(e)})

    try:
        if format_ == "json":
            return json.dumps(
                {
                    "mime": "application/json",
                    "filename": f"world-{seed}.json",
                    "data": json.dumps(config.to_dict(), indent=2),
                }
            )
        if format_ == "svg":
            svg = render_map(
                config=config,
                seed=seed,
                detail=detail,
                coast_roughness=roughness,
                embed_world=True,
                interactive=True,
            )
            return json.dumps(
                {
                    "mime": "image/svg+xml",
                    "filename": f"map-{seed}.svg",
                    "data": svg,
                }
            )
        return json.dumps({"error": "PNG export is not available on this static build"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def normalize_json(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        cfg = MapConfig.from_dict(payload.get("config") or payload)
        cfg.validate()
        return json.dumps({"config": cfg.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def add_mountain(data: str) -> str:
    """Add a new mountain range to the config."""
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))

        kind = payload.get("kind", "ridge")
        points = payload.get("points", [])
        center = payload.get("center")
        radii = payload.get("radii")
        density = float(payload.get("density", 0.7))

        from fantasy_map_generator.config import MountainRange, new_id

        mid = new_id("mountain")
        mountain = MountainRange(
            kind=kind,
            center=tuple(center) if center else None,
            radii=tuple(radii) if radii else None,
            points=[(float(x), float(y)) for x, y in points],
            density=density,
        )

        config.mountain_ranges[mid] = mountain
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def update_mountain(data: str) -> str:
    """Update a mountain's properties."""
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        mid = payload.get("id")
        if not mid or mid not in config.mountain_ranges:
            return json.dumps({"error": f"Mountain {mid} not found"})

        mr = config.mountain_ranges[mid]

        if "density" in payload:
            mr.density = float(payload["density"])
        if "kind" in payload:
            mr.kind = payload["kind"]
        if "points" in payload:
            mr.points = [(float(x), float(y)) for x, y in payload["points"]]
        if payload.get("center"):
            mr.center = tuple(payload["center"])
        if payload.get("radii"):
            mr.radii = tuple(payload["radii"])

        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def delete_mountain(data: str) -> str:
    """Delete a mountain from the config."""
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        mid = payload.get("id")
        if not mid or mid not in config.mountain_ranges:
            return json.dumps({"error": f"Mountain {mid} not found"})

        del config.mountain_ranges[mid]
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _index_from_id(prefix: str, item_id: str) -> int | None:
    """Parse the trailing index out of an index-keyed id like "ship_3" (see
    render.py's comment on why ships/volcanoes/sacred_sites, plain tuples
    with no id field of their own, use position in the list as their id)."""
    if not item_id or not item_id.startswith(prefix + "_"):
        return None
    try:
        return int(item_id[len(prefix) + 1 :])
    except ValueError:
        return None


def add_biome_region(data: str) -> str:
    """Add a new biome/territory region (a freestanding ellipse tint, not a
    political territory -- those need left_border/right_border set by hand,
    see BiomeRegion's own docstring, not something the GUI can generate)."""
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        from fantasy_map_generator.config import BiomeRegion, new_id

        rid = new_id("biome")
        region = BiomeRegion(
            name=str(payload.get("name", "")),
            biome=payload.get("biome", "plain"),
            center=tuple(payload.get("center", (500, 350))),
            radii=tuple(payload.get("radii", (80, 60))),
            density=float(payload.get("density", 0.5)),
            fill=payload.get("fill"),
            id=rid,
        )
        config.biome_regions.append(region)
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def update_biome_region(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        rid = payload.get("id")
        region = next((r for r in config.biome_regions if r.id == rid), None)
        if region is None:
            return json.dumps({"error": f"Biome region {rid} not found"})
        if "name" in payload:
            region.name = str(payload["name"])
        if "biome" in payload:
            region.biome = payload["biome"]
        if payload.get("center"):
            region.center = tuple(payload["center"])
        if payload.get("radii"):
            region.radii = tuple(payload["radii"])
        if "density" in payload:
            region.density = float(payload["density"])
        if "fill" in payload:
            region.fill = payload["fill"]
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def delete_biome_region(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        rid = payload.get("id")
        before = len(config.biome_regions)
        config.biome_regions = [r for r in config.biome_regions if r.id != rid]
        if len(config.biome_regions) == before:
            return json.dumps({"error": f"Biome region {rid} not found"})
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def add_region_label(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        from fantasy_map_generator.config import RegionLabel, new_id

        lid = new_id("region_label")
        label = RegionLabel(
            name=str(payload.get("name", "New Region")),
            center=tuple(payload.get("center", (500, 350))),
            font_size=float(payload.get("font_size", 30.0)),
            rotation=float(payload.get("rotation", 0.0)),
            id=lid,
        )
        config.region_labels.append(label)
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def update_region_label(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        lid = payload.get("id")
        label = next((r for r in config.region_labels if r.id == lid), None)
        if label is None:
            return json.dumps({"error": f"Region label {lid} not found"})
        if "name" in payload:
            label.name = str(payload["name"])
        if payload.get("center"):
            label.center = tuple(payload["center"])
        if "font_size" in payload:
            label.font_size = float(payload["font_size"])
        if "rotation" in payload:
            label.rotation = float(payload["rotation"])
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def delete_region_label(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        lid = payload.get("id")
        before = len(config.region_labels)
        config.region_labels = [r for r in config.region_labels if r.id != lid]
        if len(config.region_labels) == before:
            return json.dumps({"error": f"Region label {lid} not found"})
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def add_lake(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        from fantasy_map_generator.config import WaterBody, new_id

        wid = new_id("lake")
        lake = WaterBody(
            center=tuple(payload.get("center", (500, 350))),
            radii=tuple(payload.get("radii", (20, 15))),
            fill=payload.get("fill"),
            id=wid,
        )
        config.lakes.append(lake)
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def update_lake(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        wid = payload.get("id")
        lake = next((w for w in config.lakes if w.id == wid), None)
        if lake is None:
            return json.dumps({"error": f"Lake {wid} not found"})
        if payload.get("center"):
            lake.center = tuple(payload["center"])
        if payload.get("radii"):
            lake.radii = tuple(payload["radii"])
        if "fill" in payload:
            lake.fill = payload["fill"]
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def delete_lake(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        wid = payload.get("id")
        before = len(config.lakes)
        config.lakes = [w for w in config.lakes if w.id != wid]
        if len(config.lakes) == before:
            return json.dumps({"error": f"Lake {wid} not found"})
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


# Ships, volcanoes, and sacred sites are plain tuple lists (no id field of
# their own), so add/update/delete work by list index rather than by a
# stable id -- see render.py's own comment on the same tradeoff. Three near-
# identical trios rather than one generic function: sacred sites carry a
# third "kind" element the other two don't, so a shared implementation would
# need its own branching anyway, and separate functions keep each one a
# straight read of what it does.


def add_ship(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        center = payload.get("center", (500, 350))
        config.ships.append((float(center[0]), float(center[1])))
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def update_ship(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        idx = _index_from_id("ship", payload.get("id", ""))
        if idx is None or not (0 <= idx < len(config.ships)):
            return json.dumps({"error": f"Ship {payload.get('id')} not found"})
        if payload.get("center"):
            cx, cy = payload["center"]
            config.ships[idx] = (float(cx), float(cy))
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def delete_ship(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        idx = _index_from_id("ship", payload.get("id", ""))
        if idx is None or not (0 <= idx < len(config.ships)):
            return json.dumps({"error": f"Ship {payload.get('id')} not found"})
        del config.ships[idx]
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def add_volcano(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        center = payload.get("center", (500, 350))
        config.volcanoes.append((float(center[0]), float(center[1])))
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def update_volcano(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        idx = _index_from_id("volcano", payload.get("id", ""))
        if idx is None or not (0 <= idx < len(config.volcanoes)):
            return json.dumps({"error": f"Volcano {payload.get('id')} not found"})
        if payload.get("center"):
            cx, cy = payload["center"]
            config.volcanoes[idx] = (float(cx), float(cy))
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def delete_volcano(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        idx = _index_from_id("volcano", payload.get("id", ""))
        if idx is None or not (0 <= idx < len(config.volcanoes)):
            return json.dumps({"error": f"Volcano {payload.get('id')} not found"})
        del config.volcanoes[idx]
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def add_sacred_site(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        center = payload.get("center", (500, 350))
        kind = payload.get("kind", "kurgan")
        config.sacred_sites.append((float(center[0]), float(center[1]), str(kind)))
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def update_sacred_site(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        idx = _index_from_id("sacred", payload.get("id", ""))
        if idx is None or not (0 <= idx < len(config.sacred_sites)):
            return json.dumps({"error": f"Sacred site {payload.get('id')} not found"})
        x, y, kind = config.sacred_sites[idx]
        if payload.get("center"):
            x, y = payload["center"]
        if "kind" in payload:
            kind = payload["kind"]
        config.sacred_sites[idx] = (float(x), float(y), str(kind))
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def delete_sacred_site(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    try:
        config = _resolve_config(payload, payload.get("seed", 42))
        idx = _index_from_id("sacred", payload.get("id", ""))
        if idx is None or not (0 <= idx < len(config.sacred_sites)):
            return json.dumps({"error": f"Sacred site {payload.get('id')} not found"})
        del config.sacred_sites[idx]
        config.validate()
        return json.dumps({"config": config.to_dict()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def from_svg_json(data: str) -> str:
    try:
        payload = json.loads(data)
    except (TypeError, ValueError):
        return json.dumps({"error": "Invalid JSON payload"})
    svg = payload.get("svg") or ""
    if not svg:
        return json.dumps({"error": "Missing SVG text"})
    world = extract_world_from_svg(svg)
    if not world:
        return json.dumps(
            {"error": "No FMG world metadata found in SVG (export SVG from this app first)"}
        )
    try:
        cfg = MapConfig.from_dict(world.get("config") or world)
        meta = world.get("meta") or {}
        return json.dumps(
            {
                "config": cfg.to_dict(),
                "meta": meta,
                "seed": meta.get("seed", 7),
            }
        )
    except Exception as e:
        return json.dumps({"error": str(e)})


bridge_presets = presets_json
bridge_render = render_json
bridge_download = download_json
bridge_normalize = normalize_json
bridge_from_svg = from_svg_json
