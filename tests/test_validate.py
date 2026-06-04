from project_to_study.scanner import scan
from project_to_study.validate import validate
from project_to_study.writer import generate


def test_validate_passes_on_generated_output(tmp_path, fixture_repo):
    facts = scan(fixture_repo)
    out = tmp_path / "study-docs"
    generate(facts, str(out))

    problems = validate(str(out))
    assert problems == [], f"unexpected validation problems: {problems}"


def test_validate_flags_missing_document(tmp_path, fixture_repo):
    facts = scan(fixture_repo)
    out = tmp_path / "study-docs"
    generate(facts, str(out))

    (out / "06-architecture.md").unlink()
    problems = validate(str(out))
    assert any("06-architecture.md" in p for p in problems)


def test_validate_flags_broken_link(tmp_path, fixture_repo):
    facts = scan(fixture_repo)
    out = tmp_path / "study-docs"
    generate(facts, str(out))

    readme = out / "README.md"
    readme.write_text(readme.read_text() + "\n[broken](nope-missing.md)\n",
                      encoding="utf-8")
    problems = validate(str(out))
    assert any("nope-missing.md" in p for p in problems)


def test_validate_flags_secret_leak(tmp_path, fixture_repo):
    facts = scan(fixture_repo)
    out = tmp_path / "study-docs"
    generate(facts, str(out))

    doc = out / "02-operation-manual.md"
    doc.write_text(doc.read_text() + '\nAPI_KEY = "sk-livesecretvalue1234567"\n',
                   encoding="utf-8")
    problems = validate(str(out))
    assert any("secret" in p.lower() for p in problems)
