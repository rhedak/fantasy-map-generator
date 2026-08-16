#!/usr/bin/env bash
# Re-render every named world preset into ref-out/.
#
# ref-out/ is the only generated output under version control, and the
# README displays it (same pattern as ../anime-character-creator's own
# ref-out/). It is meant to be the *current* state of the WORLDS registry
# rather than a snapshot of a past one, so run this in the same change as any
# world/render edit; miss it and the README shows maps the code no longer
# produces.
#
#   ./refresh-ref-out.sh          re-render, report which files moved
#   ./refresh-ref-out.sh --check  compare only, write nothing, exit 1 if stale
#
# Worlds come from `worlds.WORLDS`, read out of the installed package, so
# adding a preset there is adding it here too -- nothing about the names
# below is baked in. Every world renders at the CLI's own default seed (7)
# for a stable, reproducible gallery.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

check_only=false
case "${1-}" in
    --check) check_only=true ;;
    "") ;;
    *) echo "usage: $(basename "$0") [--check]" >&2; exit 2 ;;
esac

worlds=$(cd "$root" && uv run python -c '
from fantasy_map_generator.worlds import WORLDS
print(" ".join(sorted(WORLDS)))
' 2>/dev/null) || { echo "could not read WORLDS; is the package installed?  uv sync" >&2; exit 1; }

# Render into a staging directory and only copy over ref-out/ once every file
# has come out, same reasoning as anime-character-creator's own script: PNG
# export is best-effort (warns and carries on if cairo is missing), so
# rendering straight into ref-out/ could refresh the SVGs and leave the PNGs
# the README actually displays untouched and stale.
stage="$root/out/.refresh-stage"
rm -rf "$stage"
mkdir -p "$stage"
trap 'rm -rf "$stage"' EXIT

count=0
changed=0
for world in $worlds; do
    count=$((count + 1))
    (cd "$root" && uv run python -m fantasy_map_generator --world "$world" --seed 7 --out "$stage/$world" >/dev/null 2>&1) || {
        echo "render produced no $world.svg/.png (PNG export needs cairo: brew install cairo)" >&2
        exit 1
    }
    for ext in svg png; do
        if [ ! -s "$stage/$world.$ext" ]; then
            echo "render produced no $world.$ext, leaving ref-out/ alone" >&2
            exit 1
        fi
    done
    # The SVG decides, same as the sister repo: deterministic text, where a
    # PNG can differ in bytes for reasons that are not the drawing.
    if cmp -s "$stage/$world.svg" "$root/ref-out/$world.svg" 2>/dev/null; then
        echo "  unchanged  $world"
    else
        changed=$((changed + 1))
        if $check_only; then
            echo "  STALE      $world"
        else
            echo "  updated    $world"
        fi
    fi
done

# A world removed from WORLDS leaves its old render behind, where it goes
# stale invisibly. Called out rather than deleted, same reasoning as the
# sister repo: ref-out/ is committed, and a script that removes tracked files
# without being asked is worse than a stale one.
for existing in "$root"/ref-out/*.svg; do
    [ -e "$existing" ] || continue
    name="$(basename "${existing%.svg}")"
    case " $worlds " in
        *" $name "*) ;;
        *)
            echo "  ORPHAN     $name  (no longer in WORLDS; git rm ref-out/$name.svg ref-out/$name.png)" >&2
            changed=$((changed + 1))
            ;;
    esac
done

if $check_only; then
    if [ "$changed" -gt 0 ]; then
        echo "$changed of $count in ref-out/ do not match the code; run $(basename "$0")" >&2
        exit 1
    fi
    echo "ref-out/ matches the code"
    exit 0
fi

mkdir -p "$root/ref-out"
for world in $worlds; do
    cp "$stage/$world.svg" "$stage/$world.png" "$root/ref-out/"
done
echo "wrote $count renders to ref-out/, $changed changed"
