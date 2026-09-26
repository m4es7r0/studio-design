/* @ds-bundle: {"format":4,"namespace":"__NAMESPACE__","components":[]} */
(function () {
  'use strict';

  function assign(target) {
    for (var i = 1; i < arguments.length; i++) {
      var src = arguments[i];
      if (src) for (var k in src) if (Object.prototype.hasOwnProperty.call(src, k)) target[k] = src[k];
    }
    return target;
  }

  /* ---------------- number formatting, ru-RU (README «Numbers») ---------------- */
  var NNBSP = '\u202F', NBSP = '\u00A0', MINUS = '\u2212';
  var SCALES = [[1e12, 'трлн'], [1e9, 'млрд'], [1e6, 'млн']];

  function group(n) {
    return String(Math.round(Math.abs(n))).replace(/\B(?=(\d{3})+(?!\d))/g, NNBSP);
  }
  function comma(x, digits) { return x.toFixed(digits).replace('.', ','); }
  function signOf(v) { return v < 0 ? MINUS : ''; }
  function scaled(a, scaleName) {
    var idx = -1, i;
    if (scaleName) { for (i = 0; i < SCALES.length; i++) if (SCALES[i][1] === scaleName) idx = i; }
    else { for (i = 0; i < SCALES.length; i++) if (a >= SCALES[i][0]) { idx = i; break; } }
    if (idx < 0) return null;
    var x = a / SCALES[idx][0];
    var d = x >= 100 ? 0 : x >= 10 ? 1 : 2;
    var r = Math.round(x * Math.pow(10, d)) / Math.pow(10, d);
    if (!scaleName && r >= 1000 && idx > 0) { idx -= 1; r = Math.round(a / SCALES[idx][0] * 100) / 100; d = 2; }
    var txt = comma(r, d);
    if (!scaleName) txt = txt.replace(/(,\d*?)0+$/, '$1').replace(/,$/, '');
    return txt + NBSP + SCALES[idx][1];
  }
  var format = {
    group: group,
    /** 75 000 ₽ · 1,23 млрд ₽ · 12,3 трлн ₽. opts.scale forces 'млн' | 'млрд' | 'трлн' so a pair reads in one unit. */
    money: function (v, opts) {
      var a = Math.abs(v), s = opts && opts.scale;
      var body = (s || a >= 1e6) ? scaled(a, s) : group(a);
      return signOf(v) + body + NBSP + '₽';
    },
    people: function (v) { return signOf(v) + group(v) + NBSP + 'чел.'; },
    percent: function (v) {
      var a = Math.abs(v);
      var body = (a < 10 && a % 1 !== 0) ? comma(a, 1) : group(a);
      return signOf(v) + body + NBSP + '%';
    },
    coef: function (v) { return signOf(v) + comma(Math.abs(v), 2); },
    area: function (v) {
      var a = Math.abs(v);
      return signOf(v) + (a >= 1e6 ? scaled(a) : group(a)) + NBSP + 'кв.' + NBSP + 'м';
    },
    count: function (v, unit) { return signOf(v) + group(v) + NBSP + (unit || 'ед.'); },
    pp: function (v) {
      var a = Math.abs(v);
      var body = a % 1 !== 0 ? comma(a, 1) : String(a);
      return (v > 0 ? '+' : v < 0 ? MINUS : '') + body + NBSP + 'п.п.';
    },
    /** A signed delta. type: money | people | percent (→ п.п.) | coef | area | count | pp. */
    delta: function (v, type, unit) {
      if (v === null || v === undefined) return '—';
      if (v === 0) return '0';
      if (type === 'percent' || type === 'pp') return format.pp(v);
      var plus = v > 0 ? '+' : '';
      var f = format[type] || format.count;
      return plus + f(v, unit);
    },
    value: function (v, type, unit) {
      if (v === null || v === undefined) return '—';
      var f = format[type] || format.count;
      return f(v, unit);
    }
  };

  var api = { format: format };
  window.__NAMESPACE__ = assign(window.__NAMESPACE__ || {}, api);
})();
