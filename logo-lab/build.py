#!/usr/bin/env python3
"""Generate logo candidates as SVG plus a side-by-side comparison sheet."""
import os, html

PAPER   = "#FAF4E6"
EDGE    = "#DFD2B4"
INK     = "#23211C"
INKSOFT = "#8A8272"
RED     = "#C9553D"
YEL     = "#FFD54A"
YELDEEP = "#EFAF07"

# Each entry: (slug, title, note, svg body drawn in a 128x128 viewBox)
CANDIDATES = []

def add(slug, title, note, body):
    CANDIDATES.append((slug, title, note, body.strip()))

# Rounded tile helpers -------------------------------------------------------
def tile(fill, stroke=None):
    s = f' stroke="{stroke}" stroke-width="3"' if stroke else ""
    return f'<rect x="4" y="4" width="120" height="120" rx="30" fill="{fill}"{s}/>'

# 1 -------------------------------------------------------------------------
add("swipe", "Swipe",
    "One fat highlighter stroke on ink. Nothing else. Highest contrast of the set.",
    f"""
{tile(INK)}
<path d="M22 84 L92 30 L106 49 L36 103 Z" fill="{YEL}"/>
<path d="M22 84 L36 103 L24 106 Z" fill="{YELDEEP}"/>
""")

# 2 -------------------------------------------------------------------------
add("quote", "Quote",
    "The act of quoting, marked. Reads as a glyph rather than an object.",
    f"""
{tile(PAPER, EDGE)}
<rect x="24" y="70" width="80" height="18" rx="4" fill="{YEL}"/>
<path d="M34 34 h22 v34 c0 12 -8 20 -20 22 v-12 c6 -2 9 -5 9 -10 h-11 Z" fill="{INK}"/>
<path d="M72 34 h22 v34 c0 12 -8 20 -20 22 v-12 c6 -2 9 -5 9 -10 h-11 Z" fill="{INK}"/>
""")

# 3 -------------------------------------------------------------------------
add("chisel", "Chisel",
    "The highlighter itself, mid-stroke. Most literal; busiest at 16px.",
    f"""
{tile(PAPER, EDGE)}
<clipPath id="chiselClip"><rect x="4" y="4" width="120" height="120" rx="30"/></clipPath>
<rect x="18" y="86" width="92" height="14" rx="7" fill="{YEL}"/>
<g clip-path="url(#chiselClip)">
  <g transform="rotate(-38 64 58) translate(0 6)">
    <rect x="53" y="24" width="24" height="42" rx="6" fill="{INK}"/>
    <rect x="53" y="66" width="24" height="11" fill="{INKSOFT}"/>
    <path d="M53 77 h24 l-6 17 h-12 Z" fill="{YELDEEP}"/>
  </g>
</g>
""")

# 4 -------------------------------------------------------------------------
add("ruled", "Ruled (refined)",
    "Your current direction, rebuilt: three heavy lines, real margin rule, band bleeding to the edge.",
    f"""
{tile(PAPER, EDGE)}
<rect x="34" y="4" width="4" height="120" fill="{RED}" opacity="0.9"/>
<rect x="4" y="52" width="120" height="20" fill="{YEL}"/>
<rect x="50" y="34" width="56" height="7" rx="3.5" fill="{INKSOFT}"/>
<rect x="50" y="58.5" width="56" height="7" rx="3.5" fill="{INK}"/>
<rect x="50" y="83" width="36" height="7" rx="3.5" fill="{INKSOFT}"/>
""")

