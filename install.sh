#!/usr/bin/env bash
# Install the DaedricMorrowind Aurorae decoration for the current user.  ./install.sh [--apply]
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DST=${XDG_DATA_HOME:-$HOME/.local/share}/aurorae/themes/DaedricMorrowind
mkdir -p "$DST"
cp "$HERE"/*.svg "$HERE/DaedricMorrowindrc" "$HERE/metadata.desktop" "$DST"/
echo "Installed to $DST"
if [[ ${1:-} == --apply ]]; then
    kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae.v2
    # Aurorae SVG themes are named __aurorae__svg__<folder>; a bare name gives no decoration
    kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme __aurorae__svg__DaedricMorrowind
    qdbus6 org.kde.KWin /KWin reconfigure
    echo "Applied."
else
    echo "Select it in System Settings > Colors & Themes > Window Decorations, or rerun with --apply."
fi
