// kg-network-logic.js — Rede Genealógica com family-chart (cards)
// Substitui a antiga visualização Cytoscape por árvore em cards com fragmentos coloniais

(function () {
  'use strict';

  // ========== Data index ==========
  const dataMap = {};
  F3_NETWORK_DATA.forEach(d => { dataMap[d.id] = d; });

  let f3Chart = null;
  let f3Zoom = null;
  let activeCategories = new Set(['confirmada', 'provável', 'hipotética', 'barao', 'colonial', 'historical', 'materno']);

  // ========== Footer ==========
  const totalPessoas = F3_NETWORK_DATA.filter(n => n.id !== 'virtual_root' && n.data.display !== 'none').length;
  const totalFragmentos = (dataMap['virtual_root']?.rels?.children || []).length;
  document.getElementById('pageFooter').innerHTML =
    `<p>${totalPessoas} pessoas · ${totalFragmentos} fragmentos · Rede Genealógica Gramilo Sodré · LABHDUFBA</p>`;

  // ========== Card display (5 lines, conditional) ==========
  function cardLines(node) {
    const d = node.data;
    const lines = [];
    // Line 1: First name (may include title like "Dom", "Barão")
    const fn = (d['first name'] || '').trim();
    const ln = (d['last name'] || '').trim();
    if (fn) lines.push(fn);
    if (ln) lines.push(ln);
    // Line 2: birthday + place
    const bd = (d['birthday'] || '').trim();
    const bp = (d['place_birth'] || d['birth_place'] || '').trim();
    if (bd || bp) {
      let life = '';
      if (bp) life += bp;
      if (bd) life += (life ? ' · ' : '') + bd;
      lines.push('⏎ ' + life);
    }
    // Line 3: deathday + place
    const dd = (d['deathday'] || '').trim();
    const dp = (d['place_death'] || d['death_place'] || '').trim();
    if (dd || dp) {
      let death = '';
      if (dp) death += dp;
      if (dd) death += (death ? ' · ' : '') + dd;
      lines.push('✝ ' + death);
    }
    return lines.length > 0 ? lines : ['(sem dados)'];
  }

  // ========== Category class for card ==========
  function getCategoryClass(node) {
    const d = node.data;
    const cat = d.categoria || '';
    const conf = d.confiabilidade || '';
    if (cat === 'barao') return 'cat-barao';
    if (cat === 'colonial') return 'cat-colonial';
    if (cat === 'historical') return 'cat-historical';
    if (cat === 'materno') return 'cat-materno';
    if (conf === 'hipotética') return 'cat-hipotetica';
    if (conf === 'provável') return 'cat-provavel';
    return 'cat-confirmada';
  }

  function getCategoryLabel(node) {
    const d = node.data;
    const cat = d.categoria || '';
    const conf = d.confiabilidade || '';
    if (cat === 'barao') return 'Barão Alagoinhas';
    if (cat === 'colonial') return 'Colonial';
    if (cat === 'historical') return 'Histórico';
    if (cat === 'materno') return 'Materno';
    if (conf === 'hipotética') return 'Hipotética';
    if (conf === 'provável') return 'Provável';
    return 'Confirmada';
  }

  // ========== Init chart ==========
  function initChart(rootId) {
    const container = document.getElementById('tree-chart');
    container.innerHTML = '';
    container.className = 'f3';

    f3Chart = f3.createChart('#tree-chart', F3_NETWORK_DATA);
    f3Chart
      .setTransitionTime(500)
      .setCardXSpacing(400)
      .setCardYSpacing(200);

    // Hide all virtual nodes using private_cards_config
    f3Chart.setPrivateCardsConfig({
      condition: (d) => d.id.startsWith('virtual')
    });

    // Disable auto-generated empty spouse cards (we don't want placeholder nodes)
    f3Chart.setSingleParentEmptyCard(false);

    const f3Card = f3Chart.setCardSvg();
    f3Card.setCardDim({ width: 280, height: 120 });

    // Card display for SVG: array of functions, each returns one line (tspan)
    // Note: SVG card_display functions receive the full TreeDatum (n.data has the person data)
    f3Card.setCardDisplay([
      (n) => {
        const d = n.data;
        const fn = (d['first name'] || '').trim();
        const ln = (d['last name'] || '').trim();
        return fn || ln || '(sem dados)';
      },
      (n) => {
        const d = n.data;
        const bd = (d['birthday'] || '').trim();
        const bp = (d['place_birth'] || d['birth_place'] || '').trim();
        if (!bd && !bp) return '';
        let life = '';
        if (bp) life += bp;
        if (bd) life += (life ? ' · ' : '') + bd;
        return '⏎ ' + life;
      },
      (n) => {
        const d = n.data;
        const dd = (d['deathday'] || '').trim();
        const dp = (d['place_death'] || d['death_place'] || '').trim();
        if (!dd && !dp) return '';
        let death = '';
        if (dp) death += dp;
        if (dd) death += (death ? ' · ' : '') + dd;
        return '✝ ' + death;
      }
    ]);
    f3Card.setLinkBreak(true);

    // Click handler
    f3Card.setOnCardClick((d) => {
      if (d.data.id === 'virtual_root') return;
      showInfo(d.data.id);
    });

    // Initial focus: PANORAMA COMPLETO — todos os ~158 nós (virtual_root).
    // ancestryDepth(0) = não mostrar "(sem dados)" acima dos ancestrais conhecidos.
    f3Chart.setAncestryDepth(0);
    f3Chart.setProgenyDepth(8);

    // Desabilita toggle buttons de ramos duplicados (ícones de expand/colapsa)
    f3Chart.setDuplicateBranchToggle(false);

    f3Chart.setOnUpdate(function () {
      try { applyTheme(); } catch (e) { /* silent */ }
    });

    // First render with virtual_root para mostrar TODOS os fragmentos
    f3Chart.updateMainId('virtual_root');
    f3Chart.updateTree({ initial: true });

    // Pan/zoom + custom centering after render
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        try { enablePanZoom(); } catch (e) { /* silent */ }
        try { centerOnMain(); } catch (e) { console.warn('[KG-NETWORK] centerOnMain:', e); }
        try { applyTheme(); } catch (e) { /* silent */ }
        hideLoading();
      });
    });

    // Wire view controls
    wireViewButtons();
    setTimeout(() => { try { applyTheme(); } catch (e) { /* */ } }, 500);
  }

  // ========== Center on main card ==========
  // Compute bounds of all cards and pan/zoom the svg.g.view to frame Marcelo (gp1)
  function centerOnMain() {
    const svg = document.querySelector('#tree-chart svg.main_svg');
    if (!svg) return;
    // Force SVG to fill its parent by hand (default viewBox fallback gives 300x150)
    svg.removeAttribute('viewBox');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '100%');
    svg.style.width = '100%';
    svg.style.height = '100%';
    const viewG = svg.querySelector('g.view');
    if (!viewG) return;

    // Find Marcelo's card
    const cards = Array.from(svg.querySelectorAll('.card_cont'));
    if (cards.length === 0) { console.warn('[KG-NETWORK] no cards to center'); return; }

    // The main card (Marcelo) is the one closest to (0,0) by ancestry depth, but easier:
    // use a "card-main" if it exists; otherwise the FIRST root (depth 0 or closest to 0).
    const mainCard = svg.querySelector('.card-main')?.closest('.card_cont')
                  || cards.find(c => /translate\(-?\d+, 0\)/.test(c.getAttribute('transform') || ''))
                  || cards[0];
    const t = mainCard.getAttribute('transform') || '';
    const m = t.match(/translate\(([-\d.]+),\s*([-\d.]+)\)/);
    if (!m) return;
    const cx = parseFloat(m[1]);
    const cy = parseFloat(m[2]);

    // Apply transform directly to g.view — this is what the lib's pan-zoom listens to
    const scale = 0.75;
    const parentRect = svg.getBoundingClientRect();
    const tx = parentRect.width / 2 - cx * scale;
    const ty = parentRect.height / 2 - cy * scale;
    const newTransform = `translate(${tx}, ${ty}) scale(${scale})`;
    viewG.setAttribute('transform', newTransform);

    // Update __zoomObj so zoom events continue correctly
    if (svg.__zoomObj && d3 && d3.zoomIdentity) {
      try {
        d3.select(svg).call(svg.__zoomObj.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
      } catch (e) { /* ignore */ }
    }
  }

  // ========== Pan/Zoom ==========
  function enablePanZoom() {
    const svgSel = d3.select('#tree-chart svg.main_svg');
    const svg = svgSel.node();
    if (!svg) return;

    const viewSel = svgSel.select('g.view');
    if (viewSel.empty()) return;

    viewSel.style('transform', null);

    let zoom = svg.__zoomObj;
    if (!zoom) {
      zoom = d3.zoom()
        .scaleExtent([0.15, 2.5])
        .on('zoom', function (event) {
          viewSel.style('transform', null).attr('transform', event.transform);
        });
      svg.__zoomObj = zoom;
      svgSel.call(zoom);
    } else {
      svgSel.call(zoom);
    }

    svgSel.on('dblclick.zoom', null);
    svgSel.style('touch-action', 'none');
    return zoom;
  }

  // ========== Center tree ==========
  function centerTree(options = {}) {
    const {
      padding = 50,
      preferredScale = 1,
      minReadableScale = 0.5,
      maxInitialScale = 1.15,
      fitWidth = true,
      centerMode = 'main',
      duration = 0
    } = options;

    const svgSel = d3.select('#tree-chart svg.main_svg');
    const svg = svgSel.node();
    if (!svg) return;
    const zoom = enablePanZoom();
    if (!zoom) return;

    const cardsView = svg.querySelector('.cards_view');
    if (!cardsView) return;

    let bbox;
    try { bbox = cardsView.getBBox(); } catch (e) { return; }
    if (!bbox || !isFinite(bbox.width) || bbox.width === 0) return;

    const svgRect = svg.getBoundingClientRect();
    const svgW = svgRect.width || 1400;
    const svgH = svgRect.height || 720;

    const fitScaleW = (svgW - padding * 2) / bbox.width;
    const fitScaleH = (svgH - padding * 2) / bbox.height;

    let scale;
    if (fitWidth) {
      scale = Math.min(fitScaleW, fitScaleH, maxInitialScale);
    } else {
      scale = preferredScale;
      scale = Math.min(scale, fitScaleH, maxInitialScale);
      scale = Math.max(scale, minReadableScale);
    }

    const targetCx = bbox.x + bbox.width / 2;
    const targetCy = bbox.y + bbox.height / 2;

    const tx = svgW / 2 - targetCx * scale;
    const ty = svgH / 2 - targetCy * scale;

    const transform = d3.zoomIdentity.translate(tx, ty).scale(scale);
    if (duration > 0) {
      svgSel.transition().duration(duration).call(zoom.transform, transform);
    } else {
      svgSel.call(zoom.transform, transform);
    }
  }

  // ========== Theme (parchment + category colors) ==========
  function applyTheme() {
    // Card background
    document.querySelectorAll('#tree-chart .card-body-rect').forEach(el => {
      const card = el.closest('.card');
      if (card) {
        if (card.classList.contains('card-female')) el.setAttribute('fill', '#f0dde5');
        else if (card.classList.contains('card-male')) el.setAttribute('fill', '#dde8f0');
        else el.setAttribute('fill', '#fffcf5');
      }
    });
    // Card outline
    document.querySelectorAll('#tree-chart .card-outline').forEach(el => {
      el.setAttribute('fill', '#fffcf5');
      el.setAttribute('stroke', '#c9b896');
      el.setAttribute('stroke-width', '1');
    });
    // Main outline
    document.querySelectorAll('#tree-chart .card-main-outline').forEach(el => {
      el.setAttribute('stroke', '#9e7c2e');
      el.setAttribute('stroke-width', '2');
    });
    // Text
    document.querySelectorAll('#tree-chart .card text, #tree-chart .card tspan').forEach(el => {
      el.setAttribute('fill', '#1a1008');
      el.setAttribute('font-family', "'EB Garamond', Georgia, serif");
    });
    // Text overflow mask (hide fade)
    document.querySelectorAll('#tree-chart .text-overflow-mask').forEach(el => {
      const card = el.closest('.card');
      if (card) {
        if (card.classList.contains('card-female')) el.setAttribute('fill', '#f0dde5');
        else if (card.classList.contains('card-male')) el.setAttribute('fill', '#dde8f0');
        else el.setAttribute('fill', '#fffcf5');
      }
    });
    // Links
    document.querySelectorAll('#tree-chart .link').forEach(el => {
      el.setAttribute('stroke', '#c9b896');
      el.setAttribute('stroke-width', '1.5');
    });
    // Apply category class to card containers for CSS-driven borders
    document.querySelectorAll('#tree-chart .card_cont').forEach(el => {
      // Find which data node this card belongs to
      const cardId = el.id; // "card-{nodeId}"
      if (!cardId) return;
      const nodeId = cardId.replace('card-', '');
      const node = dataMap[nodeId];
      if (!node) return;
      // Remove old cat- classes
      el.classList.remove('cat-confirmada', 'cat-provavel', 'cat-hipotetica', 'cat-barao', 'cat-colonial', 'cat-historical', 'cat-materno');
      el.classList.add(getCategoryClass(node));
    });
  }

  // ========== Info panel ==========
  function showInfo(nodeId) {
    const node = dataMap[nodeId];
    if (!node) return;
    const d = node.data;

    document.getElementById('infoName').textContent = d['nome completo'] || ((d['first name'] || '') + ' ' + (d['last name'] || '')).trim();

    // Badges
    const meta = document.getElementById('infoMeta');
    meta.innerHTML = '';
    const catLabel = getCategoryLabel(node);
    const cat = d.categoria || d.confiabilidade || '';
    const badgeClass = cat === 'barao' ? 'barao' : cat === 'colonial' ? 'colonial' : cat === 'historical' ? 'historical' : cat === 'materno' ? 'materno' : d.confiabilidade === 'hipotética' ? 'hipotetica' : d.confiabilidade === 'provável' ? 'provavel' : 'confirmada';
    meta.innerHTML = `<span class="info-badge ${badgeClass}">${catLabel}</span>`;
    if (d.gender === 'M') meta.innerHTML += '<span class="info-badge">♂ Masculino</span>';
    else if (d.gender === 'F') meta.innerHTML += '<span class="info-badge">♀ Feminino</span>';

    // Body
    const body = document.getElementById('infoBody');
    body.innerHTML = '';

    // Dates
    let datesHtml = '<div class="info-section"><div class="info-section-title">Datas & Locais</div>';
    const bd = d['birthday'] || '';
    const bp = d['place_birth'] || d['birth_place'] || '';
    if (bd || bp) datesHtml += `<div class="info-rel"><span class="rel-type">Nascimento:</span>${bp ? ' ' + bp : ''}${bd ? ' · ' + bd : ''}</div>`;
    const dd = d['deathday'] || '';
    const dp = d['place_death'] || d['death_place'] || '';
    if (dd || dp) datesHtml += `<div class="info-rel"><span class="rel-type">Falecimento:</span>${dp ? ' ' + dp : ''}${dd ? ' · ' + dd : ''}</div>`;
    const datesFull = d['dates_full'] || '';
    if (datesFull && !bd && !dd) datesHtml += `<div class="info-rel"><span class="rel-type">Período:</span> ${datesFull}</div>`;
    datesHtml += '</div>';
    body.innerHTML += datesHtml;

    // Relations
    const rels = node.rels || {};
    let relsHtml = '<div class="info-section"><div class="info-section-title">Relações</div>';
    let hasRels = false;
    if (rels.parents && rels.parents.length) {
      rels.parents.forEach(pid => {
        if (pid === 'virtual_root' || pid.startsWith('virtual_')) return;
        const p = dataMap[pid];
        if (p) { relsHtml += `<div class="info-rel" data-goto="${pid}"><span class="rel-type">Filho/a de:</span> ${p.data['nome completo'] || pid}</div>`; hasRels = true; }
      });
    }
    if (rels.spouses && rels.spouses.length) {
      rels.spouses.forEach(sid => {
        const s = dataMap[sid];
        if (s) { relsHtml += `<div class="info-rel" data-goto="${sid}"><span class="rel-type">Casou com:</span> ${s.data['nome completo'] || sid}</div>`; hasRels = true; }
      });
    }
    if (rels.children && rels.children.length) {
      rels.children.forEach(cid => {
        if (cid === 'virtual_root') return;
        const c = dataMap[cid];
        if (c) { relsHtml += `<div class="info-rel" data-goto="${cid}"><span class="rel-type">Pai/Mãe de:</span> ${c.data['nome completo'] || cid}</div>`; hasRels = true; }
      });
    }
    relsHtml += '</div>';
    if (hasRels) body.innerHTML += relsHtml;

    // Notes
    const note = d['notas'] || '';
    if (note) body.innerHTML += `<div class="info-note">${note}</div>`;

    // Click to navigate to related person
    body.querySelectorAll('.info-rel[data-goto]').forEach(el => {
      el.addEventListener('click', () => {
        const gotoId = el.dataset.goto;
        if (gotoId && dataMap[gotoId]) {
          focusOnNode(gotoId);
          showInfo(gotoId);
        }
      });
    });

    document.getElementById('infoPanel').classList.add('open');
  }

  function focusOnNode(nodeId) {
    if (!f3Chart) return;
    f3Chart.updateMainId(nodeId);
    f3Chart.updateTree({});
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        try { applyTheme(); } catch (e) { /* */ }
        // Try to center on that node
        const svgSel = d3.select('#tree-chart svg.main_svg');
        const svg = svgSel.node();
        if (!svg) return;
        const mainCard = svg.querySelector('.card-main') || svg.querySelector('.card-depth-0');
        if (mainCard) {
          const cont = mainCard.closest('.card_cont');
          if (cont && cont.transform && cont.transform.baseVal.length) {
            const zoom = svg.__zoomObj;
            if (zoom) {
              const matrix = cont.transform.baseVal.consolidate().matrix;
              const svgRect = svg.getBoundingClientRect();
              const scale = 0.65;
              const tx = svgRect.width / 2 - matrix.e * scale;
              const ty = svgRect.height / 2 - matrix.f * scale;
              svgSel.call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
            }
          }
        }
      });
    });
  }

  // Close panel
  document.getElementById('infoClose').addEventListener('click', () => {
    document.getElementById('infoPanel').classList.remove('open');
  });

  // ========== Controls ==========
  document.getElementById('btnReset').addEventListener('click', () => {
    centerTree({ preferredScale: 0.55, minReadableScale: 0.4, fitWidth: true, centerMode: 'bbox' });
  });

  document.getElementById('btnFit').addEventListener('click', () => {
    centerTree({ fitWidth: true, maxInitialScale: 0.9, centerMode: 'bbox' });
  });

  document.getElementById('btnCenter').addEventListener('click', () => {
    focusOnNode('gp1');
  });

  // ========== Search ==========
  let searchTimeout = null;
  document.getElementById('searchInput').addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      const q = e.target.value.trim().toLowerCase();
      if (!q) return;
      // Find first match
      const match = F3_NETWORK_DATA.find(n => {
        const full = (n.data['nome completo'] || ((n.data['first name'] || '') + ' ' + (n.data['last name'] || ''))).toLowerCase();
        return full.includes(q) && n.id !== 'virtual_root';
      });
      if (match) {
        focusOnNode(match.id);
        showInfo(match.id);
        toast(`Encontrado: ${match.data['nome completo'] || match.id}`);
      } else {
        toast('Nenhum resultado');
      }
    }, 400);
  });

  // ========== Category filter ==========
  document.querySelectorAll('.cat-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const cat = chip.dataset.cat;
      if (activeCategories.has(cat)) {
        activeCategories.delete(cat);
        chip.classList.remove('active');
      } else {
        activeCategories.add(cat);
        chip.classList.add('active');
      }
      applyCategoryFilter();
    });
  });

  function applyCategoryFilter() {
    // Dim cards not in active categories (CSS opacity approach, don't re-render tree)
    document.querySelectorAll('#tree-chart .card_cont').forEach(el => {
      const cardId = el.id;
      if (!cardId) return;
      const nodeId = cardId.replace('card-', '');
      const node = dataMap[nodeId];
      if (!node) return;
      const cat = getNormalizedCategory(node);
      if (activeCategories.has(cat)) {
        el.style.opacity = '1';
      } else {
        el.style.opacity = '0.15';
      }
    });
  }

  function getNormalizedCategory(node) {
    const d = node.data;
    const cat = d.categoria || '';
    const conf = d.confiabilidade || '';
    if (cat === 'barao') return 'barao';
    if (cat === 'colonial') return 'colonial';
    if (cat === 'historical') return 'historical';
    if (cat === 'materno') return 'materno';
    if (conf === 'hipotética') return 'hipotética';
    if (conf === 'provável') return 'provável';
    return 'confirmada';
  }

  // ========== Toast ==========
  function toast(msg) {
    const el = document.getElementById('toast');
    el.textContent = msg;
    el.classList.add('show');
    setTimeout(() => el.classList.remove('show'), 2000);
  }

  // ========== Loading ==========
  function hideLoading() {
    const el = document.getElementById('loadingOverlay');
    if (el) el.classList.add('hidden');
  }

  // ========== View control buttons ==========
  function wireViewButtons() {
    const btnReset = document.getElementById('btnReset');
    const btnFit = document.getElementById('btnFit');
    const btnCenter = document.getElementById('btnCenter');

    if (btnReset) {
      btnReset.addEventListener('click', () => {
        const svg = document.querySelector('#tree-chart svg.main_svg');
        if (svg && svg.__zoomObj) svg.__zoomObj.transform(svg, d3.zoomIdentity);
      });
    }

    if (btnFit) {
      btnFit.addEventListener('click', () => {
        if (!f3Chart) return;
        f3Chart.setAncestryDepth(1);
        f3Chart.setProgenyDepth(8);
        f3Chart.updateMainId('virtual_root');
        f3Chart.updateTree({ tree_position: 'fit' });
        requestAnimationFrame(() => {
          try { applyTheme(); } catch (e) { /* */ }
          try { enablePanZoom(); } catch (e) { /* */ }
          toast('Visão completa — todos os fragmentos');
        });
      });
    }

    if (btnCenter) {
      btnCenter.addEventListener('click', () => {
        if (!f3Chart) return;
        f3Chart.updateMainId('gp1');
        f3Chart.updateTree({});
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            try { applyTheme(); } catch (e) { /* */ }
            try { centerOnMain(); } catch (e) { /* */ }
          });
        });
      });
    }
  }

  // ========== Start ==========
  initChart('gp1');
})();
