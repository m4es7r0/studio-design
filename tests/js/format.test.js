// tests/js/format.test.js
const test = require('node:test');
const assert = require('node:assert/strict');
const { execFileSync, spawnSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const { makeClient } = require('./helpers');

test('template number rules pass their 25 cases', () => {
  const c = makeClient();
  const r = spawnSync('node', [path.join(c, 'design/ds/scripts/check_format.js')], { encoding: 'utf8' });
  assert.equal(r.status, 0, r.stdout + r.stderr);
  assert.match(r.stdout, /all 25 cases pass/);
});

test('fixtures render through the format functions', () => {
  const c = makeClient();
  execFileSync('node', [path.join(c, 'design/ds/scripts/format_fixtures.js')]);
  const out = JSON.parse(fs.readFileSync(path.join(c, 'design/ds/fixtures/formatted.json'), 'utf8'));
  // U+202F groups thousands, U+00A0 joins the unit.
  assert.deepEqual(out.examples.price, { name: 'Цена', value: '1\u202F290\u00A0₽', delta: null });
  assert.equal(out.examples.weight.value, '200\u00A0г');
  assert.equal(out.examples.orders.value, '12\u202F500\u00A0шт.');
  assert.equal(out.examples.orders.delta, '+800\u00A0шт.');
});
