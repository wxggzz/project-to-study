# Troubleshooting

> Audience: anyone debugging the project.
> Signature payoff: a real **symptom → check → likely cause → fix** table,
> seeded with this project's actual failure modes.

## Quick Diagnostics

```bash
<verified diagnostic commands, e.g. the test command and a health/status check>
```

## Common Issues

| Symptom | Check | Likely cause | Fix |
| --- | --- | --- | --- |
| Won't start | Read the startup error / logs | Missing/invalid env vars | Set required variables (see `02-operation-manual.md`) |
| Dependency errors | Compare local vs manifest/CI versions | Toolchain mismatch | Align versions |
| Tests fail locally | Run the test command, read output | Environment not configured | Fix config or code |

> Replace/extend with failure modes specific to this project. Prefer real ones
> seen in code, issues, or tests over generic advice.

## Debugging Workflow

1. Reproduce the issue.
2. Read logs / error output.
3. Check environment variables.
4. Run the tests.
5. Trace the relevant code path.
6. Document the fix (and update these docs if behaviour changed).

## When To Escalate

- Credentials or infrastructure access is required.
- Production data may be affected.
- The deployment path is undocumented.
- The issue cannot be reproduced locally.
