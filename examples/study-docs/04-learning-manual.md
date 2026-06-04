# Learning Manual

## Learning Goal

After this guide you should understand what `project-to-study` does, how a run
flows from input to `study-docs/`, where the important code lives, and how to
extend extraction safely.

## Reading Path

1. Read the project `README.md`.
2. Open the entry point, `project_to_study/cli.py`, and follow `main()`.
3. Read `scanner.py` to see how raw facts are gathered into `ProjectFacts`.
4. Read `analyzers.py` for route/entity extraction.
5. Read `writer.py` + `templates.py` to see how facts become Markdown.
6. Skim `tests/` to learn the expected behaviour by example.

## Key Concepts

| Concept | Plain-English Explanation | Where To See It |
| --- | --- | --- |
| `ProjectFacts` | One in-memory record holding everything learned about the repo | `model.py` |
| `Claim` + `Confidence` | A statement plus its evidence and how sure we are | `model.py`, `evidence.py` |
| The pipeline | acquire → scan → analyze → write + evidence → validate | `cli.py` orchestration |
| Deterministic extraction | Regex/string heuristics, no LLM, repeatable output | `scanner.py`, `analyzers.py` |
| Document planner | Decides which optional docs get real content vs a note | `writer.py` |

## Suggested Exercises

- Add a new detected framework keyword in `scanner.py` and see it appear in the
  overview's tech stack.
- Add a route pattern for a framework in `analyzers.py`, with a test.
- Run all four `--style` values and diff the output to see what each changes.

## Questions To Check Understanding

1. What command generates docs, and what is the default output directory?
   (`project-to-study <path> --out study-docs`)
2. Which module turns `ProjectFacts` into Markdown? (`writer.py`)
3. Where does the evidence trail get written? (`_evidence/` via `evidence.py`)
4. How does a Git URL become a local directory to scan? (`source.acquire`)
