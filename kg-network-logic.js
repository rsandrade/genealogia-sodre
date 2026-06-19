// ============ LÓGICA DO GRAFO ============
let cy = null;
let currentLayout = 'timeline';
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
  historical: '#f5e6c8',
  barao: '#e8e0f0',
  colonial: '#dce8f5',
  confirmed: '#e0f0e8',
  materno: '#f5efe0',
  hypothetical: '#f5e0e0',
  probable: '#f5efe0',
  filho: '#e0f0e8',
  sobrinho: '#e0f0e8'
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

// Parse birth year from dates string
function parseBirthYear(dates) {
  if (!dates) return null;
  // Formats: "1631–1711", "1818–1882", "~1860", "1897–1976", "1925–1999", "1933–?", "bat. 1881", "ativo 1909–1914", "n. 18/11/1913", "cas. 10/12/1941"
  const str = dates.trim();
  if (!str) return null;
  
  // Try to find first 4-digit year
  const yearMatch = str.match(/(\d{4})/);
  if (yearMatch) {
    return parseInt(yearMatch[1], 10);
  }
  return null;
}

// Parse death year for lifespan
function parseDeathYear(dates) {
  if (!dates) return null;
  const str = dates.trim();
  // Look for second year or year after dash
  const years = str.match(/(\d{4})/g);
  if (years && years.length >= 2) {
    return parseInt(years[1], 10);
  }
  return null;
}

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
  document.getElementById('btnTimeline').addEventListener('click', () => runLayout('timeline'));
  document.getElementById('btnForce').addEventListener('click', () => runLayout('force'));
  document.getElementById('btnReset').addEventListener('click', () => runLayout('reset'));
  document.getElementById('btnFit').addEventListener('click', () => runLayout('fit'));

  // Legend
  renderLegend();

  // Close panel
  document.getElementById('infoClose').addEventListener('click', hideInfoPanel);

  // Hide loading
  document.getElementById('loadingOverlay').classList.add('hidden');

  // Initial layout - timeline by birth date
  runTimelineLayout();
}

