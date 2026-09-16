#!/usr/bin/env python3
"""Flatten a PNG onto an opaque background and write it as 24-bit RGB.

The Web Store rejects screenshots and promo tiles that carry an alpha
channel ("JPEG or 24-bit PNG (no alpha)"), and Chrome's headless screenshots
are RGBA. Stdlib only.

    flatten.py in.png out.png [expected_width expected_height]
"""
import struct, sys, zlib

def read_png(path):
    d = open(path, "rb").read()
    pos, idat = 8, b""
    while pos < len(d):
        ln = struct.unpack(">I", d[pos:pos + 4])[0]
        typ = d[pos + 4:pos + 8]
        if typ == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", d[pos + 8:pos + 21])
        elif typ == b"IDAT":
            idat += d[pos + 8:pos + 8 + ln]
        pos += 12 + ln
    if depth != 8 or ctype not in (2, 6) or interlace:
        raise SystemExit(f"{path}: unsupported PNG (depth={depth} type={ctype} interlace={interlace})")
    bpp = 4 if ctype == 6 else 3
    raw, stride = zlib.decompress(idat), w * bpp
    rows, prev, p = [], bytearray(stride), 0
    for _ in range(h):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        if f:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                if f == 1:   line[i] = (line[i] + a) & 255
                elif f == 2: line[i] = (line[i] + b) & 255
                elif f == 3: line[i] = (line[i] + (a + b) // 2) & 255
                elif f == 4:
                    pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                    line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(line); prev = line
    return w, h, bpp, rows

def main():
    src, dst = sys.argv[1], sys.argv[2]
    w, h, bpp, rows = read_png(src)
    if len(sys.argv) == 5 and (w, h) != (int(sys.argv[3]), int(sys.argv[4])):
        raise SystemExit(f"{src}: expected {sys.argv[3]}x{sys.argv[4]}, got {w}x{h}")
    out = bytearray()
    for line in rows:
        out.append(0)
        if bpp == 3:
            out += line
            continue
        for i in range(0, len(line), 4):
            r, g, b, a = line[i:i + 4]
            # Composite onto white: every stage page paints an opaque
            # background, so this only matters at stray transparent edges.
            out += bytes(((r * a + 255 * (255 - a)) // 255,
                          (g * a + 255 * (255 - a)) // 255,
                          (b * a + 255 * (255 - a)) // 255))
    def chunk(t, data):
        return struct.pack(">I", len(data)) + t + data + struct.pack(">I", zlib.crc32(t + data))
    with open(dst, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n"
                 + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                 + chunk(b"IDAT", zlib.compress(bytes(out), 9))
                 + chunk(b"IEND", b""))

main()
