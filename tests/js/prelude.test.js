const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { REPO } = require('./helpers');

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const src = fs.readFileSync(path.join(REPO, 'template/design/figma/prelude.js'), 'utf8');
const load = (figma) => new AsyncFunction('figma', src + '\nreturn P;')(figma);

function fakeFigma() {
  const vars = [
    { id: 'V:1', name: 'primitive/ink', valuesByMode: { m: { r: 0.1, g: 0.1, b: 0.2, a: 1 } } },
    { id: 'V:2', name: 'text/ink', valuesByMode: { m: { type: 'VARIABLE_ALIAS', id: 'V:1' } } },
  ];
  const loaded = [];
  const figma = {
    variables: {
      getLocalVariablesAsync: async () => vars,
      getVariableByIdAsync: async (id) => vars.find((v) => v.id === id),
      setBoundVariableForPaint: (p, field, v) => ({ ...p, boundVariables: { [field]: { type: 'VARIABLE_ALIAS', id: v.id } } }),
    },
    getLocalTextStylesAsync: async () => [{ id: 'S:1', name: 'Text/body', fontName: { family: 'Inter', style: 'Regular' } }],
    getLocalEffectStylesAsync: async () => [{ id: 'E:1', name: 'shadow/m' }],
    loadFontAsync: async (f) => { loaded.push(f.family + ' ' + f.style); },
    createText: () => ({ async setTextStyleIdAsync(id) { this.textStyleId = id; } }),
  };
  return { figma, loaded };
}

test('paint resolves an alias chain and binds the named variable', async () => {
  const P = await load(fakeFigma().figma);
  const [p] = await P.paint('text/ink');
  assert.deepEqual(p.color, { r: 0.1, g: 0.1, b: 0.2 });
  assert.equal(p.boundVariables.color.id, 'V:2');
});

test('unknown names fail loudly', async () => {
  const P = await load(fakeFigma().figma);
  await assert.rejects(P.paint('text/missing'), /No variable named text\/missing/);
  assert.throws(() => P.textStyle('Nope'), /No text style named Nope/);
  assert.throws(() => P.effectStyle('shadow/xl'), /No effect style named shadow\/xl/);
});

test('txt applies style, colour and name; text style fonts are loaded up front', async () => {
  const { figma, loaded } = fakeFigma();
  const P = await load(figma);
  const t = await P.txt('Привет', 'Text/body', 'text/ink', 'label');
  assert.equal(t.textStyleId, 'S:1');
  assert.equal(t.characters, 'Привет');
  assert.equal(t.name, 'label');
  assert.equal(t.fills[0].boundVariables.color.id, 'V:2');
  assert.deepEqual(loaded, ['Inter Regular']);
});
