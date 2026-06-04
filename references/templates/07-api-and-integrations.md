# API And Integrations

> Audience: developers, maintainers, and AI coding agents.
> Signature payoff: a sourced inventory of every API surface and external
> integration — including "not found" when the repo does not expose one.

## API Summary

Use one of these shapes.

**A) API found** — summarize the discovered surface:

> Exposes <HTTP API / CLI commands / RPC / event handlers>.
> Evidence: <route files / command entry points / schema files>
> Confidence: <Verified / Inferred>

**B) No API found** — state it plainly:

> No API routes, CLI command surface, RPC handlers, or public integration entry
> points were found in this repository.
> Confidence: Unknown or Not applicable — recorded in `_evidence/assumptions.md`.

## Routes Or Commands

| Method / Command | Path / Name | Handler | Purpose | Evidence | Confidence |
| --- | --- | --- | --- | --- | --- |
| `<GET>` | `</example>` | `<handler>` | <one sentence> | `<file>` | Verified |

> Include only routes or commands supported by source files. If the project has
> no routable/API surface, write "Not applicable" and cite the evidence checked.

## External Integrations

| Integration | Purpose | Config names | Evidence | Confidence |
| --- | --- | --- | --- | --- |
| `<service>` | <why it is used> | `<ENV_VAR_NAMES_ONLY>` | `<file>` | Verified |

> List credential/configuration variable names only. Never include secret values.

## Auth And Permissions

<How requests or commands are authenticated/authorized, if visible in source.
If not visible, write "Not documented in the repository" and mark Unknown.>

## Failure Modes

| Surface | Failure mode | How to detect | Evidence |
| --- | --- | --- | --- |
| `<route / integration>` | <timeout / bad credentials / validation error> | <logs/tests/status> | `<file>` |

## Unknowns To Confirm

- <Rate limits, webhook retries, auth owner, production credentials, or other
  details not present in the repo.>
