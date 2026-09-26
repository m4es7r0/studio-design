// Figma page audit. Paste into use_figma, then: return await auditPage('<pageId>');
// Read-only. Outside instances it checks: unbound SOLID paints, text without a text style, default
// layer names, visible text clipped by a clipping ancestor. Per component set or standalone component:
// overlapping variants, layers whose property references differ between variants, component
// properties no layer references.
const DEFAULT_NAME = /^(Frame|Rectangle|Text|Component|Group|Ellipse|Vector|Instance|Line|Polygon|Star|Section)( \d+)?$/;

function walk(node, visit, insideInstance = false) {
  visit(node, insideInstance);
  if (node.children) for (const c of node.children) walk(c, visit, insideInstance || node.type === 'INSTANCE');
}
function box(node) { return node.absoluteBoundingBox || { x: node.x, y: node.y, width: node.width, height: node.height }; }
function overlap(a, b) { return a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height; }
function clippingAncestor(node) {
  let p = node.parent;
  while (p && p.type !== 'PAGE' && p.type !== 'DOCUMENT') { if (p.clipsContent === true) return p; p = p.parent; }
  return null;
}
function hidden(node) {
  for (let x = node; x && x.type !== 'PAGE' && x.type !== 'DOCUMENT'; x = x.parent) if (x.visible === false) return true;
  return false;
}
// A mixed text style is unstyled only if some range has no text style.
function unstyled(text, MIXED) {
  if (text.textStyleId === MIXED) return text.getStyledTextSegments(['textStyleId']).some((s) => !s.textStyleId);
  return !text.textStyleId;
}
function layerPath(node, root) {
  const parts = [];
  for (let x = node; x && x !== root; x = x.parent) {
    const same = x.parent && x.parent.children ? x.parent.children.filter((c) => c.name === x.name) : [x];
    const i = same.indexOf(x);
    parts.unshift(i > 0 ? x.name + '#' + i : x.name);
  }
  return parts.join(' / ');
}
function refsKey(node) {
  const r = node.componentPropertyReferences || {};
  return Object.keys(r).sort().map((k) => k + '=' + r[k]).join(',');
}
function propUsage(owner, variants, out) {
  const defs = owner.componentPropertyDefinitions || {};
  const used = new Set();
  for (const v of variants) walk(v, (x, inInst) => {
    if (inInst) return;
    const r = x.componentPropertyReferences;
    if (r) for (const k of Object.values(r)) used.add(k);
  });
  for (const [k, d] of Object.entries(defs)) if (d.type !== 'VARIANT' && !used.has(k)) out.unusedProps.push(owner.name + ': ' + k);
}
function setChecks(set, out) {
  const vs = set.children.filter((c) => c.type === 'COMPONENT');
  const rel = (v) => ({ x: v.x, y: v.y, width: v.width, height: v.height });
  for (let i = 0; i < vs.length; i++) for (let j = i + 1; j < vs.length; j++) {
    if (overlap(rel(vs[i]), rel(vs[j]))) out.overlappingVariants.push(set.name + ': ' + vs[i].name + ' × ' + vs[j].name);
  }
  const seen = new Map();
  for (const v of vs) walk(v, (x, inInst) => {
    if (inInst || x === v) return;
    const p = layerPath(x, v) + ' [' + x.type + ']';
    const k = refsKey(x);
    if (!seen.has(p)) seen.set(p, { k, v: v.name });
    else if (seen.get(p).k !== k) out.refMismatch.push(set.name + ' › ' + p + ': ' + seen.get(p).v + ' {' + seen.get(p).k + '} vs ' + v.name + ' {' + k + '}');
  });
  propUsage(set, vs, out);
}
function auditNodes(roots, MIXED) {
  const out = { unboundPaints: [], unstyledText: [], defaultNames: [], overlappingVariants: [], refMismatch: [], unusedProps: [], clippedText: [] };
  for (const root of roots) walk(root, (x, inInst) => {
    if (inInst) return;
    const id = x.id + ' ' + x.name;
    if (DEFAULT_NAME.test(x.name)) out.defaultNames.push(id);
    for (const prop of ['fills', 'strokes']) {
      const ps = x[prop];
      if (!Array.isArray(ps)) continue;
      for (const p of ps) if (p.type === 'SOLID' && p.visible !== false && !(p.boundVariables && p.boundVariables.color)) out.unboundPaints.push(id + ' ' + prop);
    }
    if (x.type === 'TEXT') {
      if (unstyled(x, MIXED)) out.unstyledText.push(id);
      const clip = hidden(x) ? null : clippingAncestor(x);
      if (clip) {
        const a = box(x), b = box(clip);
        if (a.x < b.x - 0.5 || a.y < b.y - 0.5 || a.x + a.width > b.x + b.width + 0.5 || a.y + a.height > b.y + b.height + 0.5) out.clippedText.push(id + ' in ' + clip.name);
      }
    }
    if (x.type === 'COMPONENT_SET') setChecks(x, out);
    else if (x.type === 'COMPONENT' && (!x.parent || x.parent.type !== 'COMPONENT_SET')) propUsage(x, [x], out);
  });
  return out;
}
async function auditPage(pageId) {
  const page = figma.root.children.find((p) => p.id === pageId);
  if (!page) throw new Error('No page ' + pageId);
  await figma.setCurrentPageAsync(page);
  const r = auditNodes(page.children, figma.mixed);
  const counts = Object.fromEntries(Object.entries(r).map(([k, v]) => [k, v.length]));
  const total = Object.values(counts).reduce((a, b) => a + b, 0);
  return { page: page.name, ok: total === 0, counts, samples: Object.fromEntries(Object.entries(r).map(([k, v]) => [k, v.slice(0, 8)])) };
}
if (typeof module !== 'undefined' && module.exports) module.exports = { auditNodes, DEFAULT_NAME };
