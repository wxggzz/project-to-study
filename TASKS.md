# Tasks

## Completed

- Added a README "Hallucination Test" section in English and Chinese, linking to
  the sample deployment manual and assumptions file.
- Added GitHub Pages support for the live demo:
  - `.github/workflows/pages.yml`
  - `examples/study-docs/.nojekyll`
  - live demo links in `README.md` and `README.zh-CN.md`
- Added package validation:
  - `scripts/validate-skill.py`
  - `.github/workflows/validate.yml`
  - validation badges in both READMEs
- Added an English and Chinese compatibility matrix for Claude Code plugin,
  Claude Code copy install, Codex, and other file-reading agents.
- Ran `scripts/sync-plugin.sh` so the plugin copy remains in sync with the root
  skill.

## Next Recommended Task

- After this reaches `main`, confirm GitHub Pages is set to deploy from GitHub
  Actions, then check `https://wxggzz.github.io/tracedocs/`.

## Known Blockers

- `docs/architecture.md` is referenced by `references/handoff-protocol.md` but
  does not exist in the current repository.

## Files Changed

- `.github/workflows/pages.yml`
- `.github/workflows/validate.yml`
- `README.md`
- `README.zh-CN.md`
- `TASKS.md`
- `examples/study-docs/.nojekyll`
- `scripts/validate-skill.py`

## Commands / Checks Run

- `git status --short`
- `git branch --show-current`
- `git log --oneline --decorate --max-count=5`
- `git pull --ff-only`
- `scripts/sync-plugin.sh`
- `chmod +x scripts/validate-skill.py`
- `python3 scripts/validate-skill.py`
- `git diff --check`
