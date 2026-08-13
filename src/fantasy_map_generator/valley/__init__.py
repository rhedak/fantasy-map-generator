"""Valley of Mists exact-parity renderer (sister mapgen port)."""

from __future__ import annotations

import json
import re
from typing import Any
from xml.sax.saxutils import escape as xml_escape
from xml.sax.saxutils import unescape as xml_unescape

from fantasy_map_generator.config import MapConfig, Place, Route
from fantasy_map_generator.valley.mapgen import (
    BOWL_CX,
    BOWL_CY,
    CAPITAL_ROAD,
    INN,
    KIRIGUCHI,
    KIRI_NO_SATO,
    SECRET_PASSAGE,
    render_map as render_valley_svg,
)

VALLEY_PLACE_IDS = (
    "kiriguchi",
    "kiri_no_sato",
    "valley_inn",
    "kasumikyo",
    "basin",
)

DEFAULT_PLACES: dict[str, Place] = {
    "kiriguchi": Place(
        x=KIRIGUCHI[0],
        y=KIRIGUCHI[1],
        name="Kiriguchi / Nebelmark",
        tier="town",
        id="kiriguchi",
    ),
    "kiri_no_sato": Place(
        x=KIRI_NO_SATO[0],
        y=KIRI_NO_SATO[1],
        name="Kiri no Sato",
        tier="village",
        id="kiri_no_sato",
    ),
    "valley_inn": Place(
        x=INN[0],
        y=INN[1],
        name="the Valley Inn",
        tier="hamlet",
        id="valley_inn",
    ),
    "kasumikyo": Place(
        x=640.0,
        y=414.0,
        name="Kasumikyo",
        tier="capital",
        id="kasumikyo",
    ),
    "basin": Place(
        x=BOWL_CX,
        y=BOWL_CY,
        name="the Basin",
        tier="ruin",
        id="basin",
    ),
}

DEFAULT_ROUTES: dict[str, Route] = {
    "capital_road": Route(
        points=list(CAPITAL_ROAD),
        kind="road",
        id="capital_road",
        label="capital road",
    ),
    "secret_passage": Route(
        points=list(SECRET_PASSAGE),
        kind="trail",
        id="secret_passage",
        label="secret passage",
    ),
}


def _valley_palette():
    from fantasy_map_generator.config import Palette

    return Palette(
        background="#202634",
        land="#2a3344",
        mountain="#343e54",
        mountain_stroke="#1c2333",
        water="#6f9ec4",
        water_tributary="#5a8fb5",
        water_deep="#3a5470",
        paddy="#5d7f62",
        forest="#3d5c46",
        plain="#4a5a4a",
        settlement="#b9a888",
        settlement_roof="#7a6a4f",
        road="#d9c9a3",
        road_dim="#a99670",
        text="#e8e2d2",
        text_dim="#b2a992",
        text_faint="#8f8777",
        mist_wall="#dfe6ee",
        gold="#c9b896",
        ink="#0c1018",
        paper="#2a3344",
    )


def default_valley_config(*, variant: str = "settled", seed: int = 7) -> MapConfig:
    """MapConfig describing the canonical Valley world for the editor."""
    return MapConfig(
        name="Valley of Mists",
        layout="bowl",
        style_kit="valley_parity",
        canvas_width=1000,
        canvas_height=700,
        places={
            k: Place(x=p.x, y=p.y, name=p.name, tier=p.tier, id=p.id, locked=True)
            for k, p in DEFAULT_PLACES.items()
        },
        routes={
            k: Route(points=list(r.points), kind=r.kind, id=r.id, label=r.label, locked=True)
            for k, r in DEFAULT_ROUTES.items()
        },
        palette=_valley_palette(),
        detail=0.55,
        coast_roughness=0.08,
    )


def _place_overrides(config: MapConfig) -> dict[str, tuple[float, float]]:
    ov: dict[str, tuple[float, float]] = {}
    for pid, place in config.places.items():
        key = place.id or pid
        if key in VALLEY_PLACE_IDS:
            ov[key] = (float(place.x), float(place.y))
    return ov


