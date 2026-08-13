"""Web GUI: preset gallery + interactive place editor.

Usage:
    python -m fantasy_map_generator.gui
    # http://localhost:3000
"""

from __future__ import annotations

import os
import random

try:
    import flask
except ImportError:
    flask = None

from fantasy_map_generator.config import LandBody, MapConfig, Place
from fantasy_map_generator.render import render_map
from fantasy_map_generator.worlds import WORLDS


def create_app():
    """Create and configure the Flask application."""
    if flask is None:
        raise ImportError(
            "Flask is required for the GUI. Install with: pip install fantasy-map-generator[gui]"
        )

    app = flask.Flask(__name__, static_folder=None)

    PRESETS: dict[str, tuple[str, MapConfig | None, int | None]] = {
        world_id: (config.name, config, 42) for world_id, config in WORLDS.items()
    }
    PRESETS["random"] = ("Random World", None, None)

    def _parse_knobs(data: dict) -> tuple[int, float | None, float | None]:
        try:
            seed = int(data.get("seed", 42))
        except (ValueError, TypeError):
            seed = 42
        return seed, _clamp01(data.get("detail")), _clamp01(data.get("coast_roughness"))

    def _resolve_config(data: dict, seed: int) -> MapConfig:
        """Prefer explicit config JSON; else preset id."""
        if data.get("config"):
            return MapConfig.from_dict(data["config"])
        preset_id = data.get("preset", "valley")
        if preset_id not in PRESETS:
            raise KeyError(preset_id)
        _name, config_or_none, _seed = PRESETS[preset_id]
        if config_or_none is None:
            return _random_world(seed)
        # deep copy via dict roundtrip so callers can mutate safely
        return MapConfig.from_dict(config_or_none.to_dict())

    @app.route("/")
    def index():
        return flask.render_template_string(HTML_TEMPLATE)

    @app.route("/api/presets")
    def api_presets():
        presets = []
        for preset_id, (name, config, seed) in PRESETS.items():
            preview_svg = None
            cfg_dict = None
            try:
                cfg = config if config is not None else _random_world(42)
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
        return flask.jsonify(presets)

    @app.route("/api/render", methods=["POST"])
    def api_render():
        data = flask.request.get_json(silent=True) or {}
        seed, detail, roughness = _parse_knobs(data)
        selected_id = data.get("selected_id") or None
        try:
            config = _resolve_config(data, seed)
        except KeyError:
            return flask.jsonify({"error": f"Unknown preset: {data.get('preset')}"}), 400
        except Exception as e:
            return flask.jsonify({"error": f"Invalid config: {e}"}), 400

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
            return flask.jsonify(
                {
                    "svg": svg,
                    "seed": seed,
                    "config": config.to_dict(),
                    "detail": config.detail,
                    "coast_roughness": config.coast_roughness,
                }
            )
        except Exception as e:
            return flask.jsonify({"error": str(e)}), 500

    @app.route("/api/download", methods=["POST"])
    def api_download():
        data = flask.request.get_json(silent=True) or {}
        format_ = data.get("format", "svg")
        seed, detail, roughness = _parse_knobs(data)
        try:
            config = _resolve_config(data, seed)
        except Exception as e:
            return flask.jsonify({"error": str(e)}), 400

        try:
            if format_ == "json":
                import json

                body = json.dumps(config.to_dict(), indent=2)
                return flask.Response(
                    body,
                    mimetype="application/json",
                    headers={"Content-Disposition": f"attachment; filename=world-{seed}.json"},
                )

            svg = render_map(config=config, seed=seed, detail=detail, coast_roughness=roughness)
            if format_ == "svg":
                # Re-render with embedded world metadata for round-trip
                svg = render_map(
                    config=config,
                    seed=seed,
                    detail=detail,
                    coast_roughness=roughness,
                    embed_world=True,
                    interactive=True,
                )
                return flask.Response(
                    svg,
                    mimetype="image/svg+xml",
                    headers={"Content-Disposition": f"attachment; filename=map-{seed}.svg"},
                )
            if format_ == "png":
                try:
                    import cairosvg

                    png_bytes = cairosvg.svg2png(bytestring=svg.encode(), scale=2)
                    return flask.Response(
                        png_bytes,
                        mimetype="image/png",
                        headers={"Content-Disposition": f"attachment; filename=map-{seed}.png"},
                    )
                except ImportError:
                    return flask.jsonify({"error": "cairosvg not installed"}), 501
            return flask.jsonify({"error": "Unknown format"}), 400
        except Exception as e:
            return flask.jsonify({"error": str(e)}), 500

    @app.route("/api/world/normalize", methods=["POST"])
    def api_normalize():
        data = flask.request.get_json(silent=True) or {}
        try:
            cfg = MapConfig.from_dict(data.get("config") or data)
            cfg.validate()
            return flask.jsonify({"config": cfg.to_dict()})
        except Exception as e:
            return flask.jsonify({"error": str(e)}), 400

    @app.route("/api/world/from-svg", methods=["POST"])
    def api_from_svg():
        """Extract embedded FMG world metadata from an SVG document."""
        data = flask.request.get_json(silent=True) or {}
        svg = data.get("svg") or ""
        if not svg and flask.request.data:
            svg = flask.request.data.decode("utf-8", errors="replace")
        from fantasy_map_generator.valley import extract_world_from_svg

        world = extract_world_from_svg(svg)
        if not world:
            return flask.jsonify(
                {"error": "No FMG world metadata found in SVG (export SVG from this app first)"}
            ), 400
        try:
            cfg = MapConfig.from_dict(world.get("config") or world)
            meta = world.get("meta") or {}
            return flask.jsonify(
                {
                    "config": cfg.to_dict(),
                    "meta": meta,
                    "seed": meta.get("seed", 7),
                }
            )
        except Exception as e:
            return flask.jsonify({"error": str(e)}), 400

    return app


