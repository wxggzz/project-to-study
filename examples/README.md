# Examples

## `study-docs/`

A complete, worked sample of what the **tracedocs skill** produces. It
documents this project's own deterministic CLI (the implementation kept on the
[`cli`](https://github.com/wxggzz/tracedocs/tree/cli) branch) — a real,
non-trivial Python project with a scanner, analyzers, a writer, and a test
suite.

Browse it as a linear path starting at
[`study-docs/README.md`](study-docs/README.md), or jump to any manual:
overview, quickstart, operation, deployment, learning, code introduction,
architecture, API, data model, troubleshooting, maintenance.

Note how the package follows the skill's contract even where things don't
apply: `03-deployment-manual.md` states plainly that no deployment config
exists (instead of inventing steps), `08-data-model.md` documents the in-memory
dataclass model (there is no database), and every claim carries an
`Evidence:` / `Confidence:` note backed by `_evidence/`.