# 5 -------------------------------------------------------------------------
add("fold", "Fold",
    "A page, unmistakably. The folded corner does the work the ruling used to.",
    f"""
<path d="M22 10 h58 l30 30 v78 a8 8 0 0 1 -8 8 H30 a8 8 0 0 1 -8 -8 V18 a8 8 0 0 1 8 -8 Z" fill="{PAPER}" stroke="{EDGE}" stroke-width="3"/>
<path d="M80 10 l30 30 H88 a8 8 0 0 1 -8 -8 Z" fill="{EDGE}"/>
<rect x="34" y="60" width="60" height="18" rx="4" fill="{YEL}"/>
<rect x="34" y="88" width="60" height="7" rx="3.5" fill="{INKSOFT}"/>
<rect x="34" y="104" width="36" height="7" rx="3.5" fill="{INKSOFT}"/>
""")

# 6 -------------------------------------------------------------------------
add("spark", "Spark",
    "Highlight plus the AI pass. The one that says the product does something to the text.",
    f"""
{tile(INK)}
<rect x="18" y="58" width="76" height="20" rx="5" fill="{YEL}"/>
<rect x="18" y="34" width="52" height="8" rx="4" fill="{INKSOFT}"/>
<rect x="18" y="92" width="60" height="8" rx="4" fill="{INKSOFT}"/>
<path d="M99 20 c3 14 5 16 19 19 c-14 3 -16 5 -19 19 c-3 -14 -5 -16 -19 -19 c14 -3 16 -5 19 -19 Z" fill="{PAPER}"/>
""")

# 7 -------------------------------------------------------------------------
add("flow", "Flow",
    "Raw capture at the top, resolving downward into something ordered. Abstract, wordmark-friendly.",
    f"""
{tile(PAPER, EDGE)}
<rect x="22" y="36" width="84" height="18" rx="9" fill="{YEL}"/>
<rect x="30" y="64" width="68" height="14" rx="7" fill="{INK}"/>
<rect x="42" y="88" width="44" height="12" rx="6" fill="{INKSOFT}"/>
""")

# 8 -------------------------------------------------------------------------
add("bookmark", "Bookmark",
    "Saving, not marking. Strong silhouette, but says 'read later' more than 'highlight'.",
    f"""
{tile(PAPER, EDGE)}
<rect x="24" y="44" width="80" height="18" rx="4" fill="{YEL}"/>
<path d="M76 4 h26 v78 l-13 -14 l-13 14 Z" fill="{RED}"/>
<rect x="24" y="76" width="44" height="7" rx="3.5" fill="{INKSOFT}"/>
<rect x="24" y="94" width="60" height="7" rx="3.5" fill="{INKSOFT}"/>
""")

OUT = os.path.dirname(os.path.abspath(__file__))

def svg_doc(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" '
            'width="128" height="128">\n' + body + '\n</svg>\n')

for slug, title, note, body in CANDIDATES:
    with open(os.path.join(OUT, f"{slug}.svg"), "w") as fh:
        fh.write(svg_doc(body))

# Comparison sheet ----------------------------------------------------------
import base64, sys
sys.path.insert(0, OUT)
import png as pngmod

RASTER_DIR = os.path.join(OUT, "raster")
SIZES = (128, 48, 16)

def data_uri(path):
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode()

sheets = {}
for slug, _t, _n, _b in CANDIDATES:
    svg = os.path.join(OUT, f"{slug}.svg")
    made = pngmod.render_sizes(svg, RASTER_DIR, SIZES)
    # The 16px render, nearest-neighbour enlarged, so the pixel grid is visible.
    w, h, px = pngmod.read_png(made[16])
    zw, zh, zpx = pngmod.upscale(w, h, px, 8)
    zoom = os.path.join(RASTER_DIR, f"{slug}-16x8.png")
    pngmod.write_png(zoom, zw, zh, zpx)
    sheets[slug] = {s: data_uri(p) for s, p in made.items()}
    sheets[slug]["zoom"] = data_uri(zoom)

def img(slug, key, px, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} width="{px}" height="{px}" alt="{slug}" '
            f'src="{sheets[slug][key]}"/>')

