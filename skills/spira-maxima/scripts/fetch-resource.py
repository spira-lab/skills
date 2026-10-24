#!/usr/bin/env python3
"""Fetch a hosted library file (music, sound effects) listed in assets/resources.json.

The skill does not ship its audio; resources.json maps each library path to a
hosted URL and its sha256. This fetches one file to where the video needs it.

Usage: python3 scripts/fetch-resource.py <library path> <destination>
  python3 scripts/fetch-resource.py music/DD01.mp3 editable/materials/<name>/bgm.mp3
  python3 scripts/fetch-resource.py sfx/03_whoosh.mp3 editable/materials/<name>/sfx/03_whoosh.mp3

The library path is the `path` of an entry in assets/music/Music metadata.json or
assets/sfx/SFX metadata.json. The download goes through curl (the CDN turns away
urllib's default client) and is checked against its sha256 before it lands; a
destination that already holds the right file is left alone.
"""
import hashlib, json, os, subprocess, sys, tempfile

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__.split("\n\n")[2])
    rel, dest = sys.argv[1].lstrip("./"), sys.argv[2]
    files = json.load(open(os.path.join(ASSETS, "resources.json")))["files"]
    entry = files.get(rel)
    if entry is None:
        near = [k for k in files if os.path.basename(k).split("_")[0] == os.path.basename(rel).split("_")[0]][:3]
        sys.exit(f"not in resources.json: {rel}" + (f" (did you mean {', '.join(near)}?)" if near else ""))
    if os.path.isfile(dest) and sha256(dest) == entry["sha256"]:
        print(f"already there: {dest}")
        return
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(dest)), suffix=".part"); os.close(fd)
    try:
        if subprocess.run(["curl", "-sSfL", "--retry", "3", "-o", tmp, entry["url"]]).returncode != 0:
            sys.exit(f"download failed: {entry['url']}")
        if sha256(tmp) != entry["sha256"]:
            sys.exit(f"checksum mismatch for {rel}: the hosted file is not the one resources.json lists")
        os.replace(tmp, dest)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    print(f"fetched {rel} -> {dest} ({entry['bytes'] / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
