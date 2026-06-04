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

Important rules:
- Verify commands against source files.
- Do not invent deployment details.
- Do not expose secret values.
- Include an evidence map.
- Mark inferred or unknown information clearly.
```

