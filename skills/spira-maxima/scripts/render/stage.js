// Shared plumbing for render.js and audit.js: read an editable, serve its folder, open
// it at ?render in headless Chrome, and seek it frame by frame.
// playwright-core lives in the working directory's .maxima-runtime/ (MAXIMA_RUNTIME
// overrides), never in the skill; it is required on launch only, so the file checks
// run without it.
const fs = require('fs'), path = require('path'), http = require('http');
const { spawn } = require('child_process');

const runtimeDir = () => process.env.MAXIMA_RUNTIME || path.resolve('.maxima-runtime');
const playwright = () => require(require.resolve('playwright-core', { paths: [runtimeDir()] }));

const MIME = { html:'text/html', css:'text/css', js:'text/javascript', json:'application/json',
               png:'image/png', jpg:'image/jpeg', jpeg:'image/jpeg', webp:'image/webp', gif:'image/gif', svg:'image/svg+xml', avif:'image/avif',
               mp3:'audio/mpeg', wav:'audio/wav', m4a:'audio/mp4', ogg:'audio/ogg',
               mp4:'video/mp4', webm:'video/webm', mov:'video/quicktime',
               woff:'font/woff', woff2:'font/woff2', ttf:'font/ttf', otf:'font/otf' };

/**
 * Static server rooted at `dir`; nothing outside it is served. `swap` maps a src as
 * written in the html to a local file streamed in its place.
 */
function serve(dir, swap = {}) {
  const server = http.createServer((req, res) => {
    const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\//, '');
    const p = swap[rel] || path.join(dir, rel);
    if (!swap[rel] && (!p.startsWith(dir) || !fs.existsSync(p) || fs.statSync(p).isDirectory())) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(p).slice(1).toLowerCase()] || 'application/octet-stream' });
    fs.createReadStream(p).pipe(res);
  });
  return new Promise(r => server.listen(0, '127.0.0.1', () => r(server)));
}

function launch(extraArgs = []) {
  const o = { args: ['--force-device-scale-factor=1', ...extraArgs] };
  if (process.env.CHROME_PATH) o.executablePath = process.env.CHROME_PATH; else o.channel = 'chrome';
  return playwright().chromium.launch(o);
}

// Injected once per page: pause every animation, cache the list, expose a cheap
// seek. A <video> is seeked to its own time for the stage time (data-start = stage
// ms at which the clip's time is 0) and resolves once the frame is decoded. A seek
// that has not landed in SEEK_TIMEOUT ms is issued again once, then given up on,
// so one stuck decoder costs a warning instead of hanging the render.
const PREP = `
  (() => {
    const stage = document.getElementById('stage');
    stage.classList.add('is-paused');
    const anims = document.getAnimations();
    anims.forEach(a => { try { a.pause(); } catch (e) {} });
    window.__anims = anims;
    window.__seek = ms => { const a = window.__anims; for (let i = 0; i < a.length; i++) { try { a[i].currentTime = ms; } catch (e) {} } };
    const vids = [...stage.querySelectorAll('video')];
    vids.forEach(v => { v.muted = true; v.pause(); });
    window.__stuck = 0;
    const seekOne = (v, t, tries) => new Promise(res => {
      const done = ok => { clearTimeout(timer); v.removeEventListener('seeked', onSeeked); res(ok); };
      const onSeeked = () => done(true);
      const timer = setTimeout(() => done(false), 3000);
      v.addEventListener('seeked', onSeeked);
      v.currentTime = t;
    }).then(ok => ok || tries <= 0 ? ok : seekOne(v, t, tries - 1));
    window.__seekVideos = ms => Promise.all(vids.map(v => {
      if (!v.readyState || !v.duration) return null;
      const start = parseFloat(v.dataset.start) || 0;
      const t = Math.min(Math.max((ms - start) / 1000, 0), v.duration - 0.001);
      if (Math.abs(v.currentTime - t) < 0.0005 && !v.seeking) return null;
      return seekOne(v, t, 1).then(ok => { if (!ok) window.__stuck++; });
    }));
    return anims.length;
  })()`;

/** Open the editable at ?render, sized to the stage, with fonts, images and videos ready. */
async function openStage(browser, port, rel) {
  const page = await browser.newPage({ deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('page error:', e.message));
  await page.goto(`http://127.0.0.1:${port}/${encodeURIComponent(rel)}?render`, { waitUntil: 'load' });
  const [W, H] = await page.evaluate(() => [window.STAGE.width, window.STAGE.height]);
  await page.setViewportSize({ width: W, height: H });
  const slow = await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].map(i => i.complete ? null : new Promise(r => { i.onload = i.onerror = r; })));
    // the harness swaps each video src for a blob; wait until that blob is decodable
    const late = [];
    await Promise.all([...document.querySelectorAll('#stage video')].map(v => new Promise(r => {
      if (!v.getAttribute('src')) return r();
      const ok = () => v.readyState >= 2 && v.currentSrc.startsWith('blob:');
      if (ok()) return r();
      const iv = setInterval(() => { if (ok()) { clearInterval(iv); r(); } }, 50);
      setTimeout(() => { clearInterval(iv); late.push(v.getAttribute('src')); r(); }, 20000);
    })));
    return late;
  });
  slow.forEach(s => console.error(`warning: ${s} was not decodable after 20 s`));
  const nAnims = await page.evaluate(PREP);
  return { page, W, H, nAnims };
}

