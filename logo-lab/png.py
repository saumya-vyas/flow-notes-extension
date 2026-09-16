"""Minimal stdlib PNG read/write plus SVG rasterising via qlmanage.

qlmanage renders an SVG at its intrinsic width/height, and at small intrinsic
sizes it draws well inside the canvas rather than filling it. So every SVG is
rendered once at 1024 and box-filtered down to the sizes we actually want,
which also gives better antialiasing than qlmanage's own downscale.
"""
import os, re, zlib, struct, shutil, subprocess, tempfile

# 1152 is divisible by 128, 48 and 16, so every target size is an exact
# integer box-filter of the master render.
MASTER = 1152


def read_png(path):
    d = open(path, "rb").read()
    pos, idat = 8, b""
    w = h = bitd = ct = 0
    while pos < len(d):
        ln = struct.unpack(">I", d[pos:pos + 4])[0]
        typ = d[pos + 4:pos + 8]
        if typ == b"IHDR":
            w, h, bitd, ct = struct.unpack(">IIBB", d[pos + 8:pos + 18])
        elif typ == b"IDAT":
            idat += d[pos + 8:pos + 8 + ln]
        pos += 12 + ln
    if (bitd, ct) != (8, 6):
        raise ValueError(f"{path}: expected 8-bit RGBA, got depth={bitd} type={ct}")
    raw = zlib.decompress(idat)
    stride = w * 4
    out = bytearray(w * h * 4)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        if f:
            for i in range(stride):
                a = line[i - 4] if i >= 4 else 0
                b = prev[i]
                c = prev[i - 4] if i >= 4 else 0
                if f == 1:   line[i] = (line[i] + a) & 255
                elif f == 2: line[i] = (line[i] + b) & 255
                elif f == 3: line[i] = (line[i] + (a + b) // 2) & 255
                elif f == 4:
                    pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                    pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                    line[i] = (line[i] + pr) & 255
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return w, h, out


def write_png(path, w, h, px):
    raw = b"".join(b"\x00" + bytes(px[y * w * 4:(y + 1) * w * 4]) for y in range(h))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
    open(path, "wb").write(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b""))


