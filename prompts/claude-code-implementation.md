# Claude Code Implementation Prompt

Use this prompt when asking Claude Code to implement the first version.

```text
You are working in the project-to-study repository.

Goal:
Build an MVP that generates a Markdown study documentation package from a
target codebase.

Read these files first:
- README.md
- SKILL.md
- CLAUDE.md
- TASKS.md
- docs/architecture.md
- docs/output-document-map.md
- references/analysis-checklist.md
- references/markdown-style-guide.md
- references/handoff-protocol.md

Implementation requirements:
1. Create a simple CLI command:
   project-to-study /path/to/repo --out study-docs
2. Scan the target repo for:
   - project name
   - language/framework signals
   - package manager
   - install, dev, build, test, lint scripts
   - entry points
   - environment variable names
   - deployment config
   - tests
   - important source folders
3. Generate Markdown files using references/templates/.
4. Generate evidence files under study-docs/_evidence/.
5. Mark unsupported details as Unknown or Needs confirmation.
6. Add tests using a small fixture project.
7. Update TASKS.md with completed work and next steps.

Keep the MVP deterministic. Do not add an LLM API dependency yet.
```

