#!/usr/bin/env bash
# Structural checks of the pipeline: skill and agent frontmatter (agents run on opus or sonnet), the ten stage references.
set -uo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
status=0
fm() { awk 'NR==1{ if ($0 != "---") exit; next } /^---$/{ exit } { print }' "$1"; }
field() { fm "$1" | sed -n "s/^$2:[[:space:]]*//p" | head -1; }
for f in "$repo"/skills/*/SKILL.md; do
  [ -f "$f" ] || continue
  name="$(basename "$(dirname "$f")")"
  if [ "$(field "$f" name)" = "$name" ] && fm "$f" | grep -q '^description:'; then echo "ok   skill $name"
  else echo "FAIL skill $name: frontmatter needs name and description"; status=1; fi
done
for f in "$repo"/agents/*.md; do
  [ -f "$f" ] || continue
  name="$(basename "$f" .md)"
  model="$(field "$f" model)"
  if [ "$(field "$f" name)" = "$name" ] && fm "$f" | grep -q '^description:' && { [ "$model" = "opus" ] || [ "$model" = "sonnet" ]; }; then echo "ok   agent $name"
  else echo "FAIL agent $name: frontmatter needs name, description and model: opus or sonnet"; status=1; fi
done
refs="$repo/skills/studio-design/references"
for n in 00-intake 01-tz-analysis 02-direction 03-layout-budget 04-foundations 05-components 06-screens 07-figma 08-qa-handoff 09-revisions; do
  f="$refs/stage-$n.md"
  if [ ! -f "$f" ]; then echo "FAIL stage-$n.md missing"; status=1; continue; fi
  miss=""
  for h in "## Inputs" "## Steps" "## Outputs" "## Gate" "## Skills and agents" "## Pitfalls"; do grep -qx "$h" "$f" || miss="$miss [$h]"; done
  if [ -z "$miss" ]; then echo "ok   stage-$n"; else echo "FAIL stage-$n: missing$miss"; status=1; fi
done
exit "$status"
