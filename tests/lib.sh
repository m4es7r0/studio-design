# tests/lib.sh — tiny assertion helpers for bash tests. Source it; call finish at the end.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILS=0
pass() { echo "  ok   $1"; }
fail() { echo "  FAIL $1"; FAILS=$((FAILS + 1)); }
assert_eq() { if [ "$1" = "$2" ]; then pass "$3"; else fail "$3 (expected '$1', got '$2')"; fi; }
assert_contains() { case "$1" in *"$2"*) pass "$3" ;; *) fail "$3 (missing '$2')" ;; esac; }
assert_link() { if [ -L "$1" ] && [ "$(readlink "$1")" = "$2" ]; then pass "link $1"; else fail "link $1 -> $2"; fi; }
assert_file() { if [ -f "$1" ]; then pass "file $1"; else fail "file $1"; fi; }
finish() { if [ "$FAILS" -eq 0 ]; then echo "PASS $(basename "$0")"; else echo "FAIL $(basename "$0"): $FAILS"; exit 1; fi; }
