// ============ LÓGICA DO GRAFO ============
let cy = null;
let currentLayout = 'hierarchical';
let searchIndex = new Map();

// Register Cytoscape extensions (needed for CDN loads)
if (typeof cytoscape !== 'undefined') {
  let extCount = 0;
  if (typeof window.coseBilkent !== 'undefined') {
    cytoscape.use(window.coseBilkent);
    extCount++;
    console.log('cose-bilkent registered');
  }
  if (typeof window.cola !== 'undefined' && typeof window.cytoscapeCola !== 'undefined') {
    cytoscape.use(window.cytoscapeCola);
    extCount++;
    console.log('cola registered');
  }
  if (extCount === 0) {
    console.warn('No Cytoscape extensions loaded from CDN - using built-in cose only');
  }
}

const CATEGORY_COLORS = {
  historical: '#f5e6c8',      // light gold/parchment
  barao: '#e8e0f0',           // light purple
  colonial: '#dce8f5',        // light blue
  confirmed: '#e0f0e8',       // light green
  materno: '#f5efe0',         // light amber
  hypothetical: '#f5e0e0',    // light red
  probable: '#f5efe0',        // light amber
  filho: '#e0f0e8',           // light green
  sobrinho: '#e0f0e8'         // light green
};

const CATEGORY_BORDER_COLORS = {
  historical: '#9e7c2e',
  barao: '#4a3478',
  colonial: '#2a5a8a',
  confirmed: '#2d5a3d',
  materno: '#7a5a10',
  hypothetical: '#8b2e2e',
  probable: '#b8860b',
  filho: '#2d5a3d',
  sobrinho: '#2d5a3d'
};

const CATEGORY_LABELS = {
  historical: 'Histórico (tronco)',
  barao: 'Ramo Barão de Alagoinhas',
  colonial: 'Elo colonial Sodré–Gramilo',
  confirmed: 'Confirmado (linha direta)',
  materno: 'Ramo materno (Santos)',
  hypothetical: 'Hipotético',
  probable: 'Provável',
  filho: 'Filhos (G4+)',
  sobrinho: 'Sobrinhos/Netos'
};

