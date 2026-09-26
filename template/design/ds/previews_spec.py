"""Preview specs for scripts/gen_previews.py.

PREVIEWS maps a component name to (dsCard attributes, grid CSS, extra CSS, JS body).
The JS body runs with M (the namespace object), h (React.createElement) and cell(label, node),
and renders into #root, for example:
  ReactDOM.createRoot(document.getElementById('root')).render(h('div', { className: 'grid' }, ...));
ROOT_CLASS is the design system's root class, set at stage 4."""
ROOT_CLASS = ''
PREVIEWS = {}
