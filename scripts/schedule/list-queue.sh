#!/bin/sh
set -eu

usage() {
  cat <<'EOF'
Usage:
  scripts/schedule/list-queue.sh [--status captured|prework-ready|scheduled|completed] [--priority low|medium|high] [--json]
  scripts/schedule/list-queue.sh --help

Options:
  --status VALUE     Show one queue status.
  --priority VALUE   Show one priority.
  --json             Emit a JSON array.

Exit codes: 0 queue listed, 2 invalid arguments.
EOF
}

die() {
  code="$1"; shift; printf '%s\n' "$*" >&2; exit "$code"
}

status_filter=""
priority_filter=""
json=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --json) json=1; shift ;;
    --status) [ "$#" -ge 2 ] || die 2 "ERROR: --status requires a value."; status_filter="$2"; shift 2 ;;
    --status=*) status_filter=${1#--status=}; shift ;;
    --priority) [ "$#" -ge 2 ] || die 2 "ERROR: --priority requires a value."; priority_filter="$2"; shift 2 ;;
    --priority=*) priority_filter=${1#--priority=}; shift ;;
    *) die 2 "ERROR: unknown argument: $1" ;;
  esac
done

case "$status_filter" in ""|captured|prework-ready|scheduled|completed) ;; *) die 2 "ERROR: invalid status." ;; esac
case "$priority_filter" in ""|low|medium|high) ;; *) die 2 "ERROR: invalid priority." ;; esac

queue_root="core/scheduling/queue"
statuses="captured prework-ready scheduled completed"
json_count=0
yaml_value() {
  awk -v key="$1" '
    /^---[[:space:]]*$/ { seen++; next }
    seen == 1 {
      if ($0 ~ "^" key ":[[:space:]]*") {
        sub("^[^:]*:[[:space:]]*", "", $0)
        gsub(/^"|"$/, "", $0)
        print $0
        exit
      }
    }
    seen == 2 { exit }
  ' "$2"
}

[ "$json" -eq 1 ] && printf '[\n'

for status in $statuses; do
  [ -z "$status_filter" ] || [ "$status_filter" = "$status" ] || continue
  dir="$queue_root/$status"
  tmp=$(mktemp "${TMPDIR:-/tmp}/sustaindev-queue.XXXXXX")

  if [ ! -d "$dir" ]; then
    printf 'WARNING: missing queue directory: %s\n' "$dir" >&2
  else
    for file in "$dir"/*.md; do
      [ -e "$file" ] || continue
      id=$(yaml_value id "$file")
      priority=$(yaml_value priority "$file")
      timestamp=$(yaml_value completed_at "$file")
      label="completed"
      if [ -z "$timestamp" ]; then timestamp=$(yaml_value scheduled_at "$file"); label="scheduled"; fi
      if [ -z "$timestamp" ]; then timestamp=$(yaml_value prepared_at "$file"); label="prepared"; fi
      if [ -z "$timestamp" ]; then timestamp=$(yaml_value captured_at "$file"); label="captured"; fi

      if [ -z "$id" ] || [ -z "$priority" ] || [ -z "$timestamp" ]; then
        printf 'malformed|%s\n' "$file" >> "$tmp"; continue
      fi
      [ -z "$priority_filter" ] || [ "$priority_filter" = "$priority" ] || continue
      printf '%s|%s|%s|%s|%s\n' "$timestamp" "$id" "$priority" "$label" "$file" >> "$tmp"
    done
  fi

  if [ "$json" -eq 1 ]; then
    sorted=$(mktemp "${TMPDIR:-/tmp}/sustaindev-queue-sorted.XXXXXX")
    sort -r "$tmp" > "$sorted"
    while IFS='|' read -r timestamp id priority label file; do
      [ -n "$timestamp" ] || continue
      [ "$json_count" -eq 0 ] || printf ',\n'
      if [ "$timestamp" = "malformed" ]; then
        printf '  {"malformed":"%s"}' "$id"
      else
        printf '  {"status":"%s","id":"%s","priority":"%s","timestamp_label":"%s","timestamp":"%s","file":"%s"}' "$status" "$id" "$priority" "$label" "$timestamp" "$file"
      fi
      json_count=$((json_count + 1))
    done < "$sorted"
    rm -f "$sorted"
  else
    count=$(wc -l < "$tmp" | tr -d ' ')
    printf '%s (%s):\n' "$status" "$count"
    if [ "$count" -eq 0 ]; then
      printf '  (none)\n\n'
    else
      sort -r "$tmp" | while IFS='|' read -r timestamp id priority label file; do
        if [ "$timestamp" = "malformed" ]; then
          printf '  (malformed: %s)\n' "$id"
        else
          printf '  %-36s %-7s %s %s\n' "$id" "$priority" "$label" "$timestamp"
        fi
      done
      printf '\n'
    fi
  fi
  rm -f "$tmp"
done
[ "$json" -eq 1 ] && printf '\n]\n'
exit 0
