const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { REPO } = require('./helpers');
const { zoneVerdict } = require(path.join(REPO, 'template/design/ds/scripts/measure.js'));

function zone(name, left, top, width, height) {
  return { name, left, top, width, height, right: left + width, bottom: top + height };
}

test('zones inside the viewport fit, sub-pixel edges included', () => {
  const zones = [zone('rail', -0.4, 0, 460, 1080.4), zone('map', 460, 0, 1460.4, 1080)];
  assert.deepEqual(zoneVerdict(zones, 1920, 1080), { ok: true, outside: [] });
});

test('a zone past the right edge does not fit', () => {
  const zones = [zone('rail', 0, 0, 460, 1080), zone('feed', 1500, 0, 421, 600)];
  assert.deepEqual(zoneVerdict(zones, 1920, 1080), { ok: false, outside: ['feed'] });
});

test('a zone past the bottom edge does not fit', () => {
  const zones = [zone('header', 0, 0, 1920, 80), zone('table', 0, 80, 1920, 1001)];
  assert.deepEqual(zoneVerdict(zones, 1920, 1080), { ok: false, outside: ['table'] });
});

test('a zone past the left or top edge does not fit', () => {
  const zones = [zone('back', -1, 10, 40, 40), zone('title', 10, -1, 200, 40)];
  assert.deepEqual(zoneVerdict(zones, 1920, 1080), { ok: false, outside: ['back', 'title'] });
});

test('an empty zone list is not ok', () => {
  assert.deepEqual(zoneVerdict([], 1920, 1080), { ok: false, outside: [] });
});
