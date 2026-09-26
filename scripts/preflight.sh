#!/usr/bin/env bash
# Checks what the studio-design pipeline needs on this machine. Prints ✅/❌ per item with a fix for
# each ❌, then «PREFLIGHT OK» or «PREFLIGHT FAIL: N». In-session tools (Figma MCP, artifact type,
# browser, Figma fonts) are checked by the studio-design skill at stage 0.
# Test overrides: CLAUDE_HOME, STUDIO_PY.
set -uo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
home="${CLAUDE_HOME:-$HOME/.claude}"
py="${STUDIO_PY:-$repo/.venv/bin/python}"
bad=0
ok() { echo "✅ $1"; }
no() { echo "❌ $1 — fix: $2"; bad=$((bad + 1)); }
fix_skill() {
  case "$1" in
    studio-design) echo "$repo/scripts/install.sh" ;;
    grilling) echo "$HOME/job/agent-skills/install.sh" ;;
    design-agent|mobile-design-patterns) echo "$HOME/design-intelligence-agent/scripts/install.sh" ;;
    *) echo "install the skill, see $repo/docs/manifest.md › Skills" ;;
  esac
}
fix_agent() {
  case "$1" in
    design-scout) echo "$HOME/design-intelligence-agent/scripts/install.sh" ;;
    *) echo "$repo/scripts/install.sh" ;;
  esac
}

if [ -x "$py" ] && "$py" -c 'import pymupdf, fontTools, brotli' >/dev/null 2>&1; then ok "studio python (PyMuPDF, fontTools, brotli)"
else no "studio python (PyMuPDF, fontTools, brotli)" "$repo/scripts/setup-python.sh"; fi
nv="$(node --version 2>/dev/null | sed 's/^v//' | cut -d. -f1)"
if [ -n "$nv" ] && [ "$nv" -ge 20 ]; then ok "node $(node --version)"; else no "node 20 or newer" "install Node.js 20+ from https://nodejs.org"; fi
if command -v npx >/dev/null 2>&1; then ok "npx"; else no "npx" "reinstall Node.js with npm"; fi
if git config user.name >/dev/null && git config user.email >/dev/null; then ok "git identity"
else no "git identity" "git config --global user.name 'Name' && git config --global user.email 'mail'"; fi
if command -v lsof >/dev/null 2>&1; then ok "lsof"; else no "lsof" "install lsof (new-client.sh uses it to pick a free harness port)"; fi
for s in studio-design grilling hallmark design-agent mobile-design-patterns; do
  if [ -f "$home/skills/$s/SKILL.md" ]; then ok "skill $s"; else no "skill $s" "$(fix_skill "$s")"; fi
done
if ls "$home"/plugins/cache/*/figma/*/skills/figma-use/SKILL.md >/dev/null 2>&1; then ok "Figma plugin skills (figma-use, figma-generate-library, figma-generate-design)"
else no "Figma plugin skills" "install the Figma plugin for Claude Code (claude-plugins-official › figma)"; fi
for a in tz-analyst studio-design-reviewer studio-design-figma-builder design-scout; do
  if [ -f "$home/agents/$a.md" ]; then ok "agent $a"; else no "agent $a" "$(fix_agent "$a")"; fi
done
if [ "$bad" -eq 0 ]; then echo "PREFLIGHT OK"; exit 0; fi
echo "PREFLIGHT FAIL: $bad"
exit 1
