# Examples

## `study-docs/`

A committed, real sample of the generator's output. It was produced from the
bundled test fixture so reviewers can see the result without running anything:

```bash
tracedocs tests/fixtures/sample-node-app --out examples/study-docs
tracedocs validate examples/study-docs
```

The fixture (`tests/fixtures/sample-node-app/`) is a tiny Express service with a
Dockerfile, an `.env.example`, and PostgreSQL/Stripe dependencies, so the sample
exercises framework, data-store, integration, env-var, and deployment detection.

Regenerate it whenever the writer changes so the demo stays current.
