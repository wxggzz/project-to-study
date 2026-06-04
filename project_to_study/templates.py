"""Document manifest and shared Markdown render helpers.

The ordered document list mirrors ``docs/output-document-map.md`` and the output
tree in ``README.md`` / ``SKILL.md``. The CLI builds these sections from facts
rather than string-replacing the reference templates, so the human-facing
templates under ``references/templates/`` stay untouched.
"""

from __future__ import annotations

import os
from typing import Iterable, List, Sequence

# (filename, title) in linear learning-path order.
DOCUMENTS: List[tuple] = [
    ("00-project-overview.md", "Project Overview"),
    ("01-quickstart.md", "Quickstart"),
    ("02-operation-manual.md", "Operation Manual"),
    ("03-deployment-manual.md", "Deployment Manual"),
    ("04-learning-manual.md", "Learning Manual"),
    ("05-code-introduction.md", "Code Introduction"),
    ("06-architecture.md", "Architecture"),
    ("07-api-and-integrations.md", "API and Integrations"),
    ("08-data-model.md", "Data Model"),
    ("09-troubleshooting.md", "Troubleshooting"),
    ("10-maintenance-and-contribution.md", "Maintenance and Contribution"),
]

EVIDENCE_FILES = ("source-map.md", "assumptions.md", "generation-log.md")


def heading(level: int, text: str) -> str:
    return f"{'#' * level} {text}"


def md_escape(text: str) -> str:
    """Escape pipe characters so free text is safe inside a Markdown table."""

    return text.replace("|", "\\|").replace("\n", " ").strip()


def table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    """Render a GitHub-flavored Markdown table. Returns '' if no rows."""

    rows = [list(r) for r in rows]
    if not rows:
        return ""
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = [
        "| " + " | ".join(md_escape(str(c)) for c in row) + " |"
        for row in rows
    ]
    return "\n".join([head, sep, *body])


def bullets(items: Iterable[str]) -> str:
    items = [str(i) for i in items if str(i).strip()]
    return "\n".join(f"- {i}" for i in items)


def code_block(content: str, lang: str = "") -> str:
    return f"```{lang}\n{content}\n```"


def evidence_note(evidence: str, confidence: str) -> str:
    ev = evidence or "Not directly sourced"
    return f"Evidence: {ev}\nConfidence: {confidence}"


def display_path(root: str) -> str:
    """Show a path relative to the cwd when possible.

    Keeps committed/generated output machine-agnostic; falls back to the
    absolute path when the target lives outside the current working directory.
    """

    if not root:
        return "Unknown"
    # Remote URLs (and scp-style git@host:path) are shown as-is.
    if "://" in root or root.startswith("git@"):
        return root
    try:
        rel = os.path.relpath(root, os.getcwd())
    except ValueError:
        return root
    return rel if not rel.startswith("..") else root


def join_sections(sections: Iterable[str]) -> str:
    """Join non-empty sections with blank-line separators, ending with newline."""

    parts = [s.strip() for s in sections if s and s.strip()]
    return "\n\n".join(parts) + "\n"
