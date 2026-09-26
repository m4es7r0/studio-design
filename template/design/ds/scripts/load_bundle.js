// Loads the design-system bundle in Node with a stub window and returns the namespace object.
const fs = require('node:fs');
const path = require('node:path');

function loadNamespace(dsDir) {
  const ds = JSON.parse(fs.readFileSync(path.join(dsDir, 'project/design-system.json'), 'utf8'));
  const noop = () => {};
  global.window = global.window || {
    React: { createElement: noop, useState: () => [undefined, noop], useRef: () => ({}), useEffect: noop, useCallback: (f) => f, useMemo: (f) => f() },
  };
  const file = path.join(dsDir, 'project/components/bundle.js');
  delete require.cache[require.resolve(file)];
  require(file);
  const api = global.window[ds.namespace];
  if (!api || !api.format) throw new Error(`bundle did not register ${ds.namespace}.format`);
  return api;
}

module.exports = { loadNamespace };
