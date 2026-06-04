# Quickstart

## Prerequisites

- JavaScript toolchain
- npm

## Install

```bash
npm install
```

Evidence: package.json + lockfile
Confidence: Verified

## Run Locally

```bash
npm run dev
```

Evidence: package.json scripts.dev
Confidence: Verified

## Run Tests

```bash
npm run test
```

Evidence: package.json scripts.test
Confidence: Verified

## First-Run Checklist

- Dependencies installed
- Environment variables configured (see `02-operation-manual.md`)
- Application starts
- Tests pass or known failures are documented

## Common First-Run Issues

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| Install fails | Wrong toolchain version | Match versions in the manifest/CI |
| App will not start | Missing environment variables | Copy the env template and fill required values |
