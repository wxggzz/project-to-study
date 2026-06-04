# Deployment Manual

> Audience: deployers and infrastructure owners.
> Signature payoff: either a **verified deployment path** (with evidence) or an
> explicit **"deployment not found"** — never invented steps.

## Deployment Summary

Use exactly one of these two shapes.

**A) Deployment found** — describe the discovered target with evidence:

> Deploys via <Docker / Vercel / GitHub Actions / …>.
> Evidence: <Dockerfile / .github/workflows/deploy.yml / vercel.json>
> Confidence: Verified

**B) No deployment found** — state it plainly:

> No deployment configuration was found in this repository (no Dockerfile, CI
> workflow, or hosting config). Deployment is therefore undocumented.
> Confidence: Unknown — recorded in `_evidence/assumptions.md`.

## Build

```bash
<verified build command, or "# no build step detected">
```

Evidence: <source>
Confidence: <Verified / Inferred / Unknown>

## Required Environment

| Variable | Purpose | Required | Evidence |
| --- | --- | --- | --- |
| `EXAMPLE_VAR` | <purpose> | Yes/No | <source> |

## Deployment Steps

<Only if shape A. List steps that the evidence supports. If shape B, write:
"No deployment steps can be derived from the repository.">

## Rollback

<Only if the repo provides evidence; otherwise: "Unknown — Needs confirmation.">

## Deployment Unknowns

- <Hosting target, secret management, release approval, rollback — whatever the
  repo does not answer.>
