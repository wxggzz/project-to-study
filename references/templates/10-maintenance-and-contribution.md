# Maintenance And Contribution

> Audience: future contributors, maintainers, and AI agents.
> Signature payoff: a practical change workflow: how to test, document, and hand
> off work without hidden assumptions.

## Maintenance Summary

<One short paragraph describing how this project appears to be maintained:
manual edits, CI-backed changes, package releases, generated artifacts, etc.
Cite evidence or mark Unknown.>

## Safe Change Workflow

1. Read the relevant docs and source files.
2. Identify the smallest owned area to change.
3. Update or add tests when behaviour changes.
4. Run the verified checks below.
5. Update generated docs and `index.json` if commands, APIs, env vars, data
   model, or operational behaviour changed.
6. Record assumptions and handoff notes.

## Verified Checks

| Check | Command | Evidence | Confidence |
| --- | --- | --- | --- |
| Tests | `<cmd>` | `<manifest / README / CI>` | Verified |
| Lint | `<cmd or not found>` | `<source>` | <Verified / Unknown> |
| Build | `<cmd or not found>` | `<source>` | <Verified / Unknown> |

## Contribution Conventions

| Area | Convention | Evidence | Confidence |
| --- | --- | --- | --- |
| Style | <formatter/linter/style guide> | `<file>` | Verified |
| Branching | <branch/PR expectation> | `<file or Unknown>` | <Verified / Unknown> |
| Reviews | <review/test expectation> | `<file or Unknown>` | <Verified / Unknown> |

## Release And Versioning

<Describe release process only if visible in source, CI, package metadata, or
docs. If absent, write "Release process not documented in the repository" and
mark Unknown.>

## AI-Agent Handoff

When an AI agent works on this project, it should record:

- files changed
- commands/tests run
- assumptions made
- known blockers
- next recommended task

## Documentation Maintenance

- Re-run tracedocs after changes to commands, deployment, APIs, data model, env
  vars, or architecture.
- Keep generated example outputs separate from reusable source templates.
- Keep `_evidence/assumptions.md` current when facts are unknown.
