"""Internal data model for project-to-study.

The scanner produces a :class:`ProjectFacts` instance plus a list of
:class:`Claim` objects. The writer and evidence modules consume those.

Confidence labels follow ``references/handoff-protocol.md`` exactly:
``Verified``, ``Inferred``, ``Unknown``, ``Needs confirmation``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


class Confidence:
    """Canonical confidence labels (see references/handoff-protocol.md)."""

    VERIFIED = "Verified"
    INFERRED = "Inferred"
    UNKNOWN = "Unknown"
    NEEDS_CONFIRMATION = "Needs confirmation"

    ALL = (VERIFIED, INFERRED, UNKNOWN, NEEDS_CONFIRMATION)


@dataclass
class Claim:
    """A single statement traceable to a source.

    ``evidence`` is a short, human-readable pointer such as
    ``package.json scripts.dev`` or ``Dockerfile present``.
    """

    text: str
    evidence: str
    confidence: str = Confidence.UNKNOWN


@dataclass
class Command:
    """A runnable command discovered or inferred from the project."""

    label: str          # e.g. "Start development server"
    command: str        # e.g. "npm run dev"
    evidence: str = ""
    confidence: str = Confidence.UNKNOWN


@dataclass
class EnvVar:
    """An environment variable. Only the NAME is ever recorded, never a value."""

    name: str
    purpose: str = ""
    required: str = "Unknown"   # "Yes" | "No" | "Unknown"
    evidence: str = ""
    confidence: str = Confidence.INFERRED


@dataclass
class ImportantFile:
    """A notable file or directory in the target repo."""

    path: str
    purpose: str


@dataclass
class Route:
    """An HTTP route/endpoint extracted from source code."""

    method: str          # GET/POST/... or "—" when unknown
    path: str            # e.g. "/users/:id"
    evidence: str        # "file.js:42 (Express)"


@dataclass
class Entity:
    """A data entity / model / table extracted from source or schema."""

    name: str
    kind: str            # e.g. "SQLAlchemy model", "Prisma model", "SQL table"
    evidence: str        # source file (relative path)


@dataclass
class ProjectFacts:
    """Normalized facts extracted from the target repository.

    Mirrors the model sketched in docs/architecture.md.
    """

    name: str = "Unknown project"
    root: str = ""          # local directory actually scanned
    source: str = ""        # original spec (local path or remote URL) for display
    summary: str = ""
    summary_confidence: str = Confidence.UNKNOWN

    languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    package_managers: List[str] = field(default_factory=list)

    # Commands, grouped by purpose.
    install_commands: List[Command] = field(default_factory=list)
    run_commands: List[Command] = field(default_factory=list)
    build_commands: List[Command] = field(default_factory=list)
    test_commands: List[Command] = field(default_factory=list)
    lint_commands: List[Command] = field(default_factory=list)

    entry_points: List[ImportantFile] = field(default_factory=list)
    env_vars: List[EnvVar] = field(default_factory=list)
    integrations: List[str] = field(default_factory=list)
    data_stores: List[str] = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    entities: List[Entity] = field(default_factory=list)
    deployment_signals: List[ImportantFile] = field(default_factory=list)
    test_signals: List[ImportantFile] = field(default_factory=list)
    important_files: List[ImportantFile] = field(default_factory=list)

    source_tree: str = ""
    license_name: Optional[str] = None
    has_tests: bool = False
    test_framework: Optional[str] = None

    unknowns: List[str] = field(default_factory=list)
    claims: List[Claim] = field(default_factory=list)

    def add_claim(self, text: str, evidence: str, confidence: str) -> None:
        self.claims.append(Claim(text=text, evidence=evidence, confidence=confidence))

    def all_commands(self) -> List[Command]:
        return (
            self.install_commands
            + self.run_commands
            + self.build_commands
            + self.test_commands
            + self.lint_commands
        )