/**
 * Put the page on stage time `ms` and wait for two painted frames. `videos: false`
 * leaves the clips where they are: layout and opacity checks do not need a decoded
 * frame, and on a busy worker the decode is most of a seek.
 */
function seekTo(page, ms, videos = true) {
  return page.evaluate(([ms, videos]) => {
    window.__seek(ms);
    return (videos ? window.__seekVideos(ms) : Promise.resolve()).then(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
  }, [ms, videos]);
}

/**
 * Capture frames [from, to) of the editable served on `port` into an H.264 segment
 * at `seg`. Every segment of a render is encoded with the same settings, so they
 * join with the concat demuxer without a re-encode. One call per chunk
 * (render.js -> local.js).
 */
async function renderRange({ port, rel, fps, from, to, seg, label = '', ffmpeg = 'ffmpeg', launchArgs = [] }) {
  const browser = await launch(launchArgs);
  const { page, W, H, nAnims } = await openStage(browser, port, rel);
  const ff = spawn(ffmpeg, ['-y','-v','error','-f','image2pipe','-vcodec','mjpeg','-framerate',String(fps),'-i','-',
    '-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p', seg], { stdio: ['pipe','inherit','inherit'] });
  const ffDone = new Promise((res, rej) => { ff.on('error', rej); ff.on('close', c => c === 0 ? res() : rej(new Error(`${label} ffmpeg ${c}`))); });
  const write = buf => new Promise(r => { if (!ff.stdin.write(buf)) ff.stdin.once('drain', r); else r(); });

  let tSeek = 0, tShot = 0, tPipe = 0;
  const clip = { x: 0, y: 0, width: W, height: H };
  for (let i = from; i < to; i++) {
    const t0 = Date.now();
    await seekTo(page, i * 1000 / fps);
    const t1 = Date.now();
    const shot = await page.screenshot({ type: 'jpeg', quality: 92, clip });
    const t2 = Date.now();
    await write(shot);
    tSeek += t1 - t0; tShot += t2 - t1; tPipe += Date.now() - t2;
    if ((i - from) % 100 === 0) process.stdout.write(`\r  ${label} ${i - from}/${to - from}   `);
  }
  const stuck = await page.evaluate(() => window.__stuck);
  ff.stdin.end();
  await ffDone;
  await browser.close();
  const n = to - from;
  return { frames: n, W, H, nAnims, stuck, seekMs: tSeek / n, shotMs: tShot / n, pipeMs: tPipe / n };
}

/** One log line for a finished segment. */
const rangeSummary = (label, r) =>
  `  ${label} done ${r.frames} frames | ${r.W}x${r.H} | anims ${r.nAnims} | seek ${r.seekMs.toFixed(0)}ms shot ${r.shotMs.toFixed(0)}ms pipe ${r.pipeMs.toFixed(0)}ms${r.stuck ? ` | ${r.stuck} video seeks timed out` : ''}`;

/** The stage facts a tool needs, read from the editable's html. */
function readEditable(htmlPath) {
  // Comments hold examples (the template's sample sfx tag), never cues.
  const html = fs.readFileSync(htmlPath, 'utf8').replace(/<!--[\s\S]*?-->/g, '');
  const attr = (tag, name) => (tag.match(new RegExp(`\\b${name}="([^"]*)"`)) || [])[1];
  const durationMs = parseInt((html.match(/data-duration="(\d+)"/) || [0, 0])[1], 10);
  const voTag = (html.match(/<audio\b[^>]*\bid="vo"[^>]*>/) || [])[0] || '';
  const bgmTag = (html.match(/<audio\b[^>]*\bid="bgm"[^>]*>/) || [])[0] || '';
  const num = v => (v === undefined ? null : Number(v));
  const sfx = [...html.matchAll(/<audio\b[^>]*\bclass="[^"]*\bsfx\b[^"]*"[^>]*>/g)].map(m => ({
    src: attr(m[0], 'src'), at: parseFloat(attr(m[0], 'data-at')) || 0, gainDb: num(attr(m[0], 'data-gain-db')),
  })).filter(s => s.src);
  const videos = [...new Set([...html.matchAll(/<video\b[^>]*\bsrc="([^"]+)"/g)].map(m => m[1]))];
  const name = path.basename(htmlPath).replace(/\.html?$/i, '');
  // null means the tag never got a gain, which a library bed must not be rendered without.
  const gainAttr = attr(bgmTag, 'data-gain-db');
  return {
    html, name, durationMs, videos, sfx,
    voSrc: attr(voTag, 'src'), bgmSrc: attr(bgmTag, 'src'),
    bgmGainDb: gainAttr === undefined ? null : parseFloat(gainAttr),
    // Optional level adjustments, only when asked for (stage-canvas-html section 5); validated by render.js.
    voGainDb: num(attr(voTag, 'data-gain-db')),
    bgmOffsetDb: num(attr(bgmTag, 'data-gain-offset-db')),
    bgmDuck: attr(bgmTag, 'data-duck') ?? null,
  };
}

module.exports = { serve, launch, openStage, seekTo, renderRange, rangeSummary, readEditable, playwright, runtimeDir };
