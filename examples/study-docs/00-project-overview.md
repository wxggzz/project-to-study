# Project Overview

## What This Project Does

`tracedocs` is a command-line tool that scans a target code repository
and generates a structured Markdown documentation package (`study-docs/`) —
overview, quickstart, operation, deployment, learning, code introduction,
architecture, API, data model, troubleshooting, and maintenance manuals — with
an evidence trail that ties each claim back to a source file.

It is deterministic and offline: it extracts facts with heuristics and regular
expressions rather than calling an LLM.

## Who Uses It

- Engineers onboarding to, or documenting, an unfamiliar codebase.
- Teams that want durable, version-controllable docs (not a one-off chat).
- AI coding agents that need a factual, evidence-tagged map of a project.

## Main Capabilities

- Scans any local path or a Git URL (shallow-cloned to a temp dir).
- Detects languages, package managers, run/build/test/lint commands, entry
  points, environment variable **names**, deployment signals, and tests.
- Deep extraction of API routes (Express, FastAPI, Flask, Django, Go, gRPC,
  GraphQL) and data entities (Prisma, SQLAlchemy, Django, Mongoose, TypeORM,
  SQL, Protobuf, GraphQL) — with handler names and field lists where available.
- Four output styles: `standard`, `concise`, `teaching`, `ops`.
- A `validate` command that checks the generated package for broken links,
  missing files, absent diagrams, and leaked secret values.

## Tech Stack

| Area | Technology | Evidence | Confidence |
| --- | --- | --- | --- |
| Language | Python ≥ 3.9 | `pyproject.toml` `requires-python` | Verified |
| Runtime dependencies | None (standard library only) | `pyproject.toml` `dependencies = []` | Verified |
| Packaging | setuptools (PEP 621) | `pyproject.toml` `[build-system]` | Verified |
| Tests | pytest | `pyproject.toml` `optional-dependencies.dev` | Verified |
| External tool | `git` (only for Git-URL input) | `source.py` `subprocess` git clone | Verified |
| License | MIT | `pyproject.toml` `license` | Verified |

## Important Files

| Path | Purpose |
| --- | --- |
| `pyproject.toml` | Metadata, console script, dev deps |
| `project_to_study/cli.py` | CLI entry point and dispatch |
| `project_to_study/scanner.py` | Repository fact extraction |
| `project_to_study/analyzers.py` | Route and entity extraction |
| `project_to_study/writer.py` | Markdown document generation |
| `tests/` | Test suite and fixtures |

## What To Read Next

Start with `01-quickstart.md`, then `05-code-introduction.md`.
