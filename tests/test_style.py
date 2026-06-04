import pytest

from project_to_study.scanner import scan
from project_to_study.style import StyleName, resolve
from project_to_study.validate import validate
from project_to_study.writer import generate


def _gen(tmp_path, repo, style_name):
    facts = scan(repo)
    out = tmp_path / f"docs-{style_name}"
    generate(facts, str(out), resolve(style_name))
    return out


def test_resolve_unknown_style_raises():
    with pytest.raises(ValueError, match="Unknown style"):
        resolve("fancy")


def test_resolve_defaults_to_standard():
    assert resolve(None).name == StyleName.STANDARD
    assert resolve("STANDARD").name == StyleName.STANDARD


def test_concise_is_shorter_than_standard(tmp_path, fixture_repo):
    std = _gen(tmp_path, fixture_repo, "standard")
    con = _gen(tmp_path, fixture_repo, "concise")

    std_overview = (std / "00-project-overview.md").read_text()
    con_overview = (con / "00-project-overview.md").read_text()
    assert "Who Uses It" in std_overview
    assert "Who Uses It" not in con_overview

    # Concise drops the first-run checklist from quickstart.
    assert "First-Run Checklist" in (std / "01-quickstart.md").read_text()
    assert "First-Run Checklist" not in (con / "01-quickstart.md").read_text()


def test_teaching_adds_glossary_and_callout(tmp_path, fixture_repo):
    teach = _gen(tmp_path, fixture_repo, "teaching")
    learning = (teach / "04-learning-manual.md").read_text()
    assert "Glossary" in learning  # fixture has Express -> glossary populated
    readme = (teach / "README.md").read_text()
    assert "New here?" in readme

    # Standard has no glossary.
    std = _gen(tmp_path, fixture_repo, "standard")
    assert "Glossary" not in (std / "04-learning-manual.md").read_text()


def test_ops_front_loads_operational_docs(tmp_path, fixture_repo):
    ops = _gen(tmp_path, fixture_repo, "ops")
    readme = (ops / "README.md").read_text()
    assert "Operational Quick Reference" in readme

    op_doc = (ops / "02-operation-manual.md").read_text()
    assert "Operational priority document" in op_doc

    # Standard does not include the ops callout.
    std = _gen(tmp_path, fixture_repo, "standard")
    assert "Operational priority document" not in (
        std / "02-operation-manual.md").read_text()


def test_style_recorded_in_log_and_readme(tmp_path, fixture_repo):
    ops = _gen(tmp_path, fixture_repo, "ops")
    assert "Style: `ops`" in (ops / "README.md").read_text()
    assert "Style: ops" in (ops / "_evidence" / "generation-log.md").read_text()


@pytest.mark.parametrize("style_name", StyleName.ALL)
def test_all_styles_validate(tmp_path, fixture_repo, style_name):
    out = _gen(tmp_path, fixture_repo, style_name)
    assert validate(str(out)) == []
