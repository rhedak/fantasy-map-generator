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
