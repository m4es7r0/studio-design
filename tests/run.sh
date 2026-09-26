#!/usr/bin/env bash
# tests/run.sh — runs every test of the pipeline repository.
set -uo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"; status=0
for t in "$repo"/tests/test_*.sh; do [ -f "$t" ] || continue; bash "$t" || status=1; done
if ls "$repo"/tests/js/*.test.js >/dev/null 2>&1; then node --test "$repo"/tests/js/*.test.js || status=1; fi
if ls "$repo"/tests/py/test_*.py >/dev/null 2>&1; then "$repo/scripts/py" -m unittest discover -s "$repo/tests/py" || status=1; fi
if [ "$status" -eq 0 ]; then echo "ALL TESTS PASS"; else echo "TESTS FAILED"; fi
exit "$status"
