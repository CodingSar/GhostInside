#!/usr/bin/env bash
# Deterministic checks on the harness. Exit 0 when clean, 1 otherwise.
# Run before each harness commit.

set -u

root="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$root" || exit 1

fail=0
bad() { echo "FAIL: $*"; fail=1; }

# Template-owned paths (HD-9). In a product clone they never change.
core_paths="meta/core meta/_about.md AGENTS.md CLAUDE.md .claude/skills/init-factory
  .claude/agents/test-writer.md .claude/agents/implementer.md"

# 1. Every harness path named by agents, skills, guides, or catalogs exists.
#    Product files that exist only after init-factory, or only on override, are optional.
optional='^meta/product/(architecture\.md|persistence\.md|overlays/|practices/packs/)'
refs=$(grep -rhoE '(meta|\.claude)/[A-Za-z0-9_./-]+\.(md|sh|py|yml|json)' \
  AGENTS.md .claude/agents .claude/skills meta/_about.md meta/core/guides meta/core/defaults \
  meta/core/decisions.md meta/core/design.md meta/product 2>/dev/null | sort -u)
for ref in $refs; do
  [ -e "$ref" ] || echo "$ref" | grep -qE "$optional" || bad "referenced path missing: $ref"
done

# 2. No headless launch anywhere in the harness (backlog history excluded).
if grep -rn 'claude -p' .claude meta --include='*.md' --exclude-dir=backlog; then
  bad "headless launch reference found (see above)"
fi

# 3. Every worker runs on Haiku for now, and names the guide it reads first.
for agent in .claude/agents/*.md; do
  grep -q '^model: claude-haiku-5-5$' "$agent" || bad "$agent is not on claude-haiku-5-5"
  grep -q 'meta/core/guides/' "$agent" || bad "$agent names no guide"
done

# 4. Vendored practice packs match their lock.
if [ -f meta/product/practices/practices.lock ]; then
  python3 -I meta/core/tools/practices.py verify >/dev/null || bad "practices.py verify failed"
fi

# 5. The harness tools pass their tests.
for t in meta/core/tools/test_*.py; do
  python3 -I "$t" >/dev/null 2>&1 || bad "$t failed"
done

# 6. Once init-factory has set the stack, no TBD may remain in it.
if ! grep -q '^Status: TBD' meta/product/stack.md; then
  if grep -n 'TBD' meta/product/stack.md; then
    bad "stack is set but still has TBD (see above)"
  fi
fi

# 7. In a product clone, template-owned paths match the last merged harness version.
if git rev-parse -q --verify harness/main >/dev/null 2>&1; then
  base=$(git merge-base HEAD harness/main 2>/dev/null)
  if [ -z "$base" ]; then
    bad "no shared history with harness/main"
  else
    # shellcheck disable=SC2086
    changed=$(git diff --name-only "$base" -- $core_paths)
    [ -z "$changed" ] || bad "template-owned paths changed in this clone (change them in the template): $changed"
  fi
fi

if [ "$fail" -eq 0 ]; then
  echo "ok: harness checks passed"
fi
exit "$fail"
