# Generate Study Docs Prompt

Use this prompt after the project has either a CLI implementation or a working
agent skill.

```text
Use the tracedocs workflow.

Target project:
<TARGET_PATH_OR_GITHUB_URL>

Output directory:
study-docs/

Generate Markdown documentation for:
- project overview
- quickstart
- operation manual
- deployment manual
- learning manual
- code introduction
- architecture
- API and integrations if applicable
- data model if applicable
- troubleshooting
- maintenance and contribution

Also generate:
- `index.json` as a small machine-readable manifest for AI agents
- `_evidence/source-map.md`
- `_evidence/assumptions.md`
- `_evidence/generation-log.md`

Optional:
- `index.html` as a single-file preview only if it can be derived from the
  Markdown docs without adding new facts. Markdown remains the source of truth.

Important rules:
- Verify commands against source files.
- Do not invent deployment details.
- Do not expose secret values.
- Include evidence and confidence labels for operational claims.
- Mark inferred or unknown information clearly.
- List environment variable names only; never copy secret values.
```
