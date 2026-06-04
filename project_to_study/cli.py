"""Command-line interface for project-to-study.

Primary form (matches CLAUDE.md):

    project-to-study /path/to/repo --out study-docs

Validation form:

    project-to-study validate study-docs/
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import __version__
from .scanner import scan
from .source import acquire, is_remote
from .style import StyleName, resolve as resolve_style
from .validate import validate as validate_docs
from .writer import generate


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project-to-study",
        description="Generate a Markdown study-docs package from a codebase.",
    )
    parser.add_argument("--version", action="version",
                        version=f"project-to-study {__version__}")
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Scan a repo and write study-docs/")
    gen.add_argument("path",
                     help="Local path OR a Git URL (https/ssh/git@/github.com/owner/repo)")
    gen.add_argument("--out", default="study-docs",
                     help="Output directory (default: study-docs)")
    gen.add_argument("--style", default=StyleName.STANDARD,
                     choices=StyleName.ALL,
                     help="Output emphasis/verbosity (default: standard)")

    val = sub.add_parser("validate", help="Validate a generated study-docs/")
    val.add_argument("path", help="Path to the generated docs directory")

    return parser


def _run_generate(path: str, out: str, style_name: str) -> int:
    style = resolve_style(style_name)
    remote = is_remote(path)
    if remote:
        print(f"Cloning {path} ...")
    with acquire(path) as repo_path:
        facts = scan(repo_path)
        if remote:
            facts.source = path  # show the URL in docs, not the temp dir
        result = generate(facts, out, style)
    print(f"Scanned: {facts.name}  ({facts.source})  [style: {style.name}]")
    print(f"Wrote {len(result.written)} files to {result.out_dir}")
    for note in result.skipped_notes:
        print(f"  note: {note}")
    print("Review _evidence/ for the confidence trail.")
    return 0


def _run_validate(path: str) -> int:
    problems = validate_docs(path)
    if not problems:
        print(f"OK: {path} passed validation.")
        return 0
    print(f"FAILED: {len(problems)} problem(s) in {path}:", file=sys.stderr)
    for p in problems:
        print(f"  - {p}", file=sys.stderr)
    return 1


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    # Allow the bare-path primary form: `project-to-study /path --out dir`.
    # If the first token is not a known subcommand or flag, treat it as generate.
    known = {"generate", "validate"}
    if argv and argv[0] not in known and not argv[0].startswith("-"):
        argv = ["generate", *argv]

    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate":
        try:
            return _run_generate(args.path, args.out, args.style)
        except (NotADirectoryError, FileNotFoundError, RuntimeError, ValueError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
    if args.command == "validate":
        return _run_validate(args.path)

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
