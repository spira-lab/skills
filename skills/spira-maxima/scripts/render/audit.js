#!/usr/bin/env node
// Pre-render audit of a stage editable, in the renderer's own ?render view.
// Usage: node scripts/render/audit.js <editable.html> [--at ms,ms,...]
//   Without --at: the whole video is checked (run it when every scene is written,
//   and again after the fixes). With --at: a quick look at what you just built.
//   Only those frames are shot, and leaks and text are checked only within 0.5 s
//   of each time given. Checks never decode video; only the frames shot do, and they
//   seek the same cached all-keyframe copies the render uses (intra.js), so the first
//   audit of a video pays for the copies and later audits and the render reuse them.
//   A "video seeks timed out" line is then a decoder hiccup on a busy machine: run the
//   audit again, never change the scenes for it.
//   * leaks: an element whose entry animation (first keyframe opacity 0 or fully
//     clipped) has not started yet but is visible anyway. Checked on the first frame
//     and 0.4 s before each .scene starts (a scene starts at its earliest animation).
//   * text: every phrase (the parent of .w words) at the moment its last word has
//     landed: safe-zone hits and lines holding a single short non-key word; every
//     other text block (headlines, labels, card copy) once its entry has finished:
//     safe-zone hits.
//   * edge: on each sheet frame, a frame-filling layer (media or a painted box
//     spanning most of the canvas) that stops just short of an edge.
//   * font: a @font-face that failed to load, or no text in a font from assets/fonts/.
//   * files: every materials/ file the html references (tags and CSS url()) exists,
//     and none is in deletable/ or jobs/.
//   * cut-out: talking-head clips (th-*.mp4) on the stage with no cut-out WebM.
//   * sheet: the frames at --at, or by default the first frame, each scene 0.6 s in
//     and the last frame, written to materials/<name>/deletable/audit-sheet.jpg.
// Prints "audit clean" or one line per problem. Fix every line, then run it again.
// The browser half (leaks, text, frames; inspect.js) runs in local Chrome (local.js);
// the file checks and the sheet are done here.
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const { readEditable, workTemp } = require('./stage');
const { auditLocal } = require('./local');
const { intraCopies } = require('./intra');

const args = process.argv.slice(2);
const atIdx = args.indexOf('--at');
const at = atIdx >= 0 ? args.splice(atIdx, 2)[1].split(',').map(Number) : null;
if (!args[0]) { console.error('usage: audit.js <editable.html> [--at ms,ms,...]'); process.exit(2); }
const htmlPath = path.resolve(args[0]);
const dir = path.dirname(htmlPath), rel = path.basename(htmlPath);
const ed = readEditable(htmlPath);

(async () => {
  const problems = [];

  // Files, from tags and from CSS url()s (fonts, background images).
  const refs = [...new Set([...ed.html.matchAll(/(?:src|href)="(materials\/[^"]+)"|url\(\s*['"]?(materials\/[^'")]+)/g)].map(m => m[1] || m[2]))];
  for (const ref of refs) {
    if (/\/(deletable|jobs)\//.test(ref)) problems.push(`file: ${ref} is in ${ref.includes('/jobs/') ? 'jobs/' : 'deletable/'}; move what the video uses back out`);
    else if (!fs.existsSync(path.join(dir, ref))) problems.push(`file: ${ref} does not exist`);
  }

  // A talking head is layered with its cut-out (toolkit 3f): clips on the stage and no WebM means it never is.
  if (refs.some(r => /\/th-[^/]*\.mp4$/.test(r)) && !refs.some(r => /\.webm$/.test(r))) {
    problems.push('cut-out: the talking-head clips are on the stage but none of their cut-outs is; cut every clip out (toolkit 3f) and layer the WebM over the scenes (creative-video-production section 5)');
  }

  const tmp = workTemp('stage-audit-');
  const swap = await intraCopies(dir, ed);
  const { scenes, problems: seen, errors, stuck, portrait, shots } = await auditLocal({ dir, rel, ed, at, shotDir: tmp, swap });
  problems.push(...seen);

  const deletable = path.join(dir, 'materials', ed.name, 'deletable');
  fs.mkdirSync(deletable, { recursive: true });
  const sheet = path.join(deletable, 'audit-sheet.jpg');
  // A few frames come out large enough to read detail; more are tiled small.
  const big = shots.length <= 4;
  const cols = Math.min(shots.length, big ? 4 : 6), rows = Math.ceil(shots.length / cols);
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', '1', '-i', path.join(tmp, '%03d.jpg'),
    '-vf', `scale=${big ? '540:960' : '270:480'},tile=${cols}x${rows}`, '-frames:v', '1', sheet]);
  fs.rmSync(tmp, { recursive: true, force: true });

  errors.forEach(e => problems.push(`console: ${e}`));
  if (stuck) problems.push(`${stuck} video seeks timed out`);
  console.log(`scenes: ${scenes.map(s => `${s.id}@${(s.start / 1000).toFixed(2)}s`).join(' ') || 'none (.scene[id] marks one)'}`);
  if (!portrait) console.log('stage is not 9:16: safe-zone checks skipped; keep key elements clear of the edges by eye');
  if (at) console.log(`checked: within 0.5 s of ${at.map(a => (a / 1000).toFixed(1) + 's').join(', ')} only; run without --at for the whole video`);
  console.log(`sheet: ${sheet} (${shots.map(s => (s.t / 1000).toFixed(1) + 's').join(' ')})`);
  console.log(problems.length ? problems.join('\n') : 'audit clean');
  process.exit(0);
})().catch(e => { console.error(e); process.exit(1); });
