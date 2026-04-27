#!/bin/sh
#
# install.sh — install the SustainDev tasks.json into your project's .vscode/.
#
# Run from your PROJECT root (not from the SustainDev checkout):
#
#   ~/sustaindev/adapters/vscode/install.sh
#
# Behavior:
#   - If <project>/.vscode/tasks.json does NOT exist, copy the template there.
#   - If it does exist, print a merge instruction and exit non-zero.
#     (We refuse to overwrite to protect your existing tasks.)
#
# Override target with --target if you want a different destination:
#
#   ~/sustaindev/adapters/vscode/install.sh --target /path/to/.vscode/tasks.json

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TEMPLATE="$SCRIPT_DIR/tasks.json.template"

if [ ! -f "$TEMPLATE" ]; then
  echo "ERROR: template not found at $TEMPLATE" >&2
  exit 1
fi

TARGET=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      [ "$#" -ge 2 ] || { echo "ERROR: --target requires a path"; exit 2; }
      TARGET="$2"; shift 2
      ;;
    --help|-h)
      sed -n '1,/^set -eu/p' "$0" | sed 's/^# //; /^#$/d; /^#!/d; /^set -eu$/d'
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [ -z "$TARGET" ]; then
  PROJECT_ROOT=$(pwd)
  TARGET="$PROJECT_ROOT/.vscode/tasks.json"
fi

TARGET_DIR=$(dirname "$TARGET")
mkdir -p "$TARGET_DIR"

if [ -f "$TARGET" ]; then
  cat <<EOF >&2
ERROR: $TARGET already exists. The installer refuses to overwrite an existing
       tasks.json (your tasks are likely valuable).

Manual merge:
  1. Open both files side by side:
       $TEMPLATE
       $TARGET
  2. Append the entries from "tasks": [...] in the template into your
     existing tasks array. Watch for duplicate "label" values.
  3. Append the entries from "inputs": [...] in the template into your
     existing inputs array. Inputs are keyed by "id"; duplicate ids will
     conflict. Rename or de-duplicate as needed.
  4. Save.

If you actually want to overwrite (you'll lose your existing tasks),
remove the file first:
  rm "$TARGET"
  $0
EOF
  exit 3
fi

cp "$TEMPLATE" "$TARGET"
echo "Installed: $TARGET"

cat <<EOF

Open VS Code in this project, then:
  Cmd/Ctrl+Shift+P  →  Tasks: Run Task  →  pick a "SustainDev — ..." task

On first run, VS Code prompts for the path to your SustainDev checkout.
The default is \$HOME/sustaindev. Set SUSTAINDEV_HOME in your shell config
and edit tasks.json to use \${env:SUSTAINDEV_HOME} for permanent override.

The probe-script tasks (Prepare task, Triage files, Draft catalog,
Extract risks) require LM Studio to be running with a model loaded.
See adapters/lm-studio/usage.md for setup.
EOF
