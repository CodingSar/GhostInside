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
  .claude/agents/intake.md .claude/agents/planner.md .claude/agents/researcher.md
  .claude/agents/test-writer.md .claude/agents/implementer.md .claude/agents/reviewer.md"

# 1. Every harness path named by agents, skills, guides, or catalogs exists.
#    Product files that exist only after init-factory, or only on override, are optional.
optional='^meta/product/(architecture\.md|persistence\.md|overlays/|practices/packs/|screens/)'
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

# 3. Every agent runs on Haiku, except the researcher (HD-16), names the
#    guide it reads first (a core guide, or a product guide for workers
#    init-factory adds), caps its turns, skips CLAUDE.md, and pins its effort.
for agent in .claude/agents/*.md; do
  if [ "$agent" = .claude/agents/researcher.md ]; then
    grep -qE '^model: claude-(sonnet|opus)-' "$agent" || bad "$agent is not on a research model"
  else
    grep -q '^model: claude-haiku-5-5$' "$agent" || bad "$agent is not on claude-haiku-5-5"
  fi
  grep -qE 'meta/(core/guides|product)/' "$agent" || bad "$agent names no guide"
  grep -qE '^maxTurns: [0-9]+$' "$agent" || bad "$agent sets no maxTurns"
  grep -q '^omitClaudeMd: true$' "$agent" || bad "$agent does not omit CLAUDE.md (TASK-10)"
  grep -qE '^effort: (low|medium|high)$' "$agent" || bad "$agent sets no effort (TASK-10)"
done

# 3b. Every loop agent exists, reads its loop guide, and the guide ends in RETURN lines.
python3 -I - <<'PY' || bad "loop agents and guides do not match loop.py (see above)"
import ast, pathlib, sys
src = pathlib.Path("meta/core/tools/loop.py").read_text()
guides = next(ast.literal_eval(n.value) for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "GUIDES")
ok = True
for agent, guide in guides.items():
    a, g = pathlib.Path(f".claude/agents/{agent}.md"), pathlib.Path(guide)
    if not a.exists() or guide not in a.read_text():
        print(f"{a} missing or does not name {guide}"); ok = False
    if not g.exists() or "RETURN ok" not in g.read_text():
        print(f"{guide} missing or has no RETURN ok line"); ok = False
sys.exit(0 if ok else 1)
PY

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
    # Deny entries, hooks, and the main-thread model in settings.json are
    # template-owned; allow entries are not.
    git show "$base:.claude/settings.json" 2>/dev/null | python3 -I -c '
import json, sys
base, now = json.load(sys.stdin), json.load(open(".claude/settings.json"))
deny = lambda s: sorted(s.get("permissions", {}).get("deny", []))
missing = sorted(set(deny(base)) - set(deny(now)))
hooks, model = base.get("hooks") != now.get("hooks"), base.get("model") != now.get("model")
if missing or hooks or model:
    print("deny entries removed: %s; hooks changed: %s; model changed: %s" % (missing, hooks, model))
    sys.exit(1)
' || bad "settings.json deny entries, hooks, or model differ from the harness version"
  fi
fi

if [ "$fail" -eq 0 ]; then
  echo "ok: harness checks passed"
fi
exit "$fail"
