// Renders ds/fixtures/sample.json through <namespace>.format into ds/fixtures/formatted.json.
// sample.json: { "<set>": [{ "id", "name", "type", "value", "delta"?, "unit"? }] }
const fs = require('node:fs');
const path = require('node:path');
const { loadNamespace } = require('./load_bundle');

const ds = path.resolve(__dirname, '..');
const f = loadNamespace(ds).format;
const sample = JSON.parse(fs.readFileSync(path.join(ds, 'fixtures/sample.json'), 'utf8'));
const out = {};
let n = 0;
for (const [set, items] of Object.entries(sample)) {
  out[set] = {};
  for (const it of items) {
    out[set][it.id] = {
      name: it.name,
      value: f.value(it.value, it.type, it.unit),
      delta: it.delta === undefined ? null : f.delta(it.delta, it.type, it.unit),
    };
    n++;
  }
}
fs.writeFileSync(path.join(ds, 'fixtures/formatted.json'), JSON.stringify(out, null, 2) + '\n');
console.log(`formatted ${n} items into fixtures/formatted.json`);