def box_down(w, h, px, out_w):
    """Downsample by an integer factor, averaging in premultiplied alpha."""
    f = w // out_w
    if f * out_w != w:
        raise ValueError(f"{w} is not an integer multiple of {out_w}")
    out_h = h // f
    out = bytearray(out_w * out_h * 4)
    n = f * f
    for oy in range(out_h):
        for ox in range(out_w):
            sr = sg = sb = sa = 0
            for dy in range(f):
                base = ((oy * f + dy) * w + ox * f) * 4
                for dx in range(f):
                    i = base + dx * 4
                    a = px[i + 3]
                    sr += px[i] * a; sg += px[i + 1] * a; sb += px[i + 2] * a
                    sa += a
            o = (oy * out_w + ox) * 4
            if sa:
                out[o]     = min(255, sr // sa)
                out[o + 1] = min(255, sg // sa)
                out[o + 2] = min(255, sb // sa)
            out[o + 3] = sa // n
    return out_w, out_h, out


def upscale(w, h, px, factor):
    ow, oh = w * factor, h * factor
    out = bytearray(ow * oh * 4)
    for y in range(oh):
        srow = (y // factor) * w * 4
        for x in range(ow):
            si = srow + (x // factor) * 4
            oi = (y * ow + x) * 4
            out[oi:oi + 4] = px[si:si + 4]
    return ow, oh, out


def render_master(svg_path, cache_dir, master_px=MASTER):
    """Rasterise an SVG at master_px squared. Returns (w, h, rgba)."""
    os.makedirs(cache_dir, exist_ok=True)
    slug = os.path.splitext(os.path.basename(svg_path))[0]
    master = os.path.join(cache_dir, f"{slug}-{master_px}.png")
    if not os.path.exists(master):
        src = open(svg_path).read()
        big = re.sub(r'width="\d+" height="\d+"',
                     f'width="{master_px}" height="{master_px}"', src, count=1)
        with tempfile.TemporaryDirectory() as tmp:
            probe = os.path.join(tmp, f"{slug}.svg")
            open(probe, "w").write(big)
            subprocess.run(["qlmanage", "-t", "-s", str(master_px), "-o", tmp, probe],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           check=False)
            made = probe + ".png"
            if not os.path.exists(made):
                raise RuntimeError(f"qlmanage produced nothing for {svg_path}")
            shutil.move(made, master)
    return read_png(master)


def render_sizes(svg_path, cache_dir, sizes, master_px=MASTER):
    """Rasterise an SVG to each size in `sizes`. Returns {size: png path}."""
    w, h, px = render_master(svg_path, cache_dir, master_px)
    slug = os.path.splitext(os.path.basename(svg_path))[0]
    made = {}
    for s in sizes:
        out = os.path.join(cache_dir, f"{slug}-{s}.png")
        ow, oh, opx = box_down(w, h, px, s)
        write_png(out, ow, oh, opx)
        made[s] = out
    return made


def rounded_rect_alpha(w, h, px, x0, y0, x1, y1, r, bg=(255, 255, 255), ss=4):
    """Restore transparency outside a rounded rectangle.

    qlmanage composites every SVG onto an opaque white page, so a rounded tile
    comes back with opaque white corners. Left alone that shows up as a white
    halo around the icon on dark Chrome themes and on the Web Store tile.

    The tile geometry is known exactly, so coverage is computed analytically
    (supersampled only on the boundary) and the known background is divided
    back out of the partially covered edge pixels.
    """
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    hx, hy = (x1 - x0) / 2.0, (y1 - y0) / 2.0
    r = min(r, hx, hy)

    def extent(dy):
        """Half-width of the shape at vertical offset dy from the centre."""
        ady = abs(dy)
        if ady > hy:
            return -1.0
        if ady <= hy - r:
            return hx
        t = ady - (hy - r)
        return hx - r + (max(r * r - t * t, 0.0)) ** 0.5

    out = bytearray(px)
    inv = 1.0 / (ss * ss)
    br, bgc, bb = bg

    for y in range(h):
        dy = y + 0.5 - cy
        e_lo = min(extent(dy - 0.5), extent(dy), extent(dy + 0.5))
        e_hi = max(extent(dy - 0.5), extent(dy), extent(dy + 0.5))
        if e_hi < 0:                       # row lies entirely outside
            for x in range(w):
                o = (y * w + x) * 4
                out[o:o + 4] = b"\x00\x00\x00\x00"
            continue
        for x in range(w):
            dx = abs(x + 0.5 - cx)
            if dx <= e_lo - 1.0:           # fully inside
                continue
            o = (y * w + x) * 4
            if dx >= e_hi + 1.0:           # fully outside
                out[o:o + 4] = b"\x00\x00\x00\x00"
                continue
            hits = 0                        # straddles the edge: supersample
            for sy in range(ss):
                sdy = y + (sy + 0.5) / ss - cy
                ex = extent(sdy)
                if ex < 0:
                    continue
                for sx in range(ss):
                    if abs(x + (sx + 0.5) / ss - cx) <= ex:
                        hits += 1
            cov = hits * inv
            if cov <= 0.0:
                out[o:o + 4] = b"\x00\x00\x00\x00"
                continue
            if cov >= 1.0:
                continue
            # The pixel holds shape*cov + bg*(1-cov); recover the shape colour.
            for k, bk in enumerate((br, bgc, bb)):
                v = (px[o + k] - bk * (1.0 - cov)) / cov
                out[o + k] = 0 if v < 0 else (255 if v > 255 else int(v + 0.5))
            out[o + 3] = int(cov * 255 + 0.5)
    return w, h, out
