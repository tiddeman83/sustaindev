#!/bin/sh
#
# install.sh — copy SustainDev's Warp Workflow YAMLs into the user's
# Warp launch_configurations directory.
#
# Default Warp directory: ~/.warp/launch_configurations/
# (Warp uses this folder for both Workflows and Launch Configurations
# in current versions; older versions used ~/.warp/workflows/.)
#
# Pass an explicit destination via $WARP_WORKFLOWS_DIR if your Warp
# install uses a different path:
#
#   WARP_WORKFLOWS_DIR=~/.warp/workflows ./install.sh
#
# Idempotent: re-running just overwrites the four files.

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
WORKFLOWS_SRC="$SCRIPT_DIR/workflows"

if [ ! -d "$WORKFLOWS_SRC" ]; then
  echo "ERROR: workflows directory not found at $WORKFLOWS_SRC" >&2
  exit 1
fi

# Resolve destination.
if [ -n "${WARP_WORKFLOWS_DIR:-}" ]; then
  DEST="$WARP_WORKFLOWS_DIR"
elif [ -d "$HOME/.warp/launch_configurations" ]; then
  DEST="$HOME/.warp/launch_configurations"
elif [ -d "$HOME/.warp/workflows" ]; then
  DEST="$HOME/.warp/workflows"
else
  # Default to launch_configurations and create it.
  DEST="$HOME/.warp/launch_configurations"
fi

mkdir -p "$DEST"
echo "Installing SustainDev Warp workflows into: $DEST"

count=0
for f in "$WORKFLOWS_SRC"/*.yaml; do
  [ -e "$f" ] || continue
  base=$(basename "$f")
  cp "$f" "$DEST/$base"
  echo "  $base"
  count=$((count + 1))
done

if [ "$count" -eq 0 ]; then
  echo "WARNING: no .yaml files found in $WORKFLOWS_SRC" >&2
  exit 2
fi

cat <<EOF

Installed $count Warp workflow(s).

Open Warp, hit Cmd+Shift+R, and search "SustainDev" to see them.

Notes:
  - The workflow YAMLs assume SustainDev lives at ~/sustaindev. If yours
    is elsewhere, edit the 'command' line in each YAML to point at
    your install path.
  - The probe-script workflows (Prepare task, Triage files) require
    LM Studio to be running with a model loaded. See
    adapters/lm-studio/usage.md for setup.
  - To uninstall, delete the four files matching SustainDev*.yaml from
    $DEST.
EOF
