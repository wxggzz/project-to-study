from project_to_study.scanner import scan
from project_to_study.writer import generate


def test_express_routes_extracted(fixture_repo):
    facts = scan(fixture_repo)
    by_path = {(r.method, r.path): r for r in facts.routes}
    assert ("GET", "/health") in by_path
    assert ("GET", "/users") in by_path
    assert ("POST", "/users") in by_path
    # Evidence points at the source file and framework.
    assert any("index.js" in r.evidence for r in facts.routes)
    # Named handler captured; inline arrow function leaves handler empty.
    assert by_path[("GET", "/users")].handler == "listUsers"
    assert by_path[("GET", "/health")].handler == ""


def test_fastapi_routes_extracted(py_fixture_repo):
    facts = scan(py_fixture_repo)
    by_path = {(r.method, r.path): r for r in facts.routes}
    assert ("GET", "/items") in by_path
    assert ("POST", "/items") in by_path
    assert ("GET", "/users/{user_id}") in by_path
    # FastAPI handler names come from the def after the decorator.
    assert by_path[("GET", "/items")].handler == "list_items"
    assert by_path[("GET", "/users/{user_id}")].handler == "get_user"


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


def test_entity_fields_extracted(schemas_fixture_repo):
    facts = scan(schemas_fixture_repo)
    by = {(e.name, e.kind): e for e in facts.entities}
    assert by[("User", "GraphQL type")].fields == ["id", "name"]
    assert by[("CreateUserInput", "GraphQL type")].fields == ["name"]
    assert by[("User", "Protobuf message")].fields == ["id", "name"]
    assert by[("GetUserRequest", "Protobuf message")].fields == ["id"]
    # Prisma block fields, skipping @@index block attributes.
    assert by[("Account", "Prisma model")].fields == ["id", "email", "name"]


def test_schemas_render_in_docs(tmp_path, schemas_fixture_repo):
    facts = scan(schemas_fixture_repo)
    out = tmp_path / "study-docs"
    generate(facts, str(out))

    api = (out / "07-api-and-integrations.md").read_text(encoding="utf-8")
    assert "GraphQL" in api and "gRPC" in api

    data = (out / "08-data-model.md").read_text(encoding="utf-8")
    assert "Protobuf message" in data
    assert "GraphQL type" in data
    assert "Fields" in data            # the new column header
    assert "id, name" in data          # extracted field list


def _write(tmp_path, name, content):
    repo = tmp_path / "repo"
    repo.mkdir(exist_ok=True)
    (repo / name).write_text(content, encoding="utf-8")
    return str(repo)


# --- Regression tests for Codex PR #1 review findings --------------------- #

def test_fastapi_multiple_decorators_on_one_function(tmp_path):
    repo = _write(
        tmp_path, "main.py",
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n\n"
        "@app.get('/ping')\n"
        "@app.post('/ping')\n"
        "def ping():\n"
        "    return {}\n",
    )
    by = {(r.method, r.path): r for r in scan(repo).routes}
    # Both decorators must yield a route (the old combined regex dropped one).
    assert by[("GET", "/ping")].handler == "ping"
    assert by[("POST", "/ping")].handler == "ping"


def test_express_middleware_chain_handler_is_last(tmp_path):
    repo = _write(
        tmp_path, "server.js",
        "const app = require('express')();\n"
        "app.get('/users', requireAuth, listUsers);\n",
    )
    by = {(r.method, r.path): r for r in scan(repo).routes}
    # The handler is the last identifier; requireAuth is middleware.
    assert by[("GET", "/users")].handler == "listUsers"


def test_flask_route_with_extra_kwargs(tmp_path):
    repo = _write(
        tmp_path, "views.py",
        "from flask import Flask\n"
        "app = Flask(__name__)\n\n"
        "@app.route('/items', methods=['GET', 'POST'], strict_slashes=False)\n"
        "def items():\n"
        "    return ''\n",
    )
    by = {(r.method, r.path): r for r in scan(repo).routes}
    # Extra kwargs after methods=[...] must not drop the route.
    assert ("GET", "/items") in by
    assert ("POST", "/items") in by
    assert by[("GET", "/items")].handler == "items"


def test_protobuf_oneof_fields_not_truncated(tmp_path):
    repo = _write(
        tmp_path, "x.proto",
        'syntax = "proto3";\n'
        "message Event {\n"
        "  oneof payload {\n"
        "    string text = 1;\n"
        "    int64 number = 2;\n"
        "  }\n"
        "  int64 id = 3;\n"
        "}\n",
    )
    by = {(e.name, e.kind): e for e in scan(repo).entities}
    fields = by[("Event", "Protobuf message")].fields
    # `id` after the nested oneof block was truncated before the fix.
    assert fields == ["text", "number", "id"]


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
