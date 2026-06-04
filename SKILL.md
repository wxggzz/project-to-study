---
name: project-to-study
description: Generate a structured Markdown study documentation package from a codebase, including operation, deployment, learning, architecture, code introduction, troubleshooting, and maintenance manuals.
---

# project-to-study

Turn any codebase into a practical Markdown documentation package for learning,
operating, deploying, and maintaining the project.

## When To Use

Use this workflow when the user asks to:

- generate Markdown documentation from a project
- create onboarding docs for a codebase
- explain a project as operation, deployment, study, and architecture manuals
- prepare docs for future AI-agent handoff
- turn a repo into a maintainable study guide

If the user provides a GitHub URL, clone it into a temporary directory first.
If the user says "this project" or gives no path, use the current working
directory.

## Output Contract

Write generated documents into:

```text
study-docs/
```

The default output files are:

```text
study-docs/
  README.md
  index.json                       # machine-readable manifest (always write this)
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
  _evidence/
    source-map.md
    assumptions.md
    generation-log.md
```

Skip files that clearly do not apply, but explain the omission in
`_evidence/assumptions.md`.

### AI-ready manifest: `index.json`

Always write `study-docs/index.json` — a structured map so AI agents (and future
automation) can consume the package without parsing prose. Keep it small and
factual; do not invent fields. Minimum shape:

```json
{
  "schema": "1",
  "name": "<project name>",
  "generated_at": "<YYYY-MM-DD>",
  "source": "<path or repo URL>",
  "documents": [{ "file": "00-project-overview.md", "title": "Project Overview", "audience": "maintainers" }],
  "commands": { "install": "...", "run": "...", "test": "..." },
  "env_var_names": ["DATABASE_URL"],
  "confidence": { "verified": 0, "inferred": 0, "unknown": 0, "needs_confirmation": 0 },
  "unknowns": ["No deployment config found in the repo."],
  "evidence_files": ["_evidence/source-map.md", "_evidence/assumptions.md", "_evidence/generation-log.md"],
  "routes": [],
  "entities": []
}
```

`routes` and `entities` are optional — include them only when the project
exposes an API or defines data models.

### Optional: `index.html` preview

You may also emit a single self-contained `study-docs/index.html` for browsing
and screenshots. It must be **derived only from the docs** (no new facts), be a
**single file with no build step and no JS framework**, link back to the
Markdown and `_evidence/` files, and be labelled a preview. The Markdown remains
the source of truth. See `examples/study-docs/index.html` for the reference.
Skip it if you cannot keep it tiny and faithful.

## Phase 1: Analyze The Codebase

Read enough of the project to understand:

- product purpose and user workflows
- tech stack and runtime
- source layout and important entry points
- package managers, scripts, build tools, and deployment hooks
- APIs, integrations, databases, queues, background jobs, and auth
- tests and quality checks
- environment variables and secrets shape, without exposing secret values
- operational failure modes and debugging commands

Prefer factual extraction over invention. If a claim is inferred, mark it as
inferred.

Use `references/analysis-checklist.md`.

## Phase 2: Create A Source Map

Before writing final docs, create:

```text
study-docs/_evidence/source-map.md
study-docs/_evidence/assumptions.md
study-docs/_evidence/generation-log.md
```

The source map should connect claims to files, scripts, configs, and tests.
The assumptions file should separate:

- verified facts
- reasonable inferences
- unknowns
- things the user should confirm

## Phase 3: Generate Markdown Manuals

Use the templates in `references/templates/`, adapting them to the target
project.

Each document should be useful on its own, but the package should also work as a
linear learning path:

1. overview
2. quickstart
3. operation
4. deployment
5. learning
6. code walkthrough
7. architecture
8. APIs and data
9. troubleshooting
10. maintenance

Use Mermaid diagrams for architecture, request flow, state flow, or deployment
topology when useful.

## Phase 4: Quality Check

Before finishing:

- Verify that command examples match actual scripts or explain if inferred.
- Confirm file paths exist.
- Avoid documenting files that are not present.
- Mark unverified deployment details as assumptions.
- Ensure every document has a clear audience and practical next step.
- Keep the Markdown readable in GitHub without custom styling.

## Quality Bar: Match These Examples

The single rule that makes this skill trustworthy: **state evidence and
confidence, and never invent what you cannot source.** Match the style below.

### Evidence lines

Good — sourced and labelled:

```text
Start the dev server with `npm run dev`.
Evidence: package.json `scripts.dev`
Confidence: Verified
```

Bad — an unsourced assertion:

```text
Start the dev server with `npm run dev`. The app runs on port 3000.
```

(Why it's bad: the command isn't tied to a file, and the port is asserted with
no evidence. If the port comes from `.env.example`, cite it; otherwise mark it
`Unknown`.)

### Deployment when nothing is documented

Good — refuses to invent, records the gap:

```text
## Deployment Summary
No deployment configuration was found in this repository (no Dockerfile, CI
workflow, or hosting config). Deployment steps are therefore unknown.
Confidence: Unknown — recorded in `_evidence/assumptions.md`.
```

Bad — hallucinated steps:

```text
## Deployment Steps
1. Push to main; CI builds a Docker image and deploys to AWS ECS.
2. Run database migrations on the production cluster.
```

(Why it's bad: there is no Docker/CI/AWS evidence in the repo. Inventing a
plausible pipeline is the exact failure this skill exists to prevent.)

### Gold standard

Treat [`examples/study-docs/`](examples/study-docs/) as the reference output to
match — note how it cites sources, labels confidence, lists fields/routes with
their source files, and states "not applicable / not found" honestly for
sections that don't apply.

## Tone

Write as a senior engineer onboarding a capable teammate. Be clear, concrete,
and friendly. Explain jargon the first time it appears, but do not talk down to
the reader.

