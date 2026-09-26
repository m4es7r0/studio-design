#!/usr/bin/env bash
# Creates a client container from template/.
# Usage: new-client.sh <slug> [--name "Client name"] [--port N]
# CLIENTS_DIR overrides the parent folder (default ~/job/clients).
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
clients="${CLIENTS_DIR:-$HOME/job/clients}"
usage() { echo "usage: new-client.sh <slug: a-z first, then a-z 0-9 -> [--name \"Client name\"] [--port N]" >&2; exit 2; }
[ $# -ge 1 ] || usage
slug="$1"; shift
[[ "$slug" =~ ^[a-z][a-z0-9-]*$ ]] || usage
name="$slug"; port=""
while [ $# -gt 0 ]; do
  case "$1" in
    --name) [ $# -ge 2 ] || usage; name="$2"; shift 2 ;;
    --port) [ $# -ge 2 ] || usage; port="$2"; shift 2 ;;
    *) usage ;;
  esac
done
dst="$clients/$slug"
if [ -e "$dst" ]; then echo "refusing: $dst already exists" >&2; exit 1; fi
if [ -z "$port" ]; then
  port=5190
  while lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1 || grep -Fqs "\"port\": $port }" "$clients"/*/design/.claude/launch.json; do
    port=$((port + 1))
  done
fi
ns="$(printf '%s' "$slug" | awk -F- '{ for (i = 1; i <= NF; i++) printf "%s%s", toupper(substr($i, 1, 1)), substr($i, 2) }')UI"
mkdir -p "$clients"
cp -R "$repo/template" "$dst"
export SLUG="$slug" NAME="$name" NS="$ns" TODAY="$(date +%Y-%m-%d)" PORT="$port"
{ grep -rlIE '__(CLIENT_SLUG|CLIENT_NAME|NAMESPACE|DATE|PORT)__' "$dst" || true; } | while IFS= read -r f; do
  perl -pi -e 's/__CLIENT_SLUG__/$ENV{SLUG}/g; s/__CLIENT_NAME__/$ENV{NAME}/g; s/__NAMESPACE__/$ENV{NS}/g; s/__DATE__/$ENV{TODAY}/g; s/__PORT__/$ENV{PORT}/g' "$f"
done
git -C "$dst" init -q -b main
git -C "$dst" add -A
git -C "$dst" commit -q -m "Start Client $slug"
cat <<EOF
Created $dst
  namespace  $ns
  port       $port
Next: put the brief into $dst/design/brief/, open $dst/design in Claude Code (desktop app, Code tab)
and say «studio-design: stage 0».
EOF
