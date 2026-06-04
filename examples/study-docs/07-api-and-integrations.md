# API and Integrations

## Surface

`project-to-study` has no HTTP API; its interface is the command line. The
commands below are the public surface.

## Commands

| Command | Purpose | Key options | Evidence |
| --- | --- | --- | --- |
| `generate <path>` (default) | Scan a repo and write `study-docs/` | `--out`, `--style` | `cli.py` `_run_generate` |
| `validate <dir>` | Check a generated package | — | `cli.py` `_run_validate` |
| `--version` | Print the version | — | `cli.py` argparse |

A bare first argument that is not a known subcommand is treated as the path to
`generate`, so `project-to-study ./repo --out docs` works without typing
`generate`.

Evidence: `cli.py` `main()` dispatch
Confidence: Verified

## External Integrations

| Integration | Role | Evidence |
| --- | --- | --- |
| `git` (subprocess) | `git clone --depth 1` a Git URL into a temp dir | `source.py` `acquire` |

No other external services, SDKs, or network calls are used.

## Auth And Credentials

None. The tool requires no API keys or tokens. For Git-URL input it relies on
the ambient `git` configuration of the host.

Confidence: Verified

## Failure Modes

- Git URL given but `git` is missing, or the clone fails → a clear
  `RuntimeError`, surfaced as exit code `2`. Evidence: `source.py`. Confidence:
  Verified
- Path is not a directory → `NotADirectoryError`, exit code `2`. Evidence:
  `scanner.scan`. Confidence: Verified
