# Troubleshooting

## Quick Diagnostics

```bash
pytest -q
tracedocs validate study-docs
```

## Common Issues

| Symptom | Likely Cause | Check | Fix |
| --- | --- | --- | --- |
| `command not found` | Not installed / venv inactive | `which tracedocs` | `pip install -e .` or use `.venv/bin/...` |
| `Error: git is required ...` | Git URL without `git` | `git --version` | Install `git` or pass a local path |
| `Error: Target path is not a directory` | Bad path | Confirm the directory exists | Pass a valid repo path |
| Empty/sparse docs | Language/framework not recognised | Inspect `_evidence/assumptions.md` | Add detection in `scanner.py`/`analyzers.py` |
| `validate` reports problems | Broken links / missing files / leaked value | Read the listed problems | Regenerate or fix the offending file |

## Debugging Workflow

1. Reproduce with the exact command and target path.
2. Read the stdout summary and any `Error:` line (exit code 2 = generate error).
3. Open `_evidence/source-map.md` and `assumptions.md` to see what was (and was
   not) detected.
4. For extraction gaps, add a failing test in `tests/` first, then fix.
5. Re-run `pytest -q` and `validate`.

## When To Escalate

- The target uses a framework/ORM with no detection support yet.
- A regex change risks false positives across languages — add tests and review.
- Output must be embedded somewhere with stricter Markdown constraints.
