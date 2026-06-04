# Operation Manual

> Audience: operators and maintainers running the project day to day.
> Signature payoff: the exact commands to run/observe/stop it, plus its config
> surface — names only, never secret values.

## Daily Operation

<How it is run and observed in practice: a service? a CLI? a scheduled job?>

## Runtime Commands

| Task | Command | Evidence | Confidence |
| --- | --- | --- | --- |
| Start (dev) | <cmd> | <source> | Verified |
| Start (prod) | <cmd> | <source> | Inferred |
| Run tests | <cmd> | <source> | Verified |

## Configuration

| Variable | Purpose | Required | Evidence |
| --- | --- | --- | --- |
| `EXAMPLE_VAR` | <what it controls> | Yes/No | <.env.example / source ref> |

> List variable **names only**. Never copy real secret values.

## Logs And Health Checks

<Where logs go and how to confirm health. If not detectable, say so and mark
`Needs confirmation` — do not invent a /health endpoint or log path.>

## Routine Maintenance

- Update dependencies and re-run tests
- Review configuration and rotate credentials per policy
- Re-generate these docs after notable changes

## Operational Risks

<Known or inferred risks — single points of failure, fragile scripts, manual
steps. Label each Verified/Inferred.>
