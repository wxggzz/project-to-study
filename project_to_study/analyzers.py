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

# JS/TS: <anything>.get("/path", a, b, handler). Require the path to start with
# "/" to avoid matching helpers like lodash `_.get(obj, "a.b")`. Group 3 is the
# run of identifier arguments after the path; the LAST identifier is the handler
# (earlier ones are middleware). Inline arrow/function literals leave it empty.
_JS_ROUTE = re.compile(
    r"\b\w+\.(get|post|put|patch|delete|options|head|all)\s*\(\s*['\"`](/[^'\"`]*)['\"`]"
    r"((?:\s*,\s*[A-Za-z_$][\w$.]*)*)",
    re.IGNORECASE,
)
_IDENT = re.compile(r"[A-Za-z_$][\w$.]*")
# Python route decorators (FastAPI/APIRouter), matched independently so a
# function carrying several decorators yields one route each. Anchored to line
# start (allowing indentation) so commented-out decorators (`# @app.get(...)`)
# are not matched. The handler is the def that follows (see _PY_DEF).
_PY_DECOR = re.compile(
    r"(?m)^[ \t]*@\w+\.(get|post|put|patch|delete|options|head)\("
    r"\s*['\"]([^'\"]+)['\"]",
    re.IGNORECASE,
)
# Flask: @app.route(...) — the full argument list is read with a paren-balanced
# scanner (so nested calls like defaults=dict(...) don't end it early), then the
# path and methods are pulled from those args.
_PY_ROUTE_CALL = re.compile(r"(?m)^[ \t]*@\w+\.route\(", re.IGNORECASE)
_FLASK_PATH = re.compile(r"['\"]([^'\"]+)['\"]")
_FLASK_METHODS = re.compile(r"methods\s*=\s*\[([^\]]*)\]", re.IGNORECASE)
# The def a decorator applies to (its handler name); see _handler_after.
_PY_DEF = re.compile(r"\bdef\s+(\w+)\s*\(")
# Django urls.py: path("route/", view), re_path(r"^x$", view)
_DJANGO_URL = re.compile(
    r"\b(?:re_path|path|url)\(\s*r?['\"]([^'\"]*)['\"]\s*,\s*([\w.]+)")
# Go net/http: http.HandleFunc("/path", handler)
_GO_HANDLEFUNC = re.compile(r'HandleFunc\(\s*"(/[^"]*)"\s*(?:,\s*([\w.]+))?')
# gRPC service methods: rpc GetUser (Req) returns (Resp);
_PROTO_RPC = re.compile(r"\brpc\s+(\w+)\s*\(")
# A field line inside a GraphQL block: name(args): Type  /  name: Type
_GQL_FIELD = re.compile(r"(?m)^\s*(\w+)\s*(?:\([^)]*\))?\s*:")

# --- Entity patterns ------------------------------------------------------ #

_SQLALCHEMY = re.compile(r"class\s+(\w+)\s*\([^)]*\b(?:Base|db\.Model)\b[^)]*\)")
_DJANGO_MODEL = re.compile(r"class\s+(\w+)\s*\([^)]*\bmodels\.Model\b[^)]*\)")
_MONGOOSE = re.compile(r"""(?:mongoose\.)?model\(\s*['"](\w+)['"]""")
_TYPEORM = re.compile(
    r"@Entity\([^)]*\)\s*(?:export\s+)?(?:abstract\s+)?class\s+(\w+)")
_SQL_TABLE = re.compile(
    r'(?i)create\s+table\s+(?:if\s+not\s+exists\s+)?["\'`]?([\w.]+)')

# Block-structured schemas: headers match through the opening "{"; bodies are
# read with a brace-balanced scanner (_iter_blocks) so nested blocks such as
# Protobuf `oneof`/nested messages are not truncated.
_PRISMA_HEADER = re.compile(r"(?m)^[ \t]*model\s+(\w+)\s*\{")
# Field lines in a Prisma model start with an identifier; skip @@block attrs.
_PRISMA_FIELD = re.compile(r"(?m)^\s*(\w+)\s+\S")
_PROTO_MSG_HEADER = re.compile(r"(?m)^[ \t]*message\s+(\w+)\s*\{")
_PROTO_FIELD = re.compile(r"(?m)^\s*(?:repeated\s+)?[\w.]+\s+(\w+)\s*=\s*\d+")
# Nested blocks inside a message body. `oneof` fields belong to the message, so
# we descend into it; nested `message`/`enum` blocks are their own entities and
# their fields must NOT leak into the outer message.
_PROTO_NESTED = re.compile(r"\b(message|enum|oneof)\b\s+\w*\s*\{")
# GraphQL type/input/interface carry a field block; enum/scalar do not.
_GQL_TYPE_HEADER = re.compile(
    r"(?m)^[ \t]*(?:type|input|interface)\s+(\w+)\s*\{")
