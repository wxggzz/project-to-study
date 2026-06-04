# Data Model

## Storage Overview

There is **no database**. The "data model" is a set of in-memory dataclasses in
`model.py` that carry facts through the pipeline. The only persistence is the
Markdown files written to the `--out` directory.

Confidence: Verified (`model.py`, `writer.py`)

## Important Entities

| Entity | Kind | Key fields | Source |
| --- | --- | --- | --- |
| `ProjectFacts` | dataclass | name, root, source, languages, frameworks, package_managers, *_commands, entry_points, env_vars, routes, entities, claims, … | `model.py` |
| `Command` | dataclass | label, command, evidence, confidence | `model.py` |
| `EnvVar` | dataclass | name, purpose, required, evidence, confidence | `model.py` |
| `Route` | dataclass | method, path, evidence, handler | `model.py` |
| `Entity` | dataclass | name, kind, evidence, fields | `model.py` |
| `Claim` | dataclass | text, evidence, confidence | `model.py` |
| `Confidence` | constants | Verified / Inferred / Unknown / Needs confirmation | `model.py` |

## Migrations

Not applicable — no schema, no migrations.

## State And Storage

- Input is read-only; the tool never modifies the target repository.
- Output is the `study-docs/` directory (Markdown + `assets/` + `_evidence/`).
- Git-URL input is cloned to a temporary directory that is removed after the
  run. Evidence: `source.py`. Confidence: Verified
