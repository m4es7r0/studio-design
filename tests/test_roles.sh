#!/usr/bin/env bash
# Role checks: studio-design runs the process and calls skills by the role map
# (~/job/agent-skills/docs/design-skills-role-map.md); it holds no design doctrine a skill owns.
source "$(dirname "$0")/lib.sh"
skill="$REPO/skills/studio-design"
refs="$skill/references"

assert_eq "" "$(grep -rln "hallmark" "$skill")" "no stage calls hallmark (only the reviewer reads its audit files)"
assert_eq "" "$(grep -rlnE "design-scout|frontend-design|ersatz" "$skill")" "no stage calls design-scout, frontend-design or ersatz directly"
assert_contains "$(cat "$skill/SKILL.md")" "design-agent" "SKILL.md names design-agent"
assert_contains "$(cat "$skill/SKILL.md")" "attmpt-design" "SKILL.md names attmpt-design"

for f in "$refs"/stage-*.md; do
  n="$(basename "$f" .md)"
  if grep -q "Figma" "$f"; then
    if grep -qE '`Figma: (yes|no)`' "$f"; then pass "$n names the Figma switch"; else fail "$n mentions Figma without the \`Figma: yes|no\` switch"; fi
  fi
  if grep -qi "artifact" "$f"; then
    if grep -q '`Artifact:' "$f"; then pass "$n names the Artifact switch"; else fail "$n mentions the artifact without the \`Artifact:\` switch"; fi
  fi
done

project="$(cat "$REPO/template/design/PROJECT.md")"
for line in "- Figma:" "- Artifact:" "- Themes:" "- Locale:" "- Parts:" "- Directions:" "- Review passes:"; do
  assert_contains "$project" "$line" "PROJECT.md template has «$line»"
done

reviewer="$REPO/agents/studio-design-reviewer.md"
for p in $(grep -oE '~/[A-Za-z0-9_./-]*hallmark[A-Za-z0-9_./-]*\.md' "$reviewer" | sort -u); do
  assert_file "${p/#\~/$HOME}"
done
# Final-review fixes (2026-10-22).
rev="$(cat "$reviewer")"
case "$(grep '^tools:' "$reviewer")" in *Write*) pass "the reviewer can write its report file" ;; *) fail "the reviewer has no Write tool for its report file" ;; esac
assert_contains "$rev" "your report file is your one write" "the reviewer's only write is its report"
assert_file "$REPO/template/design/reports/.gitkeep"
assert_contains "$(cat "$REPO/docs/rules/design.md")" "until the template ships a contrast script" "rules name the interim contrast method"
assert_contains "$(cat "$refs/stage-02-direction.md")" "design/directions/frozen/" "stage 2 names the frozen sketch path"
assert_contains "$(sed -n '/^## Gate/,/^## /p' "$refs/stage-02-direction.md")" "design/directions/frozen/" "the stage 2 gate checks the frozen sketch"
for n in 04-foundations 05-components; do
  assert_contains "$(sed -n '/^## Inputs/,/^## /p' "$refs/stage-$n.md")" "design/directions/frozen/" "stage $n reads the frozen sketch by path"
done
for n in 03-layout-budget 04-foundations 05-components 06-screens 07-figma; do
  assert_contains "$(cat "$refs/stage-$n.md")" "«to confirm» rows are not empty" "stage $n asks its «to confirm» rows before the gate"
done
finish