_GQL_ENUM_SCALAR = re.compile(r"(?m)^\s*(?:enum|scalar)\s+(\w+)")
# Operation containers are routes, not entities.
_GQL_OP_TYPES = {"Query", "Mutation", "Subscription"}


def _last_identifier(arg_run: str) -> str:
    """Return the last identifier in a comma-separated argument run, or ''.

    Express/Go route handlers come last; anything before is middleware.
    """

    ids = _IDENT.findall(arg_run)
    return ids[-1] if ids else ""


def _skip_string(text: str, i: int) -> int:
    """``text[i]`` is a quote; return the index just past the closing quote.

    Handles triple quotes and backslash escapes. An unterminated single-line
    string bails at the newline so a stray quote can't swallow the rest.
    """

    n = len(text)
    if text[i:i + 3] in ('"""', "'''"):
        triple = text[i:i + 3]
        j = text.find(triple, i + 3)
        return n if j == -1 else j + 3
    quote = text[i]
    i += 1
    while i < n:
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == quote:
            return i + 1
        if c == "\n":
            return i
        i += 1
    return n


def _balanced(text: str, start: int, open_ch: str, close_ch: str, *,
              hash_comment: bool = False, slash_comment: bool = False,
              block_comment: bool = False) -> int:
    """Scan from ``start`` (depth 1, just past an opener) to the matching close.

    String literals and the enabled comment styles are skipped so delimiters
    inside them do not affect the depth count. Returns the index just past the
    matching close, or ``len(text)`` if unbalanced.
    """

    n = len(text)
    depth = 1
    i = start
    while i < n and depth:
        c = text[i]
        if hash_comment and c == "#":
            j = text.find("\n", i)
            i = n if j == -1 else j + 1
            continue
        if slash_comment and c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            i = n if j == -1 else j + 1
            continue
        if block_comment and c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            i = n if j == -1 else j + 2
            continue
        if c == '"' or c == "'":
            i = _skip_string(text, i)
            continue
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
        i += 1
    return i


def _comment_flags(ext: str) -> dict:
    """Comment styles to honour when balancing delimiters, per language."""

    if ext == ".proto":
        return {"slash_comment": True, "block_comment": True}
    if ext == ".prisma":
        return {"slash_comment": True}
    if ext in (".graphql", ".gql"):
        return {"hash_comment": True}
    return {}


def _iter_blocks(text: str, header: re.Pattern, **comment_flags):
    """Yield ``(name, body)`` for each ``header { ... }`` block.

    ``header`` must match through the opening ``{`` and capture the name in
    group 1. The body is read with :func:`_balanced`, so nested ``{...}`` (e.g.
    Protobuf ``oneof``/nested messages) is kept whole and braces inside strings
    or comments do not truncate it.
    """

    n = len(text)
    for m in header.finditer(text):
        end = _balanced(text, m.end(), "{", "}", **comment_flags)
        if m.end() < end <= n and text[end - 1] == "}":
            body = text[m.end():end - 1]
        else:
            body = text[m.end():end]
        yield m.group(1), body


def _handler_after(text: str, pos: int) -> str:
    """Name of the def a decorator (ending at ``pos``) applies to, or ''.

    Finds the next ``def`` but rejects it when a blank line separates it from
    the decorator, so an unrelated later function is not picked up. Robust to
    long or multi-line decorator arguments (unlike a fixed character window).
    """

    m = _PY_DEF.search(text, pos)
    if not m:
        return ""
    if re.search(r"\n[ \t]*\n", text[pos:m.start()]):
        return ""
    return m.group(1)


def _proto_fields(body: str) -> list:
    """Field names directly on a Protobuf message body.

    Descends into ``oneof`` (its fields belong to the message) but skips nested
    ``message``/``enum`` blocks so their fields are not attributed to the outer
    message.
    """

    fields: list = []
    pos = 0
    while True:
        m = _PROTO_NESTED.search(body, pos)
        if not m:
            fields += _PROTO_FIELD.findall(body[pos:])
            return fields
        fields += _PROTO_FIELD.findall(body[pos:m.start()])
        end = _balanced(body, m.end(), "{", "}",
                        slash_comment=True, block_comment=True)
        if m.group(1) == "oneof":
            inner = (body[m.end():end - 1]
                     if m.end() < end <= len(body) and body[end - 1] == "}"
                     else body[m.end():end])
            fields += _proto_fields(inner)
        pos = end


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


