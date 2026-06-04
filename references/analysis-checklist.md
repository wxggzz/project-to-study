# Analysis Checklist

Use this checklist before generating Markdown.

## Repository Basics

- project name
- README summary
- license
- primary language
- package manager
- monorepo or single project
- important root files

## Runtime And Commands

- install command
- development command
- production start command
- build command
- test command
- lint command
- format command

Evidence sources may include:

- `package.json`
- `pyproject.toml`
- `requirements.txt`
- `Pipfile`
- `go.mod`
- `Cargo.toml`
- `pom.xml`
- `Makefile`
- `README.md`
- CI config

## Source Layout

Identify:

- app entry points
- UI components
- API routes
- services
- database layer
- scripts
- tests
- generated files

## Configuration

Collect environment variable names from:

- `.env.example`
- config files
- source references
- Docker files
- CI files

Never copy real secret values.

## Deployment Signals

Look for:

- Dockerfile
- docker-compose files
- Vercel/Netlify config
- Railway/Fly/Render config
- Kubernetes manifests
- Terraform
- GitHub Actions
- deployment scripts

## Architecture Signals

Find:

- request flow
- data flow
- background jobs
- queues
- external APIs
- auth/session logic
- caching
- state management

## Testing And Quality

Find:

- test framework
- test command
- fixture files
- coverage config
- linting
- type checking
- CI checks

## Risk And Unknowns

Record:

- missing README details
- undocumented env vars
- unclear deployment target
- missing tests
- hardcoded paths
- fragile scripts
- generated docs that require user confirmation