function initCy() {
  cy = cytoscape({
    container: document.getElementById('cy'),
    elements: [...NODES_DATA, ...EDGES_DATA],
    style: [
      {
        selector: 'node',
        style: {
          'label': 'data(label)',
          'font-family': 'Cormorant Garamond, serif',
          'font-size': '13px',
          'font-weight': 700,
          'color': '#1a1008',
          'text-valign': 'center',
          'text-halign': 'center',
          'text-wrap': 'wrap',
          'text-max-width': '140px',
          'background-color': 'data(categoryColor)',
          'border-width': 3,
          'border-color': 'data(categoryBorderColor)',
          'border-opacity': 1,
          'width': 'label',
          'height': 'label',
          'padding': '10px 12px',
          'min-width': '120px',
          'min-height': '50px',
          'shape': 'round-rectangle',
          'overlay-padding': '6px',
          'z-index': 10
        }
      },
      {
        selector: 'node:selected',
        style: {
          'border-width': 4,
          'border-color': '#9e7c2e',
          'box-shadow': '0 0 20px rgba(158,124,46,0.6)',
          'z-index': 100
        }
      },
      {
        selector: 'edge',
        style: {
          'width': 2,
          'line-color': '#c9b896',
          'target-arrow-shape': 'triangle',
          'target-arrow-color': '#c9b896',
          'curve-style': 'bezier',
          'label': 'data(label)',
          'font-family': 'Cormorant Garamond, serif',
          'font-size': '11px',
          'color': '#7a6b55',
          'edge-text-rotation': 'autorotate',
          'text-margin-y': -8,
          'text-background-color': '#f4ece1',
          'text-background-opacity': 0.9,
          'text-background-padding': '3px',
          'text-background-shape': 'round-rectangle'
        }
      },
      {
        selector: 'edge[type="casou_com"]',
        style: {
          'line-color': '#9e7c2e',
          'target-arrow-color': '#9e7c2e',
          'target-arrow-shape': 'none',
          'line-style': 'solid',
          'width': 3,
          'label': '∞'
        }
      },
      {
        selector: 'edge[type="pai_de"], edge[type="mae_de"]',
        style: {
          'target-arrow-shape': 'triangle',
          'target-arrow-color': '#2d5a3d',
          'line-color': '#2d5a3d'
        }
      },
      {
        selector: '.faded',
        style: {
          'opacity': 0.15,
          'text-opacity': 0.15
        }
      },
      {
        selector: '.highlight',
        style: {
          'border-width': 4,
          'border-color': '#9e7c2e',
          'z-index': 50
        }
      }
    ],
    layout: { name: 'preset' },
    wheelSensitivity: 0.15,
    minZoom: 0.15,
    maxZoom: 3,
    zoomingEnabled: true,
    userZoomingEnabled: true,
    panningEnabled: true,
    userPanningEnabled: true,
    boxSelectionEnabled: true,
    selectionType: 'single'
  });

  // Assign category colors to nodes
  cy.nodes().forEach(n => {
  const cat = n.data('category');
  n.data('categoryColor', CATEGORY_COLORS[cat] || '#f4ece1');
  n.data('categoryBorderColor', CATEGORY_BORDER_COLORS[cat] || '#7a6b55');
  // Build search index
  const label = n.data('label').toLowerCase();
  if (!searchIndex.has(label)) searchIndex.set(label, []);
  searchIndex.get(label).push(n.id());
  });

  // Event: tap node -> show info panel
  cy.on('tap', 'node', (e) => {
    const node = e.target;
    showInfoPanel(node);
  });

  // Event: tap background -> close panel
  cy.on('tap', (e) => {
    if (e.target === cy) hideInfoPanel();
  });

  // Search input
  const searchInput = document.getElementById('searchInput');
  let searchTimeout;
  searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      const query = searchInput.value.toLowerCase().trim();
      if (query.length === 0) {
        cy.elements().removeClass('faded highlight');
        return;
      }
      // Find matching nodes
      const matches = [];
      searchIndex.forEach((ids, label) => {
        if (label.includes(query)) matches.push(...ids);
      });
      if (matches.length > 0) {
        cy.elements().addClass('faded');
        matches.forEach(id => {
          const n = cy.getElementById(id);
          n.removeClass('faded').addClass('highlight');
        });
        // Center on first match
        if (matches.length === 1) {
          cy.getElementById(matches[0]).animate({ position: { name: 'center' } }, { duration: 500 });
        }
      } else {
        cy.elements().removeClass('faded highlight');
      }
    }, 150);
  });

  // Layout buttons
  document.getElementById('btnHierarchical').addEventListener('click', () => runLayout('hierarchical'));
  document.getElementById('btnForce').addEventListener('click', () => runLayout('force'));
  document.getElementById('btnReset').addEventListener('click', () => runLayout('reset'));
  document.getElementById('btnFit').addEventListener('click', () => runLayout('fit'));

  // Legend
  renderLegend();

  // Close panel
  document.getElementById('infoClose').addEventListener('click', hideInfoPanel);

  // Hide loading
  document.getElementById('loadingOverlay').classList.add('hidden');

  // Initial layout - use circle first to spread nodes, then hierarchical
  cy.layout({ 
    name: 'circle', 
    fit: true, 
    padding: 150,
    radius: Math.max(400, cy.nodes().length * 10),
    startAngle: 1.5 * Math.PI,
    counterclockwise: false
  }).run();
  // Then apply hierarchical after a short delay
  setTimeout(() => runLayout('hierarchical'), 500);
}
function runLayout(type) {
  if (!cy) return;

  // Update button states
  document.querySelectorAll('.ctrl-btn[data-layout]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.layout === type);
  });

  if (type === 'hierarchical') {
    currentLayout = 'hierarchical';
    // First: manually position by generation (grid per generation)
    positionByGeneration();
    // Then: run cose to refine
    setTimeout(() => {
      runCoseLayout('hierarchical');
    }, 100);
  } else if (type === 'force') {
    currentLayout = 'force';
    runCoseLayout('force');
  } else if (type === 'reset') {
    cy.animate({ zoom: 1, pan: { x: 0, y: 0 } }, { duration: 500 });
    showToast('Zoom e pan resetados');
  } else if (type === 'fit') {
    cy.fit(null, 80);
    showToast('Ajustado para mostrar todos os nós');
  }
}

