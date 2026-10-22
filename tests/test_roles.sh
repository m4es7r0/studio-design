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
finish