def _clamp01(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, v))


def _random_world(seed: int) -> MapConfig:
    rng = random.Random(seed)
    places = {
        "settlement_a": Place(
            200 + rng.uniform(-50, 50),
            250 + rng.uniform(-50, 50),
            name="Settlement A",
            tier="town",
            id="settlement_a",
        ),
        "settlement_b": Place(
            700 + rng.uniform(-50, 50),
            300 + rng.uniform(-50, 50),
            name="Settlement B",
            tier="village",
            id="settlement_b",
        ),
        "settlement_c": Place(
            500 + rng.uniform(-50, 50),
            550 + rng.uniform(-50, 50),
            name="Settlement C",
            tier="hamlet",
            id="settlement_c",
        ),
    }
    return MapConfig(
        name="Random World",
        layout="interior",
        style_kit="mist_bowl",
        landmass=[
            LandBody(
                center=(500, 350),
                radii=(380 + rng.uniform(-40, 40), 260 + rng.uniform(-30, 30)),
                rough=0.12,
            )
        ],
        places=places,
        detail=0.5,
    ).normalize()


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Fantasy Map Generator</title>
  <style>
    :root {
      --primary: #4a6fa5;
      --primary-light: #6a8fc5;
      --bg: #f0f2f5;
      --text: #222;
      --border: #d0d5dd;
      --panel: #fff;
      --accent: #c9a227;
      --danger: #c62828;
    }
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0; padding: 16px; background: var(--bg); color: var(--text);
    }
    .page-header { max-width: 1400px; margin: 0 auto 20px; text-align: center; }
    .page-header h1 { margin: 0 0 6px; color: var(--primary); font-size: 1.8em; }
    .page-header p { margin: 4px 0; color: #666; }
    main { max-width: 1400px; margin: 0 auto; }
    #status {
      padding: 10px 12px; border-radius: 4px; margin-bottom: 12px; display: none;
      background: #e8f5e9; border-left: 4px solid #4caf50;
    }
    #status.visible { display: block; }
    #status.error { background: #ffebee; border-left-color: var(--danger); color: var(--danger); }
    #gallery-section h2 { color: var(--primary); margin-top: 0; }
    .gallery {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px;
    }
    .gallery-card {
      background: var(--panel); border: 2px solid var(--border); border-radius: 8px;
      overflow: hidden; cursor: pointer; transition: 0.15s;
    }
    .gallery-card:hover { border-color: var(--primary); transform: translateY(-2px); }
    .gallery-preview { aspect-ratio: 10/7; background: #eee; overflow: hidden; }
    .gallery-preview svg { width: 100%; height: 100%; }
    .gallery-card h3 { margin: 10px 12px; color: var(--primary); font-size: 0.95em; }
    #editor-section { display: none; }
    #editor-section.visible {
      display: grid; grid-template-columns: 1fr 340px; gap: 20px;
    }
    .preview-pane {
      background: var(--panel); border-radius: 8px; padding: 14px;
      box-shadow: 0 1px 4px rgba(0,0,0,.06);
    }
    .preview-wrap {
      position: relative; width: 100%; aspect-ratio: 10/7;
      border: 1px solid var(--border); border-radius: 4px; overflow: hidden;
      background: #111; touch-action: none;
    }
    .preview-wrap.select-mode { cursor: default; }
    .preview-wrap.place-mode { cursor: crosshair; }
    #preview { width: 100%; height: 100%; }
    #preview svg { width: 100%; height: 100%; display: block; }
    .ghost {
      position: absolute; width: 18px; height: 18px; margin: -9px 0 0 -9px;
      border: 2px solid #ffcc33; border-radius: 50%; pointer-events: none;
      display: none; box-shadow: 0 0 0 1px #000;
    }
    .preview-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; align-items: center; }
    button, .file-btn {
      padding: 8px 14px; border: 1px solid var(--border); background: #fff;
      color: var(--primary); border-radius: 4px; cursor: pointer; font-size: 0.92em;
    }
    button:hover, .file-btn:hover { background: var(--primary); color: #fff; }
    button.active { background: var(--primary); color: #fff; border-color: var(--primary); }
    button.danger { color: var(--danger); }
    button.danger:hover { background: var(--danger); color: #fff; }
    button:disabled { opacity: 0.45; cursor: not-allowed; }
    .link-button { background: none; border: none; color: var(--primary); text-decoration: underline; }
    .controls-pane { display: flex; flex-direction: column; gap: 12px; max-height: calc(100vh - 80px); overflow: auto; }
    fieldset {
      border: 1px solid var(--border); border-radius: 6px; padding: 12px;
      background: var(--panel); margin: 0;
    }
    legend { padding: 0 6px; color: var(--primary); font-weight: 600; font-size: 0.9em; }
    .control-group { margin-bottom: 10px; }
    .control-group:last-child { margin-bottom: 0; }
    .control-group label { display: block; margin-bottom: 4px; font-size: 0.88em; font-weight: 500; }
    .control-group input[type="range"] { width: 100%; }
    .control-group input[type="text"], .control-group select {
      width: 100%; padding: 6px 8px; border: 1px solid var(--border); border-radius: 4px;
    }
    .control-value { text-align: right; font-size: 0.8em; color: #666; }
    .mode-row, .palette { display: flex; flex-wrap: wrap; gap: 6px; }
    .palette button { flex: 1 1 40%; font-size: 0.82em; padding: 7px 6px; }
    .hint { font-size: 0.82em; color: #666; margin: 8px 0 0; line-height: 1.4; }
    .copy-status { font-size: 0.85em; color: #4caf50; }
    .inspector-empty { color: #888; font-size: 0.9em; margin: 0; }
    .row-btns { display: flex; flex-wrap: wrap; gap: 6px; }
    @media (max-width: 900px) {
      #editor-section.visible { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header class="page-header">
    <h1>Fantasy Map Generator</h1>
    <p>Pick a world, place settlements and paths, select and edit them.</p>
  </header>
  <main>
    <p id="status" role="status" aria-live="polite"></p>
    <section id="gallery-section">
      <h2>Choose a world</h2>
      <div class="gallery" id="gallery"></div>
    </section>
    <section id="editor-section">
      <div class="preview-pane">
        <div id="preview-wrap" class="preview-wrap select-mode">
          <div id="preview"></div>
          <div id="ghost" class="ghost"></div>
        </div>
        <div class="preview-actions">
          <button id="download-svg">SVG</button>
          <button id="download-png">PNG</button>
          <button id="download-json">World JSON</button>
          <label class="file-btn">Open JSON<input type="file" id="open-json" accept="application/json,.json" hidden></label>
          <label class="file-btn">Open SVG<input type="file" id="open-svg" accept="image/svg+xml,.svg" hidden></label>
          <button id="copy-link">Copy link</button>
          <span id="copy-status" class="copy-status"></span>
        </div>
        <p class="back-link" style="text-align:center;margin-top:10px">
          <button id="back-btn" class="link-button">&larr; choose a different world</button>
        </p>
      </div>
      <div class="controls-pane">
        <fieldset>
          <legend>World</legend>
          <p id="world-name" style="margin:0 0 8px;font-weight:600">—</p>
          <div class="row-btns">
            <button id="undo-btn" disabled>Undo</button>
            <button id="redo-btn" disabled>Redo</button>
          </div>
        </fieldset>
        <fieldset>
          <legend>Parameters</legend>
          <div class="control-group">
            <label for="seed-slider">Seed</label>
            <input id="seed-slider" type="range" min="0" max="10000" value="42" step="1">
            <div class="control-value"><span id="seed-value">42</span></div>
          </div>
          <div class="control-group">
            <label for="detail-slider">Detail</label>
            <input id="detail-slider" type="range" min="0" max="100" value="55" step="1">
            <div class="control-value"><span id="detail-value">0.55</span></div>
          </div>
          <div class="control-group">
            <label for="rough-slider">Coast roughness</label>
            <input id="rough-slider" type="range" min="0" max="100" value="15" step="1">
            <div class="control-value"><span id="rough-value">0.15</span></div>
          </div>
        </fieldset>
        <fieldset>
          <legend>Mode</legend>
          <div class="mode-row">
            <button id="mode-select" class="active">Select</button>
            <button id="mode-place">Place</button>
            <button id="mode-path">Draw path</button>
          </div>
          <p id="mode-hint" class="hint">Click a settlement to select. Drag to move.</p>
        </fieldset>
        <fieldset>
          <legend>Settlements</legend>
          <div class="palette" id="palette"></div>
          <p class="hint">Choose a type, then click the map to place.</p>
        </fieldset>
        <fieldset>
          <legend>Paths</legend>
          <div class="palette" id="path-palette"></div>
          <p class="hint">Click waypoints; double-click or Enter to finish (need 2+ points). Esc cancels.</p>
        </fieldset>
        <fieldset>
          <legend>Properties</legend>
          <div id="inspector-empty" class="inspector-empty">Nothing selected</div>
          <div id="inspector-place" style="display:none">
            <div class="control-group">
              <label for="prop-name">Name</label>
              <input id="prop-name" type="text">
            </div>
            <div class="control-group">
              <label for="prop-tier">Tier</label>
              <select id="prop-tier"></select>
            </div>
            <div class="row-btns" style="margin-top:8px">
              <button id="delete-feature" class="danger">Delete</button>
            </div>
          </div>
          <div id="inspector-route" style="display:none">
            <div class="control-group">
              <label for="prop-route-label">Label</label>
              <input id="prop-route-label" type="text">
            </div>
            <div class="control-group">
              <label for="prop-route-kind">Kind</label>
              <select id="prop-route-kind">
                <option value="road">road</option>
                <option value="trail">trail</option>
                <option value="river">river</option>
                <option value="ferry">ferry</option>
              </select>
            </div>
            <p class="hint" id="route-points-hint">0 points</p>
            <div class="row-btns" style="margin-top:8px">
              <button id="delete-route" class="danger">Delete path</button>
            </div>
          </div>
        </fieldset>
      </div>
    </section>
  </main>
  <script>
    const TIERS = ["hamlet","village","town","city","capital","ruin","castle"];
    const PATH_KINDS = ["road","trail","river","ferry"];

    const statusEl = document.getElementById('status');
    const galleryEl = document.getElementById('gallery');
    const gallerySection = document.getElementById('gallery-section');
    const editorEl = document.getElementById('editor-section');
    const previewEl = document.getElementById('preview');
    const previewWrap = document.getElementById('preview-wrap');
    const ghost = document.getElementById('ghost');
    const seedSlider = document.getElementById('seed-slider');
    const seedValue = document.getElementById('seed-value');
    const detailSlider = document.getElementById('detail-slider');
    const detailValue = document.getElementById('detail-value');
    const roughSlider = document.getElementById('rough-slider');
    const roughValue = document.getElementById('rough-value');
    const worldName = document.getElementById('world-name');
    const modeHint = document.getElementById('mode-hint');
    const paletteEl = document.getElementById('palette');
    const pathPaletteEl = document.getElementById('path-palette');
    const propName = document.getElementById('prop-name');
    const propTier = document.getElementById('prop-tier');
    const propRouteLabel = document.getElementById('prop-route-label');
    const propRouteKind = document.getElementById('prop-route-kind');
    const routePointsHint = document.getElementById('route-points-hint');
    const inspectorEmpty = document.getElementById('inspector-empty');
    const inspectorPlace = document.getElementById('inspector-place');
    const inspectorRoute = document.getElementById('inspector-route');
    const undoBtn = document.getElementById('undo-btn');
    const redoBtn = document.getElementById('redo-btn');

    let presets = [];
    let currentPreset = null;
    let workingConfig = null;
    let selectedId = null;
    let selectedKind = null; // place | route
    let mode = 'select'; // select | place | path
    let placeTier = 'village';
    let pathKind = 'road';
    let draftPoints = [];
    let lastClickTime = 0;
    let renderTimer = null;
    let renderSeq = 0;
    let undoStack = [];
    let redoStack = [];
    let dragging = null;
    let placeCounters = {};
    let pathCounters = {};

    TIERS.forEach(t => {
      const o = document.createElement('option');
      o.value = t; o.textContent = t;
      propTier.appendChild(o);
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = t;
      b.dataset.tier = t;
      b.addEventListener('click', () => {
        placeTier = t;
        draftPoints = [];
        setMode('place');
        [...paletteEl.querySelectorAll('button')].forEach(x => x.classList.toggle('active', x.dataset.tier === t));
        [...pathPaletteEl.querySelectorAll('button')].forEach(x => x.classList.remove('active'));
        modeHint.textContent = `Place: ${t} — click map to drop. Esc for select.`;
      });
      paletteEl.appendChild(b);
    });

    PATH_KINDS.forEach(k => {
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = k;
      b.dataset.kind = k;
      b.addEventListener('click', () => {
        pathKind = k;
        draftPoints = [];
        setMode('path');
        [...pathPaletteEl.querySelectorAll('button')].forEach(x => x.classList.toggle('active', x.dataset.kind === k));
        [...paletteEl.querySelectorAll('button')].forEach(x => x.classList.remove('active'));
        modeHint.textContent = `Draw ${k}: click waypoints, double-click or Enter to finish.`;
      });
      pathPaletteEl.appendChild(b);
    });

    function setStatus(msg, isError = false) {
      statusEl.textContent = msg || '';
      statusEl.classList.toggle('visible', !!msg);
      statusEl.classList.toggle('error', isError);
    }

    function deepClone(o) { return JSON.parse(JSON.stringify(o)); }

    function pushUndo() {
      if (!workingConfig) return;
      undoStack.push(deepClone(workingConfig));
      if (undoStack.length > 50) undoStack.shift();
      redoStack = [];
      updateUndoButtons();
    }

    function updateUndoButtons() {
      undoBtn.disabled = undoStack.length === 0;
      redoBtn.disabled = redoStack.length === 0;
    }

    function setMode(m) {
      mode = m;
      document.getElementById('mode-select').classList.toggle('active', m === 'select');
      document.getElementById('mode-place').classList.toggle('active', m === 'place');
      document.getElementById('mode-path').classList.toggle('active', m === 'path');
      previewWrap.classList.toggle('select-mode', m === 'select');
      previewWrap.classList.toggle('place-mode', m === 'place' || m === 'path');
      if (m === 'select') {
        draftPoints = [];
        modeHint.textContent = 'Click a settlement or path to select. Drag places to move.';
        [...paletteEl.querySelectorAll('button')].forEach(x => x.classList.remove('active'));
        [...pathPaletteEl.querySelectorAll('button')].forEach(x => x.classList.remove('active'));
        drawDraftOverlay();
      } else if (m === 'path') {
        modeHint.textContent = `Draw ${pathKind}: click waypoints, double-click or Enter to finish.`;
      }
    }

    function knobs() {
      return {
        seed: parseInt(seedSlider.value, 10),
        detail: parseInt(detailSlider.value, 10) / 100,
        coast_roughness: parseInt(roughSlider.value, 10) / 100,
      };
    }

    function debounceRender() {
      if (renderTimer) clearTimeout(renderTimer);
      renderTimer = setTimeout(() => { renderTimer = null; renderMap(); }, 120);
    }

    async function loadPresets() {
      const res = await fetch('/api/presets');
      presets = await res.json();
      galleryEl.innerHTML = '';
      presets.forEach(p => {
        const card = document.createElement('div');
        card.className = 'gallery-card';
        const prev = document.createElement('div');
        prev.className = 'gallery-preview';
        prev.innerHTML = p.preview || '<p style="text-align:center;color:#999">—</p>';
        const h = document.createElement('h3');
        h.textContent = p.name;
        card.appendChild(prev); card.appendChild(h);
        card.addEventListener('click', () => selectPreset(p.id));
        galleryEl.appendChild(card);
      });
    }

    async function selectPreset(presetId) {
      const p = presets.find(x => x.id === presetId);
      if (!p || !p.config) { setStatus('Preset unavailable', true); return; }
      currentPreset = presetId;
      workingConfig = deepClone(p.config);
      if (workingConfig.detail != null) {
        detailSlider.value = Math.round(workingConfig.detail * 100);
        detailValue.textContent = workingConfig.detail.toFixed(2);
      }
      if (workingConfig.coast_roughness != null) {
        roughSlider.value = Math.round(workingConfig.coast_roughness * 100);
        roughValue.textContent = workingConfig.coast_roughness.toFixed(2);
      }
      selectedId = null;
      selectedKind = null;
      draftPoints = [];
      undoStack = []; redoStack = []; updateUndoButtons();
      placeCounters = {};
      pathCounters = {};
      gallerySection.style.display = 'none';
      editorEl.classList.add('visible');
      worldName.textContent = p.name;
      setMode('select');
      updateInspector();
      await renderMap();
      try { sessionStorage.setItem('fmg_working', JSON.stringify({ preset: presetId, config: workingConfig, ...knobs() })); } catch (_) {}
    }

    function updateInspector() {
      const place = selectedKind === 'place' && selectedId && workingConfig && workingConfig.places
        ? workingConfig.places[selectedId] : null;
      const route = selectedKind === 'route' && selectedId && workingConfig && workingConfig.routes
        ? workingConfig.routes[selectedId] : null;
      inspectorEmpty.style.display = (!place && !route) ? 'block' : 'none';
      inspectorPlace.style.display = place ? 'block' : 'none';
      inspectorRoute.style.display = route ? 'block' : 'none';
      if (place) {
        propName.value = place.name || '';
        propTier.value = place.tier || 'village';
      }
      if (route) {
        propRouteLabel.value = route.label || selectedId || '';
        propRouteKind.value = route.kind || 'road';
        routePointsHint.textContent = `${(route.points || []).length} waypoints`;
      }
    }

    async function renderMap() {
      if (!workingConfig) return;
      const seq = ++renderSeq;
      const body = {
        config: workingConfig,
        selected_id: selectedId,
        ...knobs(),
      };
      try {
        const res = await fetch('/api/render', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        if (seq !== renderSeq) return;
        if (!res.ok) {
          const err = await res.json();
          setStatus(err.error || 'Render failed', true);
          return;
        }
        const data = await res.json();
        previewEl.innerHTML = data.svg;
        if (data.config) workingConfig = data.config;
        setStatus('');
        bindSvgEvents();
        drawDraftOverlay();
        try {
          sessionStorage.setItem('fmg_working', JSON.stringify({
            preset: currentPreset, config: workingConfig, selected_id: selectedId, ...knobs()
          }));
        } catch (_) {}
      } catch (e) {
        if (seq !== renderSeq) return;
        setStatus(e.message, true);
      }
    }

    function svgPoint(evt) {
      const svg = previewEl.querySelector('svg');
      if (!svg) return null;
      const pt = svg.createSVGPoint();
      pt.x = evt.clientX; pt.y = evt.clientY;
      const ctm = svg.getScreenCTM();
      if (!ctm) return null;
      const p = pt.matrixTransform(ctm.inverse());
      return { x: p.x, y: p.y };
    }

    function findFeature(el) {
      let n = el;
      while (n && n !== previewEl) {
        if (n.getAttribute && n.getAttribute('data-id') && n.getAttribute('data-kind')) {
          return { id: n.getAttribute('data-id'), kind: n.getAttribute('data-kind') };
        }
        n = n.parentNode;
      }
      return null;
    }

    function bindSvgEvents() {
      const svg = previewEl.querySelector('svg');
      if (!svg) return;
      svg.style.userSelect = 'none';
    }

    function drawDraftOverlay() {
      const svg = previewEl.querySelector('svg');
      if (!svg) return;
      let g = svg.querySelector('#draft-overlay');
      if (g) g.remove();
      if (!draftPoints.length) return;
      g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('id', 'draft-overlay');
      g.setAttribute('pointer-events', 'none');
      if (draftPoints.length >= 2) {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', 'M ' + draftPoints.map(p => `${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' L '));
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', '#ffcc33');
        path.setAttribute('stroke-width', '2.5');
        path.setAttribute('stroke-dasharray', '6 4');
        g.appendChild(path);
      }
      draftPoints.forEach(p => {
        const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        c.setAttribute('cx', p[0]); c.setAttribute('cy', p[1]); c.setAttribute('r', '4');
        c.setAttribute('fill', '#ffcc33'); c.setAttribute('stroke', '#000'); c.setAttribute('stroke-width', '1');
        g.appendChild(c);
      });
      svg.appendChild(g);
    }

    function clampToCanvas(x, y) {
      const w = workingConfig.canvas_width || 1000;
      const h = workingConfig.canvas_height || 700;
      return {
        x: Math.max(0, Math.min(w, x)),
        y: Math.max(0, Math.min(h, y)),
      };
    }

    function nextPlaceName(tier) {
      placeCounters[tier] = (placeCounters[tier] || 0) + 1;
      const label = tier.charAt(0).toUpperCase() + tier.slice(1);
      return `${label} ${placeCounters[tier]}`;
    }

    function placeAt(x, y) {
      pushUndo();
      const id = 'place_' + Math.random().toString(16).slice(2, 10);
      const name = nextPlaceName(placeTier);
      if (!workingConfig.places) workingConfig.places = {};
      workingConfig.places[id] = {
        x, y, name, tier: placeTier, id, locked: true, icon: null
      };
      selectedId = id;
      selectedKind = 'place';
      updateInspector();
      renderMap();
    }

    function finishPath() {
      if (draftPoints.length < 2) {
        setStatus('Need at least 2 waypoints', true);
        return;
      }
      pushUndo();
      pathCounters[pathKind] = (pathCounters[pathKind] || 0) + 1;
      const id = 'route_' + Math.random().toString(16).slice(2, 10);
      const label = `${pathKind} ${pathCounters[pathKind]}`;
      if (!workingConfig.routes) workingConfig.routes = {};
      workingConfig.routes[id] = {
        points: draftPoints.map(p => [p[0], p[1]]),
        kind: pathKind,
        id,
        label,
        locked: true,
      };
      draftPoints = [];
      selectedId = id;
      selectedKind = 'route';
      setMode('select');
      updateInspector();
      renderMap();
    }

    previewWrap.addEventListener('pointerdown', (evt) => {
      if (!workingConfig) return;
      const pt = svgPoint(evt);
      if (!pt) return;
      const feat = findFeature(evt.target);
      const now = Date.now();
      const isDouble = (now - lastClickTime) < 320;
      lastClickTime = now;

      if (mode === 'place') {
        const c = clampToCanvas(pt.x, pt.y);
        placeAt(c.x, c.y);
        return;
      }

      if (mode === 'path') {
        const c = clampToCanvas(pt.x, pt.y);
        if (isDouble && draftPoints.length >= 1) {
          // double-click finishes (last click already added or not)
          if (draftPoints.length >= 2) finishPath();
          return;
        }
        draftPoints.push([c.x, c.y]);
        drawDraftOverlay();
        modeHint.textContent = `Draw ${pathKind}: ${draftPoints.length} point(s). Double-click or Enter to finish.`;
        return;
      }

      // select mode
      if (feat && feat.kind === 'place' && workingConfig.places[feat.id]) {
        selectedId = feat.id;
        selectedKind = 'place';
        updateInspector();
        const place = workingConfig.places[feat.id];
        dragging = {
          id: feat.id,
          kind: 'place',
          pointerId: evt.pointerId,
          origX: place.x,
          origY: place.y,
          moved: false,
        };
        previewWrap.setPointerCapture(evt.pointerId);
        ghost.style.display = 'block';
        const rect = previewWrap.getBoundingClientRect();
        ghost.style.left = (evt.clientX - rect.left) + 'px';
        ghost.style.top = (evt.clientY - rect.top) + 'px';
        renderMap();
      } else if (feat && feat.kind === 'route' && workingConfig.routes[feat.id]) {
        selectedId = feat.id;
        selectedKind = 'route';
        dragging = null;
        updateInspector();
        renderMap();
      } else {
        selectedId = null;
        selectedKind = null;
        updateInspector();
        renderMap();
      }
    });

    previewWrap.addEventListener('pointermove', (evt) => {
      if (!dragging) return;
      const pt = svgPoint(evt);
      if (!pt) return;
      const c = clampToCanvas(pt.x, pt.y);
      const dx = c.x - dragging.origX;
      const dy = c.y - dragging.origY;
      if (Math.hypot(dx, dy) > 2) dragging.moved = true;
      const rect = previewWrap.getBoundingClientRect();
      ghost.style.left = (evt.clientX - rect.left) + 'px';
      ghost.style.top = (evt.clientY - rect.top) + 'px';
    });

    function endDrag(evt) {
      if (!dragging) return;
      const d = dragging;
      dragging = null;
      ghost.style.display = 'none';
      try { previewWrap.releasePointerCapture(d.pointerId); } catch (_) {}
      if (!d.moved || d.kind !== 'place') return;
      const pt = svgPoint(evt);
      if (!pt || !workingConfig.places[d.id]) return;
      const c = clampToCanvas(pt.x, pt.y);
      pushUndo();
      workingConfig.places[d.id].x = c.x;
      workingConfig.places[d.id].y = c.y;
      renderMap();
    }

    previewWrap.addEventListener('pointerup', endDrag);
    previewWrap.addEventListener('pointercancel', () => {
      dragging = null; ghost.style.display = 'none';
    });

    document.getElementById('mode-select').addEventListener('click', () => setMode('select'));
    document.getElementById('mode-place').addEventListener('click', () => {
      setMode('place');
      modeHint.textContent = `Place: ${placeTier} — click map to drop. Esc for select.`;
      [...paletteEl.querySelectorAll('button')].forEach(x => x.classList.toggle('active', x.dataset.tier === placeTier));
      [...pathPaletteEl.querySelectorAll('button')].forEach(x => x.classList.remove('active'));
    });
    document.getElementById('mode-path').addEventListener('click', () => {
      setMode('path');
      [...pathPaletteEl.querySelectorAll('button')].forEach(x => x.classList.toggle('active', x.dataset.kind === pathKind));
      [...paletteEl.querySelectorAll('button')].forEach(x => x.classList.remove('active'));
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        draftPoints = [];
        setMode('select');
      }
      if (e.key === 'Enter' && mode === 'path') {
        e.preventDefault();
        finishPath();
      }
      const typing = document.activeElement === propName || document.activeElement === propRouteLabel;
      if ((e.key === 'Delete' || e.key === 'Backspace') && selectedId && !typing) {
        e.preventDefault();
        deleteSelected();
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'z') {
        e.preventDefault();
        if (e.shiftKey) redo(); else undo();
      }
    });

    function deleteSelected() {
      if (!selectedId || !workingConfig) return;
      pushUndo();
      if (selectedKind === 'place' && workingConfig.places[selectedId]) {
        delete workingConfig.places[selectedId];
      } else if (selectedKind === 'route' && workingConfig.routes[selectedId]) {
        delete workingConfig.routes[selectedId];
      }
      selectedId = null;
      selectedKind = null;
      updateInspector();
      renderMap();
    }

    document.getElementById('delete-feature').addEventListener('click', deleteSelected);
    document.getElementById('delete-route').addEventListener('click', deleteSelected);

    let propTimer = null;
    function applyPlaceProps() {
      if (selectedKind !== 'place' || !selectedId || !workingConfig.places[selectedId]) return;
      pushUndo();
      workingConfig.places[selectedId].name = propName.value || 'Unnamed';
      workingConfig.places[selectedId].tier = propTier.value || 'village';
      renderMap();
    }
    function applyRouteProps() {
      if (selectedKind !== 'route' || !selectedId || !workingConfig.routes[selectedId]) return;
      pushUndo();
      workingConfig.routes[selectedId].label = propRouteLabel.value || selectedId;
      workingConfig.routes[selectedId].kind = propRouteKind.value || 'road';
      renderMap();
    }
    propName.addEventListener('change', applyPlaceProps);
    propTier.addEventListener('change', applyPlaceProps);
    propName.addEventListener('input', () => {
      if (propTimer) clearTimeout(propTimer);
      propTimer = setTimeout(applyPlaceProps, 400);
    });
    propRouteLabel.addEventListener('change', applyRouteProps);
    propRouteKind.addEventListener('change', applyRouteProps);
    propRouteLabel.addEventListener('input', () => {
      if (propTimer) clearTimeout(propTimer);
      propTimer = setTimeout(applyRouteProps, 400);
    });

    function undo() {
      if (!undoStack.length) return;
      redoStack.push(deepClone(workingConfig));
      workingConfig = undoStack.pop();
      if (selectedKind === 'place' && selectedId && !(workingConfig.places || {})[selectedId]) {
        selectedId = null; selectedKind = null;
      }
      if (selectedKind === 'route' && selectedId && !(workingConfig.routes || {})[selectedId]) {
        selectedId = null; selectedKind = null;
      }
      updateUndoButtons(); updateInspector(); renderMap();
    }
    function redo() {
      if (!redoStack.length) return;
      undoStack.push(deepClone(workingConfig));
      workingConfig = redoStack.pop();
      updateUndoButtons(); updateInspector(); renderMap();
    }
    undoBtn.addEventListener('click', undo);
    redoBtn.addEventListener('click', redo);

    seedSlider.addEventListener('input', e => { seedValue.textContent = e.target.value; debounceRender(); });
    detailSlider.addEventListener('input', e => {
      detailValue.textContent = (e.target.value / 100).toFixed(2); debounceRender();
    });
    roughSlider.addEventListener('input', e => {
      roughValue.textContent = (e.target.value / 100).toFixed(2); debounceRender();
    });

    async function download(format) {
      const res = await fetch('/api/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config: workingConfig, format, ...knobs() }),
      });
      if (!res.ok) {
        const err = await res.json();
        setStatus(err.error || 'Download failed', true);
        return;
      }
      const blob = await res.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = format === 'json' ? `world-${knobs().seed}.json` : `map-${knobs().seed}.${format}`;
      a.click();
      URL.revokeObjectURL(a.href);
    }
    document.getElementById('download-svg').addEventListener('click', () => download('svg'));
    document.getElementById('download-png').addEventListener('click', () => download('png'));
    document.getElementById('download-json').addEventListener('click', () => download('json'));

    document.getElementById('open-json').addEventListener('change', async (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;
      try {
        const text = await file.text();
        const data = JSON.parse(text);
        const payload = data.config ? data : { config: data };
        if (data.meta && data.meta.seed != null) {
          seedSlider.value = data.meta.seed;
          seedValue.textContent = seedSlider.value;
        }
        const res = await fetch('/api/world/normalize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const out = await res.json();
        if (!res.ok) throw new Error(out.error || 'Invalid world');
        pushUndo();
        workingConfig = out.config;
        currentPreset = 'custom';
        worldName.textContent = workingConfig.name || 'Custom world';
        selectedId = null; selectedKind = null;
        updateInspector();
        await renderMap();
        setStatus('Loaded world JSON');
      } catch (err) {
        setStatus(err.message, true);
      }
      e.target.value = '';
    });

    document.getElementById('open-svg').addEventListener('change', async (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;
      try {
        const text = await file.text();
        const res = await fetch('/api/world/from-svg', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ svg: text }),
        });
        const out = await res.json();
        if (!res.ok) throw new Error(out.error || 'Invalid SVG world');
        pushUndo();
        workingConfig = out.config;
        if (out.seed != null) {
          seedSlider.value = out.seed;
          seedValue.textContent = String(out.seed);
        }
        currentPreset = 'custom';
        worldName.textContent = (workingConfig && workingConfig.name) || 'Custom world';
        selectedId = null; selectedKind = null;
        updateInspector();
        await renderMap();
        setStatus('Loaded world from SVG metadata');
      } catch (err) {
        setStatus(err.message, true);
      }
      e.target.value = '';
    });

    document.getElementById('copy-link').addEventListener('click', () => {
      const k = knobs();
      const url = `${location.origin}${location.pathname}?preset=${currentPreset}&seed=${k.seed}&detail=${k.detail}&coast_roughness=${k.coast_roughness}`;
      navigator.clipboard.writeText(url).then(() => {
        document.getElementById('copy-status').textContent = 'Copied!';
        setTimeout(() => { document.getElementById('copy-status').textContent = ''; }, 1500);
      });
    });

    document.getElementById('back-btn').addEventListener('click', () => {
      editorEl.classList.remove('visible');
      gallerySection.style.display = 'block';
      workingConfig = null;
      currentPreset = null;
    });

    const params = new URLSearchParams(location.search);
    if (params.has('seed')) {
      seedSlider.value = params.get('seed');
      seedValue.textContent = seedSlider.value;
    }
    if (params.has('detail')) {
      const d = Math.round(parseFloat(params.get('detail')) * 100);
      if (!Number.isNaN(d)) { detailSlider.value = d; detailValue.textContent = (d/100).toFixed(2); }
    }
    if (params.has('coast_roughness')) {
      const r = Math.round(parseFloat(params.get('coast_roughness')) * 100);
      if (!Number.isNaN(r)) { roughSlider.value = r; roughValue.textContent = (r/100).toFixed(2); }
    }

    loadPresets().then(() => {
      if (params.has('preset')) {
        selectPreset(params.get('preset'));
        return;
      }
      try {
        const saved = JSON.parse(sessionStorage.getItem('fmg_working') || 'null');
        if (saved && saved.config) {
          // optional restore — only if user wants; skip auto for now
        }
      } catch (_) {}
    });
  </script>
</body>
</html>
"""


def main() -> None:
    app = create_app()
    host = os.environ.get("FMG_HOST", "127.0.0.1")
    port = int(os.environ.get("FMG_PORT", "3000"))
    debug = os.environ.get("FMG_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
