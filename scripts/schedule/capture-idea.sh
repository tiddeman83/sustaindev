#!/bin/sh
set -eu

# Capture a rough idea as a scheduled-task stub.
# Writes to core/scheduling/queue/captured/ and prints the created file path.

usage() {
  cat <<'EOF'
Usage:
  scripts/schedule/capture-idea.sh [--priority low|medium|high] "idea title"
  scripts/schedule/capture-idea.sh --help

Arguments:
  --priority VALUE   Optional priority: low, medium, or high. Defaults to medium.
  idea title         The rough idea to capture.

Exit codes:
  0  Idea captured.
  2  No title was given or arguments are invalid.
  3  Queue directory is missing.
  4  Title produced an empty slug.
EOF
}

die() {
  code="$1"
  shift
  printf '%s\n' "$*" >&2
  exit "$code"
}

priority="medium"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --priority)
      [ "$#" -ge 2 ] || die 2 "ERROR: --priority requires one of: low, medium, high."
      priority="$2"
      shift 2
      ;;
    --priority=*)
      priority=${1#--priority=}
      shift
      ;;
    --*)
      die 2 "ERROR: unknown option: $1"
      ;;
    *)
      break
      ;;
  esac
done

case "$priority" in
  low|medium|high) ;;
  *) die 2 "ERROR: priority must be one of: low, medium, high." ;;
esac

[ "$#" -gt 0 ] || {
  usage >&2
  exit 2
}

title="$*"
[ -n "$title" ] || die 2 "ERROR: no title given."

queue_dir="core/scheduling/queue/captured"
[ -d "$queue_dir" ] || die 3 "ERROR: missing queue directory '$queue_dir'. Check the repository layout."

today=$(date -u '+%Y-%m-%d')
captured_at=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

slug=$(printf '%s' "$title" \
  | tr '[:upper:]' '[:lower:]' \
  | sed 's/[^a-z0-9]/-/g; s/-\{1,\}/-/g; s/^-//; s/-$//' \
  | cut -c 1-50 \
  | sed 's/-$//')

[ -n "$slug" ] || die 4 "ERROR: title is empty after slug normalization."

base_id="$today-$slug"
id="$base_id"
path="$queue_dir/$id.md"
suffix=2

while [ -e "$path" ]; do
  id="$base_id-$suffix"
  path="$queue_dir/$id.md"
  suffix=$((suffix + 1))
done

{
  printf '%s\n' '---'
  printf 'id: %s\n' "$id"
  printf 'title: %s\n' "$title"
  printf 'captured_at: %s\n' "$captured_at"
  printf 'status: captured\n'
  printf 'priority: %s\n' "$priority"
  printf '%s\n\n' '---'
  printf '## Captured Idea\n\n'
  printf '%s\n' "$title"
} > "$path"

printf '%s\n' "$path"
