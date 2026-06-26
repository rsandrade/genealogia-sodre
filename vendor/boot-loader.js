// Boot loader: carrega d3 e f3 dinamicamente com validação, depois chama startKnowledgeGraph()
(function bootKnowledgeGraph() {
  'use strict';

  const D3_SRC = 'vendor/d3.v7.min.js';
  const F3_SRC = 'vendor/family-chart.min.js';

  window.addEventListener('error', function (e) {
    console.error('[KG] Erro global:', { message: e.message, filename: e.filename, lineno: e.lineno, colno: e.colno, error: e.error });
  });

  window.addEventListener('unhandledrejection', function (e) {
    console.error('[KG] Promise rejeitada:', e.reason);
  });

  function hasD3() { return !!(window.d3 && typeof window.d3.select === 'function'); }
  function hasF3() { return !!(window.f3 && typeof window.f3.createChart === 'function'); }

  function loadScript(src, label, test) {
    return new Promise(function (resolve, reject) {
      if (test()) { console.log('[KG]', label, 'já disponível'); resolve(); return; }
      var s = document.createElement('script');
      s.src = src; s.async = false;
      s.onload = function () {
        if (test()) { console.log('[KG]', label, 'carregado:', src); resolve(); }
        else { reject(new Error(label + ' carregou, mas o global esperado não apareceu: ' + src)); }
      };
      s.onerror = function () { reject(new Error('Falha ao carregar ' + label + ': ' + src)); };
      document.head.appendChild(s);
    });
  }

  function domReady() {
    if (document.readyState !== 'loading') return Promise.resolve();
    return new Promise(function (resolve) { document.addEventListener('DOMContentLoaded', resolve, { once: true }); });
  }

  function waitForFn(name, timeout) {
    if (typeof window[name] === 'function') return Promise.resolve();
    return new Promise(function (resolve, reject) {
      var start = Date.now();
      (function poll() {
        if (typeof window[name] === 'function') { resolve(); return; }
        if (Date.now() - start > timeout) { reject(new Error(name + ' não apareceu em ' + timeout + 'ms')); return; }
        setTimeout(poll, 50);
      })();
    });
  }

  function showBootError(err) {
    console.error('[KG] Falha ao iniciar gráfico:', err);
    var container = document.getElementById('FamilyChart');
    if (container) {
      container.innerHTML = '<div style="padding:24px;color:#7a1f1f;background:#fff3f3;border:1px solid #d99;font-family:monospace;white-space:pre-wrap;">Falha ao iniciar o gráfico.\n\n' + String(err && err.stack ? err.stack : err) + '</div>';
    }
  }

  Promise.resolve()
    .then(function () { return loadScript(D3_SRC, 'D3', hasD3); })
    .then(function () { return loadScript(F3_SRC, 'family-chart/f3', hasF3); })
    .then(domReady)
    .then(function () { return waitForFn('startKnowledgeGraph', 5000); })
    .then(function () {
      if (typeof startKnowledgeGraph !== 'function') { throw new Error('startKnowledgeGraph não foi definida.'); }
      console.log('[KG] Bibliotecas prontas:', { d3: !!(window.d3), f3: !!(window.f3), createChart: !!(window.f3 && window.f3.createChart) });
      startKnowledgeGraph();
    })
    .catch(showBootError);
})();
