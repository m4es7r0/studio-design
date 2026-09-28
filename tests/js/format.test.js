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
  assert.deepEqual(out.examples.revenue, { name: 'Выручка', value: '462 млрд ₽', delta: '−18 млрд ₽' });
  assert.equal(out.examples.users.value, '1 250 000 чел.');
  assert.equal(out.examples.users.delta, '+41 000 чел.');
  assert.equal(out.examples.conversion.value, '4,5 %');
  assert.equal(out.examples.conversion.delta, '+0,7 п.п.');
});
