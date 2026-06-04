# Codex PR Review Prompt

Use this prompt to have Codex (or another coding agent) review a pull request in
this repository. Replace `<PR_NUMBER>` with the PR you want reviewed.

To have findings posted directly on the PR, append the optional last line shown
in the prompt.

```text
You are reviewing a pull request in the project-to-study repository.

Repo: https://github.com/wxggzz/project-to-study
PR #<PR_NUMBER> (develop -> main)

First, ground yourself in the project's intent and rules — read:
- AGENTS.md
- CLAUDE.md  (note the Non-Negotiables section)
- README.md
- SKILL.md
- TASKS.md
- references/handoff-protocol.md
- references/markdown-style-guide.md

Then check out the PR and read the diff:
  gh pr checkout <PR_NUMBER>
  gh pr diff <PR_NUMBER>
Concentrate on the files the PR actually changes (use the diff to scope this).

Run the suite before judging:
  python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
  .venv/bin/python -m pytest -q

Review for, in priority order:
1. Correctness of any regex/string extraction. Look for false positives and
   missed cases: e.g. JS `_.get(obj, "a.b")` vs real routes; multi-decorator
   FastAPI functions; Flask `methods=[...]`; Django `include(...)`; nested
   braces in GraphQL/Protobuf blocks; Prisma `@@`-attribute lines; a non-greedy
   `[\s\S]*?def` grabbing the wrong def.
2. Adherence to the project's Non-Negotiables (CLAUDE.md): deterministic
   (no LLM), env-var NAMES ONLY (never values), no invented deployment steps,
   every extracted claim traceable to a source file, generated Markdown
   readable on GitHub.
3. Robustness: large/binary files, encoding, file-count/size caps, display caps.
4. Test quality: are assertions meaningful, and is anything important untested?
5. Markdown output: would new tables/columns render on GitHub, including
   escaping of pipes and backticks?

Deliver:
- A short verdict (approve / request changes) with rationale.
- A list of concrete findings, each as: file:line, severity (blocker/major/
  minor/nit), the problem, and a suggested fix.
- Only flag real issues; do not rewrite working code for taste. Cite evidence
  (a failing input, a diff line) for each claim.

Post your findings as inline review comments via the gh CLI.
```
