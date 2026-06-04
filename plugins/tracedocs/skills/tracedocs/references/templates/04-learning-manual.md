# Learning Manual

> Audience: non-expert learners and AI-assisted builders.
> Signature payoff: a concrete **reading path** plus prompts you can hand to an
> AI agent to learn the codebase safely.

## Learning Goal

After this guide you should understand what the project does, how it runs, where
the important code lives, and how to ask an AI agent for safe changes.

## Reading Path

1. Read the README and `00-project-overview.md`.
2. Open the main entry point: `<path>`.
3. Follow the request/command flow into the core modules.
4. Read the tests to learn expected behaviour.

## Key Concepts

| Concept | Plain-English meaning | Where to see it |
| --- | --- | --- |
| <concept> | <one sentence, jargon-free> | `<file/dir>` |

## Exercises

- Change a small user-facing string and run the project.
- Add one small test and run the test command.
- Trace one request from entry point to output.

## Prompts For Your AI Agent

Hand these to Claude/Cursor/Codex, then verify each answer against the source:

- "Explain what `<entry point>` does, step by step, citing files."
- "List every place `<ENV_VAR>` is read, with file and line."
- "What would break if I changed `<module>`? Which tests cover it?"

## Questions To Check Understanding

1. What command starts the project?
2. Which file is the main entry point?
3. Where does configuration come from?
4. Which tests cover the core behaviour?
