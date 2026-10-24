#!/usr/bin/env node
// Preflight for render.js and audit.js, run from the working directory:
// playwright-core is installed in its .maxima-runtime/ (MAXIMA_RUNTIME overrides),
// Chrome launches (CHROME_PATH, else the installed Google Chrome channel), and the
// Python that render.js calls for the music bed (PYTHON, else python3) runs from node.
// Prints one line per check and exits 1 when any fails.
const { execFileSync } = require('child_process');
const path = require('path');
const { playwright, runtimeDir } = require('./stage');

(async () => {
  let failed = false;
  const fail = (what, fix) => { failed = true; console.log(`FAIL ${what}: ${fix}`); };

  let chromium;
  try { ({ chromium } = playwright()); console.log(`ok   playwright-core (${runtimeDir()})`); }
  catch {
    const version = require(path.join(__dirname, '..', 'package.json')).dependencies['playwright-core'];
    fail('playwright-core', `npm install --prefix "${runtimeDir()}" "playwright-core@${version}" --no-audit --no-fund`);
  }

  if (chromium) {
    const opts = process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : { channel: 'chrome' };
    try { const b = await chromium.launch(opts); await b.close(); console.log(`ok   chrome (${process.env.CHROME_PATH || 'chrome channel'})`); }
    catch (e) { fail('chrome', `install Google Chrome, or set CHROME_PATH to a Chromium/Edge executable (${e.message.split('\n')[0]})`); }
  }

  const python = process.env.PYTHON || 'python3';
  try { console.log(`ok   ${python} from node: ${execFileSync(python, ['--version']).toString().trim()}`); }
  catch { fail(`${python} from node`, 'set PYTHON to an interpreter node can run (for example PYTHON=python) in front of every render.js call'); }

  process.exit(failed ? 1 : 0);
})();
