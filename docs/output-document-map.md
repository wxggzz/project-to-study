# Output Document Map

This file defines the default `study-docs/` package.

## `README.md`

Audience: anyone opening the generated docs.

Purpose:

- explain what the project is
- link every generated manual
- state generation date, target path, and confidence notes

## `index.json`

Audience: AI agents and automation (and any tool that wants the package without
parsing prose).

Purpose:

- a machine-readable manifest of the package
- document list (file, title, audience), verified commands, env-var names
- confidence counts, unknowns, evidence files, and optional routes/entities
- always generated; keep it factual (see the shape in `SKILL.md`)

## `index.html`

Audience: humans who want a quick browser preview or screenshot.

Purpose:

- optional single-file preview of the generated package
- link back to Markdown documents and `_evidence/` files
- add no new facts; Markdown and `index.json` remain the source of truth
- no build step, no external assets, no JS framework

## `00-project-overview.md`

Audience: product owners, maintainers, new contributors.

Purpose:

- summarize the project
- explain the user-facing purpose
- list major capabilities
- identify the tech stack

## `01-quickstart.md`

Audience: someone who wants to run the project quickly.

Purpose:

- prerequisites
- install command
- local run command
- test command
- common first-run issues

## `02-operation-manual.md`

Audience: operators and maintainers.

Purpose:

- how to run the project day to day
- config and environment variables
- health checks
- logs
- routine maintenance

## `03-deployment-manual.md`

Audience: deployers and infrastructure owners.

Purpose:

- build process
- deployment targets discovered in the repo
- environment setup
- release steps
- rollback notes

If deployment is not documented by the project, say so clearly.

## `04-learning-manual.md`

Audience: non-expert learners and AI-assisted builders.

Purpose:

- learning path through the project
- concepts to understand first
- suggested file reading order
- exercises and questions

## `05-code-introduction.md`

Audience: developers and AI coding agents.

Purpose:

- source tree explanation
- important modules
- entry points
- how data moves through the code

## `06-architecture.md`

Audience: technical maintainers.

Purpose:

- system boundaries
- component diagram
- request/data flow
- dependency relationships
- architectural risks

## `07-api-and-integrations.md`

Audience: developers and maintainers.

Purpose:

- API routes or commands
- external services
- auth and credentials shape
- rate limits or failure modes if known

## `08-data-model.md`

Audience: developers and data maintainers.

Purpose:

- database/schema overview
- important entities
- migrations
- state files or storage

## `09-troubleshooting.md`

Audience: anyone debugging the project.

Purpose:

- known error classes
- likely causes
- diagnostic commands
- recovery steps

## `10-maintenance-and-contribution.md`

Audience: future contributors and AI agents.

Purpose:

- coding conventions
- testing expectations
- release checklist
- safe change workflow
- AI-agent handoff notes
