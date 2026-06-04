# Operation Manual

## Daily Operation

`project-to-study` is an on-demand CLI, not a long-running service. You invoke it
to (re)generate docs for a target repository, and optionally to validate an
existing package. Behaviour is controlled entirely by command-line flags — there
is no runtime configuration file or environment variable.

## Runtime Commands

| Task | Command | Evidence | Confidence |
| --- | --- | --- | --- |
| Generate docs | `project-to-study <path> --out study-docs` | `cli.py` `_run_generate` | Verified |
| Choose a style | `project-to-study <path> --out study-docs --style teaching` | `cli.py` `--style`, `style.py` | Verified |
| Generate from a Git URL | `project-to-study https://github.com/owner/repo --out study-docs` | `source.py` `acquire` | Verified |
| Validate a package | `project-to-study validate study-docs` | `cli.py` `_run_validate`, `validate.py` | Verified |
| Show version | `project-to-study --version` | `cli.py` argparse `--version` | Verified |

## Configuration

The tool itself reads **no environment variables** and has no config file; all
behaviour comes from CLI flags (`--out`, `--style`). When scanning a target
repo it records that repo's environment variable **names** only — never values.

Evidence: `cli.py` argparse options; `scanner.py` env handling (names only)
Confidence: Verified

## Logs And Health Checks

- Output goes to stdout: a one-line scan summary and a count of files written.
- Exit codes: `0` success; `2` on a generate error (bad path, failed clone);
  `validate` returns `1` when the package has problems.

Evidence: `cli.py` return values
Confidence: Verified

## Routine Maintenance

- Re-run `pytest -q` after any change to extraction logic.
- Re-generate sample output and `validate` it.
- Review regex heuristics when adding support for a new framework/ORM.

## Operational Risks

- Extraction is heuristic (regex), so unusual code styles may be missed or
  over-matched. Confidence: Inferred
- Very large repositories are bounded by file-count/size caps in `analyzers.py`,
  so some routes/entities in huge trees may not appear. Confidence: Verified
