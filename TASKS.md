# Tasks

## Status

Deterministic MVP implemented. A Python CLI scans a target repo and generates
the full `study-docs/` Markdown package with an evidence trail. All tests pass
and a committed sample lives in `examples/study-docs/`.

## MVP Tasks

- [x] Decide implementation language and packaging. (Python, `pyproject.toml`,
      `project-to-study` console script.)
- [x] Add CLI entry point. (`project_to_study/cli.py`: `generate` + `validate`,
      bare-path form supported.)
- [x] Implement repository scanner. (`project_to_study/scanner.py`)
- [x] Extract scripts, dependencies, entry points, env vars, tests, and config.
- [x] Implement evidence files. (`project_to_study/evidence.py` →
      `source-map.md`, `assumptions.md`, `generation-log.md`)
- [x] Implement Markdown writers. (`project_to_study/writer.py`,
      `templates.py`; mirrors `references/templates/`.)
- [x] Add tests with a small fixture project.
      (`tests/`, `tests/fixtures/sample-node-app/`)
- [x] Generate a sample `study-docs/` output from the fixture.
      (Committed at `examples/study-docs/`.)
- [x] Add installation and usage instructions. (See `README.md`.)

## High-Value Extras Done

- [x] `validate` command (`project_to_study/validate.py`): checks required docs
      and evidence exist, links resolve, diagrams are present, and no secret
      values leaked. Non-zero exit on failure (CI-friendly).
- [x] Multi-language detection (Node/Python/Go/Rust/Java/Ruby and more) via file
      census + dependency-manifest keyword matching.
- [x] Mermaid diagrams for architecture and core flow, plus `.mmd` assets.
- [x] Document planner: `07-api-and-integrations.md` / `08-data-model.md` carry
      real content only when signals exist, otherwise a not-applicable note that
      is logged in `_evidence/assumptions.md`.

## High-Value Extras Done (continued)

- [x] **GitHub / Git URL input** (`project_to_study/source.py`): `is_remote`
      detection + `acquire` shallow-clone (`git clone --depth 1`) into a temp
      dir that is cleaned up on exit. Accepts https/ssh/`git@`/`github.com/...`
      shorthand. Docs record the original URL, not the temp path. CLI exits 2
      with a clear message if `git` is missing or the clone fails.
- [x] **Deep analyzers** (`project_to_study/analyzers.py`, roadmap Phase 2):
      extract concrete **API routes** (Express/Node, FastAPI/decorator, Flask,
      Django `urls.py`, Go `net/http`, gRPC `.proto`, GraphQL operations) and
      **data entities** (Prisma, SQLAlchemy, Django models, Mongoose, TypeORM,
      SQL `CREATE TABLE`, Protobuf `message`, GraphQL types). Routes and
      entities are rendered as tables in `07-api-and-integrations.md` and
      `08-data-model.md`, with the source file as evidence, and feed the
      document planner's applicability decision. For block schemas (Prisma,
      Protobuf, GraphQL) the entity tables also list field names, and route
      tables list the handler/view name when identifiable (Express, FastAPI,
      Flask, Django, Go).
- [x] **`--style` option** (`project_to_study/style.py`): `standard` (default),
      `concise` (drops optional prose), `teaching` (plain-English callouts +
      glossary), `ops` (front-loads operation/deployment/troubleshooting). Style
      changes emphasis/verbosity only — never facts or evidence — and is
      recorded in the package README and generation log.

## Nice-To-Have Tasks (deferred)

- [ ] Add LLM provider abstraction (Phase 3 of the roadmap). Keep evidence
      visible; never let the LLM invent deployment details.
- [ ] Capture entity fields for indented-class ORMs (SQLAlchemy/Django/
      Mongoose/TypeORM); add more ORMs (Sequelize, Peewee, GORM struct tags).
      Block-schema field extraction (Prisma/Protobuf/GraphQL) and route handler
      names are done.

## How To Run

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest -q
.venv/bin/project-to-study tests/fixtures/sample-node-app --out /tmp/study-docs
.venv/bin/project-to-study validate /tmp/study-docs
```

## Handoff Notes

- Commands run: `pytest -q` (59 passed); CLI generate + validate on the fixtures
  (exit 0); all four styles validate; remote-clone failure path exits 2.
- PR #1 review (Codex): fixed 4 analyzer findings — multi-decorator FastAPI
  routes, Express middleware-vs-handler, Flask `methods=[...]` with extra
  kwargs, and Protobuf nested-block (`oneof`) field truncation; added regression
  tests for each.
- PR #1 re-review (Codex): fixed 3 follow-up boundary bugs — commented-out
  decorators no longer bind to a later def (line-anchored), Flask methods after
  a nested-call kwarg are parsed (paren-balanced args), and block/paren scanning
  now skips strings and comments (`_balanced`/`_skip_string`), so braces inside
  strings no longer truncate fields. Regression tests added for each.
- PR #1 third review (Codex): fixed 2 more — nested Protobuf `message` fields no
  longer leak into the outer message (`_proto_fields` skips nested message/enum
  but descends into `oneof`), and the route handler name survives long/multi-line
  decorator args (`_handler_after` uses a blank-line bound, not a char window).
  Regression tests added for each.
- PR #1 fourth review (Codex): unified FastAPI handling with Flask — read the
  full decorator call with the paren-balanced scanner and resolve the handler
  only after the closing `)`, so a `def` inside a decorator argument string
  (e.g. a `description=`) is no longer mistaken for the handler. Regression test
  added.
- Files added: `project_to_study/*.py` (incl. `source.py`, `analyzers.py`,
  `style.py`), `tests/*` (incl. `test_source.py`, `test_analyzers.py`,
  `test_style.py`), the `tests/fixtures/sample-py-api/` FastAPI+SQLAlchemy
  fixture, `pyproject.toml`, `examples/study-docs/**`, `examples/README.md`.
- Files edited: `README.md`, `TASKS.md`, `.gitignore` (anchored `/study-docs/`
  so the demo under `examples/` is committed).
- Known limitations: detection is heuristic; route/entity extraction is not yet
  implemented (see deferred tasks). The committed sample's
  `_evidence/generation-log.md` records an absolute target path and timestamp.
- Next recommended task: broaden analyzer coverage (GraphQL/gRPC, handler
  names, entity fields), or the optional LLM writer layer (Phase 3 — note that
  CLAUDE.md asks to keep the MVP LLM-free).
- When another agent continues, read `AGENTS.md`, `CLAUDE.md`, and
  `references/handoff-protocol.md`.
