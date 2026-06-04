# Claude Code Instructions

You are implementing `tracedocs`, inspired by
`zarazhangrui/codebase-to-course`.

The goal is not to clone that project. The goal is to reuse its successful
pattern:

- a strong `SKILL.md`
- reusable reference files
- structured templates
- a predictable output directory
- a quality-check pass before delivery

But the output is Markdown documentation, not an HTML course.

## Start Here

1. Read `README.md`.
2. Read `SKILL.md`.
3. Read `docs/architecture.md`.
4. Read `docs/output-document-map.md`.
5. Read `prompts/claude-code-implementation.md`.
6. Continue from `TASKS.md`.

## Implementation Preference

For the MVP, prefer a simple CLI over a large framework.

Suggested shape:

```text
project_to_study/
  __init__.py
  cli.py
  scanner.py
  model.py
  writer.py
  templates.py
  evidence.py
tests/
```

Suggested command:

```bash
tracedocs /path/to/repo --out study-docs
```

The CLI may be deterministic at first, with clear placeholders where LLM-backed
summarization can be added later.

## Non-Negotiables

- Generated docs must include an evidence section.
- Do not invent deployment steps.
- Do not expose secret values.
- If a target project lacks information, document the gap.
- Keep the generated Markdown readable on GitHub.

