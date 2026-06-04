# API and Integrations

## Surface

This project exposes or consumes interfaces. Routes below were extracted directly from the source; confirm any that look ambiguous.

## Routes / Endpoints

| Method | Path | Handler | Source |
| --- | --- | --- | --- |
| GET | `/health` | — | src/index.js (Express/Node) |
| GET | `/users` | `listUsers` | src/index.js (Express/Node) |
| POST | `/users` | — | src/index.js (Express/Node) |

## External Services

| Service | Role | Evidence |
| --- | --- | --- |
| Stripe | External service | dependencies |

## Auth And Credentials

Credentials are supplied via environment variables (see `02-operation-manual.md`). Variable names only are documented; secret values are never extracted.

## Failure Modes

_Rate limits and external failure modes are not documented in the repository. Confirm with maintainers._ (Confidence: Needs confirmation)
