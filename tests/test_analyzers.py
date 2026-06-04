from project_to_study.scanner import scan
from project_to_study.writer import generate


def test_express_routes_extracted(fixture_repo):
    facts = scan(fixture_repo)
    pairs = {(r.method, r.path) for r in facts.routes}
    assert ("GET", "/health") in pairs
    assert ("GET", "/users") in pairs
    assert ("POST", "/users") in pairs
    # Evidence points at the source file and framework.
    assert any("index.js" in r.evidence for r in facts.routes)


def test_fastapi_routes_extracted(py_fixture_repo):
    facts = scan(py_fixture_repo)
    pairs = {(r.method, r.path) for r in facts.routes}
    assert ("GET", "/items") in pairs
    assert ("POST", "/items") in pairs
    assert ("GET", "/users/{user_id}") in pairs


def test_sqlalchemy_entities_extracted(py_fixture_repo):
    facts = scan(py_fixture_repo)
    by_name = {e.name: e for e in facts.entities}
    assert "User" in by_name
    assert "Item" in by_name
    assert by_name["User"].kind == "SQLAlchemy model"
    assert "models.py" in by_name["User"].evidence


def test_routes_and_entities_render_in_docs(tmp_path, py_fixture_repo):
    facts = scan(py_fixture_repo)
    out = tmp_path / "study-docs"
    generate(facts, str(out))

    api = (out / "07-api-and-integrations.md").read_text(encoding="utf-8")
    assert "/items" in api
    assert "Routes / Endpoints" in api

    data = (out / "08-data-model.md").read_text(encoding="utf-8")
    assert "User" in data
    assert "SQLAlchemy model" in data


def test_no_false_routes_in_plain_repo(tmp_path):
    bare = tmp_path / "bare"
    bare.mkdir()
    (bare / "util.py").write_text(
        "import functools\n"
        "data = {}\n"
        "x = data.get('a.b')\n",  # lodash/dict .get must NOT be a route
        encoding="utf-8",
    )
    facts = scan(str(bare))
    assert facts.routes == []
    assert facts.entities == []
