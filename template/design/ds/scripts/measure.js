/* Measure: loads one harness page in an iframe of exactly w×h and reports every [data-zone]
   element's rect relative to the iframe viewport. Open harness/_measure.html?page=<Name>&w=<px>&h=<px>,
   wait until the title starts with «MEASURE», then read #result: the first line is
   «MEASURE OK: <Name> at <w>×<h>, <N> zones» or «MEASURE FAIL: <Name> at <w>×<h>: <reason>»,
   then the zones as JSON (numbers rounded to 0.1 px). */
(function () {
  var TOL = 0.5;

  // A zone fits when its rect stays inside the w×h viewport (half a pixel of rounding allowed).
  function zoneVerdict(zones, w, h) {
    var outside = [];
    for (var i = 0; i < zones.length; i++) {
      var z = zones[i];
      if (!(z.left >= -TOL && z.top >= -TOL && z.right <= w + TOL && z.bottom <= h + TOL)) outside.push(z.name);
    }
    return { ok: zones.length > 0 && outside.length === 0, outside: outside };
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { zoneVerdict: zoneVerdict };
    return;
  }

  function round(x) { return Math.round(x * 10) / 10; }

  function report(head, zones) {
    var body = zones ? '[\n' + zones.map(function (z) { return '  ' + JSON.stringify(z); }).join(',\n') + '\n]' : '';
    document.getElementById('result').textContent = head + (body ? '\n' + body : '');
    document.title = head;
  }

  function run() {
    var q = new URLSearchParams(location.search);
    var name = q.get('page'), w = parseInt(q.get('w'), 10), h = parseInt(q.get('h'), 10);
    if (!name || !(w > 0) || !(h > 0)) {
      report('MEASURE FAIL: use _measure.html?page=<Name>&w=<px>&h=<px>');
      return;
    }
    var at = name + ' at ' + w + '×' + h;
    var f = document.createElement('iframe');
    f.style.cssText = 'display:block;border:0;margin:0;padding:0;width:' + w + 'px;height:' + h + 'px';
    var loaded = false, done = false;
    function measure() {
      if (done) return;
      done = true;
      setTimeout(function () {
        try {
          var d = f.contentDocument;
          if (!loaded || d.readyState !== 'complete') { report('MEASURE FAIL: ' + at + ': page did not finish loading'); return; }
          var els = d.querySelectorAll('[data-zone]'), zones = [];
          for (var i = 0; i < els.length; i++) {
            var r = els[i].getBoundingClientRect();
            zones.push({ name: els[i].getAttribute('data-zone'), left: round(r.left), top: round(r.top), width: round(r.width),
                         height: round(r.height), right: round(r.right), bottom: round(r.bottom) });
          }
          if (!zones.length) { report('MEASURE FAIL: ' + at + ': no [data-zone] elements'); return; }
          var v = zoneVerdict(zones, w, h);
          report(v.ok ? 'MEASURE OK: ' + at + ', ' + zones.length + ' zones' : 'MEASURE FAIL: ' + at + ': ' + v.outside.join(', '), zones);
        } catch (err) {
          report('MEASURE FAIL: ' + at + ': ' + err.message);
        }
      }, 700);
    }
    f.onload = function () { loaded = true; measure(); };
    setTimeout(measure, 6000);
    f.src = name + '.html?measure=' + Date.now();
    document.body.appendChild(f);
  }

  run();
})();