function runLayout(type) {
  if (!cy) return;

  // Update button states
  document.querySelectorAll('.ctrl-btn[data-layout]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.layout === type);
  });

  if (type === 'timeline') {
    currentLayout = 'timeline';
    runTimelineLayout();
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

function runTimelineLayout() {
  // 1. Extract birth years for all nodes
  const nodeData = [];
  cy.nodes().forEach(n => {
    const birthYear = parseBirthYear(n.data('dates'));
    const deathYear = parseDeathYear(n.data('dates'));
    const generation = n.data('generation') || 5;
    const label = n.data('label');
    const width = n.width() || 140;
    
    nodeData.push({
      node: n,
      birthYear: birthYear,
      deathYear: deathYear,
      generation: generation,
      label: label,
      width: width
    });
  });

  // 2. Sort by birth year (oldest first), then by generation
  nodeData.sort((a, b) => {
    if (a.birthYear !== null && b.birthYear === null) return -1;
    if (a.birthYear === null && b.birthYear !== null) return 1;
    if (a.birthYear !== null && b.birthYear !== null) {
      if (a.birthYear !== b.birthYear) return a.birthYear - b.birthYear;
    }
    return a.generation - b.generation;
  });

  // 3. Assign vertical positions based on birth year (timeline)
  const yearsWithDates = nodeData.filter(d => d.birthYear !== null);
  let minYear = 1630, maxYear = 2020;
  if (yearsWithDates.length > 0) {
    minYear = Math.min(...yearsWithDates.map(d => d.birthYear));
    maxYear = Math.max(...yearsWithDates.map(d => d.birthYear));
  }

  const centerX = cy.width() / 2;
  const topMargin = 100;
  const bottomMargin = 100;
  const availableHeight = cy.height() - topMargin - bottomMargin;

  // 4. Position nodes in timeline buckets (20-year buckets)
  const bucketSize = 20;
  const buckets = new Map();
  
  nodeData.forEach(d => {
    let bucketKey;
    if (d.birthYear !== null) {
      bucketKey = Math.floor(d.birthYear / bucketSize) * bucketSize;
    } else {
      bucketKey = 9999 + d.generation;
    }
    if (!buckets.has(bucketKey)) buckets.set(bucketKey, []);
    buckets.get(bucketKey).push(d);
  });

  const sortedBuckets = Array.from(buckets.entries()).sort((a, b) => a[0] - b[0]);
  const bucketCount = sortedBuckets.length;
  const bucketHeight = availableHeight / Math.max(1, bucketCount - 1);

  sortedBuckets.forEach((bucket, bucketIdx) => {
    const [yearKey, nodes] = bucket;
    const y = topMargin + bucketIdx * bucketHeight;
    
    const nodeCount = nodes.length;
    const spacing = 40;
    const totalWidth = nodes.reduce((sum, d) => sum + d.width, 0) + (nodeCount - 1) * spacing;
    let startX = centerX - totalWidth / 2;
    
    if (totalWidth > cy.width() * 0.9) {
      const scale = (cy.width() * 0.9) / totalWidth;
      const newSpacing = spacing * scale;
      totalWidth = nodes.reduce((sum, d) => sum + d.width, 0) + (nodeCount - 1) * newSpacing;
      startX = centerX - totalWidth / 2;
    }

    let currentX = startX;
    nodes.forEach((d, i) => {
      d.node.position({ x: currentX + d.width / 2, y });
      // Store original Y for physics constraint
      d.node.data('timelineY', y);
      currentX += d.width + (i < nodeCount - 1 ? spacing : 0);
    });
  });

  cy.fit(null, 80);
  
  // 5. Run force-directed with differentiated edge weights
  setTimeout(() => {
    runPhysicsLayout();
  }, 100);
  
  showToast('Linha do tempo com física aplicada');
}

function runPhysicsLayout() {
  // Force-directed layout with differentiated edge weights
  // Edge weights: casamento=10 (forte atração), filiação=5, irmandade=2, outros=0.5
  
  // First, assign weights to edges based on type
  cy.edges().forEach(e => {
    const type = e.data('type');
    let weight = 1;
    if (type === 'casou_com') weight = 10;      // Casamento: atração muito forte
    else if (type === 'pai_de' || type === 'mae_de') weight = 5;  // Filiação: atração forte
    else if (type === 'irmao_de') weight = 2;   // Irmandade: atração média
    else weight = 0.5;                           // Outros: fraca
    e.data('physicsWeight', weight);
  });

  try {
    const layoutName = (typeof window.coseBilkent !== 'undefined') ? 'cose-bilkent' : 'cose';
    console.log(`Running ${layoutName} with physics weights`);
    
    cy.layout({
      name: layoutName,
      animate: true,
      animationDuration: 2000,
      fit: true,
      padding: 150,
      nodeDimensionsIncludeLabels: true,
      randomize: false,
      // Physics parameters
      idealEdgeLength: 180,
      nodeRepulsion: 15000,      // Repulsão forte entre nós não conectados
      nodeOverlap: 100,          // Penalidade máxima para sobreposição
      edgeElasticity: (edge) => {
        // Elasticidade inversa ao peso: casamentos mais rígidos
        const w = edge.data('physicsWeight') || 1;
        return 0.05 / w;  // Casamento (10) = 0.005 (muito rígido), filiação (5) = 0.01
      },
      nestingFactor: 0.05,
      gravity: 0.02,             // Gravidade muito baixa para manter timeline Y
      numIter: 6000,
      initialTemp: 3000,
      coolingFactor: 0.92,
      minTemp: 1,
      tile: false,
      // cose-bilkent specific
      gravityRange: 2.0,
      gravityCompound: 1.0,
      initialEnergyOnIncremental: 0.2
    }).run();
    
    showToast('Física aplicada: casamentos rígidos, filiação forte, repulsão entre núcleos');
  } catch (err) {
    console.warn(`${layoutName} failed:`, err);
    // Ultra-aggressive cose fallback
    cy.layout({
      name: 'cose',
      animate: true,
      animationDuration: 2500,
      fit: true,
      padding: 200,
      nodeDimensionsIncludeLabels: true,
      idealEdgeLength: 200,
      nodeRepulsion: 30000,
      nodeOverlap: 120,
      edgeElasticity: (edge) => {
        const w = edge.data('physicsWeight') || 1;
        return 0.05 / w;
      },
      nestingFactor: 0.05,
      gravity: 0.01,
      numIter: 8000,
      initialTemp: 4000,
      coolingFactor: 0.9,
      minTemp: 1
    }).run();
    showToast('Física aplicada (cose ultra)');
  }
}

// Keep the old function for 'force' button
function runCoseLayout(mode) {
  const isForce = mode === 'force';
  
  try {
    const layoutName = (typeof window.coseBilkent !== 'undefined') ? 'cose-bilkent' : 'cose';
    console.log(`Running ${layoutName} for ${mode} mode`);
    
    cy.layout({
      name: layoutName,
      animate: true,
      animationDuration: isForce ? 2000 : 1500,
      fit: true,
      padding: 150,
      nodeDimensionsIncludeLabels: true,
      randomize: isForce,
      idealEdgeLength: isForce ? 160 : 180,
      nodeRepulsion: isForce ? 12000 : 15000,
      nodeOverlap: 80,
      edgeElasticity: 0.2,
      nestingFactor: 0.05,
      gravity: isForce ? 0.1 : 0.05,
      numIter: isForce ? 5000 : 4000,
      initialTemp: 2500,
      coolingFactor: 0.93,
      minTemp: 1,
      tile: false
    }).run();
    
    showToast(`Layout ${isForce ? 'livre' : 'refinado'} aplicado (${layoutName})`);
  } catch (err) {
    console.warn(`${layoutName} failed:`, err);
    cy.layout({
      name: 'cose',
      animate: true,
      animationDuration: 2000,
      fit: true,
      padding: 200,
      nodeDimensionsIncludeLabels: true,
      idealEdgeLength: 180,
      nodeRepulsion: 25000,
      nodeOverlap: 100,
      edgeElasticity: 0.1,
      nestingFactor: 0.05,
      gravity: 0.05,
      numIter: 6000,
      initialTemp: 3500,
      coolingFactor: 0.92,
      minTemp: 1
    }).run();
    showToast('Layout aplicado (cose ultra)');
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