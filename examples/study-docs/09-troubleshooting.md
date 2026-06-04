# Troubleshooting

## Quick Diagnostics

```bash
npm run test
npm run dev
```

## Common Issues

| Symptom | Likely Cause | Check | Fix |
| --- | --- | --- | --- |
| App will not start | Missing/invalid env vars | Compare against the env template | Set required variables |
| Dependency errors | Toolchain or version mismatch | Check the manifest and CI versions | Align local versions |
| Tests fail locally | Environment not configured | Run the test command and read output | Fix config or code |

## Debugging Workflow

1. Reproduce the issue.
2. Check logs.
3. Check environment variables.
4. Run the tests.
5. Trace the relevant code path.
6. Document the fix.

## When To Escalate

- Credentials or infrastructure access is required.
- Production data may be affected.
- The deployment path is undocumented.
- The issue cannot be reproduced locally.
