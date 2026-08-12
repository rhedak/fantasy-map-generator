"""Web-based GUI for interactive map generation.

Provides a browser-based interface to:
- Select from preset worlds or random generation
- Adjust parameters (seed, terrain density, etc.)
- Preview maps in real-time (SVG)
- Export to SVG/PNG

Usage:
    python -m fantasy_map_generator.gui
    # Opens http://localhost:5000
"""

import json
import random
from pathlib import Path

try:
    import flask
except ImportError:
    flask = None

from fantasy_map_generator.config import MapConfig
from fantasy_map_generator.render import render_map
from fantasy_map_generator.worlds import (
    VALLEY_CONFIG,
    DESERT_CONFIG,
    TROPICAL_CONFIG,
    ARCTIC_CONFIG,
    AUTUMN_CONFIG,
)


def create_app():
    """Create and configure the Flask application.

    Returns:
        Flask app instance.

    Raises:
        ImportError: If Flask is not installed.
    """
    if flask is None:
        raise ImportError(
            "Flask is required for the GUI. Install with: pip install fantasy-map-generator[gui]"
        )

    app = flask.Flask(__name__, static_folder=None)

    # Map presets: name -> (description, config_or_generator, preview_svg_seed)
    PRESETS = {
        "valley": ("Valley of Mists", VALLEY_CONFIG, 42),
        "desert": ("Desert Kingdoms", DESERT_CONFIG, 42),
        "tropical": ("Tropical Islands", TROPICAL_CONFIG, 42),
        "arctic": ("Arctic Tundra", ARCTIC_CONFIG, 42),
        "autumn": ("Autumn Kingdoms", AUTUMN_CONFIG, 42),
        "random": ("Random World", None, None),
    }

    @app.route("/")
    def index():
        return flask.render_template_string(HTML_TEMPLATE)

    @app.route("/api/presets")
    def api_presets():
        """Get list of available presets with preview SVGs."""
        presets = []
        for preset_id, (name, config, seed) in PRESETS.items():
            preview_svg = None
            try:
                if config is not None:
                    preview_svg = render_map(config=config, seed=seed or 42)
                else:
                    # Random world preview
                    config = MapConfig(
                        name="Random World",
                        canvas_width=1000,
                        canvas_height=700,
                        locations=_generate_random_locations(42),
                    )
                    preview_svg = render_map(config=config, seed=42)
            except Exception:
                pass

            presets.append({
                "id": preset_id,
                "name": name,
                "preview": preview_svg,
            })
        return flask.jsonify(presets)

    @app.route("/api/render", methods=["POST"])
    def api_render():
        """Render a map based on preset and seed."""
        data = flask.request.get_json()
        preset_id = data.get("preset", "valley")
        seed = data.get("seed", 42)

        try:
            seed = int(seed)
        except (ValueError, TypeError):
            seed = 42

        # Get config for this preset
        if preset_id not in PRESETS:
            return flask.jsonify({"error": f"Unknown preset: {preset_id}"}), 400

        _, config_or_none = PRESETS[preset_id]

        if config_or_none is None:
            # Random world: generate a simple config
            config = MapConfig(
                name="Random World",
                canvas_width=1000,
                canvas_height=700,
                locations=_generate_random_locations(seed),
            )
        else:
            config = config_or_none

        # Render map
        try:
            svg = render_map(config=config, seed=seed)
            return flask.jsonify({"svg": svg, "seed": seed})
        except Exception as e:
            return flask.jsonify({"error": str(e)}), 500

    @app.route("/api/download", methods=["POST"])
    def api_download():
        """Render and download a map."""
        data = flask.request.get_json()
        preset_id = data.get("preset", "valley")
        seed = data.get("seed", 42)
        format_ = data.get("format", "svg")  # svg or png

        try:
            seed = int(seed)
        except (ValueError, TypeError):
            seed = 42

        if preset_id not in PRESETS:
            return flask.jsonify({"error": "Unknown preset"}), 400

        _, config_or_none = PRESETS[preset_id]
        if config_or_none is None:
            config = MapConfig(
                name="Random World",
                canvas_width=1000,
                canvas_height=700,
                locations=_generate_random_locations(seed),
            )
        else:
            config = config_or_none

        try:
            svg = render_map(config=config, seed=seed)

            if format_ == "svg":
                return flask.Response(
                    svg,
                    mimetype="image/svg+xml",
                    headers={"Content-Disposition": f"attachment; filename=map-{seed}.svg"},
                )

            elif format_ == "png":
                try:
                    import cairosvg

                    png_bytes = cairosvg.svg2png(bytestring=svg.encode(), scale=2)
                    return flask.Response(
                        png_bytes,
                        mimetype="image/png",
                        headers={"Content-Disposition": f"attachment; filename=map-{seed}.png"},
                    )
                except ImportError:
                    return (
                        flask.jsonify({"error": "cairosvg not installed; PNG export unavailable"}),
                        501,
                    )

            else:
                return flask.jsonify({"error": "Unknown format"}), 400

        except Exception as e:
            return flask.jsonify({"error": str(e)}), 500

    return app