def render_valley(
    config: MapConfig | None = None,
    *,
    seed: int = 7,
    variant: str = "settled",
    interactive: bool = True,
    embed_world: bool = False,
    selected_id: str | None = None,
) -> str:
    """Render Valley parity SVG, optionally interactive and with embedded world JSON."""
    cfg = (config or default_valley_config()).normalize()
    # seed/variant can live on config detail channel; prefer explicit args
    meta_seed = seed
    meta_variant = variant

    metadata = None
    if embed_world:
        world = {
            "format": "fmg-world/v1",
            "meta": {
                "renderer": "valley_parity",
                "seed": meta_seed,
                "variant": meta_variant,
            },
            "config": cfg.to_dict(),
        }
        metadata = json.dumps(world, separators=(",", ":"))

    svg = render_valley_svg(
        variant=meta_variant,
        seed=meta_seed,
        interactive=interactive,
        place_overrides=_place_overrides(cfg),
        metadata_json=metadata,
    )

    # selection highlight ring for places
    if selected_id and interactive and selected_id in cfg.places:
        p = cfg.places[selected_id]
        ring = (
            f'<circle cx="{p.x:.1f}" cy="{p.y:.1f}" r="18" fill="none" '
            f'stroke="#ffcc33" stroke-width="2.2" pointer-events="none"/>'
        )
        svg = svg.replace("</svg>", ring + "\n</svg>")

    # Extra editor-only places (not part of parity cast) drawn simply on top
    extras = []
    for pid, place in cfg.places.items():
        key = place.id or pid
        if key in VALLEY_PLACE_IDS:
            continue
        # simple marker
        extras.append(
            f'<g data-id="{xml_escape(key)}" data-kind="place" style="cursor:pointer">'
            f'<circle cx="{place.x:.1f}" cy="{place.y:.1f}" r="16" fill="#fff" opacity="0.001"/>'
            f'<circle cx="{place.x:.1f}" cy="{place.y:.1f}" r="5" fill="#b9a888" stroke="#1c2333" stroke-width="1"/>'
            f"</g>"
        )
        extras.append(
            f'<text x="{place.x:.1f}" y="{place.y + 18:.1f}" font-size="11" text-anchor="middle" '
            f'font-family="Georgia, \'Times New Roman\', serif" fill="#e8e2d2" pointer-events="none">'
            f"{xml_escape(place.name)}</text>"
        )
    if extras:
        svg = svg.replace("</svg>", "\n".join(extras) + "\n</svg>")

    return svg


_META_RE = re.compile(
    r'<metadata\b[^>]*\bid=["\']fmg-world["\'][^>]*>(.*?)</metadata>',
    re.DOTALL | re.IGNORECASE,
)
_META_RE2 = re.compile(
    r'<metadata\b[^>]*\bdata-format=["\']fmg-world/v1["\'][^>]*>(.*?)</metadata>',
    re.DOTALL | re.IGNORECASE,
)


def extract_world_from_svg(svg: str) -> dict[str, Any] | None:
    """Parse embedded FMG world JSON from an SVG string."""
    m = _META_RE.search(svg) or _META_RE2.search(svg)
    if not m:
        return None
    raw = m.group(1).strip()
    raw = xml_unescape(raw).replace("<\\/", "</")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def world_dict_from_config(
    config: MapConfig,
    *,
    seed: int = 7,
    variant: str = "settled",
    renderer: str = "valley_parity",
) -> dict[str, Any]:
    cfg = config.normalize()
    return {
        "format": "fmg-world/v1",
        "meta": {
            "renderer": renderer,
            "seed": seed,
            "variant": variant,
        },
        "config": cfg.to_dict(),
    }


__all__ = [
    "DEFAULT_PLACES",
    "DEFAULT_ROUTES",
    "VALLEY_PLACE_IDS",
    "default_valley_config",
    "extract_world_from_svg",
    "render_valley",
    "render_valley_svg",
    "world_dict_from_config",
]