rows = []
for i, (slug, title, note, body) in enumerate(CANDIDATES, 1):
    rows.append(f"""
<article class="card">
  <div class="meta">
    <span class="num">{i:02d}</span>
    <h2>{html.escape(title)}</h2>
    <p>{html.escape(note)}</p>
    <code>{slug}.svg</code>
  </div>
  <div class="sizes">
    <div class="size"><div class="frame big">{img(slug,128,128)}</div><span>128</span></div>
    <div class="size"><div class="frame">{img(slug,48,48)}</div><span>48</span></div>
    <div class="size"><div class="frame">{img(slug,16,16)}</div><span>16 actual</span></div>
    <div class="size"><div class="frame big">{img(slug,"zoom",128,"pixelated")}</div><span>16 magnified</span></div>
  </div>
  <div class="bars">
    <div class="bar light">{img(slug,16,16)}<span>light toolbar</span></div>
    <div class="bar dark">{img(slug,16,16)}<span>dark toolbar</span></div>
  </div>
</article>""")

CSS = """
:root{ --bg:#F3EEE2; --card:#FFFDF7; --ink:#23211C; --soft:#6F6857; --line:#E3D9C2; }
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#1A1815; --card:#231F1B; --ink:#F2EADA; --soft:#A79E8B; --line:#3A342C; }
}
:root[data-theme="dark"]{
  --bg:#1A1815; --card:#231F1B; --ink:#F2EADA; --soft:#A79E8B; --line:#3A342C; }
*{box-sizing:border-box}
body{background:var(--bg); color:var(--ink);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  padding:40px 24px 80px; margin:0}
header{max-width:1120px; margin:0 auto 36px}
h1{font-size:26px; margin:0 0 8px; letter-spacing:-.02em}
header p{margin:0; color:var(--soft); max-width:62ch}
.grid{max-width:1120px; margin:0 auto; display:grid; gap:20px}
.card{background:var(--card); border:1px solid var(--line); border-radius:16px;
  padding:22px 24px; display:grid; gap:22px;
  grid-template-columns:minmax(210px,1fr) auto auto; align-items:center}
@media (max-width:900px){ .card{grid-template-columns:1fr} }
.meta h2{font-size:18px; margin:2px 0 6px; letter-spacing:-.01em}
.meta p{margin:0 0 10px; color:var(--soft); font-size:13.5px}
.num{font-size:11px; letter-spacing:.14em; color:var(--soft)}
.meta code{font-size:12px; color:var(--soft)}
.sizes{display:flex; gap:18px; align-items:flex-end}
.size{display:flex; flex-direction:column; align-items:center; gap:7px}
.size span{font-size:10.5px; color:var(--soft); letter-spacing:.03em}
.frame{display:grid; place-items:center; width:56px; height:56px;
  border:1px dashed var(--line); border-radius:8px; overflow:hidden}
.frame.big{width:140px; height:140px}
img.pixelated{image-rendering:pixelated}
.bars{display:grid; gap:10px}
.bar{display:flex; align-items:center; gap:9px; padding:8px 12px; border-radius:9px;
  font-size:11px; white-space:nowrap}
.bar.light{background:#EDEDED; color:#444}
.bar.dark{background:#2B2B2B; color:#BBB}
"""

doc = f"""<title>Flow Notes Logo Candidates</title>
<style>{CSS}</style>
<header>
  <h1>Flow Notes &mdash; logo candidates</h1>
  <p>Eight directions, each rendered at 1024 and box-filtered down, so what you
  see is what Chrome will show. The column that matters is <strong>16
  actual</strong>: that is the toolbar size, where the icon is seen most, and an
  icon that fails there fails in the place it matters.
  <strong>16 magnified</strong> is that same 16&times;16 render enlarged so you
  can see exactly what survives.</p>
</header>
<div class="grid">{''.join(rows)}</div>
"""
with open(os.path.join(OUT, "candidates.html"), "w") as fh:
    fh.write(doc)
print(f"wrote {len(CANDIDATES)} svg files + candidates.html")
