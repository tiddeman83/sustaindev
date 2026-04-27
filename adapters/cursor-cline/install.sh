#!/bin/sh
#
# install.sh — install SustainDev's Cursor and/or Cline rules templates
# into the project root.
#
# Run from your PROJECT root (not from the SustainDev checkout):
#
#   ~/sustaindev/adapters/cursor-cline/install.sh             # both
#   ~/sustaindev/adapters/cursor-cline/install.sh --cursor    # cursor only
#   ~/sustaindev/adapters/cursor-cline/install.sh --cline     # cline only
#
# Behavior:
#   - Copies .cursorrules.template to <project>/.cursorrules
#   - Copies .clinerules.template to <project>/.clinerules
#   - Refuses to overwrite an existing .cursorrules or .clinerules
#     (prints a merge instruction and exits non-zero for any conflict).
#
# Override target with --target if you want a different destination
# directory:
#
#   ~/sustaindev/adapters/cursor-cline/install.sh --target /path/to/project
#
# After install, fill in the <placeholder> values for your project.
# The templates expect a SustainDev project layer (PROJECT_CONTEXT.md,
# CODEMAP.md, VERIFY.md, AI_POLICY.md, MAINTAINABILITY_NOTES.md,
# DECISIONS.md, RISKS.md). See docs/adoption/getting-started.md.

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
CURSOR_TEMPLATE="$SCRIPT_DIR/.cursorrules.template"
CLINE_TEMPLATE="$SCRIPT_DIR/.clinerules.template"

INSTALL_CURSOR=1
INSTALL_CLINE=1
TARGET_DIR=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --cursor)
      INSTALL_CLINE=0; shift
      ;;
    --cline)
      INSTALL_CURSOR=0; shift
      ;;
    --target)
      [ "$#" -ge 2 ] || { echo "ERROR: --target requires a path"; exit 2; }
      TARGET_DIR="$2"; shift 2
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

if [ -z "$TARGET_DIR" ]; then
  TARGET_DIR=$(pwd)
fi

if [ ! -d "$TARGET_DIR" ]; then
  echo "ERROR: target directory does not exist: $TARGET_DIR" >&2
  exit 2
fi

install_one() {
  src="$1"
  dst="$2"
  label="$3"

  if [ ! -f "$src" ]; then
    echo "ERROR: template not found at $src" >&2
    return 1
  fi

  if [ -f "$dst" ]; then
    cat <<EOF >&2
ERROR: $dst already exists. The installer refuses to overwrite an
       existing $label rules file (your rules are likely valuable).

Manual merge:
  1. Open both files side by side:
       $src
       $dst
  2. Copy the "Read Before Acting", "Verification Commands", "AI Policy",
     and "Maintainability Constraints" sections from the template into
     your existing file, preserving any project-specific rules you
     already have.
  3. Save.

If you actually want to overwrite, remove the file first:
  rm "$dst"
  $0
EOF
    return 3
  fi

  cp "$src" "$dst"
  echo "Installed: $dst"
}

count=0
errors=0

if [ "$INSTALL_CURSOR" -eq 1 ]; then
  if install_one "$CURSOR_TEMPLATE" "$TARGET_DIR/.cursorrules" "Cursor"; then
    count=$((count + 1))
  else
    errors=$((errors + 1))
  fi
fi

if [ "$INSTALL_CLINE" -eq 1 ]; then
  if install_one "$CLINE_TEMPLATE" "$TARGET_DIR/.clinerules" "Cline"; then
    count=$((count + 1))
  else
    errors=$((errors + 1))
  fi
fi

if [ "$count" -eq 0 ]; then
  exit 3
fi

cat <<EOF

Installed $count rules file(s) into $TARGET_DIR.

Next steps:
  1. Open the installed file(s) and replace every <placeholder> for
     your project (project-name, one-line description, paragraph).
  2. Verify your project has the SustainDev layer files:
       PROJECT_CONTEXT.md  CODEMAP.md  VERIFY.md
       AI_POLICY.md        MAINTAINABILITY_NOTES.md
       DECISIONS.md        RISKS.md
     If any are missing, scaffold them from core/templates/ in your
     SustainDev checkout. See docs/adoption/getting-started.md.
  3. For Cursor: restart Cursor or reload the workspace so it picks up
     the new .cursorrules.
  4. For Cline: open the VS Code command palette and run
     "Cline: Reload" or simply restart the extension host.

EOF

if [ "$errors" -gt 0 ]; then
  exit 3
fi
