# Operation Manual

## Daily Operation

Run, monitor, and stop the project using the commands below. Commands are sourced from the project manifest where possible.

## Runtime Commands

| Task | Command | Evidence | Confidence |
| --- | --- | --- | --- |
| Start development server | `npm run dev` | package.json scripts.dev | Verified |
| Start application | `npm run start` | package.json scripts.start | Verified |
| Run tests | `npm run test` | package.json scripts.test | Verified |
| Lint | `npm run lint` | package.json scripts.lint | Verified |

## Configuration

| Variable | Purpose | Required | Evidence |
| --- | --- | --- | --- |
| `DATABASE_URL` | — | Yes | .env.example (name only) |
| `PORT` | — | Yes | .env.example (name only) |
| `STRIPE_SECRET_KEY` | — | Yes | .env.example (name only) |

Variable **names only** are listed here; secret values are never extracted by this tool.

## Logs And Health Checks

_Logging and health-check behavior was not detected automatically. Document where logs are written and how to confirm the service is healthy._ (Confidence: Needs confirmation)

## Routine Maintenance

- Update dependencies and re-run tests
- Review deployment configuration
- Check generated files and lockfiles

## Operational Risks

- No major gaps detected during scanning.
