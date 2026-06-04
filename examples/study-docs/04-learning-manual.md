# Learning Manual

## Learning Goal

After this guide you should understand what the project does, how it runs, where the important code lives, and how to ask an AI agent for safe changes.

## Reading Path

- Start with the README and `00-project-overview.md`.
- Open the main entry point (`src/index.js`).
- Follow the request/command flow into the core modules.
- Read the tests to learn the expected behavior.

## Key Concepts

| Concept | Plain-English Explanation | Where To See It |
| --- | --- | --- |
| Express | The framework this project is built on. | dependencies |
| PostgreSQL | How and where data is persisted. | dependencies/schema |

## Suggested Exercises

- Change a small user-facing message and run the project.
- Add a small test and run the test command.
- Trace one request from entry point to output.

## Questions To Check Understanding

1. What command starts the project? (npm run dev)
2. Which file is the main entry point? (`src/index.js`)
3. Where does configuration come from?
4. Which tests cover the core behavior? (npm run test)
