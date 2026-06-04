# Assumptions

Claims grouped by confidence. Review anything not `Verified` before relying on
it.

## Verified Facts

- Python ≥ 3.9, zero runtime dependencies, MIT licensed (`pyproject.toml`).
- Console script `project-to-study` → `project_to_study.cli:main`.
- Commands `generate` (default for a bare path) and `validate`.
- Four output styles; Git-URL input via shallow `git clone`.
- Pipeline: `source.acquire` → `scanner.scan` → `analyzers.analyze` →
  `writer.generate` + `evidence.write_evidence`.
- No deployment/CI config; the tool reads no environment variables of its own.

## Reasonable Inferences

- A distributable wheel/sdist can be built via `python -m build` (setuptools
  backend is declared, but `build` is not a listed dependency).
- Heuristic regex extraction may miss or over-match unusual code styles.

## Unknowns

- The intended distribution channel (PyPI name/owner), if any.
- Versioning/release cadence beyond the current `0.1.0`.

## Needs Confirmation

- Whether PyPI publishing is planned (no publish config found).

## Omitted Or Not-Applicable Documents

- `08-data-model.md` is reframed: there is no database, so it documents the
  in-memory dataclass model and on-disk output instead.
- `03-deployment-manual.md` states plainly that no deployment configuration
  exists, rather than inventing steps.
