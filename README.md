# project-to-study

A Claude Code **skill** that turns any codebase into a structured Markdown
**study-docs package** — operation, deployment, learning, architecture, code
introduction, API/data, and troubleshooting manuals — with an evidence trail.

Inspired by [`codebase-to-course`](https://github.com/zarazhangrui/codebase-to-course):
same skill pattern (a strong `SKILL.md` + reusable references and templates), but
the output is durable Markdown documentation a team can use for onboarding,
operations, and AI-agent handoff — not an HTML course.

## What It Produces

```text
study-docs/
  README.md                       # index + generation date + confidence notes
  00-project-overview.md
  01-quickstart.md
  02-operation-manual.md
  03-deployment-manual.md
  04-learning-manual.md
  05-code-introduction.md
  06-architecture.md
  07-api-and-integrations.md
  08-data-model.md
  09-troubleshooting.md
  10-maintenance-and-contribution.md
  assets/                         # Mermaid diagrams (.mmd)
  _evidence/                      # source-map, assumptions, generation-log
```

Each manual has a clear audience and a practical next step. See
[`docs/output-document-map.md`](docs/output-document-map.md) for what each file
covers.

## Install

Install it as a personal Claude Code skill by copying `SKILL.md` and
`references/` into `~/.claude/skills/project-to-study/`:

```bash
git clone https://github.com/wxggzz/project-to-study
cd project-to-study
mkdir -p ~/.claude/skills/project-to-study
cp SKILL.md ~/.claude/skills/project-to-study/
cp -R references ~/.claude/skills/project-to-study/
```

Or symlink it so the skill tracks the repo (no re-copy after updates):

```bash
ln -s "$(pwd)" ~/.claude/skills/project-to-study
```

Then **reload/restart Claude Code** — skills are discovered at startup.

## Use

Run it from the Claude Code prompt:

```text
/project-to-study
```

…or just ask in natural language:

```text
Use project-to-study to generate study docs for ./my-app
```

- If you give a **GitHub URL**, it is cloned into a temporary directory first.
- If you say "this project" or give no path, the current directory is used.

Claude reads `SKILL.md` and works in four phases: analyze the codebase → build a
source map and assumptions → write the manuals from `references/templates/` →
run a quality check. Output lands in `study-docs/`.

## Design Principles

- **Evidence over invention.** Every operational/deployment claim cites its
  source (a script, config, or test) and a confidence label: `Verified`,
  `Inferred`, `Unknown`, or `Needs confirmation`.
- **Never invent deployment steps.** If the repo doesn't document deployment,
  the docs say so instead of guessing.
- **Never expose secret values.** Environment variables are documented by
  **name only**.
- **Document the gaps.** Missing or ambiguous information is recorded in
  `_evidence/assumptions.md`, not glossed over.
- **Readable on GitHub.** Plain Markdown, tables, and Mermaid — no custom
  styling required.

## Repository Layout

```text
project-to-study/
  SKILL.md                        # the skill: workflow + output contract
  references/
    analysis-checklist.md         # what to extract before writing
    markdown-style-guide.md       # formatting + evidence conventions
    handoff-protocol.md           # confidence labels + agent handoff
    templates/                    # one scaffold per output document
  prompts/
    generate-study-docs.md        # ready-to-paste invocation prompt
  docs/
    output-document-map.md        # what each generated document is for
```

## Deterministic CLI (optional)

A dependency-free Python CLI that produces the same `study-docs/` layout
deterministically and offline (handy for CI) lives on the
[`cli`](https://github.com/wxggzz/project-to-study/tree/cli) branch. The skill
above is the primary, recommended way to use this project.

## License

MIT
