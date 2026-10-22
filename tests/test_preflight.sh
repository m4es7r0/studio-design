#!/usr/bin/env bash
source "$(dirname "$0")/lib.sh"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
export CLAUDE_HOME="$tmp/home"; mkdir -p "$CLAUDE_HOME"
export HALLMARK_ROOT="$tmp/hallmark"
out="$(STUDIO_PY=/usr/bin/false "$REPO/scripts/preflight.sh")"; assert_eq 1 $? "fails on a bare machine"
assert_contains "$out" "❌ studio python (PyMuPDF, fontTools, brotli) — fix: $REPO/scripts/setup-python.sh" "names the python fix"
assert_contains "$out" "❌ skill studio-design — fix: $REPO/scripts/install.sh" "names the install fix"
assert_contains "$out" "❌ skill grilling — fix: $HOME/job/agent-skills/install.sh" "names the agent-skills fix"
assert_contains "$out" "❌ skill attmpt-design — fix: $HOME/design-intelligence-agent/scripts/install.sh" "names the attmpt-design fix"
assert_contains "$out" "❌ hallmark audit file references/verbs/audit.md" "names a missing hallmark audit file"
assert_contains "$out" "PREFLIGHT FAIL" "fail summary"
for s in studio-design grilling attmpt-design design-agent mobile-design-patterns auditing-accessibility; do
  mkdir -p "$CLAUDE_HOME/skills/$s"; echo x > "$CLAUDE_HOME/skills/$s/SKILL.md"
done
mkdir -p "$CLAUDE_HOME/skills/design-agent/references"; echo x > "$CLAUDE_HOME/skills/design-agent/references/hallmark-waivers.md"
for f in references/verbs/audit.md references/slop-test.md references/anti-patterns.md; do mkdir -p "$(dirname "$HALLMARK_ROOT/$f")"; echo x > "$HALLMARK_ROOT/$f"; done
mkdir -p "$CLAUDE_HOME/agents"
for a in tz-analyst studio-design-reviewer studio-design-figma-builder design-scout; do echo x > "$CLAUDE_HOME/agents/$a.md"; done
fakepy="$tmp/py"; printf '#!/bin/sh\nexit 0\n' > "$fakepy"; chmod +x "$fakepy"
out="$(STUDIO_PY="$fakepy" "$REPO/scripts/preflight.sh")"; assert_eq 0 $? "passes when everything is present"
assert_contains "$out" "PREFLIGHT OK" "ok summary (no hallmark skill link, no Figma plugin needed)"
assert_contains "$out" "ℹ Figma plugin skills: absent — needed only with \`Figma: yes\`" "the Figma plugin row is informational"
case "$out" in *"skill hallmark"*) fail "preflight does not ask for a hallmark skill link" ;; *) pass "preflight does not ask for a hallmark skill link" ;; esac
finish
