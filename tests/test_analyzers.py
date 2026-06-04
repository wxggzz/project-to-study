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


def test_graphql_operations_and_types_extracted(schemas_fixture_repo):
    facts = scan(schemas_fixture_repo)
    routes = {(r.method, r.path) for r in facts.routes}
    assert ("QUERY", "users") in routes
    assert ("QUERY", "user") in routes
    assert ("MUTATION", "createUser") in routes

    by_kind = {(e.name, e.kind) for e in facts.entities}
    assert ("User", "GraphQL type") in by_kind
    assert ("CreateUserInput", "GraphQL type") in by_kind
    assert ("Role", "GraphQL type") in by_kind
    # Operation containers must NOT be treated as entities.
    assert not any(e.name in {"Query", "Mutation"} for e in facts.entities)


def test_grpc_services_and_messages_extracted(schemas_fixture_repo):
    facts = scan(schemas_fixture_repo)
    routes = {(r.method, r.path) for r in facts.routes}
    assert ("RPC", "GetUser") in routes
    assert ("RPC", "ListUsers") in routes

    by_kind = {(e.name, e.kind) for e in facts.entities}
    assert ("GetUserRequest", "Protobuf message") in by_kind
    assert ("User", "Protobuf message") in by_kind


def test_schemas_render_in_docs(tmp_path, schemas_fixture_repo):
    facts = scan(schemas_fixture_repo)
    out = tmp_path / "study-docs"
    generate(facts, str(out))

    api = (out / "07-api-and-integrations.md").read_text(encoding="utf-8")
    assert "GraphQL" in api and "gRPC" in api

    data = (out / "08-data-model.md").read_text(encoding="utf-8")
    assert "Protobuf message" in data
    assert "GraphQL type" in data


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
