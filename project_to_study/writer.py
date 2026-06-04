"""Markdown writer.

Turns :class:`ProjectFacts` into the ``study-docs/`` package. Each document
mirrors the corresponding scaffold in ``references/templates/`` while filling in
real, evidence-tagged content. A small document planner decides whether the
API and data-model docs carry real content or a "not applicable" note.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from . import __version__, evidence as evidence_mod, templates as T
from .model import Command, Confidence, ProjectFacts
from .style import Style

UNKNOWN = "_Unknown — not enough evidence._"

_OPS_CALLOUT = (
    "> **Operational priority document.** This was front-loaded because the "
    "package was generated with `--style ops`.")


def _optional(include: bool, *blocks: str) -> list:
    """Return the blocks when ``include`` is true, else an empty list.

    Used to splice optional prose into a section list so ``concise`` style can
    drop it while ``standard``/``teaching``/``ops`` keep it.
    """

    return list(blocks) if include else []


@dataclass
class GenerationResult:
    out_dir: str
    written: List[str] = field(default_factory=list)
    skipped_notes: List[str] = field(default_factory=list)


def generate(facts: ProjectFacts, out_dir: str,
             style: Optional[Style] = None) -> GenerationResult:
    """Write the full study-docs package and return a summary."""

    style = style or Style()

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "assets").mkdir(exist_ok=True)
    (out / "_evidence").mkdir(exist_ok=True)

    result = GenerationResult(out_dir=str(out))

    # Document planner: decide applicability of the conditional docs.
    api_applicable = bool(facts.routes or facts.integrations or facts.frameworks)
    data_applicable = bool(facts.entities or facts.data_stores)

    writers: Dict[str, Callable[[ProjectFacts, Style], str]] = {
        "00-project-overview.md": _overview,
        "01-quickstart.md": _quickstart,
        "02-operation-manual.md": _operation,
        "03-deployment-manual.md": _deployment,
        "04-learning-manual.md": _learning,
        "05-code-introduction.md": _code_intro,
        "06-architecture.md": _architecture,
        "07-api-and-integrations.md": (
            _api if api_applicable
            else lambda f, s: _not_applicable(
                "API and Integrations",
                "No web framework, route files, or external integrations were "
                "detected in the repository.")),
        "08-data-model.md": (
            _data_model if data_applicable
            else lambda f, s: _not_applicable(
                "Data Model",
                "No database driver, ORM, schema, or migrations were detected "
                "in the repository.")),
        "09-troubleshooting.md": _troubleshooting,
        "10-maintenance-and-contribution.md": _maintenance,
    }

    for filename, _title in T.DOCUMENTS:
        content = writers[filename](facts, style)
        (out / filename).write_text(content, encoding="utf-8")
        result.written.append(filename)

    if not api_applicable:
        result.skipped_notes.append(
            "`07-api-and-integrations.md`: no API/integration evidence; written "
            "with a not-applicable note.")
    if not data_applicable:
        result.skipped_notes.append(
            "`08-data-model.md`: no data-store evidence; written with a "
            "not-applicable note.")

    # Mermaid asset files.
    (out / "assets" / "architecture.mmd").write_text(
        _architecture_diagram(facts) + "\n", encoding="utf-8")
    (out / "assets" / "request-flow.mmd").write_text(
        _flow_diagram(facts) + "\n", encoding="utf-8")
    result.written.extend(["assets/architecture.mmd", "assets/request-flow.mmd"])

    # README index for the package.
    (out / "README.md").write_text(_package_readme(facts, style), encoding="utf-8")
    result.written.append("README.md")

    # Evidence trail.
    evidence_files = evidence_mod.write_evidence(
        facts, out / "_evidence", result.skipped_notes, __version__, style.name)
    result.written.extend(f"_evidence/{name}" for name in evidence_files)

    return result


# --------------------------------------------------------------------------- #
# Shared rendering helpers
# --------------------------------------------------------------------------- #

def _commands_table(commands: List[Command]) -> str:
    rows = [(c.label, f"`{c.command}`", c.evidence or "—", c.confidence)
            for c in commands]
    return T.table(["Task", "Command", "Evidence", "Confidence"], rows)


def _first_command(commands: List[Command]) -> Optional[Command]:
    return commands[0] if commands else None


def _command_block(command: Optional[Command], fallback_comment: str) -> str:
    if command:
        return "\n\n".join([
            T.code_block(command.command, "bash"),
            T.evidence_note(command.evidence, command.confidence),
        ])
    return "\n\n".join([
        T.code_block(f"# {fallback_comment}", "bash"),
        T.evidence_note("", Confidence.UNKNOWN),
    ])


# --------------------------------------------------------------------------- #
# Document writers
# --------------------------------------------------------------------------- #

def _overview(f: ProjectFacts, style: Style) -> str:
    summary = f.summary or UNKNOWN
    capabilities = []
    for fw in f.frameworks[:5]:
        capabilities.append(f"Built with {fw}.")
    for store in f.data_stores[:3]:
        capabilities.append(f"Persists data using {store}.")
    for integ in f.integrations[:3]:
        capabilities.append(f"Integrates with {integ}.")
    if not capabilities:
        capabilities = ["_Capabilities inferred from code structure; confirm with maintainers._"]

    stack_rows = []
    if f.languages:
        stack_rows.append(("Language(s)", ", ".join(f.languages[:5]),
                           "file census", Confidence.VERIFIED))
    if f.frameworks:
        stack_rows.append(("Framework(s)", ", ".join(f.frameworks),
                           "dependencies", Confidence.INFERRED))
    if f.package_managers:
        stack_rows.append(("Package manager", ", ".join(f.package_managers),
                           "manifest/lockfiles", Confidence.VERIFIED))
    if f.data_stores:
        stack_rows.append(("Data store(s)", ", ".join(f.data_stores),
                           "dependencies/schema", Confidence.INFERRED))
    if f.license_name:
        stack_rows.append(("License", f.license_name, "LICENSE file",
                           Confidence.VERIFIED))

    file_rows = [(f"`{i.path}`", i.purpose) for i in f.important_files]

    sections = [
        T.heading(1, "Project Overview"),
        *_optional(
            style.teaching,
            "> **New to this project?** Read this overview, then follow the "
            "linear path in `04-learning-manual.md`. Jargon is explained the "
            "first time it appears."),
        T.heading(2, "What This Project Does"),
        summary,
        *_optional(
            style.verbose,
            T.heading(2, "Who Uses It"),
            "_Inferred audience: developers and operators of this codebase. "
            "Confirm the end-user persona with the project owner._"),
        T.heading(2, "Main Capabilities"),
        T.bullets(capabilities),
        T.heading(2, "Tech Stack"),
        _commands_or(stack_rows,
                     T.table(["Area", "Technology", "Evidence", "Confidence"], stack_rows)),
        T.heading(2, "Important Files"),
        T.table(["Path", "Purpose"], file_rows) or UNKNOWN,
        T.heading(2, "What To Read Next"),
        "Start with `01-quickstart.md`, then `05-code-introduction.md`.",
    ]
    return T.join_sections(sections)


def _commands_or(rows: list, rendered: str) -> str:
    return rendered if rows else UNKNOWN


def _quickstart(f: ProjectFacts, style: Style) -> str:
    prereqs = []
    for lang in f.languages[:3]:
        prereqs.append(f"{lang} toolchain")
    for pm in f.package_managers[:3]:
        prereqs.append(f"{pm}")
    prereqs = prereqs or ["_Prerequisites not determined; confirm with maintainers._"]

    issues = T.table(
        ["Symptom", "Likely Cause", "Fix"],
        [
            ("Install fails", "Wrong toolchain version", "Match versions in the manifest/CI"),
            ("App will not start", "Missing environment variables",
             "Copy the env template and fill required values"),
        ],
    )

    return T.join_sections([
        T.heading(1, "Quickstart"),
        T.heading(2, "Prerequisites"),
        T.bullets(prereqs),
        T.heading(2, "Install"),
        _command_block(_first_command(f.install_commands),
                       "No install command detected"),
        T.heading(2, "Run Locally"),
        _command_block(_first_command(f.run_commands),
                       "No run command detected"),
        T.heading(2, "Run Tests"),
        _command_block(_first_command(f.test_commands),
                       "No test command detected"),
        *_optional(
            style.verbose,
            T.heading(2, "First-Run Checklist"),
            T.bullets([
                "Dependencies installed",
                "Environment variables configured (see `02-operation-manual.md`)",
                "Application starts",
                "Tests pass or known failures are documented",
            ])),
        T.heading(2, "Common First-Run Issues"),
        issues,
    ])


def _operation(f: ProjectFacts, style: Style) -> str:
    runtime = _commands_table(f.run_commands + f.test_commands + f.lint_commands)
    env_rows = [(f"`{e.name}`", e.purpose or "—", e.required, e.evidence)
                for e in f.env_vars]
    env_table = T.table(["Variable", "Purpose", "Required", "Evidence"], env_rows)

    return T.join_sections([
        T.heading(1, "Operation Manual"),
        *_optional(style.ops_focus, _OPS_CALLOUT),
        T.heading(2, "Daily Operation"),
        "Run, monitor, and stop the project using the commands below. "
        "Commands are sourced from the project manifest where possible.",
        T.heading(2, "Runtime Commands"),
        runtime or UNKNOWN,
        T.heading(2, "Configuration"),
        env_table or "_No environment variables detected. Confirm whether the "
        "project needs runtime configuration._",
        "Variable **names only** are listed here; secret values are never "
        "extracted by this tool.",
        T.heading(2, "Logs And Health Checks"),
        "_Logging and health-check behavior was not detected automatically. "
        "Document where logs are written and how to confirm the service is "
        "healthy._ (Confidence: Needs confirmation)",
        *_optional(
            style.verbose,
            T.heading(2, "Routine Maintenance"),
            T.bullets([
                "Update dependencies and re-run tests",
                "Review deployment configuration",
                "Check generated files and lockfiles",
            ])),
        T.heading(2, "Operational Risks"),
        T.bullets(f.unknowns or ["No major gaps detected during scanning."]),
    ])


def _deployment(f: ProjectFacts, style: Style) -> str:
    if f.deployment_signals:
        summary_rows = [(f"`{d.path}`", d.purpose) for d in f.deployment_signals]
        summary = T.table(["Signal", "Meaning"], summary_rows)
        steps = T.bullets([
            "Prepare the required environment variables.",
            "Build the project using the verified build command below.",
            "Deploy using the mechanism implied by the signals above.",
            "Run post-deployment checks.",
        ])
        rollback = ("Rollback procedure is not documented in the repository. "
                    "_Confirm the rollback path with the infrastructure owner._ "
                    "(Confidence: Needs confirmation)")
    else:
        summary = ("**No deployment configuration was found in this repository.** "
                   "Deployment steps are therefore unknown and are not invented "
                   "here. (Confidence: Unknown)")
        steps = "_No deployment steps can be derived from the repository._"
        rollback = "_Unknown — no deployment evidence found._"

    env_rows = [(f"`{e.name}`", e.purpose or "—", e.required, e.evidence)
                for e in f.env_vars]

    return T.join_sections([
        T.heading(1, "Deployment Manual"),
        *_optional(style.ops_focus, _OPS_CALLOUT),
        T.heading(2, "Deployment Summary"),
        summary,
        T.heading(2, "Build"),
        _command_block(_first_command(f.build_commands),
                       "No build command detected"),
        T.heading(2, "Required Environment"),
        T.table(["Variable", "Purpose", "Required", "Evidence"], env_rows)
        or "_No environment variables detected._",
        T.heading(2, "Deployment Steps"),
        steps,
        T.heading(2, "Rollback"),
        rollback,
        T.heading(2, "Deployment Unknowns"),
        T.bullets([
            "Target environment / hosting provider (unless implied above)",
            "Secret management approach",
            "Release approval and rollback process",
        ]),
    ])


def _learning(f: ProjectFacts, style: Style) -> str:
    entry = f.entry_points[0].path if f.entry_points else "the main entry point"
    test_cmd = _first_command(f.test_commands)
    run_cmd = _first_command(f.run_commands)

    concept_rows = []
    for fw in f.frameworks[:4]:
        concept_rows.append((fw, f"The framework this project is built on.",
                             "dependencies"))
    for store in f.data_stores[:3]:
        concept_rows.append((store, "How and where data is persisted.",
                             "dependencies/schema"))

    questions = [
        f"What command starts the project? "
        f"({run_cmd.command if run_cmd else 'unknown'})",
        f"Which file is the main entry point? (`{entry}`)",
        "Where does configuration come from?",
        f"Which tests cover the core behavior? "
        f"({test_cmd.command if test_cmd else 'no test command found'})",
    ]

    return T.join_sections([
        T.heading(1, "Learning Manual"),
        T.heading(2, "Learning Goal"),
        "After this guide you should understand what the project does, how it "
        "runs, where the important code lives, and how to ask an AI agent for "
        "safe changes.",
        T.heading(2, "Reading Path"),
        T.bullets([
            "Start with the README and `00-project-overview.md`.",
            f"Open the main entry point (`{entry}`).",
            "Follow the request/command flow into the core modules.",
            "Read the tests to learn the expected behavior.",
        ]),
        T.heading(2, "Key Concepts"),
        T.table(["Concept", "Plain-English Explanation", "Where To See It"],
                concept_rows)
        or "_Key concepts will depend on the domain; review the source tree in "
        "`05-code-introduction.md`._",
        *_optional(
            style.verbose,
            T.heading(2, "Suggested Exercises"),
            T.bullets([
                "Change a small user-facing message and run the project.",
                "Add a small test and run the test command.",
                "Trace one request from entry point to output.",
            ])),
        T.heading(2, "Questions To Check Understanding"),
        "\n".join(f"{i}. {q}" for i, q in enumerate(questions, 1)),
        *_optional(style.teaching, *_glossary(f)),
    ])


def _glossary(f: ProjectFacts) -> list:
    """Plain-English glossary of detected tech (teaching style only)."""

    rows = []
    for fw in f.frameworks:
        rows.append((fw, "An application framework used to build this project."))
    for store in f.data_stores:
        rows.append((store, "Where and how the project stores data."))
    for integ in f.integrations:
        rows.append((integ, "An external service the project talks to."))
    if not rows:
        return []
    return [
        T.heading(2, "Glossary"),
        "Plain-English definitions of the technologies detected here:",
        T.table(["Term", "What It Means"], rows),
    ]


def _code_intro(f: ProjectFacts, style: Style) -> str:
    entry_rows = [(f"`{e.path}`", e.purpose, f"`{e.path}` present")
                  for e in f.entry_points]

    return T.join_sections([
        T.heading(1, "Code Introduction"),
        T.heading(2, "Source Tree"),
        T.code_block(f.source_tree or "(tree unavailable)", "text"),
        T.heading(2, "Entry Points"),
        T.table(["Path", "Role", "Evidence"], entry_rows)
        or "_No clear entry point detected; confirm where execution begins._",
        T.heading(2, "Main Modules"),
        "_Module responsibilities are inferred from the source tree above. "
        "Review the top-level source directories to confirm._",
        T.heading(2, "Core Flow"),
        T.code_block(_flow_diagram(f), "mermaid"),
        T.heading(2, "How To Change The Code Safely"),
        T.bullets([
            "Identify the module responsible for the behavior.",
            "Check tests before editing.",
            "Make the smallest useful change.",
            "Run the relevant test command.",
            "Update documentation when behavior changes.",
        ]),
    ])


def _architecture(f: ProjectFacts, style: Style) -> str:
    dep_rows = []
    for fw in f.frameworks:
        dep_rows.append((fw, "Application framework", "dependencies"))
    for store in f.data_stores:
        dep_rows.append((store, "Data persistence", "dependencies/schema"))
    for integ in f.integrations:
        dep_rows.append((integ, "External integration", "dependencies"))

    decisions = []
    if f.frameworks:
        decisions.append(f"Framework choice: {', '.join(f.frameworks)}.")
    if f.data_stores:
        decisions.append(f"Data storage: {', '.join(f.data_stores)}.")
    if f.deployment_signals:
        decisions.append("Deployment style: "
                         + ", ".join(d.purpose for d in f.deployment_signals) + ".")
    if not decisions:
        decisions = ["_Architectural decisions were not obvious from the repository._"]

    return T.join_sections([
        T.heading(1, "Architecture"),
        T.heading(2, "System Boundary"),
        "What is inside this project and what external systems it depends on. "
        "External dependencies are inferred from declared packages.",
        T.heading(2, "Component Diagram"),
        T.code_block(_architecture_diagram(f), "mermaid"),
        T.heading(2, "Data Flow"),
        "Data enters through the entry point(s), is processed by the core "
        "modules, and is persisted or returned. Confirm specifics against the "
        "source tree.",
        T.heading(2, "Dependencies"),
        T.table(["Dependency", "Purpose", "Evidence"], dep_rows)
        or "_No notable external dependencies detected._",
        T.heading(2, "Architectural Decisions"),
        T.bullets(decisions),
        T.heading(2, "Risks And Tradeoffs"),
        T.bullets(f.unknowns or ["No major architectural gaps detected."]),
    ])


def _api(f: ProjectFacts, style: Style) -> str:
    integ_rows = [(i, "External service", "dependencies") for i in f.integrations]
    route_rows = [(r.method, f"`{r.path}`", r.evidence) for r in f.routes]
    route_note = ""
    if len(f.routes) >= 100:
        route_note = "_Showing the first 100 routes; more exist in the source._"

    return T.join_sections([
        T.heading(1, "API and Integrations"),
        T.heading(2, "Surface"),
        "This project exposes or consumes interfaces. Routes below were "
        "extracted directly from the source; confirm any that look ambiguous.",
        T.heading(2, "Routes / Endpoints"),
        T.table(["Method", "Path", "Source"], route_rows)
        or "_No routes were extracted automatically; review the route "
        "definitions in the source tree._",
        route_note,
        T.heading(2, "External Services"),
        T.table(["Service", "Role", "Evidence"], integ_rows)
        or "_No external services detected._",
        T.heading(2, "Auth And Credentials"),
        "Credentials are supplied via environment variables (see "
        "`02-operation-manual.md`). Variable names only are documented; secret "
        "values are never extracted.",
        T.heading(2, "Failure Modes"),
        "_Rate limits and external failure modes are not documented in the "
        "repository. Confirm with maintainers._ (Confidence: Needs confirmation)",
    ])


def _fmt_fields(fields: list) -> str:
    if not fields:
        return "—"
    shown = ", ".join(fields[:8])
    return shown + (" …" if len(fields) > 8 else "")


def _data_model(f: ProjectFacts, style: Style) -> str:
    store_rows = [(s, "dependencies/schema") for s in f.data_stores]
    entity_rows = [(e.name, e.kind, _fmt_fields(e.fields), f"`{e.evidence}`")
                   for e in f.entities]
    return T.join_sections([
        T.heading(1, "Data Model"),
        T.heading(2, "Storage Overview"),
        T.table(["Data store", "Evidence"], store_rows)
        or "_No data store detected from dependencies._",
        T.heading(2, "Important Entities"),
        T.table(["Entity", "Kind", "Fields", "Source"], entity_rows)
        or "_No entities were extracted automatically. Review the schema or "
        "model files to enumerate entities._",
        T.heading(2, "Migrations"),
        "If a migrations directory is present, run migrations as part of setup "
        "and deployment. Confirm the exact command with maintainers.",
        T.heading(2, "State And Storage"),
        "_Document any local state files, caches, or object storage used by the "
        "project._ (Confidence: Needs confirmation)",
    ])


def _troubleshooting(f: ProjectFacts, style: Style) -> str:
    diag = []
    if f.test_commands:
        diag.append(f.test_commands[0].command)
    if f.run_commands:
        diag.append(f.run_commands[0].command)
    diag_block = T.code_block("\n".join(diag) if diag
                              else "# No diagnostic commands detected", "bash")

    issues = T.table(
        ["Symptom", "Likely Cause", "Check", "Fix"],
        [
            ("App will not start", "Missing/invalid env vars",
             "Compare against the env template", "Set required variables"),
            ("Dependency errors", "Toolchain or version mismatch",
             "Check the manifest and CI versions", "Align local versions"),
            ("Tests fail locally", "Environment not configured",
             "Run the test command and read output", "Fix config or code"),
        ],
    )

    return T.join_sections([
        T.heading(1, "Troubleshooting"),
        *_optional(style.ops_focus, _OPS_CALLOUT),
        T.heading(2, "Quick Diagnostics"),
        diag_block,
        T.heading(2, "Common Issues"),
        issues,
        T.heading(2, "Debugging Workflow"),
        "\n".join([
            "1. Reproduce the issue.",
            "2. Check logs.",
            "3. Check environment variables.",
            "4. Run the tests.",
            "5. Trace the relevant code path.",
            "6. Document the fix.",
        ]),
        T.heading(2, "When To Escalate"),
        T.bullets([
            "Credentials or infrastructure access is required.",
            "Production data may be affected.",
            "The deployment path is undocumented.",
            "The issue cannot be reproduced locally.",
        ]),
    ])


def _maintenance(f: ProjectFacts, style: Style) -> str:
    test_cmd = _first_command(f.test_commands)
    return T.join_sections([
        T.heading(1, "Maintenance and Contribution"),
        T.heading(2, "Coding Conventions"),
        "_Follow the conventions visible in the existing source. Document any "
        "linter/formatter configuration found in the repository._",
        T.heading(2, "Testing Expectations"),
        (f"Run `{test_cmd.command}` before submitting changes."
         if test_cmd else
         "_No test command detected. Add tests before making behavioral changes._"),
        T.heading(2, "Release Checklist"),
        T.bullets([
            "Tests pass.",
            "Documentation updated where behavior changed.",
            "Version bumped if applicable.",
            "Deployment configuration reviewed.",
        ]),
        T.heading(2, "Safe Change Workflow"),
        T.bullets([
            "Branch from the default branch.",
            "Make the smallest useful change.",
            "Run tests and linters.",
            "Open a reviewable change with context.",
        ]),
        T.heading(2, "AI-Agent Handoff Notes"),
        "When an AI agent continues work, point it at this package and at "
        "`_evidence/` so it can distinguish verified facts from inferences "
        "before making changes.",
    ])


def _not_applicable(title: str, reason: str) -> str:
    return T.join_sections([
        T.heading(1, title),
        f"**Not applicable for this project.**\n\n{reason}",
        "This omission is recorded in `_evidence/assumptions.md`. "
        "If this is wrong, the relevant files may not have been detected — "
        "confirm with the maintainers.",
    ])


# --------------------------------------------------------------------------- #
# Diagrams
# --------------------------------------------------------------------------- #

def _architecture_diagram(f: ProjectFacts) -> str:
    app = f.name.replace('"', "'") or "Application"
    lines = ["flowchart LR", '  User["User"] --> App["%s"]' % app]
    n = 0
    for store in f.data_stores[:3]:
        n += 1
        lines.append(f'  App --> DS{n}["{store}"]')
    for integ in f.integrations[:3]:
        n += 1
        lines.append(f'  App --> EXT{n}["{integ}"]')
    if n == 0:
        lines.append('  App --> Output["Output"]')
    return "\n".join(lines)


def _flow_diagram(f: ProjectFacts) -> str:
    entry = f.entry_points[0].path if f.entry_points else "Entry Point"
    entry = entry.replace('"', "'")
    return "\n".join([
        "flowchart LR",
        '  Input["Input"] --> Entry["%s"]' % entry,
        '  Entry --> Logic["Core Logic"]',
        '  Logic --> Output["Output"]',
    ])


# --------------------------------------------------------------------------- #
# Package README
# --------------------------------------------------------------------------- #

_OPS_PRIORITY_DOCS = (
    "02-operation-manual.md", "03-deployment-manual.md", "09-troubleshooting.md")


def _package_readme(f: ProjectFacts, style: Style) -> str:
    today = _dt.date.today().isoformat()
    titles = dict(T.DOCUMENTS)
    links = "\n".join(
        f"- [{title}]({fname})" for fname, title in T.DOCUMENTS)

    ops_ref = []
    if style.ops_focus:
        ops_ref = [
            T.heading(2, "Operational Quick Reference"),
            "Start with these when running or fixing the system:",
            T.bullets(f"[{titles[fn]}]({fn})" for fn in _OPS_PRIORITY_DOCS),
        ]

    return T.join_sections([
        T.heading(1, f"Study Docs: {f.name}"),
        f"Generated by `project-to-study` v{__version__} on {today}.",
        f"Target path: `{T.display_path(f.source or f.root)}`",
        f"Style: `{style.name}`",
        *_optional(
            style.teaching,
            "> **New here?** Start with `04-learning-manual.md` for a guided, "
            "plain-English path through the project."),
        *ops_ref,
        T.heading(2, "Documents"),
        links,
        T.heading(2, "Evidence"),
        T.bullets([
            "[Source map](_evidence/source-map.md)",
            "[Assumptions](_evidence/assumptions.md)",
            "[Generation log](_evidence/generation-log.md)",
        ]),
        T.heading(2, "Confidence Notes"),
        "Claims are labelled `Verified`, `Inferred`, `Unknown`, or "
        "`Needs confirmation`. Treat anything not `Verified` as a prompt to "
        "check the source before relying on it.",
    ])
