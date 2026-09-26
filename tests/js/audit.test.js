const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { REPO } = require('./helpers');
const { auditNodes } = require(path.join(REPO, 'template/design/figma/audit.js'));

const MIXED = Symbol('mixed');
let seq = 0;
function n(type, name, props = {}, children) {
  const node = { id: 'N' + ++seq, type, name, ...props };
  if (children) { node.children = children; for (const c of children) c.parent = node; }
  return node;
}
const SOLID = (bound) => ({ type: 'SOLID', visible: true, color: { r: 0, g: 0, b: 0 }, ...(bound ? { boundVariables: { color: { id: 'V:1' } } } : {}) });
const empty = (r) => Object.entries(r).filter(([, v]) => v.length).map(([k]) => k);
function variant(name, x, refs) {
  return n('COMPONENT', name, { x, y: 0, width: 100, height: 40 }, [n('TEXT', 'value', { textStyleId: 'S:1', componentPropertyReferences: refs })]);
}

test('a clean page has no findings', () => {
  const page = n('PAGE', 'Clean', {}, [n('FRAME', 'Card', { fills: [SOLID(true)] }, [n('TEXT', 'title', { textStyleId: 'S:1', fills: [SOLID(true)] })])]);
  assert.deepEqual(empty(auditNodes(page.children, MIXED)), []);
});

test('unbound paints, unstyled text and default names are found outside instances only', () => {
  const inst = n('INSTANCE', 'Button', {}, [n('RECTANGLE', 'Rectangle 3', { fills: [SOLID(false)] })]);
  const page = n('PAGE', 'P', {}, [n('FRAME', 'Frame 12', { fills: [SOLID(false)] }, [n('TEXT', 'label', { textStyleId: '' }), n('TEXT', 'mixed', { textStyleId: MIXED }), inst])]);
  const r = auditNodes(page.children, MIXED);
  assert.equal(r.unboundPaints.length, 1);
  assert.equal(r.unstyledText.length, 2);
  assert.deepEqual(r.defaultNames.map((s) => s.split(' ').slice(1).join(' ')), ['Frame 12']);
});

test('overlapping variants are found', () => {
  const set = n('COMPONENT_SET', 'Chip', { componentPropertyDefinitions: { 'Value#1': { type: 'TEXT' }, Tone: { type: 'VARIANT' } } },
    [variant('Tone=A', 0, { characters: 'Value#1' }), variant('Tone=B', 50, { characters: 'Value#1' })]);
  const r = auditNodes([set], MIXED);
  assert.deepEqual(r.overlappingVariants, ['Chip: Tone=A × Tone=B']);
  assert.deepEqual(empty(r), ['overlappingVariants']);
});

test('a variant that lost its property reference is found', () => {
  const set = n('COMPONENT_SET', 'Chip', { componentPropertyDefinitions: { 'Value#1': { type: 'TEXT' }, Tone: { type: 'VARIANT' } } },
    [variant('Tone=A', 0, { characters: 'Value#1' }), variant('Tone=B', 200, {})]);
  const r = auditNodes([set], MIXED);
  assert.equal(r.refMismatch.length, 1);
  assert.match(r.refMismatch[0], /^Chip › value \[TEXT\]: Tone=A \{characters=Value#1\} vs Tone=B \{\}$/);
});

test('a property no layer references is found', () => {
  const set = n('COMPONENT_SET', 'Chip', { componentPropertyDefinitions: { 'Value#1': { type: 'TEXT' }, 'Show value#2': { type: 'BOOLEAN' }, Tone: { type: 'VARIANT' } } },
    [variant('Tone=A', 0, { characters: 'Value#1' }), variant('Tone=B', 200, { characters: 'Value#1' })]);
  assert.deepEqual(auditNodes([set], MIXED).unusedProps, ['Chip: Show value#2']);
});

test('text clipped by a clipping ancestor is found', () => {
  const text = n('TEXT', '10', { textStyleId: 'S:1', absoluteBoundingBox: { x: 213, y: 0, width: 22, height: 24 } });
  const ticks = n('FRAME', 'ticks', { clipsContent: true, absoluteBoundingBox: { x: 0, y: 0, width: 232, height: 24 } }, [text]);
  const chart = n('FRAME', 'RoundChart', { absoluteBoundingBox: { x: 0, y: 0, width: 270, height: 158 } }, [ticks]);
  assert.deepEqual(auditNodes([chart], MIXED).clippedText, [text.id + ' 10 in ticks']);
});
