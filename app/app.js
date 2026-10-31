/* IACD Knowledge Graph — aplicação (sem frameworks; Cytoscape.js para o grafo).
 * Os dados vêm de ../data/kg.js (gerado por build/build.py). Nada de conteúdo está hardcoded aqui. */
(function () {
  'use strict';
  const DATA = window.KG_DATA;
  if (!DATA || !window.cytoscape) {
    document.getElementById('stage').innerHTML = '<p style="padding:40px">Não foi possível carregar os dados (data/kg.js). Corre <code>python build/build.py</code>.</p>';
    return;
  }
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const normTxt = (s) => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

  // ------------------------------------------------------------------ índices
  const N = new Map(DATA.nodes.map((n) => [n.id, n]));
  const UCS = DATA.nodes.filter((n) => n.type === 'uc').sort((a, b) => a.order - b.order);
  const CONCEPT_TYPES = new Set(['conceito', 'formula', 'algoritmo', 'ferramenta']);
  const isConcept = (n) => n && CONCEPT_TYPES.has(n.type);
  const DEP_TYPES = new Set(['prerequisite_of', 'applied_in', 'used_in']);
  const outE = new Map(), inE = new Map();
  DATA.nodes.forEach((n) => { outE.set(n.id, []); inE.set(n.id, []); });
  DATA.edges.forEach((e) => { outE.get(e.source)?.push(e); inE.get(e.target)?.push(e); });
  const childrenOf = (id) => outE.get(id).filter((e) => e.type === 'contains').map((e) => N.get(e.target));
  const temasOf = (uc) => childrenOf(uc).filter((n) => n.type === 'tema').sort((a, b) => a.order - b.order);
  const conceptsOf = (t) => childrenOf(t).filter(isConcept);
  const exercisesOf = (c) => outE.get(c).filter((e) => e.type === 'tested_by').map((e) => N.get(e.target))
    .concat(inE.get(c).filter((e) => e.type === 'requires').map((e) => N.get(e.source)));
  const ucNode = (n) => (n ? N.get(n.uc) : undefined);
  const hue = (n) => (n && n.type === 'uc' ? n.hue : (ucNode(n) || {}).hue) ?? 220;

  function depClosure(id, dir) { // dir: 'up' (pré-requisitos) | 'down' (dependentes)
    const seen = new Set(), q = [id];
    while (q.length) {
      const u = q.shift();
      const list = dir === 'down' ? outE.get(u).filter((e) => DEP_TYPES.has(e.type)).map((e) => e.target)
        : inE.get(u).filter((e) => DEP_TYPES.has(e.type)).map((e) => e.source);
      for (const v of list) if (!seen.has(v) && isConcept(N.get(v))) { seen.add(v); q.push(v); }
    }
    return seen;
  }

  // ------------------------------------------------------------------ tema / cores
  const root = document.documentElement;
  const isDark = () => root.dataset.theme === 'dark' || (!root.dataset.theme && matchMedia('(prefers-color-scheme: dark)').matches);
  const css = (v) => getComputedStyle(root).getPropertyValue(v).trim();
  function palette() {
    const d = isDark();
    return {
      d, text: css('--text'), text2: css('--text-2'), text3: css('--text-3'), bg: css('--bg'), surface: css('--surface'), border: d ? 'rgba(255,255,255,0.13)' : 'rgba(20,20,30,0.14)',
      uc: (h) => `hsl(${h}, ${d ? 52 : 46}%, ${d ? 62 : 50}%)`,
      ucSoft: (h) => `hsl(${h}, ${d ? 30 : 45}%, ${d ? 24 : 94}%)`,
      ucLine: (h, a = 0.55) => `hsla(${h}, ${d ? 55 : 45}%, ${d ? 65 : 48}%, ${a})`,
      ucText: (h) => `hsl(${h}, ${d ? 45 : 40}%, ${d ? 78 : 32}%)`,
    };
  }

  // ------------------------------------------------------------------ estado
  const DEFAULT_FILTERS = () => ({
    ucs: new Set(UCS.map((u) => u.id)),
    types: new Set(['conceito', 'formula', 'algoritmo', 'ferramenta']),
    dmin: 1, dmax: 5, imp: 1,
    rels: new Set(['prerequisite_of', 'applied_in', 'used_in', 'related_to']),
    onlyImportant: false, onlyDeps: false, crossUC: true, inferred: true, future: true, exercises: false, files: false,
  });
  const state = {
    view: 'map', expanded: new Set(), focus: null, focusMode: 'both', revealed: new Set(), filters: DEFAULT_FILTERS(), bneckFocus: null,
  };

  // ------------------------------------------------------------------ cytoscape
  const P0 = palette();
  const els = [];
  DATA.nodes.forEach((n) => {
    const p = n.pos?.map || { x: 0, y: 0 };
    const imp = n.importance || 0;
    let size = 10;
    if (n.type === 'root') size = 150; else if (n.type === 'uc') size = 112; else if (n.type === 'tema') size = 40;
    else if (isConcept(n)) size = 12 + imp * 3.6; else if (n.type === 'exercicio') size = 9; else size = 11;
    els.push({ group: 'nodes', data: { id: n.id, label: n.type === 'uc' ? n.short && n.short.length < 12 && n.horizon ? n.short : n.label : n.label, type: n.type, size, uc: n.uc, imp, status: n.status || '' },
      position: { x: p.x, y: p.y }, classes: [n.type, n.status, isConcept(n) ? 'concept' : '', n.horizon ? 'horizon' : ''].join(' ') });
  });
  DATA.edges.forEach((e) => {
    const s = N.get(e.source), t = N.get(e.target);
    const cross = isConcept(s) && isConcept(t) && s.uc !== t.uc;
    els.push({ group: 'edges', data: { id: e.id, source: e.source, target: e.target, type: e.type, nature: e.nature, conf: e.confidence },
      classes: [e.type, e.nature, cross ? 'cross' : '', 'c-' + e.confidence].join(' ') });
  });

  const cy = cytoscape({
    container: $('#cy'), elements: els, layout: { name: 'preset' }, minZoom: 0.05, maxZoom: 2.6,
    boxSelectionEnabled: false, selectionType: 'single', autoungrabify: false, style: [], textureOnViewport: false, hideEdgesOnViewport: false, pixelRatio: 'auto',
  });

  function buildStyle() {
    const p = palette();
    const nodeColor = (ele) => p.uc(hue(N.get(ele.id())));
    return [
      { selector: 'node', style: {
        width: 'data(size)', height: 'data(size)', 'background-color': nodeColor, 'border-width': 0, label: 'data(label)',
        'font-family': 'Inter, Segoe UI, system-ui, sans-serif', 'font-size': 11, color: p.text2, 'text-valign': 'bottom', 'text-margin-y': 5,
        'text-wrap': 'wrap', 'text-max-width': 120, 'min-zoomed-font-size': 7, 'transition-property': 'opacity, background-color, border-color, border-width, width, height',
        'transition-duration': 220, 'text-outline-width': 2.2, 'text-outline-color': p.bg, 'text-outline-opacity': 0.9, 'overlay-opacity': 0,
      } },
      { selector: 'node.root', style: { 'background-color': p.text, color: p.bg, 'font-size': 36, 'font-weight': 700, 'text-valign': 'center', 'text-margin-y': 0, 'text-outline-width': 0 } },
      { selector: 'node.uc', style: { 'font-size': 30, 'font-weight': 600, color: p.text, 'text-margin-y': 14, 'text-max-width': 380, 'border-width': 10, 'text-outline-width': 4, 'border-color': (ele) => p.ucSoft(hue(N.get(ele.id()))), 'border-opacity': 1 } },
      { selector: 'node.uc.horizon', style: { 'background-color': p.surface, 'border-style': 'dashed', 'border-width': 2, 'border-color': (ele) => p.uc(hue(N.get(ele.id()))), color: p.text2 } },
      { selector: 'node.tema', style: {
        shape: 'round-rectangle', width: (ele) => Math.round(String(ele.data('label')).length * 9.6 + 40), height: 38, padding: 0, 'background-color': (ele) => p.ucSoft(hue(N.get(ele.id()))), 'border-width': 1,
        'border-color': (ele) => p.ucLine(hue(N.get(ele.id())), 0.45), color: (ele) => p.ucText(hue(N.get(ele.id()))), 'text-valign': 'center', 'text-margin-y': 0,
        'font-size': 16.5, 'font-weight': 600, 'text-outline-width': 0, 'text-max-width': 420, 'text-wrap': 'none' } },
      { selector: 'node.tema.programado, node.tema.horizonte', style: { 'border-style': 'dashed', 'background-opacity': 0.5 } },
      { selector: 'node.concept', style: { 'font-size': 10.5, 'text-max-width': 110, 'border-width': 2, 'border-color': p.bg, 'border-opacity': 0.9 } },
      { selector: 'node.concept[imp >= 4]', style: { 'font-size': 11.5, 'font-weight': 600, color: p.text } },
      { selector: 'node.formula', style: { shape: 'round-rectangle' } },
      { selector: 'node.algoritmo', style: { shape: 'round-hexagon' } },
      { selector: 'node.ferramenta', style: { shape: 'round-tag' } },
      { selector: 'node.concept.programado', style: { 'background-opacity': 0.35, 'border-style': 'dashed', 'border-color': nodeColor, 'border-width': 1.5 } },
      { selector: 'node.concept.horizonte', style: { 'background-color': p.bg, 'border-style': 'dashed', 'border-color': nodeColor, 'border-width': 1.6, color: p.text3 } },
      { selector: 'node.exercicio', style: { shape: 'diamond', 'background-color': p.text3, 'font-size': 9, color: p.text3, 'text-max-width': 90, 'background-opacity': 0.75 } },
      { selector: 'node.ficheiro, node.aula', style: { shape: 'round-rectangle', 'background-color': p.surface, 'border-width': 1.2, 'border-color': nodeColor, 'font-size': 9.5, color: p.text3 } },
      { selector: 'node.lane', style: { shape: 'round-rectangle', width: 'data(w)', height: 'data(h)', 'background-color': (ele) => p.ucSoft(ele.data('hue')), 'background-opacity': p.d ? 0.35 : 0.55,
        'border-width': 0, label: 'data(label)', 'text-valign': 'top', 'text-halign': 'left', 'text-margin-x': 120, 'text-margin-y': 26, 'font-size': 13, 'font-weight': 600,
        color: (ele) => p.ucText(ele.data('hue')), events: 'no', 'z-compound-depth': 'bottom', 'z-index': 0, 'text-outline-width': 0 } },
      { selector: 'node.stagehdr', style: { shape: 'rectangle', width: 1, height: 1, 'background-opacity': 0, label: 'data(label)', 'font-size': 12, color: p.text3, 'text-valign': 'top', 'text-outline-width': 0, events: 'no', 'font-weight': 600, 'text-max-width': 200 } },
      { selector: 'node.lanelbl', style: { 'font-size': 16, color: p.text, 'text-halign': 'right', 'text-valign': 'center' } },
      { selector: 'edge', style: { width: 1, 'line-color': p.border, 'curve-style': 'bezier', 'target-arrow-shape': 'none', opacity: 0.9, 'arrow-scale': 0.7,
        'transition-property': 'opacity, line-color, width', 'transition-duration': 220 } },
      { selector: 'edge.contains', style: { width: 1, 'line-color': p.border, opacity: 0.4, 'curve-style': 'straight' } },
      { selector: 'edge.prerequisite_of', style: { width: 1.5, 'line-color': (e) => p.ucLine(hue(N.get(e.data('source'))), 0.6), 'target-arrow-shape': 'triangle',
        'target-arrow-color': (e) => p.ucLine(hue(N.get(e.data('source'))), 0.8) } },
      { selector: 'edge.applied_in, edge.used_in', style: { width: 1.2, 'line-color': (e) => p.ucLine(hue(N.get(e.data('source'))), 0.45), 'target-arrow-shape': 'vee',
        'target-arrow-color': (e) => p.ucLine(hue(N.get(e.data('source'))), 0.6) } },
      { selector: 'edge.related_to', style: { width: 1, 'line-style': 'dotted', 'line-color': p.text3, opacity: 0.45 } },
      { selector: 'edge.followed_by', style: { width: 1, 'line-color': p.text3, opacity: 0.35, 'target-arrow-shape': 'chevron', 'target-arrow-color': p.text3, 'line-style': 'dashed', 'line-dash-pattern': [2, 4] } },
      { selector: 'edge.inferida', style: { 'line-style': 'dashed', 'line-dash-pattern': [5, 4] } },
      { selector: 'edge.related_to.inferida', style: { 'line-style': 'dotted' } },
      { selector: 'edge.cross', style: { 'curve-style': 'bezier', 'control-point-step-size': 60, width: 1.8 } },
      { selector: 'edge.tested_by, edge.requires, edge.explained_in, edge.appears_in', style: { width: 0.8, 'line-color': p.text3, opacity: 0.3 } },
      { selector: 'edge.meta', style: { width: 'data(w)', 'line-color': (e) => e.data('cross') ? (p.d ? 'rgba(232,180,90,0.55)' : 'rgba(176,120,30,0.42)') : p.ucLine(e.data('hue'), 0.35),
        'curve-style': 'bezier', 'control-point-step-size': 50, 'target-arrow-shape': 'triangle', 'arrow-scale': 0.8,
        'target-arrow-color': (e) => e.data('cross') ? (p.d ? 'rgba(232,180,90,0.75)' : 'rgba(176,120,30,0.6)') : p.ucLine(e.data('hue'), 0.5), label: 'data(label)', 'font-size': 10,
        color: p.text2, 'font-size': 18, 'font-weight': 600, 'text-background-color': p.bg, 'text-background-opacity': 0.95, 'text-background-padding': 4, 'text-background-shape': 'roundrectangle', 'text-rotation': 'none', opacity: 0.8 } },
      { selector: 'edge.meta.allinf', style: { 'line-style': 'dashed', 'line-dash-pattern': [6, 5] } },
      { selector: '.hidden', style: { display: 'none' } },
      { selector: '.faded', style: { opacity: 0.12, 'text-opacity': 0.25 } },
      { selector: 'edge.faded', style: { opacity: 0.05 } },
      { selector: 'node.hl-up', style: { 'border-width': 3, 'border-color': p.d ? '#6fd3a8' : '#2f8f5b', 'border-opacity': 1, color: p.text } },
      { selector: 'node.hl-down', style: { 'border-width': 3, 'border-color': p.d ? '#f0b46a' : '#c0731c', 'border-opacity': 1, color: p.text } },
      { selector: 'edge.hl-up', style: { 'line-color': p.d ? '#6fd3a8' : '#2f8f5b', 'target-arrow-color': p.d ? '#6fd3a8' : '#2f8f5b', width: 2.4, opacity: 1 } },
      { selector: 'edge.hl-down', style: { 'line-color': p.d ? '#f0b46a' : '#c0731c', 'target-arrow-color': p.d ? '#f0b46a' : '#c0731c', width: 2.4, opacity: 1 } },
      { selector: 'edge.hl-rel', style: { opacity: 0.9, width: 1.5 } },
      { selector: 'node.focus', style: { 'border-width': 4, 'border-color': p.text, 'border-opacity': 1, color: p.text, 'font-weight': 700, 'font-size': 13, 'z-index': 99 } },
      { selector: 'node.bneck', style: { 'border-width': 3, 'border-style': 'double', 'border-color': p.d ? '#f0b46a' : '#c0731c' } },
      { selector: 'node:active', style: { 'overlay-opacity': 0 } },
      { selector: 'node.pulse', style: { 'border-width': 6, 'border-color': css('--accent'), 'border-opacity': 0.8 } },
    ];
  }
  cy.style(buildStyle());

  // ------------------------------------------------------------------ visibilidade
  function passFilters(n) {
    const f = state.filters;
    if (!isConcept(n)) return true;
    if (!f.ucs.has(n.uc)) return false;
    if (!f.types.has(n.type)) return false;
    if (n.difficulty && (n.difficulty < f.dmin || n.difficulty > f.dmax)) return false;
    if ((n.importance || 0) < Math.max(f.imp, f.onlyImportant ? 4 : 1)) return false;
    if (f.onlyDeps && !(n.metrics && (n.metrics.direct_dependents || n.metrics.direct_prerequisites))) return false;
    if (!f.future && (n.status === 'programado' || n.status === 'horizonte')) return false;
    return true;
  }
  function edgeTypeVisible(e) {
    const f = state.filters;
    if (e.type === 'contains') return true;
    if (['tested_by', 'requires'].includes(e.type)) return f.exercises;
    if (['explained_in', 'appears_in'].includes(e.type)) return f.files;
    if (e.type === 'followed_by') return f.rels.has('followed_by');
    if (e.nature === 'inferida' && !f.inferred) return false;
    if (e.type === 'used_in' || e.type === 'applied_in') return f.rels.has('applied_in');
    return f.rels.has(e.type);
  }

  function computeVisible() {
    const vis = new Set(state.view === 'roadmap' ? [] : ['iacd']);
    const f = state.filters;
    if (state.view === 'roadmap') {
      DATA.nodes.forEach((n) => { if (isConcept(n) && passFilters(n)) vis.add(n.id); });
      return vis;
    }
    UCS.forEach((u) => {
      if (!f.ucs.has(u.id)) return;
      if (u.horizon && !f.future) return;
      vis.add(u.id);
      if (!state.expanded.has(u.id)) return;
      temasOf(u.id).forEach((t) => {
        if (!f.future && (t.status === 'programado' || t.status === 'horizonte')) return;
        vis.add(t.id);
        if (!state.expanded.has(t.id)) return;
        conceptsOf(t.id).forEach((c) => { if (passFilters(c)) vis.add(c.id); });
      });
      if (f.files) DATA.nodes.forEach((n) => { if ((n.type === 'ficheiro' || n.type === 'aula') && n.uc === u.id) vis.add(n.id); });
    });
    state.revealed.forEach((id) => { const n = N.get(id); if (n && (!isConcept(n) || passFilters(n))) { vis.add(id); if (n.tema) vis.add(n.tema); if (n.uc) vis.add(n.uc); } });
    if (f.exercises) {
      [...vis].forEach((id) => { const n = N.get(id); if (isConcept(n)) exercisesOf(id).forEach((x) => x && vis.add(x.id)); });
    }
    return vis;
  }

  function visibleAncestor(id, vis) {
    if (vis.has(id)) return id;
    const n = N.get(id);
    if (!n) return null;
    if (n.tema && vis.has(n.tema)) return n.tema;
    if (n.uc && vis.has(n.uc)) return n.uc;
    return null;
  }

  let lastVis = new Set();
  function applyVisibility(opts = {}) {
    const vis = computeVisible();
    lastVis = vis;
    cy.batch(() => {
      cy.remove('edge.meta');
      cy.nodes().forEach((ele) => {
        const t = ele.data('type');
        if (t === 'lane' || t === 'stagehdr') { ele.toggleClass('hidden', state.view !== 'roadmap'); return; }
        ele.toggleClass('hidden', !vis.has(ele.id()));
      });
      cy.edges().forEach((ele) => {
        const e = DATA.edges[+ele.id().slice(1)];
        let show = vis.has(e.source) && vis.has(e.target) && edgeTypeVisible(e);
        if (state.view === 'roadmap' && !(DEP_TYPES.has(e.type) || (e.type === 'related_to' && state.focus))) show = false;
        if (state.view === 'roadmap' && e.type === 'related_to' && state.focus && !(e.source === state.focus || e.target === state.focus)) show = false;
        ele.toggleClass('hidden', !show);
      });
      // arestas agregadas (nível de detalhe): ligações entre conceitos escondidos sobem até ao tema/UC visível
      if (state.view === 'map') {
        const agg = new Map();
        DATA.edges.forEach((e) => {
          if (!(DEP_TYPES.has(e.type) || e.type === 'related_to')) return;
          const s = N.get(e.source), t = N.get(e.target);
          if (!isConcept(s) || !isConcept(t)) return;
          if (vis.has(e.source) && vis.has(e.target)) return;
          if (!edgeTypeVisible(e)) return;
          if (!state.filters.ucs.has(s.uc) || !state.filters.ucs.has(t.uc)) return;
          const a = visibleAncestor(e.source, vis), b = visibleAncestor(e.target, vis);
          if (!a || !b || a === b) return;
          const an = N.get(a), bn = N.get(b);
          const cross = s.uc !== t.uc;
          if (cross && !state.filters.crossUC) return;
          if (!cross && an.type === 'uc') return;
          if (!cross && (an.type !== 'tema' && bn.type !== 'tema')) return;
          if (e.type === 'related_to' && !cross) return;
          const key = a + '|' + b;
          const g = agg.get(key) || { a, b, n: 0, inf: 0, cross, hue: hue(s) };
          g.n++; if (e.nature === 'inferida') g.inf++;
          agg.set(key, g);
        });
        const add = [];
        agg.forEach((g, key) => {
          add.push({ group: 'edges', data: { id: 'm:' + key, source: g.a, target: g.b, type: 'meta', w: Math.min(9, 1.2 + Math.log2(1 + g.n) * 1.6), label: g.n > 1 && (N.get(g.a).type === 'uc' || g.cross) ? String(g.n) : '', cross: g.cross, hue: g.hue, n: g.n, inf: g.inf },
            classes: 'meta' + (g.inf === g.n ? ' allinf' : '') });
        });
        if (add.length) cy.add(add);
      }
    });
    applyFocusClasses();
    updateCrumb();
    updateFilterCount();
    drawMinimap();
    if (opts.fit) fitVisible(opts.fitPadding);
  }

  function fitVisible(pad = 60, eles) {
    const target = (eles || cy.nodes()).filter((n) => !n.hasClass('hidden') && (!['lane', 'stagehdr'].includes(n.data('type')) || state.view === 'roadmap'));
    if (!target.length) return;
    const panelW = $('#panel').hidden ? 0 : $('#panel').offsetWidth + 24;
    const bb = target.boundingBox();
    const W = cy.width() - panelW, H = cy.height();
    const z = Math.min(cy.maxZoom(), Math.max(cy.minZoom(), Math.min((W - 2 * pad) / Math.max(bb.w, 1), (H - 2 * pad) / Math.max(bb.h, 1))));
    const zz = target.length === 1 ? Math.min(z, 1.2) : z;
    cy.animate({ zoom: zz, pan: { x: W / 2 - (bb.x1 + bb.w / 2) * zz, y: H / 2 - (bb.y1 + bb.h / 2) * zz }, duration: 520, easing: 'ease-in-out-cubic' });
  }


  function groupCollection(id) {
    const n = N.get(id);
    let ids = [id];
    if (n.type === 'uc') ids = ids.concat(temasOf(id).map((t) => t.id));
    else if (n.type === 'tema') ids = ids.concat(conceptsOf(id).map((c) => c.id));
    return cy.collection(ids.map((x) => cy.getElementById(x)).filter((x) => x.length && !x.hasClass('hidden')));
  }

  // ------------------------------------------------------------------ foco
  function applyFocusClasses() {
    cy.batch(() => {
      cy.elements().removeClass('faded hl-up hl-down hl-rel focus bneck');
      if (state.view === 'bottlenecks' || state.bneckFocus) DATA.bottlenecks.forEach((b) => cy.getElementById(b.id).addClass('bneck'));
      const id = state.focus;
      if (!id) return;
      const n = N.get(id);
      cy.getElementById(id).addClass('focus');
      if (!isConcept(n)) {
        // UC/tema em foco: esbater o que não pertence ao grupo, para o grupo se ler bem
        if (n.type === 'uc' || n.type === 'tema') {
          const keepG = new Set(groupCollection(id).map((x) => x.id()));
          if (n.type === 'tema') keepG.add(n.uc);
          cy.nodes(':visible').forEach((ele) => { const t = ele.data('type'); if (!keepG.has(ele.id()) && t !== 'root' && t !== 'uc' && t !== 'tema') ele.addClass('faded'); });
          cy.edges(':visible').forEach((ele) => { if (!(keepG.has(ele.data('source')) && keepG.has(ele.data('target')))) ele.addClass('faded'); });
        }
        return;
      }
      const up = state.focusMode === 'down' ? new Set() : depClosure(id, 'up');
      const down = state.focusMode === 'up' ? new Set() : depClosure(id, 'down');
      const rel = new Set();
      outE.get(id).concat(inE.get(id)).forEach((e) => { if (e.type === 'related_to') rel.add(e.source === id ? e.target : e.source); });
      const keep = new Set([id, ...up, ...down, ...rel]);
      cy.nodes(':visible').forEach((ele) => {
        const nid = ele.id();
        if (keep.has(nid)) {
          if (up.has(nid)) ele.addClass('hl-up');
          if (down.has(nid)) ele.addClass('hl-down');
          return;
        }
        const t = ele.data('type');
        if (t === 'lane' || t === 'stagehdr') return;
        if (t === 'exercicio' && exercisesOf(id).some((x) => x && x.id === nid)) return;
        ele.addClass('faded');
      });
      cy.edges(':visible').forEach((ele) => {
        const s = ele.data('source'), t = ele.data('target'), ty = ele.data('type');
        if (DEP_TYPES.has(ty) && keep.has(s) && keep.has(t)) {
          if ((up.has(s) || s === id) && (up.has(t) || t === id) && !(s === id)) ele.addClass('hl-up');
          else if ((down.has(t)) && (down.has(s) || s === id)) ele.addClass('hl-down');
          else if (up.has(s) && t === id) ele.addClass('hl-up');
          return;
        }
        if (ty === 'related_to' && (s === id || t === id)) { ele.addClass('hl-rel'); return; }
        if ((ty === 'tested_by' && s === id) || (ty === 'requires' && t === id)) return;
        ele.addClass('faded');
      });
    });
  }

  function focusNode(id, opts = {}) {
    const n = N.get(id);
    if (!n) return;
    state.focus = id;
    if (opts.mode) state.focusMode = opts.mode; else if (!opts.keepMode) state.focusMode = 'both';
    if (isConcept(n) && state.view === 'map') {
      state.revealed = new Set([id, ...depClosure(id, 'up'), ...depClosure(id, 'down')]);
      outE.get(id).concat(inE.get(id)).forEach((e) => { if (e.type === 'related_to') state.revealed.add(e.source === id ? e.target : e.source); });
      state.expanded.add(n.uc); state.expanded.add(n.tema);
    } else if (n.type === 'exercicio' || n.type === 'ficheiro' || n.type === 'aula') {
      if (n.type === 'exercicio') { state.filters.exercises = true; (n.primary || []).forEach((c) => { const cn = N.get(c); if (cn) { state.expanded.add(cn.uc); state.expanded.add(cn.tema); } }); }
      else { state.filters.files = true; state.expanded.add(n.uc); }
      syncFilterUI();
    }
    applyVisibility();
    openPanel(id);
    if (opts.center !== false) {
      const ele = cy.getElementById(id);
      if (isConcept(n) && opts.fitNeighborhood !== false) {
        const ids = [id, ...state.revealed];
        const col = cy.collection(ids.map((x) => cy.getElementById(x)).filter((x) => x.length && !x.hasClass('hidden')));
        if (col.length > 1) fitVisible(70, col); else cy.animate({ center: { eles: ele }, zoom: Math.max(cy.zoom(), 1.1), duration: 500 });
      } else if (ele.length) cy.animate({ center: { eles: ele }, zoom: Math.max(cy.zoom(), n.type === 'uc' ? 0.6 : 1.0), duration: 500, easing: 'ease-in-out-cubic' });
      if (ele.length) { ele.addClass('pulse'); setTimeout(() => ele.removeClass('pulse'), 900); }
    }
  }

  function clearFocus() {
    state.focus = null; state.revealed = new Set(); state.bneckFocus = null;
    $('#panel').hidden = true;
    applyVisibility();
  }

  // ------------------------------------------------------------------ interação no grafo
  let tapTimer = null;
  cy.on('tap', 'node', (evt) => {
    const ele = evt.target, id = ele.id(), n = N.get(id), t = ele.data('type');
    if (t === 'lane' || t === 'stagehdr') return;
    fadeHint();
    if (t === 'root') { overview(); return; }
    if (t === 'uc') {
      const was = state.expanded.has(id);
      if (was && state.focus === id) { // segundo clique recolhe
        state.expanded.delete(id); temasOf(id).forEach((tm) => state.expanded.delete(tm.id));
        state.focus = null; $('#panel').hidden = true; applyVisibility();
        return;
      }
      state.expanded.add(id); state.focus = id; state.revealed = new Set();
      applyVisibility();
      openPanel(id);
      fitVisible(90, groupCollection(id));
      return;
    }
    if (t === 'tema') {
      if (state.expanded.has(id) && state.focus === id) {
        state.expanded.delete(id); state.focus = null; $('#panel').hidden = true; applyVisibility(); return;
      }
      state.expanded.add(id); state.expanded.add(n.uc); state.focus = id; state.revealed = new Set();
      applyVisibility();
      openPanel(id);
      fitVisible(80, groupCollection(id));
      return;
    }
    focusNode(id, { center: state.view !== 'roadmap' || true });
  });
  cy.on('tap', (evt) => { if (evt.target === cy) { if (state.focus) clearFocus(); closeMenus(); } });
  cy.on('mouseover', 'node', (evt) => { const t = evt.target.data('type'); if (t !== 'lane' && t !== 'stagehdr') $('#cy').style.cursor = 'pointer'; });
  cy.on('mouseout', 'node', () => { $('#cy').style.cursor = ''; });

  // ------------------------------------------------------------------ painel lateral
  function swatch(n) { return `<span class="sw" style="background:${palette().uc(hue(n))}"></span>`; }
  function fileHref(path, page) { return '../../' + path.split('/').map(encodeURIComponent).join('/') + (page ? '#page=' + page : ''); }
  const TYPE_LABEL = { conceito: 'Conceito', formula: 'Fórmula', algoritmo: 'Algoritmo', ferramenta: 'Ferramenta', exercicio: 'Exercício', ficheiro: 'Ficheiro', aula: 'Aula · caderno', tema: 'Tema', uc: 'Unidade curricular', root: 'Licenciatura' };
  const STATUS_LABEL = { programado: 'No programa · ainda não lecionado', horizonte: 'Horizonte · só em material de referência' };
  const REL_LABEL = { prerequisite_of: 'pré-requisito', applied_in: 'aplicado em', used_in: 'usado em', related_to: 'relacionado' };
  const confTag = (e) => `<span class="tag ${e.nature === 'inferida' ? 'inf' : ''}" title="${esc(e.justification || '')}${e.evidence ? '\nFonte: ' + esc(e.evidence) : ''}">${e.nature === 'inferida' ? 'Inferida' : 'Explícita'} · ${e.confidence === 'media' ? 'média' : e.confidence}</span>`;

  function linkItem(n, extra = '') {
    if (!n) return '';
    return `<li data-go="${esc(n.id)}">${swatch(n)}<span class="lbl">${esc(n.label)}</span>${extra}</li>`;
  }
  function meter(label, val, why, color) {
    const v = val || 0;
    return `<div class="meter" title="${esc(why || '')}"><div class="ml"><span>${label}</span><span>${v ? v + '/5' : '—'}</span></div><div class="dots">${[1, 2, 3, 4, 5].map((i) => `<i class="${i <= v ? 'f' : ''}" style="--c:${color}"></i>`).join('')}</div></div>`;
  }
  function sourcesHTML(list, limit = 6) {
    if (!list.length) return '<p class="empty-note">Sem fonte registada.</p>';
    const seen = new Set();
    const items = list.filter((s) => { const k = s.file + '#' + s.page; if (seen.has(k)) return false; seen.add(k); return true; })
      .sort((a, b) => (b.verified - a.verified));
    const row = (s) => {
      const name = s.file.split('/').pop();
      const kindIco = { caderno: '✎', resumo: '≡', slides: '▭', ficha: '✓', livro: '❐', codigo: '{}' }[s.kind] || '•';
      return `<div class="src"><span class="ico">${kindIco}</span><div class="t"><a href="${fileHref(s.file, s.page)}" target="_blank" rel="noopener">${esc(name)}${s.page ? ` · p. ${s.page}` : ''}</a>
        <small>${esc(s.note || '')}${s.verified ? '' : (s.note ? ' · ' : '') + 'localizado automaticamente'}</small></div></div>`;
    };
    const head = items.slice(0, limit).map(row).join('');
    const rest = items.slice(limit);
    return head + (rest.length ? `<details><summary class="more">+ ${rest.length} fonte(s)</summary>${rest.map(row).join('')}</details>` : '');
  }

  function openPanel(id) {
    const n = N.get(id);
    const p = palette();
    const body = $('#panel-body');
    let h = '';
    const uc = ucNode(n);
    const kicker = `<div class="p-kicker">${uc ? swatch(n) : ''}${esc(TYPE_LABEL[n.type] || n.type)}${n.status && STATUS_LABEL[n.status] ? ' · ' + (n.status === 'programado' ? 'programado' : 'horizonte') : ''}</div>`;
    if (isConcept(n)) {
      const tema = N.get(n.tema);
      const pre = inE.get(id).filter((e) => DEP_TYPES.has(e.type) && isConcept(N.get(e.source)));
      const post = outE.get(id).filter((e) => DEP_TYPES.has(e.type) && isConcept(N.get(e.target)));
      const rel = outE.get(id).concat(inE.get(id)).filter((e) => e.type === 'related_to' && isConcept(N.get(e.source === id ? e.target : e.source)));
      const exs = outE.get(id).filter((e) => e.type === 'tested_by').map((e) => N.get(e.target));
      const exs2 = inE.get(id).filter((e) => e.type === 'requires').map((e) => N.get(e.source));
      const ucTag = (other) => other.uc !== n.uc ? `<span class="ucs">${esc(ucNode(other).short)}</span>` : '';
      const color = p.uc(hue(n));
      h += kicker + `<h2 class="p-title">${esc(n.label)}</h2><div class="p-sub"><a href="#" data-go="${esc(n.uc)}">${esc(uc.label)}</a> · <a href="#" data-go="${esc(n.tema)}">${esc(tema?.label || '')}</a></div>`;
      const badges = [];
      if (n.status && STATUS_LABEL[n.status]) badges.push(`<span class="badge warn">${STATUS_LABEL[n.status]}</span>`);
      if (n.bottleneck_rank) badges.push(`<span class="badge">Bottleneck #${n.bottleneck_rank}</span>`);
      if (n.metrics?.cross_uc?.length) badges.push(`<span class="badge">Ponte com ${n.metrics.cross_uc.map((u) => esc(N.get(u).short)).join(', ')}</span>`);
      (n.aliases || []).slice(0, 4).forEach((a) => badges.push(`<span class="badge inf">${esc(a)}</span>`));
      if (badges.length) h += `<div class="badges">${badges.join('')}</div>`;
      h += `<div class="meters">${meter('★ Importância', n.importance, n.importance_why, color)}${meter('◉ Dificuldade', n.difficulty, n.difficulty_why, color)}</div>`;
      h += `<div class="p-sec"><h5>Sobre</h5><p class="p-text">${esc(n.desc)}</p>${n.formula ? `<div class="formula">${esc(n.formula)}</div>` : ''}
            <p class="why"><b>Importância:</b> ${esc(n.importance_why || '')}<br><b>Dificuldade:</b> ${esc(n.difficulty_why || '')}</p></div>`;
      h += `<div class="p-sec"><h5>Pré-requisitos <span>${pre.length}</span></h5>${pre.length ? `<ul class="links">${pre.map((e) => linkItem(N.get(e.source), ucTag(N.get(e.source)) + confTag(e))).join('')}</ul>` : '<p class="empty-note">Nenhum identificado — é um ponto de partida.</p>'}</div>`;
      h += `<div class="p-sec"><h5>Depende dele <span>${post.length}${n.metrics?.dependents > post.length ? ` diretos · ${n.metrics.dependents} no total` : ''}</span></h5>${post.length ? `<ul class="links">${post.map((e) => linkItem(N.get(e.target), ucTag(N.get(e.target)) + confTag(e))).join('')}</ul>` : '<p class="empty-note">Nenhum conceito depende diretamente deste.</p>'}</div>`;
      if (rel.length) h += `<div class="p-sec"><h5>Relacionados <span>${rel.length}</span></h5><ul class="links">${rel.map((e) => linkItem(N.get(e.source === id ? e.target : e.source), ucTag(N.get(e.source === id ? e.target : e.source)) + confTag(e))).join('')}</ul></div>`;
      const exAll = [...exs.map((x) => [x, 'principal']), ...exs2.map((x) => [x, 'secundário'])];
      h += `<div class="p-sec"><h5>Exercícios <span>${exAll.length}</span></h5>${exAll.length ? `<ul class="links">${exAll.slice(0, 8).map(([x, k]) => linkItem(x, `<span class="tag">${k}</span>`)).join('')}</ul>${exAll.length > 8 ? `<details><summary class="more">+ ${exAll.length - 8} exercício(s)</summary><ul class="links">${exAll.slice(8).map(([x, k]) => linkItem(x, `<span class="tag">${k}</span>`)).join('')}</ul></details>` : ''}` : '<p class="empty-note">Sem exercícios associados nos materiais.</p>'}</div>`;
      h += `<div class="p-sec"><h5>Fontes</h5>${sourcesHTML(n.sources || [])}</div>`;
      h += `<div class="p-actions"><button class="primary" data-act="explore">Explorar dependências</button><button class="ghost" data-act="down">Só o que depende dele</button><button class="ghost" data-act="up">Só de onde vem</button>${state.view !== 'roadmap' ? '<button class="ghost" data-act="roadmap">Ver no Roadmap</button>' : '<button class="ghost" data-act="map">Ver no Mapa</button>'}</div>`;
    } else if (n.type === 'uc' || n.type === 'root') {
      const temas = n.type === 'uc' ? temasOf(id) : UCS;
      const concepts = DATA.nodes.filter((c) => isConcept(c) && (n.type === 'root' || c.uc === id));
      const top = concepts.slice().sort((a, b) => b.importance_score - a.importance_score).slice(0, 6);
      const files = DATA.nodes.filter((f) => (f.type === 'ficheiro' || f.type === 'aula') && f.uc === id);
      h += kicker + `<h2 class="p-title">${esc(n.label)}</h2><div class="p-sub">${esc(n.code || '')}${n.code ? ' · ' : ''}${concepts.length} conceitos · ${temas.length} ${n.type === 'uc' ? 'temas' : 'UCs'}</div>`;
      h += `<div class="p-sec"><h5>Sobre</h5><p class="p-text">${esc(n.desc)}</p></div>`;
      h += `<div class="p-sec"><h5>${n.type === 'uc' ? 'Temas' : 'Unidades curriculares'}</h5><ul class="links">${temas.map((t) => linkItem(t, t.status && t.status !== 'lecionado' ? `<span class="tag inf">${t.status}</span>` : `<span class="ucs">${(n.type === 'uc' ? conceptsOf(t.id) : DATA.nodes.filter((c) => isConcept(c) && c.uc === t.id)).length}</span>`)).join('')}</ul></div>`;
      h += `<div class="p-sec"><h5>Conceitos centrais</h5><ul class="links">${top.map((c) => linkItem(c, `<span class="tag">★ ${c.importance}</span>`)).join('')}</ul></div>`;
      if (n.type === 'uc') {
        const cross = {};
        DATA.edges.forEach((e) => { const s = N.get(e.source), t = N.get(e.target); if (isConcept(s) && isConcept(t) && s.uc !== t.uc && (s.uc === id || t.uc === id) && e.type !== 'contains') { const o = s.uc === id ? t.uc : s.uc; cross[o] = (cross[o] || 0) + 1; } });
        const ks = Object.keys(cross).sort((a, b) => cross[b] - cross[a]);
        if (ks.length) h += `<div class="p-sec"><h5>Ligações a outras UCs</h5><ul class="links">${ks.map((k) => linkItem(N.get(k), `<span class="ucs">${cross[k]} relações</span>`)).join('')}</ul></div>`;
        if (files.length) h += `<div class="p-sec"><h5>Materiais <span>${files.length}</span></h5>${files.slice(0, 40).map((f) => `<div class="src"><span class="ico">${f.type === 'aula' ? '✎' : '▭'}</span><div class="t"><a href="${fileHref(f.file)}" target="_blank">${esc(f.file.split('/').pop())}</a><small>${esc(f.desc)}${f.pages ? ' · ' + f.pages + ' p.' : ''}</small></div></div>`).join('')}</div>`;
      }
    } else if (n.type === 'tema') {
      const cs = conceptsOf(id).sort((a, b) => b.importance_score - a.importance_score);
      h += kicker + `<h2 class="p-title">${esc(n.label)}</h2><div class="p-sub"><a href="#" data-go="${esc(n.uc)}">${esc(uc.label)}</a> · ${cs.length} conceitos</div>`;
      if (n.status && STATUS_LABEL[n.status]) h += `<div class="badges"><span class="badge warn">${STATUS_LABEL[n.status]}</span></div>`;
      h += `<div class="p-sec"><h5>Sobre</h5><p class="p-text">${esc(n.desc)}</p></div>`;
      h += `<div class="p-sec"><h5>Conceitos</h5><ul class="links">${cs.map((c) => linkItem(c, `<span class="tag">★ ${c.importance}</span>`)).join('')}</ul></div>`;
      const nexts = outE.get(id).filter((e) => e.type === 'followed_by').map((e) => N.get(e.target));
      const prevs = inE.get(id).filter((e) => e.type === 'followed_by').map((e) => N.get(e.source));
      if (prevs.length || nexts.length) h += `<div class="p-sec"><h5>Ordem no programa</h5><ul class="links">${prevs.map((x) => linkItem(x, '<span class="tag">antes</span>')).join('')}${nexts.map((x) => linkItem(x, '<span class="tag">depois</span>')).join('')}</ul><p class="why">A ordem temporal não implica dependência conceptual.</p></div>`;
    } else if (n.type === 'exercicio') {
      const prim = (n.primary || []).map((c) => N.get(c)).filter(Boolean);
      const sec = (n.secondary || []).map((c) => N.get(c)).filter(Boolean);
      h += kicker + `<h2 class="p-title">${esc(n.label)}</h2><div class="p-sub"><a href="#" data-go="${esc(n.uc)}">${esc(uc?.label || '')}</a>${n.page ? ' · página ' + n.page : ''}</div>`;
      if (n.status === 'programado') h += `<div class="badges"><span class="badge warn">${STATUS_LABEL.programado}</span></div>`;
      if (n.desc) h += `<div class="p-sec"><h5>Enunciado / descrição</h5><p class="p-text">${esc(n.desc)}</p></div>`;
      h += `<div class="meters">${meter('◉ Dificuldade', n.difficulty, n.difficulty_why, p.uc(hue(n)))}<div class="meter"><div class="ml"><span>Resolução</span></div><div class="mv"><small>${(n.solved_in || []).length ? 'Resolvido' : 'Por resolver / não encontrado'}</small></div></div></div>`;
      h += `<div class="p-sec"><h5>Conceito principal</h5><ul class="links">${prim.map((c) => linkItem(c)).join('') || '<p class="empty-note">—</p>'}</ul></div>`;
      if (sec.length) h += `<div class="p-sec"><h5>Conceitos secundários</h5><ul class="links">${sec.map((c) => linkItem(c)).join('')}</ul></div>`;
      const srcs = [{ file: n.file, page: n.page, note: 'Enunciado', verified: true, kind: n.file.endsWith('.py') ? 'codigo' : 'ficha' }].concat((n.solved_in || []).filter((s) => s.file !== n.file).map((s) => ({ ...s, note: 'Resolução', verified: true, kind: 'caderno' })));
      h += `<div class="p-sec"><h5>Ficheiros</h5>${sourcesHTML(srcs)}</div>`;
    } else if (n.type === 'ficheiro' || n.type === 'aula') {
      const cs = inE.get(id).filter((e) => e.type === 'explained_in' || e.type === 'appears_in').map((e) => [N.get(e.source), e]).filter(([x]) => isConcept(x));
      const exs = inE.get(id).filter((e) => e.type === 'appears_in').map((e) => N.get(e.source)).filter((x) => x && x.type === 'exercicio');
      const seq = outE.get(id).concat(inE.get(id)).filter((e) => e.type === 'followed_by');
      h += kicker + `<h2 class="p-title">${esc(n.label)}</h2><div class="p-sub">${esc(n.desc)}${n.pages ? ' · ' + n.pages + ' páginas' : ''}</div>`;
      h += `<div class="p-actions" style="margin:0 0 6px"><a class="primary" href="${fileHref(n.file)}" target="_blank" rel="noopener" style="text-decoration:none">Abrir ficheiro</a></div>`;
      const uniq = new Map(); cs.forEach(([c, e]) => { if (!uniq.has(c.id)) uniq.set(c.id, [c, e]); });
      h += `<div class="p-sec"><h5>Conceitos neste ficheiro <span>${uniq.size}</span></h5><ul class="links">${[...uniq.values()].sort((a, b) => (a[1].page || 0) - (b[1].page || 0)).map(([c, e]) => linkItem(c, e.page ? `<span class="tag ${e.nature === 'inferida' ? 'inf' : ''}">p. ${e.page}</span>` : '')).join('') || '<p class="empty-note">—</p>'}</ul></div>`;
      if (exs.length) h += `<div class="p-sec"><h5>Exercícios <span>${exs.length}</span></h5><ul class="links">${exs.slice(0, 12).map((x) => linkItem(x)).join('')}</ul></div>`;
      if (seq.length) h += `<div class="p-sec"><h5>Sequência</h5><ul class="links">${seq.map((e) => linkItem(N.get(e.source === id ? e.target : e.source), `<span class="tag">${e.source === id ? 'seguinte' : 'anterior'}</span>`)).join('')}</ul></div>`;
    }
    body.innerHTML = h;
    $('#panel').hidden = false;
    $('#panel').scrollTop = 0;
    drawMinimap();
  }

  $('#panel').addEventListener('click', (ev) => {
    const go = ev.target.closest('[data-go]');
    if (go) { ev.preventDefault(); const id = go.dataset.go; const n = N.get(id); if (n.type === 'uc' || n.type === 'tema') { state.expanded.add(n.uc); state.expanded.add(id); state.focus = id; applyVisibility(); openPanel(id); fitVisible(80, groupCollection(id)); } else focusNode(id); return; }
    const act = ev.target.closest('[data-act]');
    if (!act) return;
    const a = act.dataset.act;
    if (a === 'explore') focusNode(state.focus, { mode: 'both' });
    if (a === 'down') focusNode(state.focus, { mode: 'down' });
    if (a === 'up') focusNode(state.focus, { mode: 'up' });
    if (a === 'roadmap') { const f = state.focus; setView('roadmap'); focusNode(f, { keepMode: true }); }
    if (a === 'map') { const f = state.focus; setView('map'); focusNode(f, { keepMode: true }); }
  });

  // ------------------------------------------------------------------ pesquisa
  const SEARCHABLE = DATA.nodes.filter((n) => isConcept(n) || ['uc', 'tema', 'exercicio', 'aula', 'ficheiro'].includes(n.type)).map((n) => ({
    n, label: normTxt(n.label), aliases: (n.aliases || []).map(normTxt), desc: normTxt(n.desc), formula: normTxt(n.formula), tema: normTxt(N.get(n.tema)?.label),
  }));
  function search(q) {
    const nq = normTxt(q).trim();
    if (!nq) return [];
    const terms = nq.split(/\s+/);
    const stem = (t) => t.length > 4 ? t.replace(/(es|s|ais|oes|ões)$/, '').slice(0, Math.max(4, t.length - 2)) : t;
    const out = [];
    for (const s of SEARCHABLE) {
      let score = 0, ok = true;
      for (const t of terms) {
        const st = stem(t);
        let ts = 0;
        if (s.label.startsWith(t)) ts = 10; else if (new RegExp('\\b' + st).test(s.label)) ts = 8; else if (s.label.includes(st)) ts = 6;
        else if (s.aliases.some((a) => a.includes(st))) ts = 5; else if (s.formula.includes(st)) ts = 3; else if (s.desc.includes(st)) ts = 2; else if (s.tema.includes(st)) ts = 1.5;
        if (!ts) { ok = false; break; }
        score += ts;
      }
      if (!ok) continue;
      if (isConcept(s.n)) score += 2 + (s.n.importance || 0) * 0.3; else if (s.n.type === 'exercicio') score -= 2.5;
      out.push([score, s.n]);
    }
    return out.sort((a, b) => b[0] - a[0]).slice(0, 12).map((x) => x[1]);
  }
  const input = $('#search'), results = $('#results');
  let activeIdx = 0, current = [];
  function hlText(text, q) {
    const t = esc(text); const nq = normTxt(q).trim(); if (!nq) return t;
    const plain = normTxt(text); const i = plain.indexOf(nq.split(/\s+/)[0].slice(0, 6));
    if (i < 0) return t;
    const len = Math.min(nq.split(/\s+/)[0].length, text.length - i);
    return esc(text.slice(0, i)) + '<mark>' + esc(text.slice(i, i + len)) + '</mark>' + esc(text.slice(i + len));
  }
  function renderResults() {
    const q = input.value;
    current = search(q);
    activeIdx = 0;
    if (!q.trim()) { results.hidden = true; return; }
    results.hidden = false;
    if (!current.length) { results.innerHTML = '<div class="empty">Sem resultados nos teus materiais.</div>'; return; }
    results.innerHTML = current.map((n, i) => {
      const sub = n.type === 'uc' ? 'Unidade curricular' : n.type === 'tema' ? (ucNode(n)?.short || '') : [(ucNode(n)?.short || ''), N.get(n.tema)?.label].filter(Boolean).join(' · ');
      return `<div class="result ${i === 0 ? 'active' : ''}" data-i="${i}" role="option">${swatch(n)}<div class="rl"><b>${hlText(n.label, q)}</b><small>${esc(sub)}</small></div><span class="rt">${esc(TYPE_LABEL[n.type] || '')}</span></div>`;
    }).join('');
  }
  function pick(i) {
    const n = current[i]; if (!n) return;
    results.hidden = true; input.blur();
    if (state.view === 'stats' || state.view === 'bottlenecks') setView('map');
    if (n.type === 'uc' || n.type === 'tema') { state.expanded.add(n.uc); state.expanded.add(n.id); state.focus = n.id; applyVisibility(); openPanel(n.id); fitVisible(90, groupCollection(n.id)); }
    else focusNode(n.id);
  }
  input.addEventListener('input', renderResults);
  input.addEventListener('focus', () => { if (input.value) renderResults(); });
  input.addEventListener('keydown', (e) => {
    const items = $$('.result', results);
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); if (!items.length) return; items[activeIdx]?.classList.remove('active'); activeIdx = (activeIdx + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length; items[activeIdx].classList.add('active'); items[activeIdx].scrollIntoView({ block: 'nearest' }); }
    else if (e.key === 'Enter') { e.preventDefault(); pick(activeIdx); }
    else if (e.key === 'Escape') { results.hidden = true; input.blur(); }
  });
  results.addEventListener('mousedown', (e) => { const r = e.target.closest('.result'); if (r) { e.preventDefault(); pick(+r.dataset.i); } });
  document.addEventListener('click', (e) => { if (!e.target.closest('.search-wrap')) results.hidden = true; });

  // ------------------------------------------------------------------ filtros
  const TYPE_FILTERS = [['conceito', 'Conceitos', '●'], ['formula', 'Fórmulas', '▬'], ['algoritmo', 'Algoritmos', '⬢'], ['ferramenta', 'Ferramentas', '◆']];
  const REL_FILTERS = [['prerequisite_of', 'Pré-requisito', '→'], ['applied_in', 'Aplicado / usado em', '⇢'], ['related_to', 'Relacionado', '⋯'], ['followed_by', 'Ordem temporal', '›']];
  const TOGGLES = [['onlyImportant', 'Mostrar apenas conceitos importantes'], ['onlyDeps', 'Mostrar apenas conceitos com dependências'], ['crossUC', 'Mostrar relações entre UCs'],
    ['inferred', 'Mostrar relações inferidas'], ['future', 'Matéria programada e horizonte'], ['exercises', 'Exercícios'], ['files', 'Ficheiros e aulas']];
  function syncFilterUI() {
    const f = state.filters, p = palette();
    $('#f-ucs').innerHTML = UCS.map((u) => `<button class="chip ${f.ucs.has(u.id) ? 'on' : ''}" data-uc="${u.id}"><span class="sw" style="background:${p.uc(u.hue)}"></span>${esc(u.short)}</button>`).join('');
    const counts = {}; DATA.nodes.forEach((n) => { counts[n.type] = (counts[n.type] || 0) + 1; });
    $('#f-types').innerHTML = TYPE_FILTERS.map(([k, l, g]) => `<label class="check"><input type="checkbox" data-type="${k}" ${f.types.has(k) ? 'checked' : ''}><span class="glyph">${g}</span>${l}<small>${counts[k] || 0}</small></label>`).join('');
    const opts = (sel) => [1, 2, 3, 4, 5].map((i) => `<option ${i === sel ? 'selected' : ''}>${i}</option>`).join('');
    $('#f-dmin').innerHTML = opts(f.dmin); $('#f-dmax').innerHTML = opts(f.dmax);
    $('#f-imp').innerHTML = [1, 2, 3, 4, 5].map((i) => `<button class="${f.imp === i ? 'on' : ''}" data-imp="${i}">${i === 1 ? 'Todas' : '≥ ' + i}</button>`).join('');
    $('#f-rels').innerHTML = REL_FILTERS.map(([k, l, g]) => `<label class="check"><input type="checkbox" data-rel="${k}" ${f.rels.has(k) ? 'checked' : ''}><span class="glyph">${g}</span>${l}</label>`).join('');
    $('#f-toggles').innerHTML = TOGGLES.map(([k, l]) => `<label class="switch"><span>${l}</span><input type="checkbox" data-tog="${k}" ${f[k] ? 'checked' : ''}></label>`).join('');
  }
  function updateFilterCount() {
    const f = state.filters, d = DEFAULT_FILTERS();
    let c = 0;
    if (f.ucs.size !== d.ucs.size) c++; if (f.types.size !== d.types.size) c++; if (f.dmin !== 1 || f.dmax !== 5) c++; if (f.imp !== 1) c++;
    if (f.rels.size !== d.rels.size) c++; ['onlyImportant', 'onlyDeps', 'crossUC', 'inferred', 'future', 'exercises', 'files'].forEach((k) => { if (f[k] !== d[k]) c++; });
    $('#filter-count').hidden = !c; $('#filter-count').textContent = c;
  }
  $('#filters').addEventListener('click', (e) => {
    const f = state.filters;
    const chip = e.target.closest('[data-uc]');
    if (chip) { const id = chip.dataset.uc; f.ucs.has(id) ? f.ucs.delete(id) : f.ucs.add(id); syncFilterUI(); applyVisibility(); return; }
    const imp = e.target.closest('[data-imp]');
    if (imp) { f.imp = +imp.dataset.imp; if (f.imp > 1) expandAll(true); syncFilterUI(); applyVisibility(); }
  });
  $('#filters').addEventListener('change', (e) => {
    const f = state.filters, t = e.target;
    if (t.dataset.type) { t.checked ? f.types.add(t.dataset.type) : f.types.delete(t.dataset.type); }
    else if (t.dataset.rel) { t.checked ? f.rels.add(t.dataset.rel) : f.rels.delete(t.dataset.rel); }
    else if (t.dataset.tog) { f[t.dataset.tog] = t.checked; if ((t.dataset.tog === 'onlyImportant' || t.dataset.tog === 'onlyDeps') && t.checked) expandAll(true); }
    else if (t.id === 'f-dmin') f.dmin = +t.value; else if (t.id === 'f-dmax') f.dmax = +t.value;
    if (f.dmin > f.dmax) [f.dmin, f.dmax] = [f.dmax, f.dmin];
    applyVisibility();
  });
  function expandAll(silent) {
    UCS.forEach((u) => { state.expanded.add(u.id); temasOf(u.id).forEach((t) => state.expanded.add(t.id)); });
    if (!silent) { applyVisibility(); fitVisible(40); }
  }
  $('#btn-expand-all').onclick = () => expandAll();
  $('#btn-collapse-all').onclick = () => overview();
  $('#btn-reset-filters').onclick = () => { state.filters = DEFAULT_FILTERS(); syncFilterUI(); applyVisibility(); toast('Filtros repostos'); };

  // ------------------------------------------------------------------ vistas
  function addRoadmapDecor() {
    if (cy.$('node.lane').length) return;
    const R = DATA.roadmap, p = palette();
    const width = R.layers * R.LX + 160;
    const add = [];
    R.lanes.forEach((l) => {
      const u = N.get(l.uc);
      add.push({ group: 'nodes', data: { id: 'lane:' + l.uc, type: 'lane', label: '', w: width + 140, h: l.h + 26, hue: u.hue }, position: { x: width / 2 - 130, y: l.y + l.h / 2 + 4 }, classes: 'lane', locked: true, grabbable: false, selectable: false });
      add.push({ group: 'nodes', data: { id: 'lanelbl:' + l.uc, type: 'stagehdr', label: u.short }, position: { x: -150, y: l.y + 10 }, classes: 'stagehdr lanelbl', locked: true, grabbable: false, selectable: false });
    });
    R.stages.forEach((s) => add.push({ group: 'nodes', data: { id: 'stage:' + s.layer, type: 'stagehdr', label: `Nível ${s.layer}\n${s.name}` }, position: { x: s.layer * R.LX, y: -38 }, classes: 'stagehdr', locked: true, grabbable: false, selectable: false }));
    cy.add(add);
    cy.$('node.lane').forEach((n) => n.style('z-index', 0));
  }
  function setView(v) {
    const prev = state.view;
    if (v === 'stats') { renderStats(); $('#stats').hidden = false; markView('stats'); return; }
    $('#stats').hidden = true;
    $('#bneck').hidden = v !== 'bottlenecks';
    if (v === 'bottlenecks') { renderBottlenecks(); $('#filters').hidden = true; }
    state.view = v === 'bottlenecks' ? 'map' : v;
    state.bneckFocus = v === 'bottlenecks' ? true : null;
    markView(v);
    if (state.view === 'roadmap') {
      addRoadmapDecor();
      cy.nodes().forEach((ele) => { const n = N.get(ele.id()); if (n && n.pos?.roadmap) ele.position(n.pos.roadmap); });
      applyVisibility();
      if (!state.focus) fitVisible(40); else setTimeout(() => focusNode(state.focus, { keepMode: true }), 30);
    } else if (prev === 'roadmap' || v === 'map' || v === 'bottlenecks') {
      cy.nodes().forEach((ele) => { const n = N.get(ele.id()); if (n && n.pos?.map && savedPos.has(ele.id())) ele.position(savedPos.get(ele.id())); else if (n && n.pos?.map && prev === 'roadmap') ele.position(n.pos.map); });
      if (v === 'bottlenecks') { DATA.bottlenecks.forEach((b) => { const n = N.get(b.id); state.expanded.add(n.uc); state.expanded.add(n.tema); }); }
      applyVisibility({ fit: prev === 'roadmap' || v === 'bottlenecks', fitPadding: v === 'bottlenecks' ? 60 : 50 });
    }
    $('#hint').classList.add('fade');
  }
  const savedPos = new Map();
  cy.on('dragfree', 'node', (e) => { if (state.view === 'map') savedPos.set(e.target.id(), { ...e.target.position() }); drawMinimap(); });
  function markView(v) { $$('.views button').forEach((b) => b.classList.toggle('active', b.dataset.view === v)); }
  $$('.views button').forEach((b) => b.addEventListener('click', () => setView(b.dataset.view)));

  function renderBottlenecks() {
    const p = palette();
    const max = Math.max(...DATA.bottlenecks.map((b) => b.dependents));
    $('#bneck-list').innerHTML = `<p class="sub" style="margin:0 0 6px">Conceitos que estão no caminho de muitos outros. A barra mostra quantos conceitos dependem (direta ou indiretamente) de cada um; a cadeia é o caminho de dependência mais longo encontrado nos materiais.</p>` +
      DATA.bottlenecks.map((b, i) => {
        const n = N.get(b.id);
        const chain = b.chain.slice(1, 6).map((c) => esc(N.get(c).label)).join(' → ') + (b.chain.length > 6 ? ' → …' : '');
        return `<div class="bn" data-bn="${b.id}"><div class="bn-top"><span class="bn-rank">${String(i + 1).padStart(2, '0')}</span><span class="bn-title">${esc(n.label)}</span><span class="bn-n">${b.dependents} dependentes</span></div>
          <div class="bn-bar"><i style="width:${(b.dependents / max) * 100}%;background:${p.uc(hue(n))}"></i></div>
          <div class="bn-chain"><b>${esc(N.get(n.uc).short)}</b> · ${chain}</div>
          <div class="bn-ucs">${b.ucs.map((u) => `<span class="badge">${esc(N.get(u).short)}</span>`).join('')}${b.horizon.length ? `<span class="badge warn">${b.horizon.length} no horizonte</span>` : ''}</div></div>`;
      }).join('');
  }
  $('#bneck-list').addEventListener('click', (e) => { const r = e.target.closest('[data-bn]'); if (r) { state.bneckFocus = true; focusNode(r.dataset.bn, { mode: 'down' }); } });

  // ------------------------------------------------------------------ estatísticas
  function bars(rows, opts = {}) {
    const max = Math.max(...rows.map((r) => r.v), 1);
    return `<div class="bars">${rows.map((r) => `<div class="bar ${r.id ? 'click' : ''}" ${r.id ? `data-go="${esc(r.id)}"` : ''}><span class="bl" title="${esc(r.l)}">${esc(r.l)}</span><span class="bt"><i style="width:${(r.v / max) * 100}%;background:${r.c || 'var(--accent)'}"></i></span><span class="bv">${opts.fmt ? opts.fmt(r.v) : r.v}</span></div>`).join('')}</div>`;
  }
  function renderStats() {
    const s = DATA.stats, p = palette();
    const conc = DATA.nodes.filter(isConcept);
    const deg = (id) => outE.get(id).concat(inE.get(id)).filter((e) => e.type !== 'contains' && isConcept(N.get(e.source)) && isConcept(N.get(e.target))).length;
    $('#stats-sub').textContent = `Gerado a partir de ${s.ficheiros_analisados} ficheiros · ${DATA.meta.generated.replace('T', ' ')}`;
    const kpi = (k, v, sub) => `<div class="kpi"><div class="k">${k}</div><div class="v">${v}</div><div class="s">${sub || ''}</div></div>`;
    let h = `<div class="kpis">${kpi('Unidades curriculares', s.ucs, '+ grupo Horizonte')}${kpi('Temas', s.temas, '')}${kpi('Conceitos', s.conceitos, 'conceitos, fórmulas, algoritmos, ferramentas')}${kpi('Exercícios', s.exercicios, 'fichas, cadernos e código')}${kpi('Ficheiros analisados', s.ficheiros_analisados, 'de ' + s.ficheiros_total)}${kpi('Relações', s.relacoes, `${s.explicitas} explícitas · ${s.inferidas} inferidas`)}</div>`;
    h += `<div class="grid2">`;
    h += `<div class="card"><h3>Conceitos por UC</h3><p class="sub">Inclui matéria programada e horizonte.</p>${bars(UCS.map((u) => ({ l: u.label, v: s.by_uc[u.id] || 0, c: p.uc(u.hue), id: u.id })))}</div>`;
    const topDep = conc.slice().sort((a, b) => b.metrics.dependents - a.metrics.dependents).slice(0, 10);
    h += `<div class="card"><h3>Pré-requisitos de mais conceitos</h3><p class="sub">Nº de conceitos que dependem (direta ou indiretamente).</p>${bars(topDep.map((c) => ({ l: c.label, v: c.metrics.dependents, c: p.uc(hue(c)), id: c.id })))}</div>`;
    const topDeg = conc.slice().sort((a, b) => deg(b.id) - deg(a.id)).slice(0, 10);
    h += `<div class="card"><h3>Conceitos mais conectados</h3><p class="sub">Relações conceptuais (todas as naturezas).</p>${bars(topDeg.map((c) => ({ l: c.label, v: deg(c.id), c: p.uc(hue(c)), id: c.id })))}</div>`;
    const topBr = conc.slice().sort((a, b) => b.metrics.betweenness - a.metrics.betweenness).slice(0, 10);
    h += `<div class="card"><h3>Pontes entre áreas</h3><p class="sub">Intermediação: conceitos por onde passam mais caminhos.</p>${bars(topBr.map((c) => ({ l: c.label, v: Math.round(c.metrics.betweenness), c: p.uc(hue(c)), id: c.id })))}</div>`;
    const temas = DATA.nodes.filter((n) => n.type === 'tema').map((t) => {
      const cs = new Set(conceptsOf(t.id).map((c) => c.id));
      let e = 0; DATA.edges.forEach((x) => { if (cs.has(x.source) && cs.has(x.target) && x.type !== 'contains') e++; });
      return { t, d: cs.size ? +(e / cs.size).toFixed(2) : 0, n: cs.size };
    }).filter((x) => x.n >= 3).sort((a, b) => b.d - a.d).slice(0, 10);
    h += `<div class="card"><h3>Temas com maior densidade</h3><p class="sub">Relações internas por conceito (temas com ≥ 3 conceitos).</p>${bars(temas.map((x) => ({ l: `${x.t.label} · ${N.get(x.t.uc).short}`, v: x.d, c: p.uc(hue(x.t)), id: x.t.id })), { fmt: (v) => v.toFixed(1) })}</div>`;
    // matriz UC×UC
    const M = {}; UCS.forEach((a) => { M[a.id] = {}; UCS.forEach((b) => { M[a.id][b.id] = 0; }); });
    DATA.edges.forEach((e) => { const a = N.get(e.source), b = N.get(e.target); if (isConcept(a) && isConcept(b) && a.uc !== b.uc && e.type !== 'contains') M[a.uc][b.uc]++; });
    const mx = Math.max(1, ...UCS.flatMap((a) => UCS.map((b) => M[a.id][b.id])));
    h += `<div class="card"><h3>Relações entre UCs</h3><p class="sub">Linha = origem, coluna = destino (pré-requisitos, aplicações e relações).</p><table class="matrix"><tr><th></th>${UCS.map((u) => `<th>${esc(u.short)}</th>`).join('')}</tr>${UCS.map((a) => `<tr><th class="r">${esc(a.short)}</th>${UCS.map((b) => { const v = M[a.id][b.id]; return `<td style="background:${a.id === b.id ? 'transparent' : `hsla(${a.hue},45%,50%,${v ? 0.1 + 0.55 * v / mx : 0.03})`};color:${v ? 'var(--text)' : 'var(--text-3)'}">${a.id === b.id ? '·' : v}</td>`; }).join('')}</tr>`).join('')}</table></div>`;
    const cb = DATA.confidence_breakdown;
    const cbRows = Object.keys(cb).sort().map((k) => ({ l: k.replace('explicita', 'Explícita').replace('inferida', 'Inferida').replace('/media', ' · média').replace('/alta', ' · alta').replace('/baixa', ' · baixa'), v: cb[k], c: k.startsWith('inferida') ? 'var(--text-3)' : 'var(--accent)' }));
    h += `<div class="card"><h3>Confiança das relações</h3><p class="sub">Sem contar a hierarquia (contains).</p>${bars(cbRows)}</div>`;
    h += `<div class="card"><h3>Tipos de relação</h3><p class="sub">Todas as arestas guardadas.</p>${bars(Object.entries(s.by_edge).sort((a, b) => b[1] - a[1]).map(([k, v]) => ({ l: k, v })))}</div>`;
    h += `</div>`;
    h += `<div class="card mt"><h3>Ficheiros</h3><p class="sub">Estado da análise de cada ficheiro da pasta do semestre.</p><table class="files-table">${DATA.files.map((f) => `<tr><td><a href="${fileHref(f.path)}" target="_blank">${esc(f.path)}</a></td><td>${esc(f.kind)}</td><td class="${/parcial|vazio/.test(f.status) ? 'st-part' : 'st-ok'}">${esc(f.status)}</td></tr>`).join('')}</table></div>`;
    $('#stats-body').innerHTML = h;
  }
  $('#stats-body').addEventListener('click', (e) => { const r = e.target.closest('[data-go]'); if (!r) return; setView('map'); const n = N.get(r.dataset.go); if (isConcept(n)) focusNode(n.id); else { state.expanded.add(n.uc); state.expanded.add(n.id); state.focus = n.id; applyVisibility(); openPanel(n.id); fitVisible(80, groupCollection(n.id)); } });

  // ------------------------------------------------------------------ overview, zoom, minimapa
  function overview() {
    state.expanded = new Set(); state.focus = null; state.revealed = new Set();
    $('#panel').hidden = true;
    if (state.view !== 'map') setView('map');
    applyVisibility({ fit: true, fitPadding: 80 });
  }
  $('#z-in').onclick = () => cy.animate({ zoom: { level: cy.zoom() * 1.3, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } }, duration: 200 });
  $('#z-out').onclick = () => cy.animate({ zoom: { level: cy.zoom() / 1.3, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } }, duration: 200 });
  $('#z-overview').onclick = overview;

  const mm = $('#minimap'), mctx = mm.getContext('2d');
  let mmT = 0, mmBox = null;
  function drawMinimap() {
    if (mmT) return;
    mmT = requestAnimationFrame(() => {
      mmT = 0;
      const dpr = window.devicePixelRatio || 1, W = 200, H = 132;
      if (mm.width !== W * dpr) { mm.width = W * dpr; mm.height = H * dpr; }
      mctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      mctx.clearRect(0, 0, W, H);
      const vis = cy.nodes(':visible').filter((n) => n.data('type') !== 'stagehdr');
      if (!vis.length) return;
      const bb = vis.boundingBox();
      const ext = cy.extent();
      const x1 = Math.min(bb.x1, ext.x1), y1 = Math.min(bb.y1, ext.y1), x2 = Math.max(bb.x2, ext.x2), y2 = Math.max(bb.y2, ext.y2);
      const s = Math.min((W - 16) / (x2 - x1 || 1), (H - 16) / (y2 - y1 || 1));
      const ox = (W - (x2 - x1) * s) / 2 - x1 * s, oy = (H - (y2 - y1) * s) / 2 - y1 * s;
      mmBox = { s, ox, oy };
      const p = palette();
      vis.forEach((n) => {
        const t = n.data('type');
        if (t === 'lane') { const b = n.boundingBox(); mctx.fillStyle = p.ucSoft(n.data('hue')); mctx.fillRect(b.x1 * s + ox, b.y1 * s + oy, b.w * s, b.h * s); return; }
        const pos = n.position(), nn = N.get(n.id());
        const r = t === 'root' ? 4 : t === 'uc' ? 3.4 : t === 'tema' ? 2.2 : 1.4;
        mctx.globalAlpha = n.hasClass('faded') ? 0.2 : 0.9;
        mctx.fillStyle = t === 'root' ? p.text : p.uc(hue(nn || {}));
        mctx.beginPath(); mctx.arc(pos.x * s + ox, pos.y * s + oy, r, 0, Math.PI * 2); mctx.fill();
      });
      mctx.globalAlpha = 1;
      mctx.strokeStyle = css('--accent'); mctx.lineWidth = 1.5;
      mctx.fillStyle = isDark() ? 'rgba(139,147,245,0.08)' : 'rgba(79,91,213,0.07)';
      const rx = ext.x1 * s + ox, ry = ext.y1 * s + oy, rw = ext.w * s, rh = ext.h * s;
      mctx.fillRect(rx, ry, rw, rh); mctx.strokeRect(rx, ry, rw, rh);
    });
  }
  function mmPan(ev) {
    if (!mmBox) return;
    const r = mm.getBoundingClientRect();
    const x = (ev.clientX - r.left - mmBox.ox) / mmBox.s, y = (ev.clientY - r.top - mmBox.oy) / mmBox.s;
    cy.center(); const z = cy.zoom();
    cy.pan({ x: cy.width() / 2 - x * z, y: cy.height() / 2 - y * z });
  }
  let mmDrag = false;
  mm.addEventListener('mousedown', (e) => { mmDrag = true; mmPan(e); });
  window.addEventListener('mousemove', (e) => { if (mmDrag) mmPan(e); });
  window.addEventListener('mouseup', () => { mmDrag = false; });
  cy.on('viewport', drawMinimap);
  cy.on('position', 'node', () => drawMinimap());

  // ------------------------------------------------------------------ legenda, tema, menus
  function renderLegend() {
    $('#legend').innerHTML = `
      <div class="li"><span class="line"></span>pré-requisito</div><div class="li"><span class="line dash"></span>inferida</div>
      <div class="li"><span class="line dot"></span>relacionado</div><div class="li"><span class="line faint"></span>hierarquia</div>
      <div class="li"><span class="shape"></span>conceito</div><div class="li"><span class="shape hollow"></span>horizonte</div>
      <div class="li"><span class="shape dia"></span>exercício</div><div class="li"><span class="line" style="border-color:#c0731c"></span>depende dele</div>`;
  }
  $('#btn-theme').onclick = () => {
    const next = isDark() ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('kg-theme', next); } catch (e) {}
    cy.style(buildStyle()); syncFilterUI(); drawMinimap();
    if (!$('#stats').hidden) renderStats();
    if (!$('#bneck').hidden) renderBottlenecks();
  };
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { if (!root.dataset.theme) { cy.style(buildStyle()); drawMinimap(); } });
  function closeMenus() { $('#export-menu').hidden = true; $('#btn-export').classList.remove('on'); }
  $('#btn-export').onclick = (e) => { e.stopPropagation(); const m = $('#export-menu'); m.hidden = !m.hidden; $('#btn-export').classList.toggle('on', !m.hidden); };
  document.addEventListener('click', (e) => { if (!e.target.closest('.menu-wrap')) closeMenus(); });
  $('#btn-png').onclick = () => {
    const png = cy.png({ full: false, scale: 2, bg: css('--bg') });
    const a = document.createElement('a'); a.href = png; a.download = 'iacd-knowledge-graph.png'; a.click(); closeMenus();
  };
  $('#btn-filters').onclick = () => { const d = $('#filters'); d.hidden = !d.hidden; $('#bneck').hidden = true; if (state.bneckFocus && !d.hidden) markView('map'); $('#btn-filters').classList.toggle('on', !d.hidden); };
  $$('[data-close]').forEach((b) => b.addEventListener('click', () => {
    const t = b.dataset.close; $('#' + t).hidden = true;
    if (t === 'panel') { state.focus = null; state.revealed = new Set(); applyFocusClasses(); applyVisibility(); }
    if (t === 'stats') markView(state.view);
    if (t === 'bneck') { state.bneckFocus = null; markView('map'); applyFocusClasses(); }
    if (t === 'filters') $('#btn-filters').classList.remove('on');
  }));
  function toast(msg) { const t = $('#toast'); t.textContent = msg; t.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(() => { t.hidden = true; }, 1800); }
  function fadeHint() { $('#hint').classList.add('fade'); }
  function updateCrumb() {
    const f = state.focus ? N.get(state.focus) : null;
    const parts = ['1.º semestre'];
    if (state.view === 'roadmap') parts.push('Roadmap');
    if (f) { if (f.uc && f.type !== 'uc') parts.push(N.get(f.uc).short); if (f.tema) parts.push(N.get(f.tema).label); parts.push(f.label); }
    $('#crumb').textContent = parts.join(' › ');
  }

  document.addEventListener('keydown', (e) => {
    if (e.target.matches('input, select, textarea')) return;
    if (e.key === '/' || (e.key.toLowerCase() === 'k' && (e.ctrlKey || e.metaKey))) { e.preventDefault(); input.focus(); input.select(); }
    else if (e.key === 'Escape') { if (!$('#stats').hidden) { $('#stats').hidden = true; markView(state.view); } else if (state.focus) clearFocus(); else { $('#filters').hidden = true; $('#bneck').hidden = true; } }
    else if (e.key.toLowerCase() === 'o') overview();
    else if (e.key.toLowerCase() === 'f') $('#btn-filters').click();
    else if (e.key.toLowerCase() === 'r') setView('roadmap');
    else if (e.key.toLowerCase() === 'm') setView('map');
  });
  window.addEventListener('resize', () => { cy.resize(); drawMinimap(); });

  // ------------------------------------------------------------------ arranque
  syncFilterUI();
  renderLegend();
  applyVisibility();
  cy.fit(cy.nodes().filter((n) => !n.hasClass('hidden')), 70);
  setTimeout(() => $('#hint').classList.add('fade'), 7000);
  // API mínima para testes e consola
  window.KG = { cy, state, focusNode, setView, overview, search, applyVisibility, expandAll, N, DATA };
})();
