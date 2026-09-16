#!/bin/sh
# Renders the Chrome Web Store listing images from the stage pages here.
#
#   ./render.sh
#
# The screenshots use the REAL popup.html and content.js, driven by stub.js
# (a stand-in for the chrome.* APIs with sample notes), so what the store
# shows is the actual UI rather than a mockup.
#
# Output: out/*.png at the exact sizes the store asks for, as 24-bit RGB --
# the store rejects any PNG with an alpha channel.
#
# Rendering is forced to the LIGHT colour scheme (preferredColorScheme=1).
# Headless Chrome otherwise follows the Mac's appearance, and the ruled-paper
# light theme is the one the listing should show.
#
# NOTE: keep this file ASCII-only -- see package.sh for why.
set -eu
cd "$(dirname "$0")"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "Google Chrome not found at $CHROME" >&2; exit 1; }

mkdir -p build out

# The real popup, with the stub loaded ahead of popup.js.
sed -e 's#<script src="popup.js"></script>#<script src="../stub.js"></script><script src="../../popup.js"></script>#' \
    ../popup.html > build/popup-demo.html
grep -q 'stub.js' build/popup-demo.html || {
    echo "could not inject the stub into popup.html -- did its script tag change?" >&2
    exit 1
}

PROFILES=$(mktemp -d)
trap 'rm -rf "$PROFILES"' EXIT

shot() {
    page=$1; name=$2; w=$3; h=$4
    raw="build/$name-raw.png"
    rm -f "$raw"
    # A fresh profile per shot, so a straggling helper from the previous
    # shot cannot hold the profile lock.
    profile=$(mktemp -d "$PROFILES/p.XXXXXX")
    "$CHROME" --headless=new --disable-gpu --hide-scrollbars --no-first-run \
        --no-default-browser-check --disable-extensions \
        --user-data-dir="$profile" --force-device-scale-factor=1 \
        --window-size="$w,$h" --virtual-time-budget=4000 \
        --blink-settings=preferredColorScheme=1 \
        --screenshot="$raw" "file://$PWD/$page" >/dev/null 2>&1 &
    pid=$!
    # Headless Chrome writes the screenshot and then, on some pages, never
    # exits. So wait for a COMPLETE file -- the IEND chunk is the last thing
    # written -- and then stop Chrome ourselves.
    i=0
    until [ -s "$raw" ] && tail -c 12 "$raw" | grep -q IEND; do
        i=$((i + 1))
        if [ "$i" -gt 60 ]; then
            kill "$pid" 2>/dev/null || true
            echo "timed out rendering $page" >&2
            exit 1
        fi
        sleep 0.5
    done
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
    python3 flatten.py "build/$name-raw.png" "out/$name.png" "$w" "$h"
    echo "  out/$name.png  ${w}x${h}"
}

echo "Rendering:"
shot shot-1-capture.html   screenshot-1-capture   1280 800
shot shot-2-popup.html     screenshot-2-notes     1280 800
shot shot-3-summarise.html screenshot-3-summarise 1280 800
shot shot-4-privacy.html   screenshot-4-privacy   1280 800
shot tile-small.html       promo-small-440x280    440  280
shot tile-marquee.html     promo-marquee-1400x560 1400 560
