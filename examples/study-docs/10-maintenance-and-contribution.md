# Maintenance and Contribution

## Coding Conventions

_Follow the conventions visible in the existing source. Document any linter/formatter configuration found in the repository._

## Testing Expectations

Run `npm run test` before submitting changes.

## Release Checklist

- Tests pass.
- Documentation updated where behavior changed.
- Version bumped if applicable.
- Deployment configuration reviewed.

## Safe Change Workflow

- Branch from the default branch.
- Make the smallest useful change.
- Run tests and linters.
- Open a reviewable change with context.

## AI-Agent Handoff Notes

When an AI agent continues work, point it at this package and at `_evidence/` so it can distinguish verified facts from inferences before making changes.
