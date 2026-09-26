#!/usr/bin/env bash
# Builds the studio venv (.venv) with the pipeline's Python dependencies.
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
python3 -m venv "$repo/.venv"
"$repo/.venv/bin/pip" install --quiet --upgrade pip
"$repo/.venv/bin/pip" install --quiet -r "$repo/requirements.txt"
"$repo/.venv/bin/python" -c "import pymupdf, fontTools, brotli; print('studio python ready')"
