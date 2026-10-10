#!/usr/bin/env bash
# Deterministic checks on the harness. Exit 0 when clean, 1 otherwise.
# Run before each harness commit.

set -u

root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$root" || exit 1

fail=0
bad() { echo "FAIL: $*"; fail=1; }

# 1. Every harness path named by agents, guides, or catalogs exists.
refs=$(grep -rhoE '(meta|\.claude)/[A-Za-z0-9_./-]+\.(md|sh|yml|json)' \
  .claude/agents meta/guides meta/_about.md meta/architecture meta/registry meta/practices 2>/dev/null \
  | sort -u)
for ref in $refs; do
  [ -e "$ref" ] || bad "referenced path missing: $ref"
done

# 2. No headless launch anywhere in the harness.
if grep -rn 'claude -p' .claude meta --include='*.md'; then
  bad "headless launch reference found (see above)"
fi

# 3. No plan files: plans live in Backlog.
if grep -rn 'meta/plans' .claude meta PLAN.md AGENTS.md --include='*.md'; then
  bad "reference to meta/plans found (see above)"
fi

# 4. Every worker runs on Haiku for now.
for agent in .claude/agents/*.md; do
  grep -q '^model: claude-haiku-5-5$' "$agent" || bad "$agent is not on claude-haiku-5-5"
done

# 5. Every worker names a guide to read first.
for agent in .claude/agents/*.md; do
  grep -q 'meta/guides/' "$agent" || bad "$agent names no guide"
done

if [ "$fail" -eq 0 ]; then
  echo "ok: harness checks passed"
fi
exit "$fail"
