#!/usr/bin/env bash
source "$(dirname "$0")/lib.sh"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
fake="$tmp/repo"; mkdir -p "$fake/scripts" "$fake/skills/demo" "$fake/agents"
cp "$REPO/scripts/install.sh" "$fake/scripts/"
printf -- '---\nname: demo\ndescription: x\n---\n' > "$fake/skills/demo/SKILL.md"
printf -- '---\nname: demo-agent\ndescription: x\nmodel: opus\n---\n' > "$fake/agents/demo-agent.md"
export CLAUDE_HOME="$tmp/home"
out="$("$fake/scripts/install.sh")"; assert_eq 0 $? "first install exits 0"
assert_link "$CLAUDE_HOME/skills/demo" "$fake/skills/demo"
assert_link "$CLAUDE_HOME/agents/demo-agent.md" "$fake/agents/demo-agent.md"
out="$("$fake/scripts/install.sh")"; assert_eq 0 $? "second install exits 0"
assert_contains "$out" "ok       $CLAUDE_HOME/skills/demo" "second run keeps the link"
rm "$CLAUDE_HOME/skills/demo"; mkdir "$CLAUDE_HOME/skills/demo"
out="$("$fake/scripts/install.sh")"; assert_eq 1 $? "a foreign folder blocks the install"
assert_contains "$out" "skipped  $CLAUDE_HOME/skills/demo" "reports the conflict"
finish
