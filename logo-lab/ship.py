#!/usr/bin/env python3
"""Render mark.svg into every asset slot the product needs, then verify.

1920 is the master render size because it divides exactly by all four targets
(16, 48, 120, 128), so each output is an integer box-filter of one render
rather than a resample of a resample.
"""
import os, shutil, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import png as pngmod

MASTER = 1920
SRC = os.path.join(HERE, "mark.svg")
BUILD = os.path.join(HERE, "build")

EXT_ICONS = "/Users/saumya/Desktop/files/flow-notes-extension/icons"
SITE = "/Users/saumya/Desktop/flownotesapp.github.io"

# (size, destination) -- 120 is fixed by Google's OAuth consent screen branding,
# which requires exactly 120x120.
TARGETS = [
    (16,  os.path.join(EXT_ICONS, "icon16.png")),
    (48,  os.path.join(EXT_ICONS, "icon48.png")),
    (128, os.path.join(EXT_ICONS, "icon128.png")),
    (120, os.path.join(SITE, "logo-120.png")),
]

for d in (MASTER, *(s for s, _ in TARGETS)):
    if MASTER % d:
        raise SystemExit(f"{MASTER} does not divide evenly by {d}")

os.makedirs(BUILD, exist_ok=True)
sizes = sorted({s for s, _ in TARGETS})

# The tile is x=4..124 with rx=30 in a 128 viewBox; scale that to the master.
K = MASTER / 128.0
w, h, px = pngmod.render_master(SRC, BUILD, MASTER)
w, h, px = pngmod.rounded_rect_alpha(w, h, px, 4 * K, 4 * K, 124 * K, 124 * K, 30 * K)
pngmod.write_png(os.path.join(BUILD, f"mark-{MASTER}-alpha.png"), w, h, px)

made = {}
for size in sizes:
    dest = os.path.join(BUILD, f"mark-{size}.png")
    pngmod.write_png(dest, *pngmod.box_down(w, h, px, size))
    made[size] = dest

def dims(path):
    with open(path, "rb") as fh:
        return struct.unpack(">II", fh.read(24)[16:24])

print(f"master render: {MASTER}x{MASTER}\n")
for size, dest in TARGETS:
    src = made[size]
    shutil.copy2(src, dest)
    w, h = dims(dest)
    if (w, h) != (size, size):
        raise SystemExit(f"FAIL {dest}: expected {size}x{size}, got {w}x{h}")
    _, _, ipx = pngmod.read_png(dest)
    corner = ipx[3]
    mid = ipx[((h // 2) * w + w // 2) * 4 + 3]
    if corner != 0 or mid != 255:
        raise SystemExit(f"FAIL {dest}: corner alpha={corner} centre alpha={mid}")
    rel = dest.replace("/Users/saumya/Desktop/", "~/Desktop/")
    print(f"  {w:>3}x{h:<3} {os.path.getsize(dest):>6} bytes  "
          f"corner a={corner} centre a={mid}  {rel}")
