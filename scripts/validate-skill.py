#!/usr/bin/env python3
"""Validate the tracedocs skill package and public demo assets."""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path
from typing import Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_DOCS = [
    "00-project-overview.md",
    "01-quickstart.md",
    "02-operation-manual.md",
    "03-deployment-manual.md",
    "04-learning-manual.md",
    "05-code-introduction.md",
    "06-architecture.md",
    "07-api-and-integrations.md",
    "08-data-model.md",
    "09-troubleshooting.md",
    "10-maintenance-and-contribution.md",
]

EVIDENCE_FILES = [
    "_evidence/source-map.md",
    "_evidence/assumptions.md",
    "_evidence/generation-log.md",
]

errors: list[str] = []


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def require_file(path: str) -> Path:
    target = ROOT / path
    check(target.is_file(), f"Missing file: {path}")
    return target


def load_json(path: str) -> dict:
    target = require_file(path)
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {path}: {exc}")
        return {}


def read_text(path: str) -> str:
    target = require_file(path)
    return target.read_text(encoding="utf-8") if target.exists() else ""


def file_map(base: Path) -> dict[str, Path]:
    if not base.exists():
        errors.append(f"Missing directory: {rel(base)}")
        return {}
    return {
        str(path.relative_to(base)): path
        for path in sorted(base.rglob("*"))
        if path.is_file()
    }


def check_same_file(left: Path, right: Path) -> None:
    if not left.is_file() or not right.is_file():
        errors.append(f"Cannot compare missing files: {rel(left)} / {rel(right)}")
        return
    check(left.read_bytes() == right.read_bytes(), f"Out of sync: {rel(left)} != {rel(right)}")


def png_dimensions(path: Path) -> Optional[Tuple[int, int]]:
    try:
        with path.open("rb") as handle:
            signature = handle.read(8)
            if signature != b"\x89PNG\r\n\x1a\n":
                errors.append(f"Not a PNG: {rel(path)}")
                return None
            length, chunk_type = struct.unpack(">I4s", handle.read(8))
            if chunk_type != b"IHDR" or length < 8:
                errors.append(f"Missing PNG IHDR: {rel(path)}")
                return None
            width, height = struct.unpack(">II", handle.read(8))
            return width, height
    except OSError as exc:
        errors.append(f"Cannot read {rel(path)}: {exc}")
        return None


def validate_marketplace() -> None:
    marketplace = load_json(".claude-plugin/marketplace.json")
    check(marketplace.get("name") == "tracedocs", "Marketplace name must be tracedocs")
    plugins = marketplace.get("plugins", [])
    check(isinstance(plugins, list) and len(plugins) == 1, "Marketplace must expose one plugin")
    if plugins:
        plugin = plugins[0]
        check(plugin.get("source") == "./plugins/tracedocs", "Marketplace source must be ./plugins/tracedocs")
        check((ROOT / "plugins/tracedocs").is_dir(), "Marketplace plugin source directory is missing")

    plugin_json = load_json("plugins/tracedocs/.claude-plugin/plugin.json")
    check(plugin_json.get("name") == "tracedocs", "Plugin name must be tracedocs")
    check(plugin_json.get("skills") == "./skills/", "Plugin skills path must be ./skills/")
    check(plugin_json.get("license") == "MIT", "Plugin license must be MIT")


def validate_skill_sync() -> None:
    check_same_file(ROOT / "SKILL.md", ROOT / "plugins/tracedocs/skills/tracedocs/SKILL.md")

    root_refs = file_map(ROOT / "references")
    plugin_refs = file_map(ROOT / "plugins/tracedocs/skills/tracedocs/references")
    check(set(root_refs) == set(plugin_refs), "Root references and plugin references have different file sets")
    for name in sorted(set(root_refs) & set(plugin_refs)):
        check_same_file(root_refs[name], plugin_refs[name])


def validate_templates() -> None:
    for base in [
        ROOT / "references/templates",
        ROOT / "plugins/tracedocs/skills/tracedocs/references/templates",
    ]:
        for doc in EXPECTED_DOCS:
            check((base / doc).is_file(), f"Missing template: {rel(base / doc)}")


def validate_examples() -> None:
    base = ROOT / "examples/study-docs"
    for path in ["README.md", "index.json", "index.html", ".nojekyll", *EXPECTED_DOCS, *EVIDENCE_FILES]:
        check((base / path).is_file(), f"Missing example output: {rel(base / path)}")

    preview = read_text("examples/study-docs/index.html")
    for marker in [
        "tracedocs visual system tokens",
        "--surface-1:#171a23",
        "--radius-lg:12px",
        "Live study-docs showroom",
        "Hallucination Test",
        "Evidence Trace",
        "Document Showroom",
        "AI-ready index.json",
        "<details class=\"doc\"",
        "Open Markdown",
    ]:
        check(marker in preview, f"examples/study-docs/index.html missing showroom marker: {marker}")

    index = load_json("examples/study-docs/index.json")
    for key in ["schema", "name", "generated_at", "source", "documents", "commands", "confidence", "unknowns", "evidence_files"]:
        check(key in index, f"examples/study-docs/index.json missing key: {key}")
    if isinstance(index.get("documents"), list):
        listed_docs = {doc.get("file") for doc in index["documents"] if isinstance(doc, dict)}
        missing = sorted(set(EXPECTED_DOCS) - listed_docs)
        check(not missing, f"index.json documents missing: {', '.join(missing)}")


def validate_assets() -> None:
    social = require_file("docs/assets/social-preview.png")
    if social.exists():
        check(social.stat().st_size < 1_000_000, "social-preview.png must stay under 1MB")
        dimensions = png_dimensions(social)
        check(dimensions in {(1280, 640), (2560, 1280)}, f"Unexpected social preview size: {dimensions}")

    require_file("docs/assets/social-preview.html")
    require_file("docs/assets/hero.png")
    require_file("docs/assets/hero.zh.png")


def validate_workflows_and_docs() -> None:
    require_file(".github/workflows/pages.yml")
    require_file(".github/workflows/validate.yml")
    visual_system = read_text("docs/visual-system.md")
    for marker in [
        "# tracedocs Visual System",
        "## Color Tokens",
        "## Components",
        "### Evidence Label",
        "### Code Block",
        "### Flow Node",
    ]:
        check(marker in visual_system, f"docs/visual-system.md missing marker: {marker}")

    readme = read_text("README.md")
    readme_zh = read_text("README.zh-CN.md")
    for text, label in [(readme, "README.md"), (readme_zh, "README.zh-CN.md")]:
        check("https://wxggzz.github.io/tracedocs/" in text, f"{label} missing live demo link")
        check("/plugin marketplace add https://github.com/wxggzz/tracedocs" in text, f"{label} missing plugin install command")
    check("## Hallucination Test" in readme, "README.md missing Hallucination Test")
    check("## 不幻觉测试" in readme_zh, "README.zh-CN.md missing 不幻觉测试")
    check("## Compatibility Matrix" in readme, "README.md missing Compatibility Matrix")
    check("## 兼容矩阵" in readme_zh, "README.zh-CN.md missing 兼容矩阵")


def main() -> int:
    validate_marketplace()
    validate_skill_sync()
    validate_templates()
    validate_examples()
    validate_assets()
    validate_workflows_and_docs()

    if errors:
        print("tracedocs validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("tracedocs validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
