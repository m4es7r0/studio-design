#!/usr/bin/env bash
# Checks what the studio-design pipeline needs on this machine. Prints ✅/❌ per item with a fix for
# each ❌, then «PREFLIGHT OK» or «PREFLIGHT FAIL: N». In-session tools (Figma MCP, artifact type,
# browser, Figma fonts) are checked by the studio-design skill at stage 0.
# Test overrides: CLAUDE_HOME, STUDIO_PY, HALLMARK_ROOT.
set -uo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
home="${CLAUDE_HOME:-$HOME/.claude}"
hallmark="${HALLMARK_ROOT:-$HOME/.agents/skills/hallmark}"
py="${STUDIO_PY:-$repo/.venv/bin/python}"
bad=0
ok() { echo "✅ $1"; }
no() { echo "❌ $1 — fix: $2"; bad=$((bad + 1)); }
fix_skill() {
  case "$1" in
    studio-design) echo "$repo/scripts/install.sh" ;;
    grilling) echo "$HOME/job/agent-skills/install.sh" ;;
    design-agent|mobile-design-patterns|attmpt-design) echo "$HOME/design-intelligence-agent/scripts/install.sh" ;;
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
for s in studio-design grilling attmpt-design design-agent mobile-design-patterns; do
  if [ -f "$home/skills/$s/SKILL.md" ]; then ok "skill $s"; else no "skill $s" "$(fix_skill "$s")"; fi
done
# hallmark is not a linked skill: only its audit files are read, by studio-design-reviewer (marketing surfaces).
for f in references/verbs/audit.md references/slop-test.md references/anti-patterns.md; do
  if [ -f "$hallmark/$f" ]; then ok "hallmark audit file $f"; else no "hallmark audit file $f" "install hallmark into ~/.agents/skills (npx skills add nutlope/hallmark); do not link it into ~/.claude/skills"; fi
done
if [ -f "$home/skills/design-agent/references/hallmark-waivers.md" ]; then ok "hallmark waivers (design-agent)"
else no "hallmark waivers (design-agent)" "$HOME/design-intelligence-agent/scripts/install.sh"; fi
# Figma is optional (PROJECT.md › Figma: yes); stage 0 checks it in-session when the switch is on.
if ls "$home"/plugins/cache/*/figma/*/skills/figma-use/SKILL.md >/dev/null 2>&1; then echo "ℹ Figma plugin skills: present"
else echo "ℹ Figma plugin skills: absent — needed only with \`Figma: yes\`"; fi
for a in tz-analyst studio-design-reviewer studio-design-figma-builder design-scout; do
  if [ -f "$home/agents/$a.md" ]; then ok "agent $a"; else no "agent $a" "$(fix_agent "$a")"; fi
done
if [ "$bad" -eq 0 ]; then echo "PREFLIGHT OK"; exit 0; fi
echo "PREFLIGHT FAIL: $bad"
exit 1
