// Shared prelude for use_figma scripts in a studio-design project. Paste it before the task code.
// It finds variables and styles by name, so it carries no IDs. Naming conventions (stage 7):
// colour variables «<group>/<token>» (e.g. «text/ink»), text styles «<Group>/<name>»,
// effect styles «shadow/<size>». Components are passed by ID from design/figma/figma-state.json.
const PRELUDE_CONFIG = { titleStyle: 'Display/title', bodyStyle: 'Text/body', titleColor: 'text/ink', bodyColor: 'text/ink-2' };
const P = await (async () => {
  const vars = await figma.variables.getLocalVariablesAsync();
  const byName = new Map(vars.map((v) => [v.name, v]));
  const colours = {};
  async function resolve(v) {
    let val = Object.values(v.valuesByMode)[0];
    while (val && val.type === 'VARIABLE_ALIAS') {
      const a = await figma.variables.getVariableByIdAsync(val.id);
      val = Object.values(a.valuesByMode)[0];
    }
    return val;
  }
  function variable(name) {
    const v = byName.get(name);
    if (!v) throw new Error('No variable named ' + name);
    return v;
  }
  async function paint(name) {
    const v = variable(name);
    if (!colours[name]) { const c = await resolve(v); colours[name] = { r: c.r, g: c.g, b: c.b }; }
    return [figma.variables.setBoundVariableForPaint({ type: 'SOLID', color: colours[name] }, 'color', v)];
  }
  const textStyles = await figma.getLocalTextStylesAsync();
  const effectStyles = await figma.getLocalEffectStylesAsync();
  const fonts = new Map(textStyles.map((s) => [s.fontName.family + '|' + s.fontName.style, s.fontName]));
  await Promise.all([...fonts.values()].map((f) => figma.loadFontAsync(f)));
  function textStyle(name) {
    const s = textStyles.find((x) => x.name === name);
    if (!s) throw new Error('No text style named ' + name);
    return s;
  }
  function effectStyle(name) {
    const s = effectStyles.find((x) => x.name === name);
    if (!s) throw new Error('No effect style named ' + name);
    return s;
  }
  async function txt(chars, style, colour, name) {
    const t = figma.createText();
    await t.setTextStyleIdAsync(textStyle(style).id);
    t.characters = chars;
    t.fills = await paint(colour);
    if (name) t.name = name;
    return t;
  }
  async function doc(page, title, body, width = 1000) {
    const d = figma.createAutoLayout('VERTICAL', { name: 'Doc', itemSpacing: 12 });
    d.fills = [];
    page.appendChild(d);
    d.appendChild(await txt(title, PRELUDE_CONFIG.titleStyle, PRELUDE_CONFIG.titleColor));
    const b = await txt(body, PRELUDE_CONFIG.bodyStyle, PRELUDE_CONFIG.bodyColor);
    d.appendChild(b);
    b.layoutSizingHorizontal = 'FIXED';
    b.resize(width, b.height);
    b.textAutoResize = 'HEIGHT';
    return d;
  }
  return { variable, resolve, paint, textStyle, effectStyle, txt, doc };
})();
