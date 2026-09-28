"""Preview specs for scripts/gen_previews.py.

PREVIEWS maps a component name to (dsCard attributes, grid CSS, extra CSS, JS body).
The JS body runs after the fonts load, with M (the namespace object), h (React.createElement),
cell(label, node) and window.FIXTURES ({"copy": fixtures/copy.json, "formatted": fixtures/formatted.json},
read when the previews are generated), and renders into #root, for example:
  ReactDOM.createRoot(document.getElementById('root')).render(h('div', { className: 'grid' }, ...));
A card with the `page` token in its attributes gets no body padding.
ROOT_CLASS is the design system's root class, set at stage 4.
FONT_LINKS: Google Fonts CSS URLs, linked in every preview's head.
FONT_LOADS: CSS font shorthands such as '400 18px "Face"'; the JS body waits for them."""
ROOT_CLASS = ''
FONT_LINKS = []
FONT_LOADS = []
PREVIEWS = {}
