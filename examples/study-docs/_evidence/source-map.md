# Source Map

Every notable claim and the evidence behind it.

| Claim | Evidence | Confidence |
| --- | --- | --- |
| Project name is `project-to-study`. | `pyproject.toml` `[project].name` | Verified |
| Requires Python ≥ 3.9. | `pyproject.toml` `requires-python` | Verified |
| Has no runtime dependencies. | `pyproject.toml` `dependencies = []` | Verified |
| Installed as the `project-to-study` console script → `cli:main`. | `pyproject.toml` `[project.scripts]` | Verified |
| Dev/test dependency is pytest. | `pyproject.toml` `optional-dependencies.dev` | Verified |
| Licensed MIT. | `pyproject.toml` `license` | Verified |
| Entry/dispatch lives in `cli.py:main`; bare path → `generate`. | `cli.py` `main()` | Verified |
| Commands are `generate` and `validate`. | `cli.py` subparsers | Verified |
| Output styles: standard/concise/teaching/ops. | `style.py`, `cli.py` `--style` | Verified |
| Git URL input is shallow-cloned via `git` and cleaned up. | `source.py` `acquire` | Verified |
| The pipeline is scan → analyze → write + evidence. | `cli.py`, `writer.py` | Verified |
| Largest modules are `scanner.py` (~714) and `writer.py` (~702). | `wc -l project_to_study/*.py` | Verified |
| No deployment/CI configuration exists. | absence of Dockerfile/CI/Makefile | Verified |
| The tool reads no environment variables of its own. | `cli.py` argparse-only config | Verified |
| A wheel could be built with `python -m build`. | `pyproject.toml` `[build-system]` | Inferred |
| PyPI publishing is not configured. | no publish workflow/config found | Needs confirmation |
