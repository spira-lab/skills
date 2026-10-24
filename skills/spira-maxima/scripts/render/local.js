// The browser work of render.js and audit.js, on this machine: the editable's folder is
// served from 127.0.0.1 (stage.js serve, with intra.js's all-keyframe copies swapped in)
// and opened in local Chrome (CHROME_PATH, else the installed Google Chrome channel).
//   * the timeline is cut into contiguous chunks of about CM_RENDER_FRAMES_PER_CHUNK
//     frames (default 240); CM_RENDER_CONCURRENCY browsers (default half the cores,
//     at most 4) render them at once with the same stage.js code and encoder
//     settings, so the segments concat without a re-encode
//   * a chunk that fails is run once more; the segments come back in timeline order
//   * an audit is one browser over the same server (inspect.js); its sheet frames are
//     written straight to shotDir
const os = require('os'), path = require('path');
const { serve, launch, openStage, renderRange, rangeSummary } = require('./stage');
const { inspect } = require('./inspect');

const FRAMES_PER_CHUNK = parseInt(process.env.CM_RENDER_FRAMES_PER_CHUNK || '240', 10);
const CONCURRENCY = parseInt(process.env.CM_RENDER_CONCURRENCY || String(Math.max(1, Math.min(4, Math.floor(os.cpus().length / 2)))), 10);
// The render Lambda's flags that change pixels, not the ones it needs for its sandbox.
const CHROME_ARGS = ['--hide-scrollbars', '--mute-audio', '--font-render-hinting=none', '--force-color-profile=srgb'];

/** Contiguous, near-equal frame ranges [from, to). */
function planChunks(frames) {
  const n = Math.max(1, Math.ceil(frames / FRAMES_PER_CHUNK));
  return Array.from({ length: n }, (_, i) => [Math.floor(i * frames / n), Math.floor((i + 1) * frames / n)]);
}

async function pool(items, n, fn) {
  const out = new Array(items.length); let next = 0;
  await Promise.all(Array.from({ length: Math.min(n, items.length) }, async () => {
    while (next < items.length) { const i = next++; out[i] = await fn(items[i], i); }
  }));
  return out;
}

/** Run `fn`, once more if it throws (a chunk is idempotent). */
async function twice(label, fn) {
  try { return await fn(); } catch (e) {
    console.error(`  ${label} failed, retrying: ${e.message}`);
    try { return await fn(); } catch (e2) { throw new Error(`${label} failed twice: ${e2.message}`); }
  }
}

async function withServer(dir, swap, fn) {
  const server = await serve(dir, swap);
  try { return await fn(server.address().port); } finally {
    server.closeAllConnections && server.closeAllConnections();
    server.close();
  }
}

async function renderChunks({ dir, rel, ed, swap, fps, frames, tmp }) {
  const chunks = planChunks(frames);
  console.log(`rendering ${rel}: ${frames} frames @ ${fps} fps in ${chunks.length} chunks, ${Math.min(CONCURRENCY, chunks.length)} at a time | ${ed.sfx.length} sound effects`);
  const tCap = Date.now();
  const segs = await withServer(dir, swap, port => pool(chunks, CONCURRENCY, async ([from, to], i) => {
    const label = `c${String(i).padStart(2, '0')}`;
    const seg = path.join(tmp, `${label}.mp4`);
    const t0 = Date.now();
    const r = await twice(label, () => renderRange({ port, rel, fps, from, to, seg, label, launchArgs: CHROME_ARGS }));
    console.log(`${rangeSummary(label, r)} | ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    return seg;
  }));
  console.log(`  ${chunks.length} chunks captured in ${((Date.now() - tCap) / 1000).toFixed(0)}s`);
  return segs;
}

/** inspect.js in local Chrome; the sheet frames are written to `shotDir`. `swap` is intra.js's copies. */
async function auditLocal({ dir, rel, ed, at, shotDir, swap = {} }) {
  return withServer(dir, swap, async port => {
    const browser = await launch(CHROME_ARGS);
    try {
      const { page } = await openStage(browser, port, rel);
      return await inspect(page, { at, durationMs: ed.durationMs, shotDir });
    } finally {
      await browser.close();
    }
  });
}

module.exports = { renderChunks, auditLocal, planChunks };
