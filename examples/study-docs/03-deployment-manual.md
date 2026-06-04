# Deployment Manual

## Deployment Summary

| Signal | Meaning |
| --- | --- |
| `Dockerfile` | Container image build (Docker) |

## Build

```bash
npm run build
```

Evidence: package.json scripts.build
Confidence: Verified

## Required Environment

| Variable | Purpose | Required | Evidence |
| --- | --- | --- | --- |
| `DATABASE_URL` | — | Yes | .env.example (name only) |
| `PORT` | — | Yes | .env.example (name only) |
| `STRIPE_SECRET_KEY` | — | Yes | .env.example (name only) |

## Deployment Steps

- Prepare the required environment variables.
- Build the project using the verified build command below.
- Deploy using the mechanism implied by the signals above.
- Run post-deployment checks.

## Rollback

Rollback procedure is not documented in the repository. _Confirm the rollback path with the infrastructure owner._ (Confidence: Needs confirmation)

## Deployment Unknowns

- Target environment / hosting provider (unless implied above)
- Secret management approach
- Release approval and rollback process
