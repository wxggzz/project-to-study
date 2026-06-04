"""Deep, language-aware extraction of API routes and data entities.

This is the Phase 2 step from ``docs/roadmap.md``: instead of only detecting
*whether* a project exposes an API or uses a database, it extracts the concrete
routes and entities so the generated docs list real endpoints and models.

Covered surfaces: REST-style routes (Express/Node, FastAPI/decorator, Flask,
Django ``urls.py``, Go ``net/http``), gRPC service methods (``.proto``), and
GraphQL operations (``.graphql``/``.gql``). Entities come from Prisma,
SQLAlchemy, Django models, Mongoose, TypeORM, SQL ``CREATE TABLE``, Protobuf
``message``, and GraphQL ``type``/``input``/``interface``/``enum``.

Everything here is deterministic regex/string analysis over the source tree —
no execution, no parsing of untrusted config, no network. Matches are
best-effort and tagged with their source file as evidence; ambiguous results
should still be confirmed against the code.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

from .model import Confidence, Entity, ProjectFacts, Route

# Kept independent of scanner to avoid a circular import.
_IGNORE_DIRS = {
    ".git", "node_modules", "dist", "build", ".next", "out", "coverage",
    "venv", ".venv", "env", "__pycache__", ".mypy_cache", ".pytest_cache",
    "target", ".idea", ".vscode", "vendor", ".tox", ".gradle",
    ".cache", "tmp", ".terraform",
}

_SOURCE_EXT = {
    ".js", ".jsx", ".ts", ".tsx", ".py", ".go", ".prisma", ".sql", ".rb",
    ".proto", ".graphql", ".gql",
}

_MAX_FILES = 3000
_MAX_BYTES = 600_000
_DISPLAY_CAP = 100

# --- Route patterns ------------------------------------------------------- #

# JS/TS: <anything>.get("/path", ...). Require the path to start with "/" to
# avoid matching helpers like lodash `_.get(obj, "a.b")`.
_JS_ROUTE = re.compile(
    r"\b\w+\.(get|post|put|patch|delete|options|head|all)\s*\(\s*['\"`](/[^'\"`]*)['\"`]",
    re.IGNORECASE,
)
# Python decorators: @app.get("/path"), @router.post("/path")
_PY_DECOR = re.compile(
    r"@\w+\.(get|post|put|patch|delete|options|head)\(\s*['\"]([^'\"]+)['\"]",
    re.IGNORECASE,
)
# Flask: @app.route("/path", methods=["GET", "POST"])
_PY_FLASK = re.compile(
    r"@\w+\.route\(\s*['\"]([^'\"]+)['\"](?:[^)]*methods\s*=\s*\[([^\]]*)\])?",
    re.IGNORECASE | re.DOTALL,
)
# Django urls.py: path("route/", view), re_path(r"^x$", view)
_DJANGO_URL = re.compile(r"\b(?:re_path|path|url)\(\s*r?['\"]([^'\"]*)['\"]")
# Go net/http: http.HandleFunc("/path", handler)
_GO_HANDLEFUNC = re.compile(r'HandleFunc\(\s*"(/[^"]*)"')
# gRPC service methods: rpc GetUser (Req) returns (Resp);
_PROTO_RPC = re.compile(r"\brpc\s+(\w+)\s*\(")
# GraphQL operation blocks: type Query { ... } / Mutation / Subscription
_GQL_OP_BLOCK = re.compile(
    r"\btype\s+(Query|Mutation|Subscription)\s*\{([^}]*)\}", re.DOTALL)
# A field line inside a GraphQL block: name(args): Type  /  name: Type
_GQL_FIELD = re.compile(r"(?m)^\s*(\w+)\s*(?:\([^)]*\))?\s*:")

# --- Entity patterns ------------------------------------------------------ #

_PRISMA = re.compile(r"(?m)^\s*model\s+(\w+)\s*\{")
_SQLALCHEMY = re.compile(r"class\s+(\w+)\s*\([^)]*\b(?:Base|db\.Model)\b[^)]*\)")
_DJANGO_MODEL = re.compile(r"class\s+(\w+)\s*\([^)]*\bmodels\.Model\b[^)]*\)")
_MONGOOSE = re.compile(r"""(?:mongoose\.)?model\(\s*['"](\w+)['"]""")
_TYPEORM = re.compile(
    r"@Entity\([^)]*\)\s*(?:export\s+)?(?:abstract\s+)?class\s+(\w+)")
_SQL_TABLE = re.compile(
    r'(?i)create\s+table\s+(?:if\s+not\s+exists\s+)?["\'`]?([\w.]+)')
_PROTO_MESSAGE = re.compile(r"(?m)^\s*message\s+(\w+)\s*\{")
# GraphQL type/input/interface/enum/scalar definitions.
_GQL_TYPE = re.compile(
    r"(?m)^\s*(?:type|input|interface|enum|scalar)\s+(\w+)")
# Operation containers are routes, not entities.
_GQL_OP_TYPES = {"Query", "Mutation", "Subscription"}


def analyze(root: Path, facts: ProjectFacts) -> None:
    """Populate ``facts.routes`` and ``facts.entities`` from the source tree."""

    routes: Dict[Tuple[str, str], Route] = {}
    entities: Dict[Tuple[str, str], Entity] = {}
    scanned = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in _IGNORE_DIRS and not d.startswith(".")]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in _SOURCE_EXT:
                continue
            if scanned >= _MAX_FILES:
                break
            path = Path(dirpath) / fname
            try:
                if path.stat().st_size > _MAX_BYTES:
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            scanned += 1
            rel = os.path.relpath(path, root)
            _extract_routes(text, ext, fname, rel, routes)
            _extract_entities(text, ext, rel, entities)

    facts.routes = list(routes.values())[:_DISPLAY_CAP]
    facts.entities = list(entities.values())[:_DISPLAY_CAP]

    if facts.routes:
        facts.add_claim(
            f"Extracted {len(routes)} API route(s) from source.",
            "route definitions in source", Confidence.VERIFIED)
    if facts.entities:
        facts.add_claim(
            f"Extracted {len(entities)} data entity/model(s) from source.",
            "model/schema definitions in source", Confidence.VERIFIED)


