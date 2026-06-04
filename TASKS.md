# Tasks

## Completed

- Clarified the first screen of `README.md` and `README.zh-CN.md` so new
  visitors immediately understand tracedocs as: repo path/Git URL in,
  `study-docs/` Markdown manuals plus AI-ready `index.json` out, with source
  evidence and unknowns instead of invented deployment steps.
- Added `docs/visual-system.md`, a lightweight Figma-style component spec for
  tracedocs previews: colors, typography, spacing, cards, evidence labels, code
  blocks, flow nodes, and responsive rules.
- Synced the live demo CSS to the visual system tokens (`--surface-*`,
  `--space-*`, `--radius-*`) so the HTML behaves like a reusable component
  implementation rather than one-off styling.
- Extended `scripts/validate-skill.py` to check the visual-system doc and the
  matching showroom token markers.
- Upgraded `examples/study-docs/index.html` from a Markdown link directory into
  a single-file showroom:
  - hero actions for docs / Markdown / `index.json`
  - Hallucination Test comparison
  - Evidence Trace flow
  - expandable document cards with summaries, evidence, confidence, and raw
    Markdown links
  - AI-ready `index.json` preview card
- Extended `scripts/validate-skill.py` so CI checks the showroom markers and
  prevents the demo from regressing back to a plain directory page.
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

- After this reaches GitHub, check the repository landing page and confirm the
  first screen explains the product clearly before visitors scroll.

## Known Blockers

- `docs/architecture.md` is referenced by `references/handoff-protocol.md` but
  does not exist in the current repository.

## Files Changed

- `.github/workflows/pages.yml`
- `.github/workflows/validate.yml`
- `README.md`
- `README.zh-CN.md`
- `TASKS.md`
- `docs/visual-system.md`
- `examples/study-docs/.nojekyll`
- `examples/study-docs/index.html`
- `scripts/validate-skill.py`

## Commands / Checks Run

- `git status --short`
- `git branch --show-current`
- `git log --oneline --decorate --max-count=5`
- `git pull --ff-only`
- `sed -n '1,120p' README.md`
- `sed -n '1,120p' README.zh-CN.md`
- `sed -n '1,180p' TASKS.md`
- `sed -n '1,120p' SKILL.md`
- `sed -n '1,120p' references/handoff-protocol.md`
- `test -f docs/architecture.md && sed -n '1,120p' docs/architecture.md || printf 'MISSING docs/architecture.md\n'`
- `scripts/sync-plugin.sh`
- `chmod +x scripts/validate-skill.py`
- `python3 scripts/validate-skill.py`
- `git diff --check`
- Chrome headless screenshot QA:
  - desktop-ish: `1440x1200`
  - small viewport: `520x1100`
