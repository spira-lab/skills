#!/usr/bin/env python3
"""Cut one generated sheet into its separate images.

  python3 scripts/cut-sheet.py grid <sheet.png> <rows>x<cols> --names a,b,c,d
  python3 scripts/cut-sheet.py elements <sheet.png> --names a,b,c,d

grid      a b-roll collage of equally divided frames: each frame is cropped
          whole, left to right, then top to bottom.
elements  transparent-background elements laid out apart: each object is
          found by its alpha, cropped with a small margin, and everything
          that belongs to the other objects is cleared from its crop, so no
          neighbour bleeds in. Parts of one object that do not touch (a pole
          and its flag) stay together when they sit close.

--names are the output names in reading order (left to right, top to
bottom); each is written as <name>.png beside the sheet. Without --names
the outputs are <sheet>-1.png, <sheet>-2.png, ... The sheet itself is left
where it is; move it to deletable/ once the cut-outs are in.
"""
import argparse, json, pathlib, subprocess, sys

try:
    import numpy as np
except ImportError:
    sys.exit("cut-sheet needs numpy (it comes with openai-whisper)")


def size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    return s["width"], s["height"]


def read_rgba(path):
    w, h = size(path)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 4).copy()


def write_png(path, rgba):
    h, w = rgba.shape[:2]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}", "-i", "-",
                    "-frames:v", "1", str(path)], input=rgba.tobytes(), check=True)


def outputs(sheet, n, names):
    if names and len(names) != n:
        sys.exit(f"cut-sheet: found {n} images but got {len(names)} names; check the sheet and pass {n} names")
    return [sheet.with_name(f"{nm}.png") for nm in names] if names else \
        [sheet.with_name(f"{sheet.stem}-{i + 1}.png") for i in range(n)]


def cut_grid(sheet, spec, names):
    rows, cols = (int(x) for x in spec.lower().split("x"))
    w, h = size(sheet)
    cw, ch = w // cols, h // rows
    if min(cw, ch) < 1080:
        print(f"warning: frames are {cw}x{ch}, under the 1080 px stage width: the sheet came back at {w}x{h}, "
              f"lower than asked. Use them only as insets or cards; for full-bleed stills generate each one "
              f"on its own at 2K (toolkit 3d).")
    outs = outputs(sheet, rows * cols, names)
    for i, out in enumerate(outs):
        r, c = divmod(i, cols)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(sheet), "-vf", f"crop={cw}:{ch}:{c * cw}:{r * ch}",
                        "-frames:v", "1", str(out)], check=True)
        print(f"{out.name}  {cw}x{ch}")


def label(mask):
    """8-connected components of a small boolean grid; returns (labels, count)."""
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32)
    n = 0
    for y0, x0 in zip(*np.nonzero(mask)):
        if lab[y0, x0]:
            continue
        n += 1
        lab[y0, x0] = n
        stack = [(y0, x0)]
        while stack:
            y, x = stack.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = n
                        stack.append((yy, xx))
    return lab, n


def cut_elements(sheet, names, pad=12, gap=24):
    img = read_rgba(sheet)
    h, w = img.shape[:2]
    solid = img[:, :, 3] > 24
    if solid.mean() > 0.9:
        sys.exit("cut-sheet: the sheet has no transparent background; regenerate it with a transparent background")
    f = 4  # label a 1/4 grid: fast, and gaps under 4 px between objects do not matter at this scale
    hs, ws = h // f, w // f
    small = solid[:hs * f, :ws * f].reshape(hs, f, ws, f).any(axis=(1, 3))
    lab, n = label(small)
    boxes = []
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if len(ys) < 0.0004 * hs * ws:  # specks and stray pixels
            continue
        boxes.append([{k}, ys.min(), xs.min(), ys.max(), xs.max()])
    # Parts of one object that sit within `gap` px of each other are one element.
    g = gap // f
    merged = True
    while merged:
        merged = False
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i], boxes[j]
                if a[1] - g <= b[3] and b[1] - g <= a[3] and a[2] - g <= b[4] and b[2] - g <= a[4]:
                    boxes[i] = [a[0] | b[0], min(a[1], b[1]), min(a[2], b[2]), max(a[3], b[3]), max(a[4], b[4])]
                    del boxes[j]
                    merged = True
                    break
            if merged:
                break
    # Reading order: rows by centre height, then left to right.
    boxes.sort(key=lambda b: (b[1] + b[3]) / 2)
    rows, row = [], []
    for b in boxes:
        if row and (b[1] + b[3]) / 2 > max(r[3] for r in row):
            rows.append(row)
            row = []
        row.append(b)
    if row:
        rows.append(row)
    ordered = [b for r in rows for b in sorted(r, key=lambda b: b[2])]
    outs = outputs(sheet, len(ordered), names)
    full_lab = np.kron(lab, np.ones((f, f), np.int32))
    full_lab = np.pad(full_lab, ((0, h - full_lab.shape[0]), (0, w - full_lab.shape[1])))
    for (keys, y0, x0, y1, x1), out in zip(ordered, outs):
        mine = np.isin(full_lab, list(keys))
        top, left = max(y0 * f - pad, 0), max(x0 * f - pad, 0)
        bottom, right = min((y1 + 1) * f + pad, h), min((x1 + 1) * f + pad, w)
        crop = img[top:bottom, left:right].copy()
        crop[~mine[top:bottom, left:right], 3] = 0  # clear every pixel that belongs to another object
        write_png(out, crop)
        print(f"{out.name}  {right - left}x{bottom - top}  from x {left}-{right}, y {top}-{bottom}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)
    g = sub.add_parser("grid"); g.add_argument("sheet"); g.add_argument("layout", help="rows x cols, e.g. 2x2")
    g.add_argument("--names", default="")
    e = sub.add_parser("elements"); e.add_argument("sheet"); e.add_argument("--names", default="")
    a = ap.parse_args()
    sheet = pathlib.Path(a.sheet).resolve()
    names = [x.strip() for x in a.names.split(",") if x.strip()]
    if a.mode == "grid":
        cut_grid(sheet, a.layout, names)
    else:
        cut_elements(sheet, names)


if __name__ == "__main__":
    main()
