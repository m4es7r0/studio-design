// tests/js/helpers.js
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const REPO = path.resolve(__dirname, '../..');

function makeClient(slug = 'demo-client') {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'studio-'));
  execFileSync(path.join(REPO, 'scripts/new-client.sh'), [slug, '--name', 'Demo Client', '--port', '5299'], {
    env: { ...process.env, CLIENTS_DIR: dir },
    stdio: 'pipe',
  });
  return path.join(dir, slug);
}

module.exports = { REPO, makeClient };
