"""Validator for a generated study-docs/ package.

Implements the quality check described in ``docs/roadmap.md`` (Phase 4) and the
SKILL.md "Phase 4: Quality Check". Returns a list of problems; an empty list
means the package passed.

Checks performed:
- required documents and evidence files exist
- relative Markdown links resolve to files that exist
- architecture/code docs contain a Mermaid diagram
- no obvious secret-looking values leaked into the docs
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from . import templates as T

# Matches a markdown link target, capturing the path part (ignoring anchors).
_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

# Heuristic: KEY = "long-secret-ish-value". Names only should appear in docs,
# so a value that looks like a real secret is a leak.
_SECRET_RE = re.compile(
    r"(?i)(secret|token|password|api[_-]?key)\s*[:=]\s*['\"][A-Za-z0-9/_+\-]{12,}['\"]"
)


def validate(docs_dir: str) -> List[str]:
    root = Path(docs_dir)
    problems: List[str] = []

    if not root.is_dir():
        return [f"Docs directory does not exist: {root}"]

    # Required documents.
    for fname, _title in T.DOCUMENTS:
        if not (root / fname).exists():
            problems.append(f"Missing required document: {fname}")
    if not (root / "README.md").exists():
        problems.append("Missing package README.md")

    # Evidence files.
    for name in T.EVIDENCE_FILES:
        if not (root / "_evidence" / name).exists():
            problems.append(f"Missing evidence file: _evidence/{name}")

    # Per-file checks.
    for md in sorted(root.rglob("*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")

        # Broken relative links.
        for target in _LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            path_part = target.split("#", 1)[0].strip()
            if not path_part:
                continue
            if not (md.parent / path_part).exists():
                problems.append(
                    f"Broken link in {md.relative_to(root)}: `{target}`")

        # Secret leakage.
        if _SECRET_RE.search(text):
            problems.append(
                f"Possible secret value in {md.relative_to(root)} "
                "(should be names only)")

    # Diagram presence in architecture + code introduction.
    for fname in ("06-architecture.md", "05-code-introduction.md"):
        p = root / fname
        if p.exists() and "```mermaid" not in p.read_text(encoding="utf-8"):
            problems.append(f"{fname} is missing a Mermaid diagram")

    return problems
