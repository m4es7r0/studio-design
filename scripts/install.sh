#!/usr/bin/env bash
# Links skills/* and agents/*.md into $CLAUDE_HOME (default ~/.claude). Idempotent; never overwrites.
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
home="${CLAUDE_HOME:-$HOME/.claude}"
mkdir -p "$home/skills" "$home/agents"
status=0
link() {
  if [ -L "$2" ] && [ "$(readlink "$2")" = "$1" ]; then echo "ok       $2"
  elif [ -e "$2" ] || [ -L "$2" ]; then echo "skipped  $2 exists and is not a link to this repository"; status=1
  else ln -s "$1" "$2"; echo "linked   $2"; fi
}
for d in "$repo"/skills/*/; do [ -d "$d" ] || continue; link "${d%/}" "$home/skills/$(basename "$d")"; done
for f in "$repo"/agents/*.md; do [ -f "$f" ] || continue; link "$f" "$home/agents/$(basename "$f")"; done
exit "$status"
