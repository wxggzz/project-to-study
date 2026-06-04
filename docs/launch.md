# Launch & Distribution Playbook

Internal notes for promoting **tracedocs**. A great README only converts visitors
who actually arrive — these posts bring the first wave.

- **Social posts can go out now** (no age limit).
- **awesome-claude-code must wait until the repo is ≥ 1 week old** → submit on or
  after **2026-06-11** (a one-time reminder is scheduled:
  https://claude.ai/code/routines/trig_01VvLxH81sAKHrjXh1Ay3Rdx).
- Always attach the hero image: `docs/assets/hero.png` (English) /
  `docs/assets/hero.zh.png` (Chinese). Posts with an image get far more clicks.

---

## X / Twitter thread (attach `docs/assets/hero.png`)

**1/**
> Most AI doc generators hallucinate deployment steps and quietly go stale.
>
> I built **tracedocs** — a Claude Code skill that turns any repo into docs where **every claim cites its source**, and it *refuses* to write steps it can't prove.
>
> Markdown + a machine-readable `index.json`. 🧵

**2/**
> Point `/tracedocs` at a repo (or a Git URL). It analyzes the code, builds an **evidence map**, writes 11 manuals (operation, deployment, architecture, API, troubleshooting…), and runs a quality check.
>
> Every claim is labelled **Verified / Inferred / Unknown / Needs confirmation**.

**3/**
> vs codebase-to-course: that one *teaches a human* with an interactive course.
> tracedocs *briefs your team **and** your AI agents* — durable Markdown that lives in your repo, diffs in PRs, and never invents a deploy pipeline that isn't there.

**4/**
> MIT. Install as a Claude Code skill, then `/tracedocs`.
> Repo + a full sample output 👉 https://github.com/wxggzz/tracedocs
>
> ⭐ if "AI docs that cite their sources" sounds useful.

---

## Reddit — r/ClaudeAI

**Title:** tracedocs — a Claude Code skill for repo docs that cite their sources (and refuse to invent deploy steps)

**Body:**
> AI doc generators tend to hallucinate deployment steps and go stale. I made **tracedocs**, a Claude Code skill that takes the opposite stance: every operational/deployment claim is tied to a source file and labelled `Verified / Inferred / Unknown / Needs confirmation`, and it documents gaps instead of inventing them.
>
> It produces a `study-docs/` package — overview, quickstart, operation, deployment, learning, architecture, API/data, troubleshooting, maintenance — plus a machine-readable `index.json` so AI agents can consume it too.
>
> Try it from any repo (paste into Claude Code):
> `Use tracedocs to generate evidence-grounded study docs for this repository. Write the output to study-docs/.`
>
> Repo + a complete validated sample: https://github.com/wxggzz/tracedocs · MIT. Feedback welcome.

---

## Hacker News — Show HN

**Title:** Show HN: tracedocs – Claude Code skill for repo docs that cite their sources

**Text:**
> tracedocs turns any codebase into an evidence-grounded Markdown doc package + a machine-readable index.json. Every operational/deployment claim links to its source file and carries a confidence label; it refuses to invent deployment steps and records gaps instead. Built as a Claude Code skill (the codebase-to-course pattern), MIT. The repo has a full sample output. Happy to answer questions.

---

## 中文版 (X / 即刻 / V2EX,配 `docs/assets/hero.zh.png`)

> 大多数 AI 文档工具会编造部署步骤、还会悄悄过时。
>
> 我做了 **tracedocs** —— 一个 Claude Code skill:把任意代码库变成**每条结论都标注来源**的文档,凡是无法溯源的步骤**直接拒绝写**,缺口如实记录。
>
> 产出 Markdown + 机器可读的 `index.json`(给 AI agent 用)。每条结论带 已验证/推断/未知/待确认 标签。
>
> MIT,装成 skill 后 `/tracedocs` 即用 👉 https://github.com/wxggzz/tracedocs ⭐

---

## How to post (per platform)

- **X / Twitter:** post `1/` with the hero image attached, then *reply to your own
  tweet* with `2/` `3/` `4/` to form a thread. Best time: weekday evenings
  Asia/Shanghai (= US daytime). Reply to comments to boost reach.
- **Reddit r/ClaudeAI:** needs an account with some karma. Create Post →
  Text/Image → paste title + body. Check the sidebar rules / add flair if
  required. Keep the tone "I built this, feedback welcome", not an ad.
- **Hacker News (Show HN):** news.ycombinator.com → submit → title + repo URL +
  text. Best Tue–Thu morning US-Pacific. Show HN must be something people can try
  (the README + sample cover this).
- **Chinese:** 即刻 (AI/创作者节点), V2EX (分享创造节点), 小红书 — use the 中文版 with
  `hero.zh.png`.

Tip: don't blast every platform at once. Start with **X + r/ClaudeAI**, learn from
the response, then do the rest.

---

## awesome-claude-code submission kit

> ⚠ Submit **only** via the web issue form, **as a human**. Do **not** open a PR
> or use the `gh` CLI — that risks a ban. The repo must be **≥ 1 week old**
> (eligible on/after 2026-06-11).

**Form:** https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=recommend-resource.yml

| Field | Value |
| --- | --- |
| Display Name | `tracedocs` |
| Category | Agent Skills |
| Sub-Category | General |
| Primary Link | `https://github.com/wxggzz/tracedocs` |
| Author Name | `wxggzz` |
| Author Link | `https://github.com/wxggzz` |
| License | MIT |

**Description (paste):**
> tracedocs is a Claude Code skill that turns any codebase into an evidence-grounded Markdown documentation package (overview, operation, deployment, learning, architecture, API/data, troubleshooting, maintenance) plus a machine-readable `index.json` for AI agents. Every operational/deployment claim is labelled Verified / Inferred / Unknown / Needs confirmation and linked to its source file; it never invents deployment steps and records gaps instead.
>
> Validate it: copy `SKILL.md` + `references/` into `~/.claude/skills/tracedocs/`, reload Claude Code, then run `/tracedocs` on a repo — or paste into any repo: "Use tracedocs to generate evidence-grounded study docs for this repository. Write the output to study-docs/." A complete, validated sample output is committed at `examples/study-docs/`.
>
> Network calls: the skill itself makes none. (A separate, optional CLI on the `cli` branch can `git clone` a Git URL you explicitly pass it.) No elevated/bypass-permissions needed. Uninstall: `rm -rf ~/.claude/skills/tracedocs`. License: MIT.

**After approval**, add the badge to the README:
`[![Mentioned in Awesome Claude Code](https://awesome.re/mentioned-badge.svg)](https://github.com/hesreallyhim/awesome-claude-code)`

---

## More distribution channels (skill lists & hubs)

These are additional high-traffic lists. Each is **PR-based** (read its
CONTRIBUTING first, one focused PR each, pick the right category, don't spam).
Reusable one-line entry for awesome-style lists:

```markdown
- [tracedocs](https://github.com/wxggzz/tracedocs) — Evidence-grounded project docs that cite their sources, plus an AI-ready `index.json`; never invents deployment steps. (Claude Code skill · MIT)
```

| List | ★ | Branch | How to submit |
| --- | --- | --- | --- |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | 63k | `master` | PR. Their CONTRIBUTING wants a folder `tracedocs/SKILL.md` (real use case, tested, safe, portable) — consider a self-contained SKILL.md that links back here for `references/`. Heavier but highest reach. |
| [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | 13k | `main` | Simple PR: add the bullet above under the right category in `README.md` (see CONTRIBUTING.md). |
| [BehiSecc/awesome-claude-skills](https://github.com/BehiSecc/awesome-claude-skills) | 9k | `main` | Fork → add the bullet → PR (or open an Issue). |
| [davepoon/buildwithclaude](https://github.com/davepoon/buildwithclaude) | 3k | `main` | Plugin marketplace/discovery hub. PR adding tracedocs per their `plugins/` structure — a natural fit now that we ship a `.claude-plugin` plugin. |

Tips:
- Lead with the evidence/no-hallucination angle and link the validated sample
  (`examples/study-docs/`) — these lists value tested, focused resources.
- Suggested category on most lists: **Documentation** / **Developer Tools**.
- Space the PRs out over a few days; engage with maintainer feedback.