def _add_route(routes: dict, method: str, path: str, rel: str, framework: str,
               handler: str = "") -> None:
    method = method.upper() if method else "—"
    path = path.strip()
    if not path:
        return
    key = (method, path)
    routes.setdefault(key, Route(method=method, path=path,
                                 evidence=f"{rel} ({framework})",
                                 handler=handler or ""))


def _extract_routes(text, ext, fname, rel, routes) -> None:
    if ext in {".js", ".jsx", ".ts", ".tsx"}:
        for method, path, args in _JS_ROUTE.findall(text):
            _add_route(routes, method, path, rel, "Express/Node",
                       _last_identifier(args))
    elif ext == ".go":
        # Gin/Echo style r.GET("/path") is covered by the JS pattern shape too,
        # but reuse the case-insensitive verb matcher here for Go uppercase.
        for method, path, args in _JS_ROUTE.findall(text):
            _add_route(routes, method, path, rel, "Go", _last_identifier(args))
        for path, handler in _GO_HANDLEFUNC.findall(text):
            _add_route(routes, "—", path, rel, "Go net/http", handler)
    elif ext == ".py":
        # Each decorator is matched on its own (so a function with several
        # decorators yields a route each); the handler is the next def within a
        # small window, so an unrelated later def is not picked up.
        for m in _PY_DECOR.finditer(text):
            _add_route(routes, m.group(1), m.group(2), rel,
                       "FastAPI/decorator", _handler_after(text, m.end()))
        for m in _PY_ROUTE_CALL.finditer(text):
            end = _balanced(text, m.end(), "(", ")", hash_comment=True)
            args = (text[m.end():end - 1]
                    if m.end() < end <= len(text) and text[end - 1] == ")"
                    else text[m.end():end])
            pm = _FLASK_PATH.search(args)
            if not pm:
                continue
            methods = _FLASK_METHODS.search(args)
            verbs = ([v.strip().strip("'\"").upper()
                      for v in methods.group(1).split(",") if v.strip()]
                     if methods else []) or ["GET"]
            handler = _handler_after(text, end)
            for verb in verbs:
                _add_route(routes, verb, pm.group(1), rel, "Flask", handler)
        if fname == "urls.py":
            for path, handler in _DJANGO_URL.findall(text):
                _add_route(routes, "—", "/" + path.lstrip("^/"), rel, "Django",
                           handler)
    elif ext == ".proto":
        for method in _PROTO_RPC.findall(text):
            _add_route(routes, "RPC", method, rel, "gRPC")
    elif ext in {".graphql", ".gql"}:
        for name, body in _iter_blocks(text, _GQL_TYPE_HEADER,
                                       **_comment_flags(ext)):
            if name in _GQL_OP_TYPES:
                for field in _GQL_FIELD.findall(body):
                    _add_route(routes, name.upper(), field, rel, "GraphQL")


def _add_entity(entities: dict, name: str, kind: str, rel: str,
                fields=None) -> None:
    if not name:
        return
    entities.setdefault(
        (name, kind),
        Entity(name=name, kind=kind, evidence=rel, fields=list(fields or [])))


def _extract_entities(text, ext, rel, entities) -> None:
    if ext == ".prisma":
        for name, body in _iter_blocks(text, _PRISMA_HEADER,
                                       **_comment_flags(ext)):
            _add_entity(entities, name, "Prisma model", rel,
                        _PRISMA_FIELD.findall(body))
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
        for name, body in _iter_blocks(text, _PROTO_MSG_HEADER,
                                       **_comment_flags(ext)):
            _add_entity(entities, name, "Protobuf message", rel,
                        _proto_fields(body))
    elif ext in {".graphql", ".gql"}:
        for name, body in _iter_blocks(text, _GQL_TYPE_HEADER,
                                       **_comment_flags(ext)):
            if name not in _GQL_OP_TYPES:
                _add_entity(entities, name, "GraphQL type", rel,
                            _GQL_FIELD.findall(body))
        for name in _GQL_ENUM_SCALAR.findall(text):
            _add_entity(entities, name, "GraphQL type", rel)
