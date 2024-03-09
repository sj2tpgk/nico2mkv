#!/bin/bash

SCRIPTDIR="$(dirname "$(realpath "$0")")"
VENVDIR="$SCRIPTDIR/nico2mkv/.venv-unix"

[ ! -d "$VENVDIR" ] && { echo "Creating venv ..."; python3 -m venv "$VENVDIR"; }
source "$VENVDIR/bin/activate"

python3 "$SCRIPTDIR/nico2mkv/nico2mkv.py" "$@"
