# Deployment Manual

## Deployment Summary

**No deployment configuration was found in this repository.** There is no
Dockerfile, no CI workflow, no `Makefile`, and no hosting-provider config. This
is expected: `tracedocs` is a developer CLI distributed as a Python
package / source checkout, not a deployed service.

Evidence: absence of `Dockerfile`, `.github/workflows/`, `Makefile`, etc.
Confidence: Verified

## Build

The project is pure Python with a PEP 621 / setuptools backend, so there is no
compile step. To produce a distributable wheel/sdist you would run:

```bash
python -m build
```

Evidence: `pyproject.toml` `[build-system]` uses `setuptools.build_meta`
Confidence: Inferred (the `build` tool is not declared as a dependency)

## Required Environment

None. The tool reads no environment variables of its own.

Confidence: Verified

## Distribution Steps

1. Install from source for local/CI use: `pip install -e ".[dev]"`.
2. (Optional) Build artifacts with `python -m build`.
3. (Optional) Publish to an index with `twine`.

Publishing to PyPI is **not** configured in this repository.
Confidence: Needs confirmation

## Rollback

Not applicable — there is no deployed instance. Reverting is a `git` operation
on the consuming side.

## Deployment Unknowns

- Whether the package is intended for PyPI, and under what name/owner.
- Versioning/release policy (current version is `0.1.0`).
