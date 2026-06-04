# Handoff Protocol

This protocol keeps work continuous when one AI agent starts and another
continues.

## Before Starting

The agent should read:

- `README.md`
- `SKILL.md`
- `TASKS.md`
- `docs/architecture.md`
- this file

## During Work

Keep changes scoped. Prefer creating or updating one layer at a time:

1. scanner
2. internal model
3. evidence writer
4. document writer
5. CLI
6. tests

## At The End Of Each Session

Update `TASKS.md` with:

- what changed
- what remains
- commands run
- known issues
- the next recommended task

## Generated Documentation Handoff

When generating docs for a target project, always create:

```text
study-docs/_evidence/source-map.md
study-docs/_evidence/assumptions.md
study-docs/_evidence/generation-log.md
```

This lets the next agent distinguish facts from guesses.

## Confidence Language

Use these labels consistently:

- `Verified`: directly supported by source files
- `Inferred`: likely based on repository structure
- `Unknown`: not enough evidence
- `Needs confirmation`: user or maintainer should verify