function positionByGeneration() {
  // Group nodes by generation
  const byGen = {};
  cy.nodes().forEach(n => {
    const gen = n.data('generation') || 5;
    if (!byGen[gen]) byGen[gen] = [];
    byGen[gen].push(n);
  });

  const generations = Object.keys(byGen).map(Number).sort((a,b) => a-b);
  const genCount = generations.length;
  const centerX = cy.width() / 2;
  const centerY = cy.height() / 2;
  const ySpacing = Math.max(180, cy.height() / (genCount + 1));
  const xSpacing = 200;

  generations.forEach((gen, genIdx) => {
    const nodes = byGen[gen];
    const y = centerY - (genCount - 1) * ySpacing / 2 + genIdx * ySpacing;
    const totalWidth = (nodes.length - 1) * xSpacing;
    const startX = centerX - totalWidth / 2;
    
    nodes.forEach((n, i) => {
      n.position({ x: startX + i * xSpacing, y });
    });
  });
  
  cy.fit(null, 100);
}

function runCoseLayout(mode) {
  const isHierarchical = mode === 'hierarchical';
  
  try {
    const layoutName = (typeof window.coseBilkent !== 'undefined') ? 'cose-bilkent' : 'cose';
    console.log(`Running ${layoutName} for ${mode} mode`);
    
    cy.layout({
      name: layoutName,
      animate: true,
      animationDuration: isHierarchical ? 1500 : 1200,
      fit: true,
      padding: 120,
      nodeDimensionsIncludeLabels: true,
      randomize: false,
      idealEdgeLength: isHierarchical ? 160 : 140,
      nodeRepulsion: isHierarchical ? 10000 : 12000,
      nodeOverlap: 60,
      edgeElasticity: isHierarchical ? 0.25 : 0.2,
      nestingFactor: 0.05,
      gravity: isHierarchical ? 0.35 : 0.15,
      numIter: 4000,
      initialTemp: 2000,
      coolingFactor: 0.95,
      minTemp: 1,
      // cose-bilkent specific
      tile: isHierarchical,
      tilingPaddingVertical: isHierarchical ? 120 : 0,
      tilingPaddingHorizontal: isHierarchical ? 100 : 0,
      gravityRange: isHierarchical ? 5.0 : 3.0,
      gravityCompound: 1.5,
      gravityRangeCompound: isHierarchical ? 5.0 : 3.0,
      initialEnergyOnIncremental: 0.3
    }).run();
    
    showToast(`Layout ${isHierarchical ? 'hierárquico' : 'livre'} aplicado (${layoutName})`);
  } catch (err) {
    console.warn(`${layoutName} failed, falling back to cose:`, err);
    // Ultra-aggressive cose fallback
    cy.layout({
      name: 'cose',
      animate: true,
      animationDuration: 1800,
      fit: true,
      padding: 150,
      nodeDimensionsIncludeLabels: true,
      idealEdgeLength: isHierarchical ? 180 : 160,
      nodeRepulsion: 20000,
      nodeOverlap: 80,
      edgeElasticity: 0.15,
      nestingFactor: 0.05,
      gravity: isHierarchical ? 0.4 : 0.1,
      numIter: 5000,
      initialTemp: 3000,
      coolingFactor: 0.93,
      minTemp: 1
    }).run();
    showToast(`Layout ${isHierarchical ? 'hierárquico' : 'livre'} aplicado (cose ultra)`);
  }
}

