    const TIERS = ["hamlet","village","town","city","capital","ruin","castle","camp"];
    const PATH_KINDS = ["road","trail","river","ferry"];
    const PALETTE_KEYS = [
      ["background", "Background"],
      ["land", "Land"],
      ["mountain", "Mountain"],
      ["mountain_stroke", "Mountain stroke"],
      ["water", "Water"],
      ["water_tributary", "Tributary"],
      ["water_deep", "Deep water"],
      ["paddy", "Paddy"],
      ["forest", "Forest"],
      ["desert", "Desert"],
      ["swamp", "Swamp"],
      ["ice", "Ice"],
      ["plain", "Plain"],
      ["coast", "Coast"],
      ["settlement", "Settlement"],
      ["settlement_roof", "Roof"],
      ["road", "Road"],
      ["road_dim", "Road (dim)"],
      ["text", "Text"],
      ["text_dim", "Text (dim)"],
      ["text_faint", "Text (faint)"],
      ["mist_wall", "Mist wall"],
      ["mist_wall_stroke", "Mist wall stroke"],
      ["passage", "Passage"],
      ["zone", "Zone"],
      ["old_wall", "Old wall"],
      ["palace_roof", "Palace roof"],
      ["palace_roof_light", "Palace roof light"],
      ["palace_trim", "Palace trim"],
      ["ink", "Ink"],
      ["paper", "Paper"],
      ["gold", "Gold"],
    ];

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
    const propMountainKind = document.getElementById('prop-mountain-kind');
    const propMountainDensity = document.getElementById('prop-mountain-density');
    const propMountainSize = document.getElementById('prop-mountain-size');
    const propMountainRotation = document.getElementById('prop-mountain-rotation');
    const mountainDensityVal = document.getElementById('mountain-density-val');
    const mountainSizeVal = document.getElementById('mountain-size-val');
    const mountainRotationVal = document.getElementById('mountain-rotation-val');
    const mountainSizeGroup = document.getElementById('prop-mountain-size-group');
    const mountainRotationGroup = document.getElementById('prop-mountain-rotation-group');
    const routePointsHint = document.getElementById('route-points-hint');
    const mountainPointsHint = document.getElementById('mountain-points-hint');
    const inspectorEmpty = document.getElementById('inspector-empty');
    const inspectorTitle = document.getElementById('inspector-title');
    const inspectorPlace = document.getElementById('inspector-place');
    const inspectorRoute = document.getElementById('inspector-route');
    const inspectorMountain = document.getElementById('inspector-mountain');
    const inspectorBiome = document.getElementById('inspector-biome');
    const inspectorRegionLabel = document.getElementById('inspector-region-label');
    const inspectorLake = document.getElementById('inspector-lake');
    const inspectorShip = document.getElementById('inspector-ship');
    const inspectorVolcano = document.getElementById('inspector-volcano');
    const inspectorSacredSite = document.getElementById('inspector-sacred-site');
    const propBiomeName = document.getElementById('prop-biome-name');
    const propBiomeType = document.getElementById('prop-biome-type');
    const propBiomeFill = document.getElementById('prop-biome-fill');
    const propBiomeDensity = document.getElementById('prop-biome-density');
    const biomeDensityVal = document.getElementById('biome-density-val');
    const propLabelName = document.getElementById('prop-label-name');
    const propLabelSize = document.getElementById('prop-label-size');
    const labelSizeVal = document.getElementById('label-size-val');
    const propLakeRx = document.getElementById('prop-lake-rx');
    const propLakeRy = document.getElementById('prop-lake-ry');
    const lakeRxVal = document.getElementById('lake-rx-val');
    const lakeRyVal = document.getElementById('lake-ry-val');
    const propLakeFill = document.getElementById('prop-lake-fill');
    const propSacredKind = document.getElementById('prop-sacred-kind');
    const sacredKindSelect = document.getElementById('sacred-kind');
    const landmarkHint = document.getElementById('landmark-hint');
    const propTitle = document.getElementById('prop-title');
    const propTitleSize = document.getElementById('prop-title-size');
    const propTitleSizeValue = document.getElementById('prop-title-size-value');
    const propTitleBold = document.getElementById('prop-title-bold');
    const propTitleItalic = document.getElementById('prop-title-italic');
    const undoBtn = document.getElementById('undo-btn');
    const redoBtn = document.getElementById('redo-btn');

    let presets = [];
    let currentPreset = null;
    let workingConfig = null;
    let selectedId = null;
    let selectedKind = null; // place | route | mountain
    let mode = 'select'; // select | place | path | mountain
    let placeTier = 'village';
    let pathKind = 'road';
    let mountainKind = 'ridge';
    let draftPoints = [];
    let lastClickTime = 0;
    let renderTimer = null;
    let renderSeq = 0;
    let undoStack = [];
    let redoStack = [];
    let dragging = null;
    let placeCounters = {};
    let pathCounters = {};
    let mountainCounters = {};

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

    const PYODIDE_VERSION = '0.26.4';
    let bridge = null;

    async function initBridge() {
      setStatus('Loading the in-browser Python runtime (one-time download, may take a moment)…');
      const pyodide = await loadPyodide({
        indexURL: `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`,
      });
      pyodide.FS.mkdirTree('/pkg');
      pyodide.runPython('import sys; sys.path.insert(0, "/pkg")');
      const manifest = await (await fetch('src/fantasy_map_generator-files.json')).json();
      for (const rel of manifest) {
        const resp = await fetch('src/fantasy_map_generator/' + rel);
        if (!resp.ok) throw new Error(`Could not load ${rel}`);
        const text = await resp.text();
        const path = '/pkg/fantasy_map_generator/' + rel;
        const dir = path.slice(0, path.lastIndexOf('/'));
        pyodide.FS.mkdirTree(dir);
        pyodide.FS.writeFile(path, text);
      }
      const bridgeSrc = await (await fetch('bridge.py')).text();
      pyodide.runPython(bridgeSrc);
      const g = pyodide.globals;
      bridge = {
        presets: () => g.get('bridge_presets')(),
        render: (payload) => g.get('bridge_render')(payload),
        download: (payload) => g.get('bridge_download')(payload),
        normalize: (payload) => g.get('bridge_normalize')(payload),
        fromSvg: (payload) => g.get('bridge_from_svg')(payload),
        addMountain: (payload) => g.get('add_mountain')(payload),
        updateMountain: (payload) => g.get('update_mountain')(payload),
        deleteMountain: (payload) => g.get('delete_mountain')(payload),
      };
      setStatus('');
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
      document.getElementById('mode-mountain').classList.toggle('active', m === 'mountain');
      const landmarkModes = ['region', 'label', 'lake', 'ship', 'volcano', 'sacred'];
      landmarkModes.forEach(k => document.getElementById('mode-' + k).classList.toggle('active', m === k));
      previewWrap.classList.toggle('select-mode', m === 'select');
      previewWrap.classList.toggle('place-mode', m === 'place' || m === 'path' || m === 'mountain' || landmarkModes.includes(m));
      if (m === 'select') {
        draftPoints = [];
        modeHint.textContent = 'Click a settlement, path, mountain, or landmark to select. Drag to move.';
        [...paletteEl.querySelectorAll('button')].forEach(x => x.classList.remove('active'));
        [...pathPaletteEl.querySelectorAll('button')].forEach(x => x.classList.remove('active'));
        drawDraftOverlay();
      } else if (m === 'path') {
        modeHint.textContent = `Draw ${pathKind}: click waypoints, double-click or Enter to finish.`;
      } else if (m === 'mountain') {
        const hint = mountainKind === 'single'
          ? `Place ${mountainKind} mountain: click to place. Esc to cancel.`
          : `Draw ${mountainKind} mountain: click waypoints, double-click or Enter to finish.`;
        modeHint.textContent = hint;
      } else if (landmarkModes.includes(m)) {
        landmarkHint.textContent = `Click the map to drop a ${m === 'sacred' ? 'sacred site' : m}. Esc to cancel.`;
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
      const out = JSON.parse(bridge.presets());
      presets = out;
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
      capturePaletteSnapshot();
      syncColorGrid();
      updateInspector();
      await renderMap();
      try { sessionStorage.setItem('fmg_working', JSON.stringify({ preset: presetId, config: workingConfig, ...knobs() })); } catch (_) {}
    }

    // Index-keyed collections (ships/volcanoes/sacred_sites: plain tuples,
    // no id field of their own) address items by position in the array, via
    // an id like "ship_3" -- same convention as render.py/bridge.py.
    function indexFromId(prefix, id) {
      if (!id || !id.startsWith(prefix + '_')) return null;
      const n = Number(id.slice(prefix.length + 1));
      return Number.isInteger(n) ? n : null;
    }

    // Current [x, y] for one of the six landmark kinds, by id -- used both
    // to start a drag (as the drag's origin) and to apply one (endDrag).
    function landmarkCenter(kind, id) {
      if (!workingConfig) return null;
      if (kind === 'biome') {
        const r = (workingConfig.biome_regions || []).find(x => x.id === id);
        return r ? r.center : null;
      }
      if (kind === 'region_label') {
        const r = (workingConfig.region_labels || []).find(x => x.id === id);
        return r ? r.center : null;
      }
      if (kind === 'lake') {
        const w = (workingConfig.lakes || []).find(x => x.id === id);
        return w ? w.center : null;
      }
      if (kind === 'ship') {
        const i = indexFromId('ship', id);
        return i !== null ? (workingConfig.ships || [])[i] || null : null;
      }
      if (kind === 'volcano') {
        const i = indexFromId('volcano', id);
        return i !== null ? (workingConfig.volcanoes || [])[i] || null : null;
      }
      if (kind === 'sacred_site') {
        const i = indexFromId('sacred', id);
        const s = i !== null ? (workingConfig.sacred_sites || [])[i] : null;
        return s ? [s[0], s[1]] : null;
      }
      return null;
    }

    function updateInspector() {
      const title = selectedKind === 'title' && selectedId === 'map_title' && workingConfig ? workingConfig : null;
      const place = selectedKind === 'place' && selectedId && workingConfig && workingConfig.places
        ? workingConfig.places[selectedId] : null;
      const route = selectedKind === 'route' && selectedId && workingConfig && workingConfig.routes
        ? workingConfig.routes[selectedId] : null;
      const mountain = selectedKind === 'mountain' && selectedId && workingConfig && workingConfig.mountain_ranges
        ? workingConfig.mountain_ranges[selectedId] : null;
      const biome = selectedKind === 'biome' && selectedId && workingConfig && workingConfig.biome_regions
        ? workingConfig.biome_regions.find(r => r.id === selectedId) : null;
      const regionLabel = selectedKind === 'region_label' && selectedId && workingConfig && workingConfig.region_labels
        ? workingConfig.region_labels.find(r => r.id === selectedId) : null;
      const lake = selectedKind === 'lake' && selectedId && workingConfig && workingConfig.lakes
        ? workingConfig.lakes.find(w => w.id === selectedId) : null;
      const shipIdx = selectedKind === 'ship' ? indexFromId('ship', selectedId) : null;
      const ship = shipIdx !== null && workingConfig && workingConfig.ships ? workingConfig.ships[shipIdx] : null;
      const volcanoIdx = selectedKind === 'volcano' ? indexFromId('volcano', selectedId) : null;
      const volcano = volcanoIdx !== null && workingConfig && workingConfig.volcanoes ? workingConfig.volcanoes[volcanoIdx] : null;
      const sacredIdx = selectedKind === 'sacred_site' ? indexFromId('sacred', selectedId) : null;
      const sacred = sacredIdx !== null && workingConfig && workingConfig.sacred_sites ? workingConfig.sacred_sites[sacredIdx] : null;
      const anySelected = title || place || route || mountain || biome || regionLabel || lake || ship || volcano || sacred;
      inspectorEmpty.style.display = anySelected ? 'none' : 'block';
      inspectorTitle.style.display = title ? 'block' : 'none';
      inspectorPlace.style.display = place ? 'block' : 'none';
      inspectorRoute.style.display = route ? 'block' : 'none';
      inspectorMountain.style.display = mountain ? 'block' : 'none';
      inspectorBiome.style.display = biome ? 'block' : 'none';
      inspectorRegionLabel.style.display = regionLabel ? 'block' : 'none';
      inspectorLake.style.display = lake ? 'block' : 'none';
      inspectorShip.style.display = ship ? 'block' : 'none';
      inspectorVolcano.style.display = volcano ? 'block' : 'none';
      inspectorSacredSite.style.display = sacred ? 'block' : 'none';
      if (biome) {
        propBiomeName.value = biome.name || '';
        propBiomeType.value = biome.biome || 'plain';
        propBiomeFill.value = biome.fill || '#808080';
        propBiomeFill.dataset.cleared = biome.fill ? '0' : '1';
        propBiomeDensity.value = biome.density ?? 0.5;
        biomeDensityVal.textContent = (biome.density ?? 0.5).toFixed(2);
      }
      if (regionLabel) {
        propLabelName.value = regionLabel.name || '';
        propLabelSize.value = regionLabel.font_size || 30;
        labelSizeVal.textContent = (regionLabel.font_size || 30).toFixed(0);
      }
      if (lake) {
        propLakeRx.value = lake.radii ? lake.radii[0] : 20;
        propLakeRy.value = lake.radii ? lake.radii[1] : 15;
        lakeRxVal.textContent = propLakeRx.value;
        lakeRyVal.textContent = propLakeRy.value;
        propLakeFill.value = lake.fill || '#6f9ec4';
        propLakeFill.dataset.cleared = lake.fill ? '0' : '1';
      }
      if (sacred) {
        propSacredKind.value = sacred[2] || 'kurgan';
      }
      if (title) {
        propTitle.value = workingConfig.name || '';
        propTitleSize.value = workingConfig.title_font_size || 26;
        propTitleSizeValue.textContent = propTitleSize.value;
        propTitleBold.checked = workingConfig.title_bold || false;
        propTitleItalic.checked = workingConfig.title_italic || false;
      }
      if (place) {
        propName.value = place.name || '';
        propTier.value = place.tier || 'village';
      }
      if (route) {
        propRouteLabel.value = route.label || selectedId || '';
        propRouteKind.value = route.kind || 'road';
        routePointsHint.textContent = `${(route.points || []).length} waypoints`;
      }
      if (mountain) {
        propMountainKind.value = mountain.kind || 'ridge';
        propMountainDensity.value = mountain.density || 0.5;
        propMountainSize.value = mountain.size || 50;
        propMountainRotation.value = mountain.rotation || 0;
        mountainDensityVal.textContent = (mountain.density || 0.5).toFixed(2);
        mountainSizeVal.textContent = (mountain.size || 50).toFixed(0);
        mountainRotationVal.textContent = (mountain.rotation || 0).toFixed(0) + '°';

        // Show size and rotation controls for all mountain types
        mountainSizeGroup.style.display = 'block';
        mountainRotationGroup.style.display = 'block';

        const pointCount = (mountain.points || []).length;
        mountainPointsHint.textContent = mountain.kind === 'ridge' ? `${pointCount} waypoints` : `— ${mountain.kind}`;
      }
    }

    const colorInputs = {};
    let paletteSnapshot = null;
    let colorDirty = false;

    function buildColorGrid() {
      const grid = document.getElementById('color-grid');
      grid.innerHTML = '';
      for (const [key, label] of PALETTE_KEYS) {
        const row = document.createElement('div');
        row.className = 'color-row';
        const lab = document.createElement('label');
        lab.textContent = label;
        lab.htmlFor = 'color-' + key;
        const inp = document.createElement('input');
        inp.type = 'color';
        inp.id = 'color-' + key;
        inp.value = '#000000';
        row.appendChild(lab); row.appendChild(inp);
        grid.appendChild(row);
        colorInputs[key] = inp;
        inp.addEventListener('input', () => {
          if (!workingConfig) return;
          if (!workingConfig.palette) workingConfig.palette = {};
          if (!colorDirty) { pushUndo(); colorDirty = true; }
          workingConfig.palette[key] = inp.value;
          debounceRender();
        });
        inp.addEventListener('change', () => { colorDirty = false; });
      }
    }

    function syncColorGrid() {
      const pal = (workingConfig && workingConfig.palette) || {};
      for (const [key] of PALETTE_KEYS) {
        const v = pal[key];
        if (typeof v === 'string' && /^#[0-9a-fA-F]{6}$/.test(v)) {
          colorInputs[key].value = v;
        }
      }
    }

    function capturePaletteSnapshot() {
      paletteSnapshot = workingConfig && workingConfig.palette
        ? deepClone(workingConfig.palette) : null;
    }

    function resetColors() {
      if (!workingConfig || !paletteSnapshot) return;
      pushUndo();
      workingConfig.palette = deepClone(paletteSnapshot);
      syncColorGrid();
      renderMap();
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
        const out = JSON.parse(bridge.render(JSON.stringify(body)));
        if (seq !== renderSeq) return;
        if (out.error) {
          setStatus(out.error, true);
          return;
        }
        previewEl.innerHTML = out.svg;
        if (out.config) workingConfig = out.config;
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

    function placeLandmarkAt(kind, x, y) {
      pushUndo();
      if (kind === 'region') {
        const id = 'biome_' + Math.random().toString(16).slice(2, 10);
        if (!workingConfig.biome_regions) workingConfig.biome_regions = [];
        workingConfig.biome_regions.push({
          name: '', biome: 'plain', center: [x, y], radii: [80, 60], density: 0.5, fill: null, id,
        });
        selectedId = id; selectedKind = 'biome';
      } else if (kind === 'label') {
        const id = 'region_label_' + Math.random().toString(16).slice(2, 10);
        if (!workingConfig.region_labels) workingConfig.region_labels = [];
        workingConfig.region_labels.push({
          name: 'New Region', center: [x, y], font_size: 30, rotation: 0, id,
        });
        selectedId = id; selectedKind = 'region_label';
      } else if (kind === 'lake') {
        const id = 'lake_' + Math.random().toString(16).slice(2, 10);
        if (!workingConfig.lakes) workingConfig.lakes = [];
        workingConfig.lakes.push({ center: [x, y], radii: [20, 15], fill: null, id });
        selectedId = id; selectedKind = 'lake';
      } else if (kind === 'ship') {
        if (!workingConfig.ships) workingConfig.ships = [];
        workingConfig.ships.push([x, y]);
        selectedId = `ship_${workingConfig.ships.length - 1}`; selectedKind = 'ship';
      } else if (kind === 'volcano') {
        if (!workingConfig.volcanoes) workingConfig.volcanoes = [];
        workingConfig.volcanoes.push([x, y]);
        selectedId = `volcano_${workingConfig.volcanoes.length - 1}`; selectedKind = 'volcano';
      } else if (kind === 'sacred') {
        if (!workingConfig.sacred_sites) workingConfig.sacred_sites = [];
        workingConfig.sacred_sites.push([x, y, sacredKindSelect.value || 'kurgan']);
        selectedId = `sacred_${workingConfig.sacred_sites.length - 1}`; selectedKind = 'sacred_site';
      }
      setMode('select');
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

    function finishMountain() {
      if (mountainKind === 'ridge' && draftPoints.length < 2) {
        setStatus('Need at least 2 waypoints for ridge mountain', true);
        return;
      }
      if (mountainKind === 'single' && draftPoints.length < 1) {
        setStatus('Click to place a single mountain', true);
        return;
      }
      pushUndo();
      mountainCounters[mountainKind] = (mountainCounters[mountainKind] || 0) + 1;
      const id = 'mountain_' + Math.random().toString(16).slice(2, 10);
      if (!workingConfig.mountain_ranges) workingConfig.mountain_ranges = {};
      const mountain = {
        kind: mountainKind,
        density: 0.7,
        size: 50,
        rotation: 0,
        id,
      };
      if (mountainKind === 'ridge') {
        mountain.points = draftPoints.map(p => [p[0], p[1]]);
      } else if (mountainKind === 'single') {
        mountain.center = [draftPoints[0][0], draftPoints[0][1]];
      } else {
        mountain.center = [workingConfig.canvas_width / 2, workingConfig.canvas_height / 2];
        mountain.radii = [80, 60];
      }
      workingConfig.mountain_ranges[id] = mountain;
      draftPoints = [];
      selectedId = id;
      selectedKind = 'mountain';
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

      if (['region', 'label', 'lake', 'ship', 'volcano', 'sacred'].includes(mode)) {
        const c = clampToCanvas(pt.x, pt.y);
        placeLandmarkAt(mode, c.x, c.y);
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

      if (mode === 'mountain') {
        const c = clampToCanvas(pt.x, pt.y);
        if (isDouble && draftPoints.length >= 1) {
          // double-click finishes
          if (mountainKind === 'ridge' && draftPoints.length >= 2) finishMountain();
          return;
        }
        draftPoints.push([c.x, c.y]);
        drawDraftOverlay();
        if (mountainKind === 'single') {
          // Single mountains finish immediately
          finishMountain();
          return;
        }
        modeHint.textContent = `Draw ${mountainKind}: ${draftPoints.length} point(s). Double-click or Enter to finish.`;
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
        const route = workingConfig.routes[feat.id];
        dragging = {
          id: feat.id,
          kind: 'route',
          pointerId: evt.pointerId,
          origX: route.points?.[0]?.[0] ?? 0,
          origY: route.points?.[0]?.[1] ?? 0,
          moved: false,
        };
        previewWrap.setPointerCapture(evt.pointerId);
        ghost.style.display = 'block';
        const rect = previewWrap.getBoundingClientRect();
        ghost.style.left = (evt.clientX - rect.left) + 'px';
        ghost.style.top = (evt.clientY - rect.top) + 'px';
        updateInspector();
        renderMap();
      } else if (feat && feat.kind === 'mountain' && workingConfig.mountain_ranges[feat.id]) {
        selectedId = feat.id;
        selectedKind = 'mountain';
        const mr = workingConfig.mountain_ranges[feat.id];
        const origX = mr.kind === 'ridge' ? mr.points?.[0]?.[0] ?? 0 : mr.center?.[0] ?? 0;
        const origY = mr.kind === 'ridge' ? mr.points?.[0]?.[1] ?? 0 : mr.center?.[1] ?? 0;
        dragging = {
          id: feat.id,
          kind: 'mountain',
          pointerId: evt.pointerId,
          origX: origX,
          origY: origY,
          moved: false,
        };
        previewWrap.setPointerCapture(evt.pointerId);
        ghost.style.display = 'block';
        const rect = previewWrap.getBoundingClientRect();
        ghost.style.left = (evt.clientX - rect.left) + 'px';
        ghost.style.top = (evt.clientY - rect.top) + 'px';
        updateInspector();
        renderMap();
      } else if (feat && ['biome', 'region_label', 'lake', 'ship', 'volcano', 'sacred_site'].includes(feat.kind)) {
        const center = landmarkCenter(feat.kind, feat.id);
        if (!center) { selectedId = null; selectedKind = null; updateInspector(); renderMap(); return; }
        selectedId = feat.id;
        selectedKind = feat.kind;
        dragging = { id: feat.id, kind: feat.kind, pointerId: evt.pointerId, origX: center[0], origY: center[1], moved: false };
        previewWrap.setPointerCapture(evt.pointerId);
        ghost.style.display = 'block';
        const rect = previewWrap.getBoundingClientRect();
        ghost.style.left = (evt.clientX - rect.left) + 'px';
        ghost.style.top = (evt.clientY - rect.top) + 'px';
        updateInspector();
        renderMap();
      } else if (feat && feat.kind === 'title') {
        selectedId = 'map_title';
        selectedKind = 'title';
        dragging = {
          id: 'map_title',
          kind: 'title',
          pointerId: evt.pointerId,
          origX: workingConfig.title_x || (workingConfig.canvas_width / 2),
          origY: workingConfig.title_y || 30,
          moved: false,
        };
        previewWrap.setPointerCapture(evt.pointerId);
        ghost.style.display = 'block';
        const rect = previewWrap.getBoundingClientRect();
        ghost.style.left = (evt.clientX - rect.left) + 'px';
        ghost.style.top = (evt.clientY - rect.top) + 'px';
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
      if (!d.moved) return;
      const pt = svgPoint(evt);
      if (!pt) return;
      const c = clampToCanvas(pt.x, pt.y);
      pushUndo();

      if (d.kind === 'place' && workingConfig.places[d.id]) {
        workingConfig.places[d.id].x = c.x;
        workingConfig.places[d.id].y = c.y;
      } else if (d.kind === 'mountain' && workingConfig.mountain_ranges[d.id]) {
        const mr = workingConfig.mountain_ranges[d.id];
        if (mr.kind === 'ridge') {
          // Move all waypoints by the same offset
          const dx = c.x - d.origX;
          const dy = c.y - d.origY;
          if (mr.points) {
            mr.points = mr.points.map(p => [p[0] + dx, p[1] + dy]);
          }
        } else {
          // For single/ring/stacked, just move the center
          mr.center = [c.x, c.y];
        }
      } else if (d.kind === 'route' && workingConfig.routes[d.id]) {
        // Move all waypoints by the same offset
        const dx = c.x - d.origX;
        const dy = c.y - d.origY;
        if (workingConfig.routes[d.id].points) {
          workingConfig.routes[d.id].points = workingConfig.routes[d.id].points.map(p => [p[0] + dx, p[1] + dy]);
        }
      } else if (d.kind === 'title') {
        // Move the title
        workingConfig.title_x = c.x;
        workingConfig.title_y = c.y;
      } else if (d.kind === 'biome') {
        const r = workingConfig.biome_regions.find(x => x.id === d.id);
        if (r) r.center = [c.x, c.y];
      } else if (d.kind === 'region_label') {
        const r = workingConfig.region_labels.find(x => x.id === d.id);
        if (r) r.center = [c.x, c.y];
      } else if (d.kind === 'lake') {
        const w = workingConfig.lakes.find(x => x.id === d.id);
        if (w) w.center = [c.x, c.y];
      } else if (d.kind === 'ship') {
        const i = indexFromId('ship', d.id);
        if (i !== null) workingConfig.ships[i] = [c.x, c.y];
      } else if (d.kind === 'volcano') {
        const i = indexFromId('volcano', d.id);
        if (i !== null) workingConfig.volcanoes[i] = [c.x, c.y];
      } else if (d.kind === 'sacred_site') {
        const i = indexFromId('sacred', d.id);
        if (i !== null) workingConfig.sacred_sites[i] = [c.x, c.y, workingConfig.sacred_sites[i][2]];
      }

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

    document.getElementById('mode-mountain').addEventListener('click', () => {
      mountainKind = document.getElementById('mountain-kind').value;
      draftPoints = [];
      setMode('mountain');
      [...paletteEl.querySelectorAll('button')].forEach(x => x.classList.remove('active'));
      [...pathPaletteEl.querySelectorAll('button')].forEach(x => x.classList.remove('active'));
    });

    document.getElementById('mountain-kind').addEventListener('change', (e) => {
      mountainKind = e.target.value;
    });

    ['region', 'label', 'lake', 'ship', 'volcano', 'sacred'].forEach(k => {
      document.getElementById('mode-' + k).addEventListener('click', () => setMode(k));
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
      if (e.key === 'Enter' && mode === 'mountain') {
        e.preventDefault();
        finishMountain();
      }
      const typing = [propName, propRouteLabel, propTitle, propBiomeName, propLabelName].includes(document.activeElement);
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
      } else if (selectedKind === 'mountain' && workingConfig.mountain_ranges[selectedId]) {
        delete workingConfig.mountain_ranges[selectedId];
      } else if (selectedKind === 'biome') {
        workingConfig.biome_regions = (workingConfig.biome_regions || []).filter(x => x.id !== selectedId);
      } else if (selectedKind === 'region_label') {
        workingConfig.region_labels = (workingConfig.region_labels || []).filter(x => x.id !== selectedId);
      } else if (selectedKind === 'lake') {
        workingConfig.lakes = (workingConfig.lakes || []).filter(x => x.id !== selectedId);
      } else if (selectedKind === 'ship') {
        const i = indexFromId('ship', selectedId);
        if (i !== null) workingConfig.ships.splice(i, 1);
      } else if (selectedKind === 'volcano') {
        const i = indexFromId('volcano', selectedId);
        if (i !== null) workingConfig.volcanoes.splice(i, 1);
      } else if (selectedKind === 'sacred_site') {
        const i = indexFromId('sacred', selectedId);
        if (i !== null) workingConfig.sacred_sites.splice(i, 1);
      }
      selectedId = null;
      selectedKind = null;
      updateInspector();
      renderMap();
    }

    document.getElementById('delete-feature').addEventListener('click', deleteSelected);
    document.getElementById('delete-route').addEventListener('click', deleteSelected);
    document.getElementById('delete-mountain').addEventListener('click', deleteSelected);
    document.getElementById('delete-biome').addEventListener('click', deleteSelected);
    document.getElementById('delete-region-label').addEventListener('click', deleteSelected);
    document.getElementById('delete-lake').addEventListener('click', deleteSelected);
    document.getElementById('delete-ship').addEventListener('click', deleteSelected);
    document.getElementById('delete-volcano').addEventListener('click', deleteSelected);
    document.getElementById('delete-sacred-site').addEventListener('click', deleteSelected);

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

    function applyMountainProps() {
      if (selectedKind !== 'mountain' || !selectedId || !workingConfig.mountain_ranges[selectedId]) return;
      pushUndo();
      const mr = workingConfig.mountain_ranges[selectedId];
      mr.kind = propMountainKind.value || 'ridge';
      mr.density = parseFloat(propMountainDensity.value) || 0.5;
      mr.size = parseFloat(propMountainSize.value) || 50;
      mr.rotation = parseFloat(propMountainRotation.value) || 0;
      renderMap();
    }
    propMountainKind.addEventListener('change', applyMountainProps);
    propMountainDensity.addEventListener('input', (e) => {
      mountainDensityVal.textContent = parseFloat(e.target.value).toFixed(2);
      if (propTimer) clearTimeout(propTimer);
      propTimer = setTimeout(applyMountainProps, 400);
    });
    propMountainSize.addEventListener('input', (e) => {
      mountainSizeVal.textContent = parseFloat(e.target.value).toFixed(0);
      if (propTimer) clearTimeout(propTimer);
      propTimer = setTimeout(applyMountainProps, 400);
    });
    propMountainRotation.addEventListener('input', (e) => {
      mountainRotationVal.textContent = parseFloat(e.target.value).toFixed(0) + '°';
      if (propTimer) clearTimeout(propTimer);
      propTimer = setTimeout(applyMountainProps, 400);
    });

    function applyTitleProps() {
      if (selectedKind !== 'title' || !workingConfig) return;
      pushUndo();
      workingConfig.name = propTitle.value || 'Untitled Fantasy World';
      workingConfig.title_font_size = parseFloat(propTitleSize.value) || 26;
      workingConfig.title_bold = propTitleBold.checked;
      workingConfig.title_italic = propTitleItalic.checked;
      renderMap();
    }
    propTitle.addEventListener('change', applyTitleProps);
    propTitle.addEventListener('input', () => {
      if (propTimer) clearTimeout(propTimer);
      propTimer = setTimeout(applyTitleProps, 400);
    });
    propTitleSize.addEventListener('input', (e) => {
      propTitleSizeValue.textContent = parseFloat(e.target.value).toFixed(0);
      if (propTimer) clearTimeout(propTimer);
      propTimer = setTimeout(applyTitleProps, 400);
    });
    propTitleBold.addEventListener('change', applyTitleProps);
    propTitleItalic.addEventListener('change', applyTitleProps);

    function applyBiomeProps() {
      if (selectedKind !== 'biome' || !selectedId) return;
      const r = (workingConfig.biome_regions || []).find(x => x.id === selectedId);
      if (!r) return;
      pushUndo();
      r.name = propBiomeName.value || '';
      r.biome = propBiomeType.value || 'plain';
      r.fill = propBiomeFill.dataset.cleared === '1' ? null : propBiomeFill.value;
      r.density = parseFloat(propBiomeDensity.value) || 0.5;
      renderMap();
    }
    propBiomeName.addEventListener('change', applyBiomeProps);
    propBiomeName.addEventListener('input', () => {
      if (propTimer) clearTimeout(propTimer);
      propTimer = setTimeout(applyBiomeProps, 400);
    });
    propBiomeType.addEventListener('change', applyBiomeProps);
    propBiomeFill.addEventListener('input', () => { propBiomeFill.dataset.cleared = '0'; applyBiomeProps(); });
    propBiomeDensity.addEventListener('input', (e) => {
      biomeDensityVal.textContent = parseFloat(e.target.value).toFixed(2);
      if (propTimer) clearTimeout(propTimer);
      propTimer = setTimeout(applyBiomeProps, 400);
    });
    document.getElementById('prop-biome-fill-clear').addEventListener('click', () => {
      propBiomeFill.dataset.cleared = '1';
      applyBiomeProps();
    });

    function applyRegionLabelProps() {
      if (selectedKind !== 'region_label' || !selectedId) return;
      const r = (workingConfig.region_labels || []).find(x => x.id === selectedId);
      if (!r) return;
      pushUndo();
      r.name = propLabelName.value || 'New Region';
      r.font_size = parseFloat(propLabelSize.value) || 30;
      renderMap();
    }
    propLabelName.addEventListener('change', applyRegionLabelProps);
    propLabelName.addEventListener('input', () => {
      if (propTimer) clearTimeout(propTimer);
      propTimer = setTimeout(applyRegionLabelProps, 400);
    });
    propLabelSize.addEventListener('input', (e) => {
      labelSizeVal.textContent = parseFloat(e.target.value).toFixed(0);
      if (propTimer) clearTimeout(propTimer);
      propTimer = setTimeout(applyRegionLabelProps, 400);
    });

    function applyLakeProps() {
      if (selectedKind !== 'lake' || !selectedId) return;
      const w = (workingConfig.lakes || []).find(x => x.id === selectedId);
      if (!w) return;
      pushUndo();
      w.radii = [parseFloat(propLakeRx.value) || 20, parseFloat(propLakeRy.value) || 15];
      w.fill = propLakeFill.dataset.cleared === '1' ? null : propLakeFill.value;
      renderMap();
    }
    propLakeRx.addEventListener('input', (e) => {
      lakeRxVal.textContent = e.target.value;
      if (propTimer) clearTimeout(propTimer);
      propTimer = setTimeout(applyLakeProps, 400);
    });
    propLakeRy.addEventListener('input', (e) => {
      lakeRyVal.textContent = e.target.value;
      if (propTimer) clearTimeout(propTimer);
      propTimer = setTimeout(applyLakeProps, 400);
    });
    propLakeFill.addEventListener('input', () => { propLakeFill.dataset.cleared = '0'; applyLakeProps(); });
    document.getElementById('prop-lake-fill-clear').addEventListener('click', () => {
      propLakeFill.dataset.cleared = '1';
      applyLakeProps();
    });

    function applySacredSiteProps() {
      if (selectedKind !== 'sacred_site' || !selectedId) return;
      const i = indexFromId('sacred', selectedId);
      if (i === null || !workingConfig.sacred_sites[i]) return;
      pushUndo();
      const [x, y] = workingConfig.sacred_sites[i];
      workingConfig.sacred_sites[i] = [x, y, propSacredKind.value || 'kurgan'];
      renderMap();
    }
    propSacredKind.addEventListener('change', applySacredSiteProps);

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
      if (format === 'png') { downloadPng(); return; }
      const out = JSON.parse(bridge.download(JSON.stringify({ config: workingConfig, format, ...knobs() })));
      if (out.error) {
        setStatus(out.error, true);
        return;
      }
      const blob = new Blob([out.data], { type: out.mime });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = out.filename;
      a.click();
      URL.revokeObjectURL(a.href);
    }
    async function downloadPng() {
      const svg = previewEl.querySelector('svg');
      if (!svg) return;
      const svgUrl = URL.createObjectURL(new Blob(
        [new XMLSerializer().serializeToString(svg)],
        { type: 'image/svg+xml;charset=utf-8' }
      ));
      try {
        const img = new Image();
        await new Promise((resolve, reject) => {
          img.onload = resolve;
          img.onerror = reject;
          img.src = svgUrl;
        });
        const box = svg.viewBox.baseVal;
        const scale = 2;
        const canvas = document.createElement('canvas');
        canvas.width = Math.round(box.width * scale);
        canvas.height = Math.round(box.height * scale);
        canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
        const a = document.createElement('a');
        a.href = canvas.toDataURL('image/png');
        a.download = `map-${knobs().seed}.png`;
        a.click();
      } catch (e) {
        setStatus(e.message, true);
      } finally {
        URL.revokeObjectURL(svgUrl);
      }
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
        const out = JSON.parse(bridge.normalize(JSON.stringify(payload)));
        if (out.error) throw new Error(out.error || 'Invalid world');
        pushUndo();
        workingConfig = out.config;
        currentPreset = 'custom';
        worldName.textContent = workingConfig.name || 'Custom world';
        selectedId = null; selectedKind = null;
        capturePaletteSnapshot();
        syncColorGrid();
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
        const out = JSON.parse(bridge.fromSvg(JSON.stringify({ svg: text })));
        if (out.error) throw new Error(out.error || 'Invalid SVG world');
        pushUndo();
        workingConfig = out.config;
        if (out.seed != null) {
          seedSlider.value = out.seed;
          seedValue.textContent = String(out.seed);
        }
        currentPreset = 'custom';
        worldName.textContent = (workingConfig && workingConfig.name) || 'Custom world';
        selectedId = null; selectedKind = null;
        capturePaletteSnapshot();
        syncColorGrid();
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

    document.getElementById('reset-colors').addEventListener('click', resetColors);
    buildColorGrid();

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

    (async function boot() {
      try {
        await initBridge();
      } catch (err) {
        setStatus('Could not start the map engine: ' + (err && err.message ? err.message : err), true);
        return;
      }
      await loadPresets();
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
    })();
