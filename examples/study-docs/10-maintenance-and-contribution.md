# Maintenance and Contribution

## Coding Conventions

- Keep the **standard library as the only runtime dependency**.
- Use dataclasses for the model; keep extraction in `scanner.py`/`analyzers.py`
  and rendering in `writer.py`/`templates.py`.
- Comment non-obvious regular expressions with the case they handle.

## Testing Expectations

Run `pytest -q` before submitting changes; the suite covers the scanner, writer,
validator, analyzers, source resolution, and styles, over Node, FastAPI, and
schema fixtures. Add a regression test with every extraction change.

Evidence: `tests/` suite, `pyproject.toml` dev dependency
Confidence: Verified

## Release Checklist

- Tests pass (`pytest -q`).
- Sample output regenerated and `validate` passes.
- Version bumped in `project_to_study/__init__.py` and `pyproject.toml`.
- Documentation updated where behaviour changed.

## Safe Change Workflow

- Branch from the default branch.
- Make the smallest useful change; add or update tests.
- Run `pytest -q`, regenerate and validate sample docs.
- Open a reviewable change describing the input that motivated it.

## AI-Agent Handoff Notes

When an AI agent continues this work, point it at this package and at
`_evidence/` so it can distinguish verified facts from inferences before making
changes. New extractors should always record a `Claim` with evidence and a
confidence label rather than asserting facts silently.
