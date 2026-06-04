# Quickstart

> Audience: anyone who wants to run the project now.
> Signature payoff: copy-paste **verified** install / run / test commands — each
> sourced, or clearly marked inferred.

## Prerequisites

- <Tool + version, e.g. "Node 20+"> — Evidence: <engines field / CI / README>

## Install

```bash
<verified install command>
```

Evidence: <e.g. package.json + lockfile>
Confidence: Verified

## Run Locally

```bash
<verified run command>
```

Evidence: <e.g. package.json `scripts.dev`>
Confidence: Verified

## Run Tests

```bash
<verified test command>
```

Evidence: <e.g. pyproject dev deps + tests/>
Confidence: Verified

> If a command is not in the repo, write `# no <install/run/test> command found`
> and label it `Confidence: Unknown` — do not guess one.

## First-Run Checklist

- [ ] Dependencies installed
- [ ] Required environment variables set (see `02-operation-manual.md`)
- [ ] App starts / command runs
- [ ] Tests pass, or known failures are documented

## Common First-Run Issues

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Install fails | Toolchain/version mismatch | Match the version in the manifest/CI |
| Won't start | Missing env vars | Copy the env template and fill required values |
