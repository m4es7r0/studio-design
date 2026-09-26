#!/usr/bin/env bash
source "$(dirname "$0")/lib.sh"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
"$REPO/scripts/validate.sh" >/dev/null; assert_eq 0 $? "the real pipeline validates"
fake="$tmp/repo"; mkdir -p "$fake/scripts" "$fake/agents" "$fake/skills/studio-design/references"
cp "$REPO/scripts/validate.sh" "$fake/scripts/"
printf -- '---\nname: studio-design\ndescription: x\n---\n' > "$fake/skills/studio-design/SKILL.md"
printf -- '---\nname: bad-agent\ndescription: x\nmodel: sonnet\n---\n' > "$fake/agents/bad-agent.md"
printf '## Inputs\n## Steps\n' > "$fake/skills/studio-design/references/stage-00-intake.md"
out="$("$fake/scripts/validate.sh")"; assert_eq 1 $? "a broken pipeline fails"
assert_contains "$out" "FAIL agent bad-agent" "agent without opus fails"
assert_contains "$out" "FAIL stage-00-intake: missing [## Outputs] [## Gate] [## Skills and agents] [## Pitfalls]" "missing headings are named"
assert_contains "$out" "FAIL stage-01-tz-analysis.md missing" "missing stage file is named"
finish
