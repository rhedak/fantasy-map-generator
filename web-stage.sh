#!/usr/bin/env bash
# Assemble the deployable static site into out/web-stage/.
#
# web/index.html loads app.js and style.css (split out from what used to be
# one inline file, later session, matching ../anime-character-creator's own
# index.html/app.js/style.css layout), then app.js bootstraps Pyodide and
# fetches "bridge.py", "src/fantasy_map_generator-files.json", and the
# package files themselves as plain relative paths, which only resolve
# correctly if those files are siblings of index.html at whatever root
# serves the page. They are not siblings in the repository: web/ sits at the
# top level and src/fantasy_map_generator/ is shared with the Python
# package, on purpose.
# This script does the one thing that reconciles the two: copy the pieces into
# one flat directory, which is what both a local test server and the GitHub
# Actions deploy (.github/workflows/pages.yml) serve from, so neither can
# disagree with the other about the layout.
#
#   ./web-stage.sh            stage into out/web-stage/
#   ./web-stage.sh --serve    stage, then serve it on http://localhost:8000
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
stage="$root/out/web-stage"

rm -rf "$stage"
mkdir -p "$stage"
cp "$root"/web/*.html "$stage/"
cp "$root/web/app.js" "$stage/"
cp "$root/web/style.css" "$stage/"
cp "$root"/web/*.jpg "$stage/"
cp "$root/web/bridge.py" "$stage/"
mkdir -p "$stage/src/fantasy_map_generator"
rsync -a --exclude '__pycache__' --exclude '*.pyc' \
    "$root/src/fantasy_map_generator/." "$stage/src/fantasy_map_generator/"

# Manifest of package files (relative paths, JSON) that web/index.html fetches
# into the in-browser Pyodide filesystem.
(
    cd "$stage/src/fantasy_map_generator"
    find . -name '*.py' -type f | sort | sed 's#^\./##'
) | python3 -c 'import json, sys; print(json.dumps([l.rstrip("\n") for l in sys.stdin]))' \
    > "$stage/src/fantasy_map_generator-files.json"

echo "staged at $stage"

if [ "${1-}" = "--serve" ]; then
    cd "$stage"
    python3 -m http.server 8000
fi
