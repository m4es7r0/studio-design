const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { REPO } = require('./helpers');
const { isRealOverflow, inFlowFits, summarize, TOL } = require(path.join(REPO, 'template/design/ds/scripts/sweep.js'));

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

test('an overhang with no in-flow content past the box (pseudo-element only) is absolute-only', () => {
  assert.equal(inFlowFits([], 100), true);
});

test('nested in-flow content within the tolerance fits', () => {
  assert.equal(inFlowFits([90, 100 + TOL], 100), true);
});

test('overflowing in-flow text next to an absolute badge does not fit', () => {
  assert.equal(inFlowFits([100, 158], 100), false);
});

const clean = (page) => ({ page, errors: [], overflows: [], empty: false });

test('a sweep over zero pages fails', () => {
  assert.equal(summarize([], 0), 'SWEEP FAIL: 0 pages');
});

test('one clean page passes', () => {
  assert.equal(summarize([clean('Button')], 1), 'SWEEP OK: 1 pages, 0 errors, 0 overflows, 0 empty');
});

test('a page with an error fails', () => {
  const results = [clean('Button'), { ...clean('Card'), errors: ['sweep: HTTP 404'] }];
  assert.equal(summarize(results, 2), 'SWEEP FAIL: 2 pages, 1 errors, 0 overflows, 0 empty');
});
