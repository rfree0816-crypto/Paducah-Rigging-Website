/**
 * Test runner: starts a static file server for the repo root, waits for it
 * to come up, runs the Playwright e2e spec against it, then shuts the
 * server down — so `npm test` is a single self-contained command with
 * nothing left running afterward.
 */
const { spawn } = require('child_process');
const http = require('http');
const path = require('path');

const PORT = 8791; // unlikely to collide with a dev server the user has open
const ROOT = path.join(__dirname, '..');

function waitForServer(url, timeoutMs) {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    (function poll() {
      http.get(url, res => { res.resume(); resolve(); })
        .on('error', () => {
          if (Date.now() - start > timeoutMs) reject(new Error('server did not start in time'));
          else setTimeout(poll, 150);
        });
    })();
  });
}

async function main() {
  const server = spawn('python3', ['-m', 'http.server', String(PORT), '--bind', '127.0.0.1'], {
    cwd: ROOT, stdio: 'ignore'
  });

  const cleanup = () => { try { server.kill(); } catch (e) {} };
  process.on('exit', cleanup);
  process.on('SIGINT', () => { cleanup(); process.exit(1); });

  try {
    await waitForServer(`http://127.0.0.1:${PORT}/index.html`, 8000);
  } catch (e) {
    cleanup();
    console.error('Could not start local server for tests:', e.message);
    process.exit(1);
  }

  const test = spawn(process.execPath, [path.join(__dirname, 'e2e.spec.js')], {
    cwd: ROOT, stdio: 'inherit',
    env: { ...process.env, BASE_URL: `http://127.0.0.1:${PORT}/index.html` }
  });

  test.on('exit', code => { cleanup(); process.exit(code || 0); });
}

main();
