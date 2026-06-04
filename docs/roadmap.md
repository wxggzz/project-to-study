# Roadmap

## Phase 0: Design

- Create skill instructions.
- Define generated document map.
- Create templates and style guide.
- Create handoff prompts for Claude Code and Codex.

## Phase 1: Deterministic MVP

Build a CLI that scans a repository and generates Markdown from templates.

Core capabilities:

- detect package manager
- detect scripts and commands
- detect source layout
- detect tests
- detect env var names
- detect deployment signals
- write evidence files

## Phase 2: Better Analysis

Add language-aware analyzers:

- Node.js and TypeScript
- Python
- Go
- Java
- Rust

Add source-specific extraction:

- API routes
- database schema
- config files
- Docker and CI/CD

## Phase 3: LLM-Assisted Writing

Add an optional LLM writer that converts project facts and evidence into richer
Markdown explanations.

Rules:

- never send unnecessary files
- never let the LLM invent unsupported deployment details
- keep evidence visible
- support Claude, OpenAI, and local/manual modes later

## Phase 4: Validation

Add a validation command:

```bash
project-to-study validate study-docs/
```

Validation should check:

- referenced paths exist
- commands appear in source files or assumptions
- required docs exist
- evidence files exist
- Mermaid diagrams are present when architecture docs mention diagrams

