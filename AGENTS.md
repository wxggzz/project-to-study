# Agent Handoff Guide

This repository is meant to be shared by multiple coding agents. Follow these
rules so Claude Code and Codex can work on it in sequence.

## Current Mission

Build `project-to-study`: a system or skill that generates Markdown study docs
from a codebase.

The project should stay agent-friendly:

- keep instructions explicit
- keep templates reusable
- record assumptions
- avoid hidden state
- make every generated claim traceable to source files when possible

## Before You Work

Read these files first:

1. `README.md`
2. `SKILL.md`
3. `TASKS.md`
4. `docs/architecture.md`
5. `references/handoff-protocol.md`

## Editing Rules

- Prefer small, focused changes.
- Do not rewrite templates unless the task requires it.
- When implementation starts, add or update tests for generator behavior.
- Keep generated example outputs separate from source templates.
- Do not store real secrets in examples.

## Handoff Rule

At the end of a work session, update `TASKS.md` with:

- completed work
- next recommended task
- known blockers
- files changed
- commands/tests run

