# tracedocs Visual System

This document is the design-spec counterpart to the generated demo HTML. It is
written like a lightweight Figma component library: tokens first, then reusable
components, then usage rules.

The goal is to make tracedocs feel more polished without making the output less
verifiable. Markdown and `index.json` remain the source of truth; HTML previews
are presentation layers derived from them.

## Design Principles

- **Evidence first:** visual hierarchy should make claims, sources, confidence,
  and unknowns easy to scan.
- **Dark, operational, calm:** the product should feel like a serious developer
  tool, not a marketing landing page.
- **Few colors, strong semantics:** accent colors mean something; avoid one-off
  decorative color.
- **Repo-native:** every visual preview must link back to Markdown,
  `index.json`, or `_evidence/`.
- **Single-file friendly:** generated previews should work without build tools,
  frameworks, network fonts, or external assets.

## Color Tokens

| Token | Hex | Use |
| --- | --- | --- |
| `--bg` | `#0f1117` | page background |
| `--surface-1` | `#171a23` | primary panels and cards |
| `--surface-2` | `#11141c` | nested cards and code-adjacent panels |
| `--surface-3` | `#0b0d13` | code blocks, flow nodes, quiet controls |
| `--line` | `#262b38` | borders and separators |
| `--ink` | `#e7e9ee` | primary text |
| `--muted` | `#9aa3b2` | secondary text |
| `--accent` | `#8a63ff` | primary action, active/open state |
| `--green` | `#37c97f` | `Verified` |
| `--blue` | `#5aa9ff` | `Inferred` |
| `--amber` | `#f0b32f` | `Needs confirmation` |
| `--red` | `#ff6b6b` | hallucinated/unsafe contrast example |

## Typography

System fonts only:

```css
system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif
```

Monospace:

```css
ui-monospace, SFMono-Regular, Menlo, Consolas, monospace
```

| Role | Desktop | Mobile | Notes |
| --- | --- | --- | --- |
| Product title | `54px / 1` | `38px / 1.05` | largest text on the page |
| Tagline | `22px / 1.35` | `17px / 1.45` | concise product promise |
| Section label | `15px uppercase` | same | scanning anchor |
| Card title | `18px` | same | document and component names |
| Body | `15px / 1.55` | same | GitHub-like readability |
| Microcopy | `12-13px` | same | labels, audience, evidence notes |

## Spacing And Shape

| Token | Value | Use |
| --- | --- | --- |
| `--space-1` | `4px` | tiny gaps |
| `--space-2` | `8px` | chips, small controls |
| `--space-3` | `12px` | card internal rhythm |
| `--space-4` | `16px` | grid gaps |
| `--space-5` | `20px` | section body spacing |
| `--space-6` | `28px` | hero / major gaps |
| `--radius-sm` | `8px` | buttons, links, nodes |
| `--radius-md` | `10px` | code blocks, compact cards |
| `--radius-lg` | `12px` | feature cards and major panels |

Use `12px` only for major panels and cards. Controls and nested elements should
stay at `8px` or `10px`.

## Components

### Chip

Use for metadata and state context.

- Shape: pill
- Border: `--line`
- Text: `--muted`
- Optional status dot: semantic color

Examples: `Live study-docs showroom`, `Markdown remains the source of truth`.

### Button

Use only for clear actions.

- Primary: filled `--accent`, white text
- Secondary: transparent, `--line` border
- Radius: `--radius-sm`
- Mobile: full-width stacked

Examples: `Explore the docs`, `Open raw Markdown`, `View index.json`.

### Surface Card

Use for grouped information: stats, hallucination comparison, JSON preview,
document cards.

- Background: `--surface-1`
- Border: `--line`
- Radius: `--radius-lg`
- Optional semantic border color for contrast examples

### Evidence Label

Confidence labels are semantic and must not be used decoratively.

| Label | Color | Meaning |
| --- | --- | --- |
| `Verified` | `--green` | directly supported by source |
| `Inferred` | `--blue` | likely from repository structure |
| `Unknown` | `--muted` | not enough evidence |
| `Needs confirmation` | `--amber` | maintainer should verify |

### Code Block

- Background: `--surface-3`
- Border: `--line`
- Radius: `--radius-md`
- Monospace only
- Mobile: wrap long commands instead of overflowing the viewport

### Flow Node

Use for source-backed chains such as:

```text
Claim -> Evidence -> Confidence
Repo -> Evidence map -> Markdown + index.json
```

Rules:

- Each node should have one clear label and one compact body.
- Arrows disappear on small screens; nodes stack vertically.
- Output nodes may use the accent border.

### Document Card

Use for generated manuals in the showroom.

Required content:

- title
- audience
- confidence label
- short summary
- evidence table or evidence line
- raw Markdown link

Optional:

- `_evidence/assumptions.md` link for unknowns or gaps
- Mermaid asset link for architecture

## Responsive Rules

- At `860px`, multi-column sections become one column except stats.
- At `520px`, stats become one column and actions stack.
- Long text, code, and chips must wrap; no horizontal scrolling for the main
  reading flow.
- Keep interactive cards readable before adding density.

## Current Implementations

- `examples/study-docs/index.html` — live GitHub Pages showroom.
- `docs/assets/social-preview.html` — GitHub social preview source.

When changing the visual system, update the HTML previews and run:

```bash
python3 scripts/validate-skill.py
```
