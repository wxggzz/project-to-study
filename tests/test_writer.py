from pathlib import Path

from project_to_study.scanner import scan
from project_to_study.templates import DOCUMENTS, EVIDENCE_FILES
from project_to_study.writer import generate


def test_writer_produces_full_package(tmp_path, fixture_repo):
    facts = scan(fixture_repo)
    out = tmp_path / "study-docs"
    result = generate(facts, str(out))

    # All documents + package README exist.
    for fname, _title in DOCUMENTS:
        assert (out / fname).exists(), f"missing {fname}"
    assert (out / "README.md").exists()

    # Evidence trail.
    for name in EVIDENCE_FILES:
        assert (out / "_evidence" / name).exists()

    # Mermaid assets.
    assert (out / "assets" / "architecture.mmd").exists()
    assert (out / "assets" / "request-flow.mmd").exists()

    assert "README.md" in result.written


def test_quickstart_contains_real_dev_command(tmp_path, fixture_repo):
    facts = scan(fixture_repo)
    out = tmp_path / "study-docs"
    generate(facts, str(out))

    quickstart = (out / "01-quickstart.md").read_text(encoding="utf-8")
    assert "npm run dev" in quickstart
    assert "npm install" in quickstart


def test_no_secret_values_leak(tmp_path, fixture_repo):
    facts = scan(fixture_repo)
    out = tmp_path / "study-docs"
    generate(facts, str(out))

    # The env var names should appear; no fabricated values.
    op = (out / "02-operation-manual.md").read_text(encoding="utf-8")
    assert "STRIPE_SECRET_KEY" in op
    assert "names only" in op.lower()


def test_data_doc_applicable_for_fixture(tmp_path, fixture_repo):
    facts = scan(fixture_repo)
    out = tmp_path / "study-docs"
    generate(facts, str(out))
    data = (out / "08-data-model.md").read_text(encoding="utf-8")
    # PostgreSQL detected -> real content, not the not-applicable note.
    assert "Not applicable" not in data
    assert "PostgreSQL" in data


def test_api_and_data_not_applicable_for_bare_repo(tmp_path):
    bare = tmp_path / "bare"
    bare.mkdir()
    (bare / "main.py").write_text("print('hello')\n", encoding="utf-8")

    facts = scan(str(bare))
    out = tmp_path / "study-docs"
    result = generate(facts, str(out))

    data = (out / "08-data-model.md").read_text(encoding="utf-8")
    assert "Not applicable" in data
    assert any("08-data-model" in note for note in result.skipped_notes)
