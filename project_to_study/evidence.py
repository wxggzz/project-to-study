"""Evidence-trail writer.

Writes the three files mandated by ``references/handoff-protocol.md`` so the
next agent can distinguish facts from guesses:

- ``source-map.md``      claim -> evidence -> confidence
- ``assumptions.md``     verified / inferred / unknown / needs-confirmation
- ``generation-log.md``  run metadata and scanner statistics
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import List

from . import templates as T
from .model import Confidence, ProjectFacts


def write_evidence(
    facts: ProjectFacts,
    evidence_dir: Path,
    skipped_notes: List[str],
    version: str,
    style_name: str = "standard",
) -> List[str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)

    (evidence_dir / "source-map.md").write_text(
        _source_map(facts), encoding="utf-8")
    (evidence_dir / "assumptions.md").write_text(
        _assumptions(facts, skipped_notes), encoding="utf-8")
    (evidence_dir / "generation-log.md").write_text(
        _generation_log(facts, version, style_name), encoding="utf-8")

    return list(T.EVIDENCE_FILES)


def _source_map(facts: ProjectFacts) -> str:
    rows = [(c.text, f"`{c.evidence}`" if c.evidence else "—", c.confidence)
            for c in facts.claims]
    return T.join_sections([
        T.heading(1, "Source Map"),
        "Every generated claim and the evidence behind it.",
        T.table(["Claim", "Evidence", "Confidence"], rows)
        or "_No claims recorded._",
    ])


def _assumptions(facts: ProjectFacts, skipped_notes: List[str]) -> str:
    buckets = {c: [] for c in Confidence.ALL}
    for claim in facts.claims:
        buckets.setdefault(claim.confidence, []).append(claim.text)

    sections = [
        T.heading(1, "Assumptions"),
        "Generated claims grouped by confidence. Review anything that is not "
        "`Verified` before relying on it.",
        T.heading(2, "Verified Facts"),
        T.bullets(buckets.get(Confidence.VERIFIED, []))
        or "_None recorded._",
        T.heading(2, "Reasonable Inferences"),
        T.bullets(buckets.get(Confidence.INFERRED, []))
        or "_None recorded._",
        T.heading(2, "Unknowns"),
        T.bullets(facts.unknowns + buckets.get(Confidence.UNKNOWN, []))
        or "_None recorded._",
        T.heading(2, "Needs Confirmation"),
        T.bullets(buckets.get(Confidence.NEEDS_CONFIRMATION, []))
        or "_See individual documents for items marked Needs confirmation._",
    ]

    if skipped_notes:
        sections += [
            T.heading(2, "Omitted Or Not-Applicable Documents"),
            T.bullets(skipped_notes),
        ]

    return T.join_sections(sections)


def _generation_log(facts: ProjectFacts, version: str, style_name: str) -> str:
    now = _dt.datetime.now().isoformat(timespec="seconds")
    stats_rows = [
        ("Target path", f"`{T.display_path(facts.source or facts.root)}`"),
        ("Project name", facts.name),
        ("Languages", ", ".join(facts.languages) or "Unknown"),
        ("Package managers", ", ".join(facts.package_managers) or "Unknown"),
        ("Commands detected", str(len(facts.all_commands()))),
        ("Env var names", str(len(facts.env_vars))),
        ("API routes", str(len(facts.routes))),
        ("Data entities", str(len(facts.entities))),
        ("Entry points", str(len(facts.entry_points))),
        ("Deployment signals", str(len(facts.deployment_signals))),
        ("Has tests", "Yes" if facts.has_tests else "No"),
        ("Total claims", str(len(facts.claims))),
    ]
    return T.join_sections([
        T.heading(1, "Generation Log"),
        T.table(["Field", "Value"], stats_rows),
        T.heading(2, "Run Metadata"),
        T.bullets([
            f"Tool: project-to-study v{version}",
            f"Generated at: {now}",
            f"Style: {style_name}",
            "Mode: deterministic (no LLM)",
        ]),
    ])
