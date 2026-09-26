const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { REPO } = require('./helpers');
const { isRealOverflow, TOL } = require(path.join(REPO, 'template/design/ds/scripts/sweep.js'));

const base = { scrollWidth: 120, clientWidth: 100, textOverflow: 'clip', overflowX: 'visible', display: 'block' };

test('overflow within the tolerance is not real', () => {
  assert.equal(isRealOverflow({ ...base, scrollWidth: 100 + TOL }), false);
});

test('overflow past the tolerance is real', () => {
  assert.equal(isRealOverflow(base), true);
});

test('ellipsis, scroll containers, inline boxes, ignored and absolute-only overhangs are not real', () => {
  for (const extra of [{ textOverflow: 'ellipsis' }, { overflowX: 'auto' }, { overflowX: 'scroll' }, { display: 'inline' }, { ignored: true }, { absoluteOnly: true }]) {
    assert.equal(isRealOverflow({ ...base, ...extra }), false, JSON.stringify(extra));
  }
});
