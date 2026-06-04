"""tracedocs: generate a Markdown study-docs package from a codebase.

This package implements the deterministic MVP described in CLAUDE.md and
prompts/claude-code-implementation.md. It scans a target repository, extracts
factual signals, and writes a structured set of Markdown documents plus an
evidence trail under ``study-docs/``.
"""

__version__ = "0.1.0"