def _add_route(routes: dict, method: str, path: str, rel: str, framework: str) -> None:
    method = method.upper() if method else "—"
    path = path.strip()
    if not path:
        return
    key = (method, path)
    routes.setdefault(key, Route(method=method, path=path,
                                 evidence=f"{rel} ({framework})"))


def _extract_routes(text, ext, fname, rel, routes) -> None:
    if ext in {".js", ".jsx", ".ts", ".tsx"}:
        for method, path in _JS_ROUTE.findall(text):
            _add_route(routes, method, path, rel, "Express/Node")
    elif ext == ".go":
        # Gin/Echo style r.GET("/path") is covered by the JS pattern shape too,
        # but reuse the case-insensitive verb matcher here for Go uppercase.
        for method, path in _JS_ROUTE.findall(text):
            _add_route(routes, method, path, rel, "Go")
        for path in _GO_HANDLEFUNC.findall(text):
            _add_route(routes, "—", path, rel, "Go net/http")
    elif ext == ".py":
        for method, path in _PY_DECOR.findall(text):
            _add_route(routes, method, path, rel, "FastAPI/decorator")
        for path, methods in _PY_FLASK.findall(text):
            verbs = [m.strip().strip("'\"").upper()
                     for m in methods.split(",") if m.strip()] or ["GET"]
            for verb in verbs:
                _add_route(routes, verb, path, rel, "Flask")
        if fname == "urls.py":
            for path in _DJANGO_URL.findall(text):
                _add_route(routes, "—", "/" + path.lstrip("^/"), rel, "Django")
    elif ext == ".proto":
        for method in _PROTO_RPC.findall(text):
            _add_route(routes, "RPC", method, rel, "gRPC")
    elif ext in {".graphql", ".gql"}:
        for op_type, body in _GQL_OP_BLOCK.findall(text):
            for field in _GQL_FIELD.findall(body):
                _add_route(routes, op_type.upper(), field, rel, "GraphQL")


def _add_entity(entities: dict, name: str, kind: str, rel: str) -> None:
    if not name:
        return
    entities.setdefault((name, kind), Entity(name=name, kind=kind, evidence=rel))


def _extract_entities(text, ext, rel, entities) -> None:
    if ext == ".prisma":
        for name in _PRISMA.findall(text):
            _add_entity(entities, name, "Prisma model", rel)
    elif ext == ".sql":
        for name in _SQL_TABLE.findall(text):
            _add_entity(entities, name, "SQL table", rel)
    elif ext == ".py":
        for name in _DJANGO_MODEL.findall(text):
            _add_entity(entities, name, "Django model", rel)
        for name in _SQLALCHEMY.findall(text):
            _add_entity(entities, name, "SQLAlchemy model", rel)
    elif ext in {".js", ".jsx", ".ts", ".tsx"}:
        for name in _MONGOOSE.findall(text):
            _add_entity(entities, name, "Mongoose model", rel)
        for name in _TYPEORM.findall(text):
            _add_entity(entities, name, "TypeORM entity", rel)
    elif ext == ".proto":
        for name in _PROTO_MESSAGE.findall(text):
            _add_entity(entities, name, "Protobuf message", rel)
    elif ext in {".graphql", ".gql"}:
        for name in _GQL_TYPE.findall(text):
            if name not in _GQL_OP_TYPES:
                _add_entity(entities, name, "GraphQL type", rel)
