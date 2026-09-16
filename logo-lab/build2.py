#!/usr/bin/env python3
"""Round 2: refinements of the chosen Bookmark mark.

Two problems carried over from round 1, both visible in the round-1 render:
  * the ribbon ran off the tile's rounded top-right corner;
  * the grey body lines were the first thing to grey out at 16px, which is
    what made the mark read as mush in the toolbar.
Every variant here clips the ribbon to the tile and cuts the line count.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sheet import make_sheet

PAPER   = "#FAF4E6"
PAPER_D = "#F2E9D2"
EDGE    = "#DFD2B4"
INK     = "#23211C"
INKSOFT = "#8A8272"
RED     = "#C9553D"
RED_D   = "#A8402C"
YEL     = "#FFD54A"
CREAM   = "#F7EFDC"

V = []
def add(slug, name, note, body):
    V.append((slug, name, note, body))

def clip(cid):
    return (f'<clipPath id="{cid}">'
            f'<rect x="4" y="4" width="120" height="120" rx="30"/></clipPath>')

# The ribbon hangs from the top edge and is clipped to the tile, so its own
# top-right corner picks up the tile's radius instead of jutting past it.
def ribbon(cid, x=74, w=26, bottom=54, notch=12, fill=RED):
    return (f'<g clip-path="url(#{cid})">'
            f'<path d="M{x} 4 h{w} v{bottom - 4} l-{w//2} -{notch} l-{w//2} {notch} Z" '
            f'fill="{fill}"/></g>')

# A -------------------------------------------------------------------------
add("bm-a", "A · As picked, corner fixed",
    "Exactly what you chose. Only the corner overflow is repaired and the two grey lines become one.",
    f"""
{clip('cA')}
<rect x="4" y="4" width="120" height="120" rx="30" fill="{PAPER}" stroke="{EDGE}" stroke-width="3"/>
{ribbon('cA')}
<rect x="24" y="66" width="80" height="18" rx="4" fill="{YEL}"/>
<rect x="24" y="94" width="56" height="7" rx="3.5" fill="{INKSOFT}"/>
""")

# B -------------------------------------------------------------------------
add("bm-b", "B · Ink border",
    "Paper ground kept, but the tile gets a real ink edge and the line goes full-strength ink. Rescues the light version.",
    f"""
{clip('cB')}
<rect x="5.5" y="5.5" width="117" height="117" rx="29" fill="{PAPER}" stroke="{INK}" stroke-width="7"/>
{ribbon('cB')}
<rect x="26" y="66" width="76" height="18" rx="4" fill="{YEL}"/>
<rect x="26" y="94" width="52" height="8" rx="4" fill="{INK}"/>
""")

# C -------------------------------------------------------------------------
add("bm-c", "C · Ink ground",
    "Near-black tile, paper-white line. Same mark, maximum silhouette — the trick that made 01 and 06 win.",
    f"""
{clip('cC')}
<rect x="4" y="4" width="120" height="120" rx="30" fill="{INK}"/>
{ribbon('cC')}
<rect x="24" y="66" width="80" height="18" rx="4" fill="{YEL}"/>
<rect x="24" y="94" width="56" height="8" rx="4" fill="{CREAM}" opacity="0.55"/>
""")

# D -------------------------------------------------------------------------
add("bm-d", "D · Ribbon left",
    "Ribbon moved to the left edge, where a real bookmark sits in a bound page. Band and line shift right of it.",
    f"""
{clip('cD')}
<rect x="4" y="4" width="120" height="120" rx="30" fill="{PAPER}" stroke="{EDGE}" stroke-width="3"/>
{ribbon('cD', x=28, bottom=58)}
<rect x="66" y="30" width="38" height="16" rx="4" fill="{YEL}"/>
<rect x="24" y="74" width="80" height="18" rx="4" fill="{YEL}"/>
<rect x="24" y="102" width="52" height="7" rx="3.5" fill="{INKSOFT}"/>
""")

# E -------------------------------------------------------------------------
add("bm-e", "E · Bold ribbon",
    "Ribbon widened and dropped deeper, band shortened. The red does more of the identifying work.",
    f"""
{clip('cE')}
<rect x="4" y="4" width="120" height="120" rx="30" fill="{PAPER}" stroke="{EDGE}" stroke-width="3"/>
{ribbon('cE', x=68, w=36, bottom=72, notch=16)}
<rect x="24" y="30" width="34" height="16" rx="4" fill="{YEL}"/>
<rect x="24" y="88" width="80" height="18" rx="4" fill="{YEL}"/>
""")

# F -------------------------------------------------------------------------
add("bm-f", "F · Ribbon and band only",
    "Every grey line removed. Two shapes, two colours, nothing that can turn to mush.",
    f"""
{clip('cF')}
<rect x="4" y="4" width="120" height="120" rx="30" fill="{PAPER}" stroke="{EDGE}" stroke-width="3"/>
{ribbon('cF', x=74, w=28, bottom=62, notch=13)}
<rect x="22" y="78" width="84" height="22" rx="5" fill="{YEL}"/>
""")

# G -------------------------------------------------------------------------
add("bm-g", "G · Ink ground, bold ribbon",
    "C and E combined: black ground, wide ribbon, single band. The most legible bookmark I can draw at 16px.",
    f"""
{clip('cG')}
<rect x="4" y="4" width="120" height="120" rx="30" fill="{INK}"/>
{ribbon('cG', x=68, w=36, bottom=70, notch=15)}
<rect x="24" y="86" width="80" height="20" rx="5" fill="{YEL}"/>
<rect x="24" y="34" width="34" height="9" rx="4.5" fill="{CREAM}" opacity="0.5"/>
""")

# H -------------------------------------------------------------------------
add("bm-h", "H · Bare ribbon",
    "No tile at all — the ribbon becomes the whole silhouette, with the band as its shadow. Most distinctive outline, least conventional.",
    f"""
<rect x="20" y="72" width="88" height="22" rx="6" fill="{YEL}"/>
<path d="M36 10 h56 a6 6 0 0 1 6 6 v100 l-34 -30 l-34 30 V16 a6 6 0 0 1 6 -6 Z" fill="{RED}"/>
<path d="M64 86 l34 30 V96 Z" fill="{RED_D}"/>
""")

OUT = os.path.dirname(os.path.abspath(__file__))
path = make_sheet(
    V, OUT, "round2.html",
    "Flow Notes — Bookmark, round 2",
    "Eight refinements of the mark you picked. Ribbon is now clipped to the tile "
    "in every variant, and the grey body lines are cut back or gone, since those "
    "were what dissolved at 16px. Compare the "
    "<strong>16 magnified</strong> column against round 1's bookmark: that is the "
    "whole question.",
    label=lambda i: "ABCDEFGH"[i - 1])
print("wrote", path)