function renderLegend() {
  const legend = document.getElementById('legend');
  legend.innerHTML = '';
  Object.entries(CATEGORY_LABELS).forEach(([cat, label]) => {
    if (cat === 'filho' || cat === 'sobrinho') return; // Skip duplicates
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.innerHTML = `<div class="legend-dot" style="background:${CATEGORY_COLORS[cat]}"></div> ${label}`;
    legend.appendChild(item);
  });
}

function showInfoPanel(node) {
  const data = node.data();
  const panel = document.getElementById('infoPanel');
  document.getElementById('infoName').textContent = data.label;
  document.getElementById('infoMeta').innerHTML = `
    <span class="info-badge ${data.category}">${CATEGORY_LABELS[data.category] || data.category}</span>
    ${data.dates ? `<span class="info-badge">${data.dates}</span>` : ''}
    ${data.generation !== undefined ? `<span class="info-badge">Geração ${data.generation}</span>` : ''}
  `;

  // Build relationships
  let html = '';
  const edges = node.connectedEdges();

  // Spouse
  const spouseEdges = edges.filter(e => e.data('type') === 'casou_com');
  if (spouseEdges.length > 0) {
    html += `<div class="info-section"><div class="info-section-title">💍 Cônjuge(s)</div>`;
    spouseEdges.forEach(e => {
      const other = e.source().id() === data.id ? e.target() : e.source();
      html += `<div class="info-rel"><span class="rel-type">Casou com </span><span class="rel-target">${other.data('label')}</span></div>`;
    });
    html += '</div>';
  }

  // Parents
  const parentEdges = edges.filter(e => e.data('type') === 'pai_de' || e.data('type') === 'mae_de').filter(e => e.target().id() === data.id);
  if (parentEdges.length > 0) {
    html += `<div class="info-section"><div class="info-section-title">👨‍👩‍👧 Pais</div>`;
    parentEdges.forEach(e => {
      const rel = e.data('type') === 'pai_de' ? 'Pai' : 'Mãe';
      html += `<div class="info-rel"><span class="rel-type">${rel}: </span><span class="rel-target">${e.source().data('label')}</span></div>`;
    });
    html += '</div>';
  }

  // Children
  const childEdges = edges.filter(e => e.data('type') === 'pai_de' || e.data('type') === 'mae_de').filter(e => e.source().id() === data.id);
  if (childEdges.length > 0) {
    html += `<div class="info-section"><div class="info-section-title">👶 Filhos (${childEdges.length})</div>`;
    childEdges.forEach(e => {
      const rel = e.data('type') === 'pai_de' ? 'Pai de' : 'Mãe de';
      html += `<div class="info-rel"><span class="rel-type">${rel} </span><span class="rel-target">${e.target().data('label')}</span></div>`;
    });
    html += '</div>';
  }

  // Siblings (shared parents)
  const siblings = new Set();
  parentEdges.forEach(e => {
    const parent = e.source();
    parent.outgoers('edge[type="pai_de"], edge[type="mae_de"]').forEach(sib => {
      if (sib.id() !== data.id) siblings.add(sib);
    });
  });
  if (siblings.size > 0) {
    html += `<div class="info-section"><div class="info-section-title">👫 Irmãos (${siblings.size})</div>`;
    siblings.forEach(sib => {
      html += `<div class="info-rel"><span class="rel-target">${sib.data('label')}</span></div>`;
    });
    html += '</div>';
  }

  // Note
  if (data.note) {
    html += `<div class="info-note">${data.note}</div>`;
  }

  document.getElementById('infoBody').innerHTML = html;
  panel.classList.add('open');
}

function hideInfoPanel() {
  document.getElementById('infoPanel').classList.remove('open');
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2500);
}

// Init on DOM ready
document.addEventListener('DOMContentLoaded', initCy);

// Handle resize
window.addEventListener('resize', () => {
  if (cy) cy.resize();
});