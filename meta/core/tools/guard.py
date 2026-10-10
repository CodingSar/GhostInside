#!/usr/bin/env python3
"""PreToolUse hook for Bash: block commands the harness never allows.

Blocked, in any spelling the shell accepts:
  - force push: git push with -f, --force, --force-with-lease,
    --force-if-includes, --mirror (or a unique abbreviation), or a +refspec;
  - recursive force remove: rm with both a recursive and a force flag;
  - sudo.

Also checked: commands on separate lines, after shell keywords (if, then, do,
{, !), behind wrappers (env, timeout, nice, xargs, ...), inside `bash -c` (any
flag group containing c), `eval`, backticks, `$(...)`, and `find -exec`.
Reads the hook JSON on stdin. Exit 2 with the reason on stderr blocks the
call; exit 0 allows it. When unsure, it blocks: a heredoc line that looks
like a blocked command is blocked too. Deny entries in .claude/settings.json
stay as a second line of defence.
Python standard library only.
"""

import json
import re
import shlex
import sys

PUNCT = ";&|()"
KEYWORDS = {"if", "then", "else", "elif", "fi", "do", "done", "while", "until",
            "for", "case", "esac", "{", "}", "!", "time", "in"}
# Wrapper -> its options that take a separate value.
WRAPPERS = {
    "env": {"-u", "--unset", "-C", "--chdir", "-S", "--split-string"},
    "command": set(), "exec": set(), "nohup": set(), "setsid": set(),
    "time": set(), "stdbuf": {"-i", "-o", "-e"},
    "nice": {"-n", "--adjustment"}, "ionice": {"-c", "-n", "-p", "-P", "-u"},
    "timeout": {"-s", "--signal", "-k", "--kill-after"},
    "xargs": {"-n", "-I", "-P", "-L", "-s", "-d", "-E", "-a", "--max-args",
              "--max-procs", "--delimiter", "--arg-file", "--replace"},
}
SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}
FORCE_PUSH = ("--force", "--force-with-lease", "--force-if-includes", "--mirror")
OTHER_PUSH = ("--follow-tags",)
RM_LONG = ("--recursive", "--force", "--interactive", "--one-file-system",
           "--no-preserve-root", "--preserve-root", "--dir", "--verbose")
NESTED = re.compile(r"`([^`]*)`|\$\(([^()]*)\)")
DURATION = re.compile(r"^\d+(\.\d+)?[smhd]?$")


def expand_long(opt, options):
    """The long option an abbreviation names, or None when unknown or ambiguous."""
    name = opt.split("=", 1)[0]
    hits = [o for o in options if o.startswith(name)]
    if name in options:
        return name
    return hits[0] if len(hits) == 1 and len(name) >= 3 else None


def split_commands(text):
    lexer = shlex.shlex(text.replace("\n", " ; "), posix=True, punctuation_chars=PUNCT)
    lexer.whitespace_split = True
    lexer.commenters = ""
    commands, words = [], []
    for tok in lexer:
        if set(tok) <= set(PUNCT):
            commands.append(words)
            words = []
        else:
            words.append(tok)
    commands.append(words)
    return [w for w in commands if w]


def strip_prefix(words):
    """Drop keywords, env assignments, and wrappers in front of the real command."""
    while words:
        w, name = words[0], words[0].rsplit("/", 1)[-1]
        if w in KEYWORDS or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w):
            words = words[1:]
        elif name in WRAPPERS:
            takes_value, words = WRAPPERS[name], words[1:]
            while words and (words[0].startswith("-") or DURATION.match(words[0])):
                words = words[2:] if words[0] in takes_value else words[1:]
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
        name = a.split("=", 1)[0]
        if (a.startswith("--") and len(name) >= 3
                and any(o.startswith(name) for o in FORCE_PUSH)
                and not any(o.startswith(name) for o in OTHER_PUSH)):
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
        if a.startswith("--"):
            opt = expand_long(a, RM_LONG)
            recursive |= opt == "--recursive"
            force |= opt == "--force"
        elif re.match(r"^-[a-zA-Z]+$", a):
            recursive |= "r" in a or "R" in a
            force |= "f" in a
    return "recursive force remove" if recursive and force else None


def check_find(args, depth):
    for i, a in enumerate(args):
        if a in ("-exec", "-execdir", "-ok", "-okdir"):
            inner = []
            for w in args[i + 1:]:
                if w in (";", "+"):
                    break
                inner.append(w)
            reason = check(shlex.join(inner), depth + 1)
            if reason:
                return reason
    return None


def check_words(words, depth):
    words = strip_prefix(words)
    if not words:
        return None
    name, args = words[0].rsplit("/", 1)[-1], words[1:]
    if name == "sudo":
        return "sudo"
    if name == "git":
        return check_git(args)
    if name == "rm":
        return check_rm(args)
    if name == "find":
        return check_find(args, depth)
    if name in SHELLS:
        for i, a in enumerate(args[:-1]):
            if re.match(r"^-[a-zA-Z]*c[a-zA-Z]*$", a):
                return check(args[i + 1], depth + 1)
        return None
    if name == "eval":
        return check(" ".join(args), depth + 1)
    return None


def check(text, depth=0):
    if depth > 4:
        return None
    for m in NESTED.finditer(text):
        reason = check(m.group(1) or m.group(2) or "", depth + 1)
        if reason:
            return reason
    try:
        commands = split_commands(text)
    except ValueError:
        # Unbalanced quotes: check each line's words without quote handling.
        commands = [line.split() for line in re.split(r"[;\n&|]", text)]
    for words in commands:
        reason = check_words(words, depth)
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
