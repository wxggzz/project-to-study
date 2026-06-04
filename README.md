# tracedocs

`tracedocs` is an agent-first documentation generator design inspired by
`codebase-to-course`, but focused on producing a complete Markdown study package
for any software project.

Instead of building an interactive HTML course, this project asks Claude Code,
Codex, or another coding agent to inspect a target codebase and generate a
structured set of Markdown documents:

- operation manual
- deployment manual
- learning manual
- code introduction
- architecture overview
- API and data notes when applicable
- troubleshooting and maintenance notes

The repository is designed so you can let Claude Code implement or run the first
version, then let Codex continue from the same instructions and templates.

## Core Idea

`codebase-to-course` uses a strong skill file plus reference templates to turn a
repo into a learning experience. `tracedocs` keeps that pattern:

1. Read and understand the target codebase.
2. Extract facts from source files, configs, README files, scripts, and tests.
3. Build a project map.
4. Generate a Markdown documentation package.
5. Record what was inferred, what was verified, and what remains uncertain.

The important difference is the output. This project produces durable Markdown
documents that a team can use for onboarding, deployment, operations, and future
AI-agent handoff.

## Planned Output

For a target project, the generated output should look like this:

```text
study-docs/
  README.md
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
  assets/
    architecture.mmd
    request-flow.mmd
  _evidence/
    source-map.md
    assumptions.md
    generation-log.md
```

## Repository Structure

```text
tracedocs/
  SKILL.md
  AGENTS.md
  CLAUDE.md
  TASKS.md
  docs/
    architecture.md
    roadmap.md
    output-document-map.md
  references/
    analysis-checklist.md
    handoff-protocol.md
    markdown-style-guide.md
    templates/
      00-project-overview.md
      01-quickstart.md
      02-operation-manual.md
      03-deployment-manual.md
      04-learning-manual.md
      05-code-introduction.md
      06-architecture.md
      09-troubleshooting.md
  prompts/
    claude-code-implementation.md
    generate-study-docs.md
```

## How To Use This Design

Give Claude Code this repository and start with:

```text
Read CLAUDE.md and prompts/claude-code-implementation.md, then implement the
MVP for tracedocs.
```

After Claude Code reaches its quota, continue with Codex:

```text
Read AGENTS.md, TASKS.md, and references/handoff-protocol.md. Continue from the
latest completed task without rewriting unrelated files.
```

## Install & Usage (CLI)

The deterministic MVP is implemented as a dependency-free Python CLI
(Python 3.9+).

```bash
# From the repository root
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"

# Generate the study-docs package for any local repo
.venv/bin/tracedocs /path/to/repo --out study-docs

# ...or straight from a Git URL (shallow-cloned to a temp dir, then cleaned up)
.venv/bin/tracedocs https://github.com/owner/repo --out study-docs

# Choose an output style: standard (default), concise, teaching, or ops
.venv/bin/tracedocs /path/to/repo --out study-docs --style teaching

# Validate a generated package (exits non-zero on problems)
.venv/bin/tracedocs validate study-docs
```

Styles only change emphasis and verbosity, never facts or evidence:
`concise` drops optional prose, `teaching` adds plain-English callouts and a
glossary, and `ops` front-loads the operation/deployment/troubleshooting docs.

Remote input accepts `https://`, `ssh://`, `git@host:owner/repo.git`, and the
`github.com/owner/repo` shorthand. It requires `git` on PATH and only does a
`--depth 1` clone. The generated docs record the original URL, not the temp
path.

After `pip install -e .`, the `tracedocs` command is on your PATH inside
the environment. The bare-path form shown above is equivalent to
`tracedocs generate /path/to/repo --out study-docs`.

A committed sample of real output lives in
[`examples/study-docs/`](examples/study-docs/), generated from the bundled
fixture at `tests/fixtures/sample-node-app/`.

Run the tests with:

```bash
.venv/bin/python -m pytest -q
```

The CLI is **deterministic and offline** — it adds no LLM dependency. It records
environment variable *names only* (never values) and never invents deployment
steps; gaps are written into `study-docs/_evidence/`.

It also performs **deep extraction**: concrete API routes (Express, FastAPI,
Flask, Django, Go `net/http`, gRPC `.proto`, GraphQL operations) and data
entities (Prisma, SQLAlchemy, Django models, Mongoose, TypeORM, SQL
`CREATE TABLE`, Protobuf `message`, GraphQL types) are pulled from the source
and listed in `07-api-and-integrations.md` and `08-data-model.md`, each with its
source file as evidence. For block schemas (Prisma, Protobuf, GraphQL) the
entity tables also list field names.

## Use As A Claude Code Skill

Besides the CLI, this repo ships a Claude Code **skill** (`SKILL.md` +
`references/`), the same pattern as `codebase-to-course`. Installed, it becomes a
`/tracedocs` slash command: Claude reads `SKILL.md` and generates the docs
itself (more adaptive prose), optionally calling the CLI to extract facts first.

Install it as a personal skill by copying `SKILL.md` and `references/` into
`~/.claude/skills/tracedocs/`:

```bash
# From the repository root
mkdir -p ~/.claude/skills/tracedocs
cp SKILL.md ~/.claude/skills/tracedocs/
cp -R references ~/.claude/skills/tracedocs/
```

Or symlink it so the skill tracks the repo (no re-copy after updates):

```bash
ln -s "$(pwd)" ~/.claude/skills/tracedocs
```

Then **reload/restart Claude Code** (skills are discovered at startup). After
that, run it from the prompt:

```text
/tracedocs
```

or trigger it in natural language, e.g. "use tracedocs to generate study
docs for /path/to/repo". The resulting layout matches the CLI output above.

> Skill vs CLI: the skill is Claude-driven (adaptive, richer narrative); the CLI
> is deterministic and offline (CI-friendly, templated prose). They are
> complementary — a skill run can call the CLI to pin facts, then write around
> them. If you installed by copying (not symlinking), re-copy after repo updates.

## MVP Definition

The first useful version does not need a complex app. It only needs to:

1. Accept a target project path.
2. Inspect important source, config, README, script, and test files.
3. Produce the Markdown document tree under `study-docs/`.
4. Include Mermaid diagrams where useful.
5. Keep an evidence trail for generated claims.

