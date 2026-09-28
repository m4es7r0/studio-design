#!/usr/bin/env bash
source "$(dirname "$0")/lib.sh"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
export CLAUDE_HOME="$tmp/home"; mkdir -p "$CLAUDE_HOME"
out="$(STUDIO_PY=/usr/bin/false "$REPO/scripts/preflight.sh")"; assert_eq 1 $? "fails on a bare machine"
assert_contains "$out" "❌ studio python (PyMuPDF, fontTools, brotli) — fix: $REPO/scripts/setup-python.sh" "names the python fix"
assert_contains "$out" "❌ skill studio-design — fix: $REPO/scripts/install.sh" "names the install fix"
assert_contains "$out" "❌ skill grilling — fix: $HOME/job/agent-skills/install.sh" "names the agent-skills fix"
assert_contains "$out" "PREFLIGHT FAIL" "fail summary"
for s in studio-design grilling hallmark design-agent mobile-design-patterns auditing-accessibility; do
  mkdir -p "$CLAUDE_HOME/skills/$s"; echo x > "$CLAUDE_HOME/skills/$s/SKILL.md"
done
mkdir -p "$CLAUDE_HOME/plugins/cache/official/figma/1.0.0/skills/figma-use"; echo x > "$CLAUDE_HOME/plugins/cache/official/figma/1.0.0/skills/figma-use/SKILL.md"
mkdir -p "$CLAUDE_HOME/agents"
for a in tz-analyst studio-design-reviewer studio-design-figma-builder design-scout; do echo x > "$CLAUDE_HOME/agents/$a.md"; done
fakepy="$tmp/py"; printf '#!/bin/sh\nexit 0\n' > "$fakepy"; chmod +x "$fakepy"
out="$(STUDIO_PY="$fakepy" "$REPO/scripts/preflight.sh")"; assert_eq 0 $? "passes when everything is present"
assert_contains "$out" "PREFLIGHT OK" "ok summary"
finish
