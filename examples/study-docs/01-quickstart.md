# Quickstart

## Prerequisites

- Python 3.9 or newer (`pyproject.toml` `requires-python`). Confidence: Verified
- `git` on PATH — only needed if you pass a Git URL instead of a local path.
  Confidence: Verified (`source.py`)

## Install

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

Evidence: `pyproject.toml` `[project.optional-dependencies] dev = ["pytest>=7.0"]`
Confidence: Verified

## Run Locally

```bash
tracedocs /path/to/repo --out study-docs
```

Evidence: `pyproject.toml` `[project.scripts] tracedocs = "project_to_study.cli:main"`
Confidence: Verified

## Run Tests

```bash
pytest -q
```

Evidence: `pyproject.toml` dev dependency `pytest`; `tests/` suite
Confidence: Verified

## First-Run Checklist

- Virtual environment created and dependencies installed
- `tracedocs --version` prints a version
- A run against a sample repo produces a `study-docs/` directory
- `tracedocs validate study-docs` exits 0

## Common First-Run Issues

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| `command not found: tracedocs` | venv not active / not installed | Use `.venv/bin/tracedocs` or activate the venv |
| `Error: git is required ...` | Git URL used without `git` installed | Install `git`, or pass a local path |
| `Error: Target path is not a directory` | Bad path argument | Point at an existing repository directory |
