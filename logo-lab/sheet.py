"""Render a set of icon candidates into a side-by-side comparison sheet.

Shared by every iteration round so the rounds stay directly comparable.
"""
import base64, html, os
import png as pngmod

SIZES = (128, 48, 16)


def _data_uri(path):
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode()


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
header p{margin:0 0 10px; color:var(--soft); max-width:64ch}
.grid{max-width:1120px; margin:0 auto; display:grid; gap:20px}
.card{background:var(--card); border:1px solid var(--line); border-radius:16px;
  padding:22px 24px; display:grid; gap:22px;
  grid-template-columns:minmax(210px,1fr) auto auto; align-items:center}
@media (max-width:900px){ .card{grid-template-columns:1fr} }
.card.pick{border-color:#C9553D; box-shadow:0 0 0 1px #C9553D inset}
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


def make_sheet(candidates, out_dir, out_name, title, blurb, label=str):
    """candidates: list of (slug, name, note, svg_body). Writes SVGs + an HTML sheet."""
    raster_dir = os.path.join(out_dir, "raster")

    def svg_doc(body):
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" '
                'width="128" height="128">\n' + body.strip() + '\n</svg>\n')

    rows = []
    for i, (slug, name, note, body) in enumerate(candidates, 1):
        svg_path = os.path.join(out_dir, f"{slug}.svg")
        with open(svg_path, "w") as fh:
            fh.write(svg_doc(body))

        made = pngmod.render_sizes(svg_path, raster_dir, SIZES)
        # The 16px render, nearest-neighbour enlarged, so the pixel grid shows.
        w, h, px = pngmod.read_png(made[16])
        zoom_path = os.path.join(raster_dir, f"{slug}-16x8.png")
        pngmod.write_png(zoom_path, *pngmod.upscale(w, h, px, 8))

        uris = {s: _data_uri(p) for s, p in made.items()}
        uris["zoom"] = _data_uri(zoom_path)

        def img(key, px_, cls=""):
            c = f' class="{cls}"' if cls else ""
            return (f'<img{c} width="{px_}" height="{px_}" alt="{slug}" '
                    f'src="{uris[key]}"/>')

        rows.append(f"""
<article class="card">
  <div class="meta">
    <span class="num">{html.escape(label(i))}</span>
    <h2>{html.escape(name)}</h2>
    <p>{html.escape(note)}</p>
    <code>{slug}.svg</code>
  </div>
  <div class="sizes">
    <div class="size"><div class="frame big">{img(128,128)}</div><span>128</span></div>
    <div class="size"><div class="frame">{img(48,48)}</div><span>48</span></div>
    <div class="size"><div class="frame">{img(16,16)}</div><span>16 actual</span></div>
    <div class="size"><div class="frame big">{img("zoom",128,"pixelated")}</div><span>16 magnified</span></div>
  </div>
  <div class="bars">
    <div class="bar light">{img(16,16)}<span>light toolbar</span></div>
    <div class="bar dark">{img(16,16)}<span>dark toolbar</span></div>
  </div>
</article>""")

    doc = (f"<title>{html.escape(title)}</title>\n<style>{CSS}</style>\n"
           f"<header>\n  <h1>{html.escape(title)}</h1>\n  <p>{blurb}</p>\n</header>\n"
           f'<div class="grid">{"".join(rows)}</div>\n')

    path = os.path.join(out_dir, out_name)
    with open(path, "w") as fh:
        fh.write(doc)
    return path
