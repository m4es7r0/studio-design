/* Sweep: loads every harness page in a 1920 px iframe and reports JS errors, real overflows and
   empty roots. Open harness/_sweep.html and read #result; its first line is «SWEEP OK: …» or
   «SWEEP FAIL: …». Wrap an intentional overhang in [data-sweep-ignore]. */
(function () {
  var TOL = 4;

  function isRealOverflow(m) {
    if (m.ignored || m.absoluteOnly) return false;
    if (!(m.scrollWidth > m.clientWidth + TOL)) return false;
    if (m.textOverflow === 'ellipsis') return false;
    if (m.overflowX === 'auto' || m.overflowX === 'scroll') return false;
    if (m.display === 'inline') return false;
    return true;
  }

  // True when every in-flow right edge stays within the box, so the overhang comes only from
  // absolute or fixed descendants or pseudo-elements.
  function inFlowFits(rights, boxRight) {
    for (var i = 0; i < rights.length; i++) if (rights[i] > boxRight + TOL) return false;
    return true;
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { isRealOverflow: isRealOverflow, inFlowFits: inFlowFits, TOL: TOL };
    return;
  }

  // Collects the right edges of e's in-flow descendants: skips absolute and fixed subtrees,
  // descends only through overflow-x: visible boxes, and measures text nodes with a Range.
  function inFlowRights(e, w, out) {
    for (var n = e.firstChild; n; n = n.nextSibling) {
      if (n.nodeType === 1) {
        var cs = w.getComputedStyle(n);
        if (cs.position === 'absolute' || cs.position === 'fixed') continue;
        out.push(n.getBoundingClientRect().right);
        if (cs.overflowX === 'visible') inFlowRights(n, w, out);
      } else if (n.nodeType === 3 && /\S/.test(n.nodeValue)) {
        var range = e.ownerDocument.createRange();
        range.selectNodeContents(n);
        var rects = range.getClientRects();
        for (var k = 0; k < rects.length; k++) out.push(rects[k].right);
      }
    }
    return out;
  }

  function label(e) {
    var c = typeof e.className === 'string' && e.className ? e.className.split(' ')[0] : e.tagName.toLowerCase();
    return c + ': ' + (e.textContent || '').trim().slice(0, 40) + ' (' + (e.scrollWidth - e.clientWidth) + 'px)';
  }

  function checkPage(name) {
    return new Promise(function (resolve) {
      var f = document.createElement('iframe');
      f.style.cssText = 'position:fixed;left:0;top:0;width:1920px;height:1200px;opacity:0;pointer-events:none';
      var done = false;
      function finish() {
        if (done) return;
        done = true;
        setTimeout(function () {
          var r = { page: name, errors: [], overflows: [], empty: false };
          try {
            var d = f.contentDocument, w = f.contentWindow;
            r.errors = (w.__errs || []).slice();
            var root = d.getElementById('root');
            r.empty = !!root && root.children.length === 0;
            var els = d.querySelectorAll('body *');
            for (var i = 0; i < els.length; i++) {
              var e = els[i], cs = w.getComputedStyle(e);
              var m = { scrollWidth: e.scrollWidth, clientWidth: e.clientWidth, textOverflow: cs.textOverflow, overflowX: cs.overflowX, display: cs.display, ignored: !!e.closest('[data-sweep-ignore]'), absoluteOnly: false };
              if (isRealOverflow(m)) {
                m.absoluteOnly = inFlowFits(inFlowRights(e, w, []), e.getBoundingClientRect().right);
                if (isRealOverflow(m)) r.overflows.push(label(e));
              }
            }
          } catch (err) {
            r.errors.push('sweep: ' + err.message);
          }
          f.remove();
          resolve(r);
        }, 700);
      }
      f.onload = finish;
      setTimeout(finish, 6000);
      f.src = name + '.html?sweep=' + Date.now();
      document.body.appendChild(f);
    });
  }

  async function run() {
    var pages = window.SWEEP_PAGES || [], results = [];
    for (var i = 0; i < pages.length; i++) results.push(await checkPage(pages[i]));
    var bad = results.filter(function (r) { return r.errors.length || r.overflows.length || r.empty; });
    var errs = results.reduce(function (a, r) { return a + r.errors.length; }, 0);
    var over = results.reduce(function (a, r) { return a + r.overflows.length; }, 0);
    var empty = results.filter(function (r) { return r.empty; }).length;
    var head = (bad.length ? 'SWEEP FAIL: ' : 'SWEEP OK: ') + pages.length + ' pages, ' + errs + ' errors, ' + over + ' overflows, ' + empty + ' empty';
    document.getElementById('result').textContent = head + '\n' + JSON.stringify(bad, null, 2);
    document.title = head;
  }

  run();
})();
