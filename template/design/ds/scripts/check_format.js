// Checks <namespace>.format against ds/fixtures/format-cases.json. Run: node ds/scripts/check_format.js
const fs = require('node:fs');
const path = require('node:path');
const { loadNamespace } = require('./load_bundle');

const ds = path.resolve(__dirname, '..');
const f = loadNamespace(ds).format;
const show = (x) => x.replace(/ /g, '⍽').replace(/ /g, '·');
const cases = JSON.parse(fs.readFileSync(path.join(ds, 'fixtures/format-cases.json'), 'utf8'));
let failed = 0;
for (const c of cases) {
  const got = show(f[c.fn](...c.args));
  if (got !== c.want) { failed++; console.log('FAIL', c.fn, JSON.stringify(c.args), got, 'want', c.want); }
}
console.log(failed ? `${failed} of ${cases.length} failed` : `all ${cases.length} cases pass`);
process.exit(failed ? 1 : 0);
