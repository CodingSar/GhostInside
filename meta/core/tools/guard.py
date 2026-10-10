#!/usr/bin/env python3
"""PreToolUse hook for Bash: block commands the harness never allows.

Blocked, in any spelling the shell accepts:
  - force push: git push with -f, --force, --force-with-lease,
    --force-if-includes, --mirror, or a +refspec;
  - recursive force remove: rm with both a recursive and a force flag;
  - sudo.

Commands nested in `bash -c`, `sh -c`, `eval`, `env`, `command`, `xargs`, or
`nohup` are checked too. Reads the hook JSON on stdin. Exit 2 with the reason
on stderr blocks the call; exit 0 allows it. Deny entries in
.claude/settings.json stay as a second line of defence.
Python standard library only.
"""

import json
import re
import shlex
import sys

SEPARATORS = {";", "&&", "||", "|", "&", "\n", "(", ")"}
WRAPPERS = {"env", "command", "xargs", "nohup", "time", "exec"}
SHELLS = {"bash", "sh", "zsh", "dash"}
GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}
FORCE_PUSH = {"--force", "--force-with-lease", "--force-if-includes", "--mirror"}


def split_commands(text):
    lexer = shlex.shlex(text, posix=True, punctuation_chars=";&|()")
    lexer.whitespace_split = True
    lexer.commenters = ""
    words, out = [], []
    for tok in lexer:
        if tok in SEPARATORS or set(tok) <= set(";&|()"):
            out.append(words)
            words = []
        else:
            words.append(tok)
    out.append(words)
    return [w for w in out if w]


def strip_prefix(words):
    """Drop env assignments and wrapper commands in front of the real command."""
    while words:
        w = words[0]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w):
            words = words[1:]
        elif w.rsplit("/", 1)[-1] in WRAPPERS:
            words = words[1:]
            while words and words[0].startswith("-"):
                words = words[1:]
        else:
            break
    return words


def check_git(args):
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in GIT_OPTS_WITH_VALUE else 1
    if i >= len(args) or args[i] != "push":
        return None
    for a in args[i + 1:]:
        if a in FORCE_PUSH or a.split("=", 1)[0] in FORCE_PUSH:
            return f"force push ({a})"
        if re.match(r"^-[a-zA-Z]*f[a-zA-Z]*$", a):
            return f"force push ({a})"
        if a.startswith("+"):
            return f"force push (refspec {a})"
    return None


def check_rm(args):
    recursive = force = False
    for a in args:
        if a == "--":
            break
        if a in ("--recursive",):
            recursive = True
        elif a == "--force":
            force = True
        elif re.match(r"^-[a-zA-Z]+$", a):
            recursive |= "r" in a or "R" in a
            force |= "f" in a
    return "recursive force remove" if recursive and force else None


def check(text, depth=0):
    if depth > 3:
        return None
    try:
        commands = split_commands(text)
    except ValueError:
        # Unbalanced quotes: fall back to a plain scan of the raw text.
        if re.search(r"git\b.*\bpush\b.*(\s-[a-zA-Z]*f|--force|--mirror|\s\+)", text) \
                or re.search(r"\brm\s+-[a-zA-Z]*[rR][a-zA-Z]*f|\brm\s+-[a-zA-Z]*f[a-zA-Z]*[rR]", text) \
                or re.search(r"\bsudo\b", text):
            return "blocked pattern in unparsable command"
        return None
    for words in commands:
        words = strip_prefix(words)
        if not words:
            continue
        name, args = words[0].rsplit("/", 1)[-1], words[1:]
        if name == "sudo":
            return "sudo"
        if name == "git":
            reason = check_git(args)
        elif name == "rm":
            reason = check_rm(args)
        elif name in SHELLS and "-c" in args[:-1]:
            reason = check(args[args.index("-c") + 1], depth + 1)
        elif name == "eval":
            reason = check(" ".join(args), depth + 1)
        else:
            reason = None
        if reason:
            return reason
    return None


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    command = (event.get("tool_input") or {}).get("command") or ""
    reason = check(command)
    if reason:
        print(f"Blocked by meta/core/tools/guard.py: {reason}. "
              "The harness never force-pushes, force-removes recursively, or uses sudo. "
              "Changing this needs the user's explicit confirmation (AGENTS.md, Governance).",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
