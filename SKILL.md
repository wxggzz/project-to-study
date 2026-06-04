---
name: tracedocs
description: Generate a structured Markdown study documentation package from a codebase, including operation, deployment, learning, architecture, code introduction, troubleshooting, and maintenance manuals.
---

# tracedocs

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

## Tone

Write as a senior engineer onboarding a capable teammate. Be clear, concrete,
and friendly. Explain jargon the first time it appears, but do not talk down to
the reader.