def _generate_random_locations(seed: int) -> dict[str, tuple[float, float]]:
    """Generate a few random settlement locations."""
    rng = random.Random(seed)
    return {
        "Settlement A": (200 + rng.uniform(-50, 50), 250 + rng.uniform(-50, 50)),
        "Settlement B": (700 + rng.uniform(-50, 50), 300 + rng.uniform(-50, 50)),
        "Settlement C": (500 + rng.uniform(-50, 50), 550 + rng.uniform(-50, 50)),
    }


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Fantasy Map Generator</title>
  <style>
    :root {
      --primary: #4a6fa5;
      --primary-light: #6a8fc5;
      --accent: #d4a373;
      --bg: #f5f5f5;
      --text: #333;
      --border: #ddd;
    }

    * {
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      padding: 20px;
      background: var(--bg);
      color: var(--text);
    }

    .page-header {
      max-width: 1400px;
      margin: 0 auto 40px;
      text-align: center;
    }

    .page-header h1 {
      margin: 0 0 10px;
      font-size: 2.5em;
      color: var(--primary);
    }

    .page-header p {
      margin: 8px 0;
      font-size: 1.1em;
      color: #666;
    }

    main {
      max-width: 1400px;
      margin: 0 auto;
    }

    #status {
      padding: 15px;
      background: #e8f5e9;
      border-left: 4px solid #4caf50;
      border-radius: 4px;
      margin-bottom: 20px;
      display: none;
    }

    #status.visible {
      display: block;
    }

    #status.error {
      background: #ffebee;
      border-left-color: #f44336;
      color: #c62828;
    }

    /* Gallery */
    #gallery-section {
      margin-bottom: 40px;
    }

    #gallery-section h2 {
      margin-top: 0;
      color: var(--primary);
    }

    .gallery {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 24px;
    }

    .gallery-card {
      background: white;
      border: 2px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      flex-direction: column;
    }

    .gallery-card:hover {
      border-color: var(--primary);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      transform: translateY(-4px);
    }

    .gallery-preview {
      width: 100%;
      aspect-ratio: 10 / 7;
      background: #f5f5f5;
      border-bottom: 1px solid var(--border);
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .gallery-preview svg {
      width: 100%;
      height: 100%;
    }

    .gallery-card h3 {
      margin: 12px;
      margin-bottom: 0;
      color: var(--primary);
      font-size: 1em;
    }

    /* Editor layout */
    #editor-section {
      display: none;
    }

    #editor-section.visible {
      display: grid;
      grid-template-columns: 1fr 350px;
      gap: 30px;
      margin-bottom: 40px;
    }

    .preview-pane {
      background: white;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    .preview {
      width: 100%;
      aspect-ratio: 10 / 7;
      border: 1px solid var(--border);
      border-radius: 4px;
      overflow: auto;
      background: #fafafa;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 300px;
    }

    .preview svg {
      width: 100%;
      height: auto;
    }

    .preview-actions {
      display: flex;
      gap: 10px;
      margin-top: 15px;
      flex-wrap: wrap;
    }

    button {
      padding: 10px 20px;
      border: 1px solid var(--border);
      background: white;
      color: var(--primary);
      border-radius: 4px;
      cursor: pointer;
      font-size: 1em;
      transition: all 0.2s;
    }

    button:hover {
      background: var(--primary);
      color: white;
      border-color: var(--primary);
    }

    button:active {
      transform: scale(0.98);
    }

    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .back-link {
      margin-top: 15px;
      text-align: center;
    }

    .link-button {
      background: none;
      border: none;
      color: var(--primary);
      text-decoration: underline;
      padding: 5px;
      font-size: 0.95em;
    }

    .link-button:hover {
      color: var(--primary-light);
    }

    /* Controls panel */
    .controls-pane {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    fieldset {
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 15px;
      background: white;
    }

    legend {
      padding: 0 8px;
      color: var(--primary);
      font-weight: 600;
    }

    .control-group {
      margin-bottom: 15px;
    }

    .control-group:last-child {
      margin-bottom: 0;
    }

    .control-group label {
      display: block;
      margin-bottom: 8px;
      font-size: 0.95em;
      font-weight: 500;
    }

    .control-group input[type="range"] {
      width: 100%;
    }

    .control-value {
      text-align: right;
      font-size: 0.85em;
      color: #666;
      margin-top: 4px;
    }

    .copy-status {
      font-size: 0.9em;
      color: #4caf50;
    }

    @media (max-width: 900px) {
      #editor-section.visible {
        grid-template-columns: 1fr;
      }

      .page-header h1 {
        font-size: 1.8em;
      }
    }
  </style>
</head>
<body>
  <header class="page-header">
    <h1>Fantasy Map Generator</h1>
    <p>Procedurally generated worlds as scalable SVG. Pick a preset, adjust the seed, and explore.</p>
    <p><a href="https://github.com/rhedak/fantasy-map-generator" target="_blank">View source</a></p>
  </header>

  <main>
    <p id="status" role="status" aria-live="polite"></p>

    <section id="gallery-section">
      <h2>Choose a world</h2>
      <div class="gallery" id="gallery"></div>
    </section>

    <section id="editor-section">
      <div class="preview-pane">
        <div id="preview" class="preview" aria-live="polite">
          <p style="color: #999;">Select a world to start</p>
        </div>
        <div class="preview-actions">
          <button id="download-svg">Download SVG</button>
          <button id="download-png">Download PNG</button>
          <button id="copy-link">Copy link</button>
          <span id="copy-status" class="copy-status"></span>
        </div>
        <p class="back-link">
          <button id="back-btn" class="link-button">&larr; choose a different world</button>
        </p>
      </div>

      <div class="controls-pane">
        <fieldset>
          <legend>Parameters</legend>
          <div class="control-group">
            <label for="seed-slider">Seed</label>
            <input id="seed-slider" type="range" min="0" max="10000" value="42" step="1">
            <div class="control-value"><span id="seed-value">42</span></div>
          </div>
        </fieldset>

        <fieldset>
          <legend>Info</legend>
          <div id="world-info" style="font-size: 0.9em; line-height: 1.6;">
            <p id="world-name" style="margin: 0 0 8px;"><strong>—</strong></p>
            <p style="margin: 0; color: #666;">Select a world to see details</p>
          </div>
        </fieldset>
      </div>
    </section>
  </main>

  <script>
    const statusEl = document.getElementById('status');
    const galleryEl = document.getElementById('gallery');
    const editorEl = document.getElementById('editor-section');
    const galleryEl2 = document.getElementById('gallery-section');
    const previewEl = document.getElementById('preview');
    const seedSlider = document.getElementById('seed-slider');
    const seedValue = document.getElementById('seed-value');
    const downloadSvgBtn = document.getElementById('download-svg');
    const downloadPngBtn = document.getElementById('download-png');
    const copyLinkBtn = document.getElementById('copy-link');
    const copyStatus = document.getElementById('copy-status');
    const backBtn = document.getElementById('back-btn');
    const worldName = document.getElementById('world-name');

    let currentPreset = null;
    let presets = [];

    function setStatus(msg, isError = false) {
      statusEl.textContent = msg;
      statusEl.classList.toggle('visible', !!msg);
      statusEl.classList.toggle('error', isError);
    }

    async function loadPresets() {
      try {
        const res = await fetch('/api/presets');
        presets = await res.json();
        buildGallery();
      } catch (e) {
        setStatus(`Failed to load presets: ${e.message}`, true);
      }
    }

    function buildGallery() {
      presets.forEach(p => {
        const card = document.createElement('div');
        card.className = 'gallery-card';
        card.dataset.preset = p.id;

        const preview = document.createElement('div');
        preview.className = 'gallery-preview';

        if (p.preview) {
          preview.innerHTML = p.preview;
        } else {
          preview.innerHTML = '<p style="text-align:center;color:#999;">Loading...</p>';
        }

        const title = document.createElement('h3');
        title.textContent = p.name;

        card.appendChild(preview);
        card.appendChild(title);
        galleryEl.appendChild(card);

        card.addEventListener('click', () => selectPreset(p.id));
      });
    }

    async function selectPreset(presetId) {
      currentPreset = presetId;
      galleryEl2.style.display = 'none';
      editorEl.classList.add('visible');
      worldName.textContent = `<strong>${presets.find(p => p.id === presetId).name}</strong>`;
      await renderMap();
    }

    async function renderMap() {
      if (!currentPreset) return;

      previewEl.innerHTML = '<p style="color: #999;">Generating map…</p>';
      const seed = parseInt(seedSlider.value);

      try {
        const res = await fetch('/api/render', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ preset: currentPreset, seed }),
        });

        if (!res.ok) {
          const err = await res.json();
          setStatus(`Render error: ${err.error}`, true);
          previewEl.innerHTML = '<p style="color: #f44336;">Error rendering map</p>';
          return;
        }

        const data = await res.json();
        previewEl.innerHTML = data.svg;
      } catch (e) {
        setStatus(`Error: ${e.message}`, true);
        previewEl.innerHTML = '<p style="color: #f44336;">Error rendering map</p>';
      }
    }

    async function downloadMap(format) {
      if (!currentPreset) return;
      downloadSvgBtn.disabled = downloadPngBtn.disabled = true;

      try {
        const seed = parseInt(seedSlider.value);
        const res = await fetch('/api/download', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ preset: currentPreset, seed, format }),
        });

        if (!res.ok) {
          const err = await res.json();
          setStatus(`Download error: ${err.error}`, true);
          return;
        }

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `map-${seed}.${format}`;
        a.click();
        URL.revokeObjectURL(url);
        setStatus(`Downloaded map-${seed}.${format}`);
      } catch (e) {
        setStatus(`Download error: ${e.message}`, true);
      } finally {
        downloadSvgBtn.disabled = downloadPngBtn.disabled = false;
      }
    }

    seedSlider.addEventListener('input', e => {
      seedValue.textContent = e.target.value;
      renderMap();
    });

    downloadSvgBtn.addEventListener('click', () => downloadMap('svg'));
    downloadPngBtn.addEventListener('click', () => downloadMap('png'));

    copyLinkBtn.addEventListener('click', () => {
      const url = `${window.location.origin}?preset=${currentPreset}&seed=${seedSlider.value}`;
      navigator.clipboard.writeText(url).then(() => {
        copyStatus.textContent = '✓ Copied!';
        setTimeout(() => { copyStatus.textContent = ''; }, 2000);
      });
    });

    backBtn.addEventListener('click', () => {
      editorEl.classList.remove('visible');
      galleryEl2.style.display = 'block';
      currentPreset = null;
    });

    // Load URL params
    const params = new URLSearchParams(window.location.search);
    if (params.has('preset')) {
      seedSlider.value = params.get('seed') || 42;
      seedValue.textContent = seedSlider.value;
      selectPreset(params.get('preset'));
    }

    loadPresets();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=3000, debug=True)
