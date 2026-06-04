"""Repository scanner.

Reads a target repository and produces :class:`ProjectFacts`. The scanner is
deterministic and dependency-free: it only uses the standard library and simple
heuristics. It never reads secret *values* — environment handling records names
only.

Design note: the scanner collects enough structured context for the writer. It
does not attempt deep semantic analysis of source code (see
docs/architecture.md, "Scanner").
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import analyzers
from .model import (
    Command,
    Confidence,
    EnvVar,
    ImportantFile,
    ProjectFacts,
)

# Directories that are noise for analysis and tree summaries.
IGNORE_DIRS = {
    ".git", "node_modules", "dist", "build", ".next", "out", "coverage",
    "venv", ".venv", "env", "__pycache__", ".mypy_cache", ".pytest_cache",
    "target", ".idea", ".vscode", "vendor", ".tox", ".gradle", "bin", "obj",
    ".cache", "tmp", ".terraform",
}

# File extension -> language.
EXT_LANG = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".go": "Go", ".rs": "Rust",
    ".java": "Java", ".kt": "Kotlin", ".rb": "Ruby", ".php": "PHP",
    ".cs": "C#", ".cpp": "C++", ".c": "C", ".swift": "Swift",
    ".scala": "Scala", ".sh": "Shell", ".vue": "Vue",
}

# Dependency-manifest keyword -> framework label.
FRAMEWORK_KEYWORDS = {
    "next": "Next.js", "react": "React", "vue": "Vue", "nuxt": "Nuxt",
    "svelte": "Svelte", "@angular/core": "Angular", "express": "Express",
    "fastify": "Fastify", "koa": "Koa", "nestjs": "NestJS",
    "@nestjs/core": "NestJS", "fastapi": "FastAPI", "django": "Django",
    "flask": "Flask", "starlette": "Starlette", "tornado": "Tornado",
    "spring-boot": "Spring Boot", "gin-gonic": "Gin", "gin": "Gin",
    "echo": "Echo", "fiber": "Fiber", "actix-web": "Actix",
    "axum": "Axum", "rocket": "Rocket", "rails": "Ruby on Rails",
    "laravel": "Laravel", "click": "Click (CLI)", "typer": "Typer (CLI)",
}

# Dependency-manifest keyword -> data store label.
DATASTORE_KEYWORDS = {
    "pg": "PostgreSQL", "postgres": "PostgreSQL", "psycopg": "PostgreSQL",
    "mysql": "MySQL", "mysql2": "MySQL", "sqlite": "SQLite",
    "better-sqlite3": "SQLite", "mongodb": "MongoDB", "mongoose": "MongoDB",
    "redis": "Redis", "ioredis": "Redis", "prisma": "Prisma ORM",
    "@prisma/client": "Prisma ORM", "sequelize": "Sequelize ORM",
    "typeorm": "TypeORM", "sqlalchemy": "SQLAlchemy", "alembic": "Alembic",
    "gorm": "GORM", "diesel": "Diesel", "elasticsearch": "Elasticsearch",
    "dynamodb": "DynamoDB", "cassandra": "Cassandra",
}

# Dependency-manifest keyword -> external integration label.
INTEGRATION_KEYWORDS = {
    "stripe": "Stripe", "aws-sdk": "AWS", "@aws-sdk": "AWS", "boto3": "AWS",
    "openai": "OpenAI", "anthropic": "Anthropic", "twilio": "Twilio",
    "sendgrid": "SendGrid", "@sentry": "Sentry", "sentry-sdk": "Sentry",
    "googleapis": "Google APIs", "firebase": "Firebase",
    "@supabase": "Supabase", "supabase": "Supabase", "kafkajs": "Kafka",
    "amqplib": "RabbitMQ", "celery": "Celery", "graphql": "GraphQL",
}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _load_json(path: Path) -> Optional[dict]:
    text = _read_text(path)
    if not text.strip():
        return None
    try:
        return json.loads(text)
    except (ValueError, json.JSONDecodeError):
        return None


def _exists(root: Path, *names: str) -> Optional[Path]:
    for name in names:
        candidate = root / name
        if candidate.exists():
            return candidate
    return None


def scan(repo_path: str) -> ProjectFacts:
    """Scan ``repo_path`` and return :class:`ProjectFacts`."""

    root = Path(repo_path).expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Target path is not a directory: {root}")

    facts = ProjectFacts(root=str(root), source=str(root))

    pkg = _load_json(root / "package.json")
    pyproject_text = _read_text(root / "pyproject.toml")

    _detect_name_and_summary(facts, root, pkg, pyproject_text)
    _detect_languages(facts, root)
    _detect_ecosystems(facts, root, pkg)
    _detect_commands(facts, root, pkg)
    _detect_frameworks_and_services(facts, root, pkg, pyproject_text)
    _detect_entry_points(facts, root, pkg)
    _detect_env_vars(facts, root)
    _detect_deployment(facts, root)
    _detect_tests(facts, root, pkg)
    _detect_license(facts, root)
    _collect_important_files(facts, root)
    facts.source_tree = _summarize_tree(root)

    # Phase 2 deep extraction: concrete routes and data entities.
    analyzers.analyze(root, facts)

    _record_unknowns(facts)
    return facts


# --------------------------------------------------------------------------- #
# Individual detectors
# --------------------------------------------------------------------------- #

def _detect_name_and_summary(
    facts: ProjectFacts, root: Path, pkg: Optional[dict], pyproject_text: str
) -> None:
    name = None
    evidence = None

    if pkg and isinstance(pkg.get("name"), str):
        name = pkg["name"]
        evidence = "package.json name"
    if not name and pyproject_text:
        m = re.search(r'(?m)^\s*name\s*=\s*["\']([^"\']+)["\']', pyproject_text)
        if m:
            name = m.group(1)
            evidence = "pyproject.toml name"
    if not name:
        cargo = _read_text(root / "Cargo.toml")
        m = re.search(r'(?m)^\s*name\s*=\s*["\']([^"\']+)["\']', cargo)
        if m:
            name = m.group(1)
            evidence = "Cargo.toml name"
    if not name:
        gomod = _read_text(root / "go.mod")
        m = re.search(r'(?m)^\s*module\s+(\S+)', gomod)
        if m:
            name = m.group(1).rsplit("/", 1)[-1]
            evidence = "go.mod module"

    if name:
        facts.name = name
        facts.add_claim(f"Project name is `{name}`.", evidence, Confidence.VERIFIED)
    else:
        facts.name = root.name
        facts.add_claim(
            f"Project name inferred from directory name `{root.name}`.",
            "directory name", Confidence.INFERRED,
        )

    # Summary: package.json description, then README first paragraph.
    if pkg and isinstance(pkg.get("description"), str) and pkg["description"].strip():
        facts.summary = pkg["description"].strip()
        facts.summary_confidence = Confidence.VERIFIED
        facts.add_claim("Project summary taken from package description.",
                        "package.json description", Confidence.VERIFIED)
        return

    readme = _exists(root, "README.md", "README.rst", "README.txt", "README")
    if readme:
        summary = _readme_first_paragraph(_read_text(readme))
        if summary:
            facts.summary = summary
            facts.summary_confidence = Confidence.INFERRED
            facts.add_claim("Project summary inferred from README.",
                            f"{readme.name} first paragraph", Confidence.INFERRED)
            return

    facts.summary = ""
    facts.summary_confidence = Confidence.UNKNOWN


def _readme_first_paragraph(text: str) -> str:
    paragraph: List[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if paragraph:
                break
            continue
        if line.startswith("#") or line.startswith("![") or line.startswith("<"):
            continue
        if line.startswith("[![") or line.startswith("---"):
            continue
        paragraph.append(line)
        if len(" ".join(paragraph)) > 400:
            break
    return " ".join(paragraph).strip()


def _detect_languages(facts: ProjectFacts, root: Path) -> None:
    counts: Dict[str, int] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            lang = EXT_LANG.get(ext)
            if lang:
                counts[lang] = counts.get(lang, 0) + 1

    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    facts.languages = [lang for lang, _ in ranked]
    if ranked:
        top = ", ".join(f"{lang} ({n})" for lang, n in ranked[:5])
        facts.add_claim(f"Languages detected by file census: {top}.",
                        "source file extensions", Confidence.VERIFIED)


def _detect_ecosystems(facts: ProjectFacts, root: Path, pkg: Optional[dict]) -> None:
    managers: List[Tuple[str, str]] = []  # (label, evidence)

    if pkg is not None:
        if (root / "pnpm-lock.yaml").exists():
            managers.append(("pnpm", "pnpm-lock.yaml"))
        elif (root / "yarn.lock").exists():
            managers.append(("yarn", "yarn.lock"))
        elif (root / "package-lock.json").exists():
            managers.append(("npm", "package-lock.json"))
        else:
            managers.append(("npm", "package.json"))

    if (root / "pyproject.toml").exists():
        text = _read_text(root / "pyproject.toml")
        if "[tool.poetry]" in text:
            managers.append(("Poetry", "pyproject.toml [tool.poetry]"))
        else:
            managers.append(("pip / PEP 621", "pyproject.toml"))
    if (root / "requirements.txt").exists():
        managers.append(("pip", "requirements.txt"))
    if (root / "Pipfile").exists():
        managers.append(("pipenv", "Pipfile"))
    if (root / "go.mod").exists():
        managers.append(("Go modules", "go.mod"))
    if (root / "Cargo.toml").exists():
        managers.append(("Cargo", "Cargo.toml"))
    if (root / "pom.xml").exists():
        managers.append(("Maven", "pom.xml"))
    if (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
        managers.append(("Gradle", "build.gradle"))
    if (root / "Gemfile").exists():
        managers.append(("Bundler", "Gemfile"))
    if (root / "composer.json").exists():
        managers.append(("Composer", "composer.json"))

    seen = set()
    for label, evidence in managers:
        if label in seen:
            continue
        seen.add(label)
        facts.package_managers.append(label)
        facts.add_claim(f"Package manager / ecosystem: {label}.",
                        evidence, Confidence.VERIFIED)


def _detect_commands(facts: ProjectFacts, root: Path, pkg: Optional[dict]) -> None:
    """Populate install/run/build/test/lint commands from scripts + defaults."""

    # --- Node package.json scripts ---
    if pkg and isinstance(pkg.get("scripts"), dict):
        runner = "npm run"
        if (root / "pnpm-lock.yaml").exists():
            runner = "pnpm"
        elif (root / "yarn.lock").exists():
            runner = "yarn"
        scripts = pkg["scripts"]

        # Install command from lockfile/runner.
        install = {"pnpm": "pnpm install", "yarn": "yarn install"}.get(runner, "npm install")
        facts.install_commands.append(
            Command("Install dependencies", install, "package.json + lockfile",
                    Confidence.VERIFIED))

        def add(label: str, key: str, bucket: List[Command]) -> bool:
            if key in scripts:
                cmd = f"{runner} {key}" if runner != "npm run" else f"npm run {key}"
                bucket.append(Command(label, cmd, f"package.json scripts.{key}",
                                      Confidence.VERIFIED))
                return True
            return False

        add("Start development server", "dev", facts.run_commands)
        add("Start application", "start", facts.run_commands)
        add("Build for production", "build", facts.build_commands)
        if not add("Run tests", "test", facts.test_commands):
            pass
        add("Lint", "lint", facts.lint_commands)
        add("Format", "format", facts.lint_commands)

    # --- Python pyproject / requirements ---
    py_text = _read_text(root / "pyproject.toml")
    if py_text or (root / "requirements.txt").exists():
        if (root / "requirements.txt").exists():
            facts.install_commands.append(
                Command("Install dependencies", "pip install -r requirements.txt",
                        "requirements.txt", Confidence.VERIFIED))
        elif "[tool.poetry]" in py_text:
            facts.install_commands.append(
                Command("Install dependencies", "poetry install",
                        "pyproject.toml [tool.poetry]", Confidence.VERIFIED))
        elif py_text:
            facts.install_commands.append(
                Command("Install dependencies", "pip install -e .",
                        "pyproject.toml", Confidence.INFERRED))

        # Console scripts as entry/run hints handled in entry points.
        if not facts.test_commands and (
            "pytest" in py_text or (root / "pytest.ini").exists()
            or (root / "tests").is_dir() or (root / "test").is_dir()
        ):
            facts.test_commands.append(
                Command("Run tests", "pytest", "pytest config / tests directory",
                        Confidence.INFERRED))

    # --- Go ---
    if (root / "go.mod").exists():
        facts.build_commands.append(
            Command("Build", "go build ./...", "go.mod", Confidence.INFERRED))
        if not facts.test_commands:
            facts.test_commands.append(
                Command("Run tests", "go test ./...", "go.mod", Confidence.INFERRED))

    # --- Rust ---
    if (root / "Cargo.toml").exists():
        facts.build_commands.append(
            Command("Build", "cargo build", "Cargo.toml", Confidence.INFERRED))
        facts.run_commands.append(
            Command("Run", "cargo run", "Cargo.toml", Confidence.INFERRED))
        if not facts.test_commands:
            facts.test_commands.append(
                Command("Run tests", "cargo test", "Cargo.toml", Confidence.INFERRED))

    # --- Makefile targets (supplemental) ---
    makefile = _exists(root, "Makefile", "makefile")
    if makefile:
        targets = re.findall(r"(?m)^([a-zA-Z][\w-]*):", _read_text(makefile))
        for target in targets:
            low = target.lower()
            cmd = Command(f"make {target}", f"make {target}",
                          f"Makefile target: {target}", Confidence.VERIFIED)
            if low in {"test", "tests", "check"} and not facts.test_commands:
                facts.test_commands.append(cmd)
            elif low in {"build", "compile"}:
                facts.build_commands.append(cmd)
            elif low in {"run", "dev", "serve", "start"}:
                facts.run_commands.append(cmd)
            elif low in {"lint", "fmt", "format"}:
                facts.lint_commands.append(cmd)

    for cmd in facts.all_commands():
        facts.add_claim(f"{cmd.label}: `{cmd.command}`.", cmd.evidence, cmd.confidence)


def _gather_dependency_text(root: Path, pkg: Optional[dict]) -> str:
    """Concatenate dependency declarations for keyword matching (lowercased)."""

    parts: List[str] = []
    if pkg:
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            deps = pkg.get(key)
            if isinstance(deps, dict):
                parts.extend(deps.keys())
    for fname in ("pyproject.toml", "requirements.txt", "Pipfile",
                  "go.mod", "Cargo.toml", "pom.xml", "Gemfile", "composer.json"):
        parts.append(_read_text(root / fname))
    return "\n".join(parts).lower()


def _detect_frameworks_and_services(
    facts: ProjectFacts, root: Path, pkg: Optional[dict], pyproject_text: str
) -> None:
    blob = _gather_dependency_text(root, pkg)

    def collect(keywords: Dict[str, str], target: List[str], kind: str) -> None:
        for needle, label in keywords.items():
            if needle in blob and label not in target:
                target.append(label)
                facts.add_claim(f"{kind}: {label}.",
                                f"dependency keyword: {needle}", Confidence.INFERRED)

    collect(FRAMEWORK_KEYWORDS, facts.frameworks, "Framework")
    collect(DATASTORE_KEYWORDS, facts.data_stores, "Data store")
    collect(INTEGRATION_KEYWORDS, facts.integrations, "External integration")

    # Schema / migration directories strengthen the data-store story.
    for rel in ("prisma/schema.prisma", "migrations", "alembic", "db/migrate",
                "schema.sql"):
        p = root / rel
        if p.exists() and "Database schema/migrations" not in facts.data_stores:
            facts.data_stores.append("Database schema/migrations")
            facts.add_claim("Database schema or migrations present.",
                            rel, Confidence.VERIFIED)
            break


def _detect_entry_points(facts: ProjectFacts, root: Path, pkg: Optional[dict]) -> None:
    candidates: List[Tuple[str, str, str]] = []  # (path, role, evidence)

    if pkg:
        main = pkg.get("main")
        if isinstance(main, str) and (root / main).exists():
            candidates.append((main, "Node main module", "package.json main"))

    # package.json bin (string or dict)
    if pkg and pkg.get("bin"):
        binval = pkg["bin"]
        if isinstance(binval, str):
            candidates.append((binval, "CLI binary", "package.json bin"))
        elif isinstance(binval, dict):
            for _, target in binval.items():
                if isinstance(target, str):
                    candidates.append((target, "CLI binary", "package.json bin"))

    common = [
        ("src/index.ts", "Application entry"),
        ("src/index.js", "Application entry"),
        ("src/main.ts", "Application entry"),
        ("index.js", "Application entry"),
        ("main.py", "Application entry"),
        ("app.py", "Application entry"),
        ("manage.py", "Django management entry"),
        ("wsgi.py", "WSGI entry"),
        ("asgi.py", "ASGI entry"),
        ("main.go", "Go entry"),
        ("cmd", "Go command packages"),
        ("src/main.rs", "Rust entry"),
        ("src/lib.rs", "Rust library root"),
    ]
    for rel, role in common:
        if (root / rel).exists():
            candidates.append((rel, role, f"{rel} present"))

    # Python console scripts from pyproject.
    py_text = _read_text(root / "pyproject.toml")
    for m in re.finditer(r'(?m)^\s*([\w-]+)\s*=\s*["\']([\w\.]+):([\w]+)["\']', py_text):
        script, module, func = m.group(1), m.group(2), m.group(3)
        candidates.append((module.replace(".", "/") + ".py",
                           f"Console script `{script}` -> {module}:{func}",
                           "pyproject scripts"))

    seen = set()
    for path, role, evidence in candidates:
        if path in seen:
            continue
        seen.add(path)
        facts.entry_points.append(ImportantFile(path=path, purpose=role))
        facts.add_claim(f"Entry point `{path}` ({role}).", evidence, Confidence.VERIFIED)


_ENV_PATTERNS = [
    re.compile(r"process\.env\.([A-Z_][A-Z0-9_]*)"),
    re.compile(r"process\.env\[['\"]([A-Z_][A-Z0-9_]*)['\"]\]"),
    re.compile(r"os\.environ\[['\"]([A-Z_][A-Z0-9_]*)['\"]\]"),
    re.compile(r"os\.environ\.get\(['\"]([A-Z_][A-Z0-9_]*)['\"]"),
    re.compile(r"os\.getenv\(['\"]([A-Z_][A-Z0-9_]*)['\"]"),
    re.compile(r"std::env::var\(['\"]([A-Z_][A-Z0-9_]*)['\"]"),
    re.compile(r"os\.Getenv\(['\"]([A-Z_][A-Z0-9_]*)['\"]"),
]


def _detect_env_vars(facts: ProjectFacts, root: Path) -> None:
    """Collect env var NAMES only. Never reads or stores values."""

    found: Dict[str, EnvVar] = {}

    # 1) .env example files: parse keys to the left of '=' only.
    for fname in (".env.example", ".env.sample", ".env.template",
                  ".env.dist", "env.example"):
        p = root / fname
        if not p.exists():
            continue
        for raw in _read_text(p).splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            key = line.split("=", 1)[0].strip()
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key or ""):
                found.setdefault(key, EnvVar(
                    name=key, required="Yes",
                    evidence=f"{fname} (name only)", confidence=Confidence.VERIFIED))

    # 2) Light source scan for references.
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        for fname in filenames:
            if os.path.splitext(fname)[1].lower() not in {
                ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs"
            }:
                continue
            if scanned > 400:
                break
            scanned += 1
            text = _read_text(Path(dirpath) / fname)
            for pattern in _ENV_PATTERNS:
                for key in pattern.findall(text):
                    if key not in found:
                        found[key] = EnvVar(
                            name=key, required="Unknown",
                            evidence="referenced in source",
                            confidence=Confidence.INFERRED)

    facts.env_vars = [found[k] for k in sorted(found)]
    if facts.env_vars:
        facts.add_claim(
            f"Detected {len(facts.env_vars)} environment variable name(s).",
            "env example files / source references", Confidence.VERIFIED)


_DEPLOY_SIGNALS = [
    ("Dockerfile", "Container image build (Docker)"),
    ("docker-compose.yml", "Multi-container orchestration (Docker Compose)"),
    ("docker-compose.yaml", "Multi-container orchestration (Docker Compose)"),
    ("compose.yaml", "Multi-container orchestration (Docker Compose)"),
    ("vercel.json", "Vercel deployment config"),
    ("netlify.toml", "Netlify deployment config"),
    ("fly.toml", "Fly.io deployment config"),
    ("render.yaml", "Render deployment config"),
    ("railway.json", "Railway deployment config"),
    ("Procfile", "Process declaration (Heroku-style)"),
    ("app.yaml", "Google App Engine config"),
    ("Chart.yaml", "Helm chart"),
    ("serverless.yml", "Serverless Framework config"),
]


def _detect_deployment(facts: ProjectFacts, root: Path) -> None:
    for fname, purpose in _DEPLOY_SIGNALS:
        if (root / fname).exists():
            facts.deployment_signals.append(ImportantFile(path=fname, purpose=purpose))
            facts.add_claim(f"Deployment signal: {purpose}.", fname, Confidence.VERIFIED)

    workflows = root / ".github" / "workflows"
    if workflows.is_dir():
        files = sorted(p.name for p in workflows.glob("*.y*ml"))
        if files:
            facts.deployment_signals.append(ImportantFile(
                path=".github/workflows/", purpose="CI/CD via GitHub Actions"))
            facts.add_claim("CI/CD configured via GitHub Actions.",
                            f".github/workflows/ ({', '.join(files)})",
                            Confidence.VERIFIED)

    if any(root.glob("*.tf")):
        facts.deployment_signals.append(ImportantFile(
            path="*.tf", purpose="Infrastructure as code (Terraform)"))
        facts.add_claim("Infrastructure as code present (Terraform).",
                        "*.tf files", Confidence.VERIFIED)

    k8s = root / "k8s"
    if k8s.is_dir() or (root / "kubernetes").is_dir():
        facts.deployment_signals.append(ImportantFile(
            path="k8s/", purpose="Kubernetes manifests"))
        facts.add_claim("Kubernetes manifests present.", "k8s/ directory",
                        Confidence.VERIFIED)


def _detect_tests(facts: ProjectFacts, root: Path, pkg: Optional[dict]) -> None:
    test_dirs = []
    for rel in ("tests", "test", "__tests__", "spec"):
        if (root / rel).is_dir():
            test_dirs.append(rel)

    # Test files scattered in the tree.
    test_file_count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        for fname in filenames:
            low = fname.lower()
            if (low.startswith("test_") or low.endswith("_test.py")
                    or ".test." in low or ".spec." in low
                    or low.endswith("_test.go")):
                test_file_count += 1

    facts.has_tests = bool(test_dirs) or test_file_count > 0

    blob = _gather_dependency_text(root, pkg)
    framework = None
    for needle, label in (("pytest", "pytest"), ("jest", "Jest"),
                          ("vitest", "Vitest"), ("mocha", "Mocha"),
                          ("@testing-library", "Testing Library"),
                          ("junit", "JUnit"), ("rspec", "RSpec")):
        if needle in blob:
            framework = label
            break
    if not framework and any(d in test_dirs for d in ("tests", "test")) and "Python" in facts.languages:
        framework = "pytest"
    facts.test_framework = framework

    for rel in test_dirs:
        facts.test_signals.append(ImportantFile(path=rel + "/", purpose="Test suite"))
    if facts.has_tests:
        ev = ", ".join(test_dirs) if test_dirs else f"{test_file_count} test file(s)"
        facts.add_claim(
            f"Project has tests ({framework or 'framework unknown'}).",
            ev, Confidence.VERIFIED)
    else:
        facts.add_claim("No tests detected.", "no test dirs/files found",
                        Confidence.INFERRED)


def _detect_license(facts: ProjectFacts, root: Path) -> None:
    lic = _exists(root, "LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")
    if not lic:
        return
    head = _read_text(lic)[:600]
    name = None
    for needle, label in (("MIT License", "MIT"), ("Apache License", "Apache-2.0"),
                          ("GNU GENERAL PUBLIC", "GPL"),
                          ("BSD 3-Clause", "BSD-3-Clause"),
                          ("Mozilla Public License", "MPL-2.0")):
        if needle in head:
            name = label
            break
    facts.license_name = name or "Present (type unclear)"
    facts.add_claim(f"License: {facts.license_name}.", lic.name,
                    Confidence.VERIFIED if name else Confidence.INFERRED)


def _collect_important_files(facts: ProjectFacts, root: Path) -> None:
    notable = [
        ("README.md", "Project introduction"),
        ("package.json", "Node manifest and scripts"),
        ("pyproject.toml", "Python project metadata"),
        ("requirements.txt", "Python dependencies"),
        ("go.mod", "Go module definition"),
        ("Cargo.toml", "Rust crate manifest"),
        ("Makefile", "Task automation"),
        ("Dockerfile", "Container build"),
        ("docker-compose.yml", "Local orchestration"),
        (".env.example", "Environment variable template"),
        ("tsconfig.json", "TypeScript configuration"),
    ]
    for rel, purpose in notable:
        if (root / rel).exists():
            facts.important_files.append(ImportantFile(path=rel, purpose=purpose))


def _summarize_tree(root: Path, max_depth: int = 2, max_entries: int = 60) -> str:
    """Render a compact 2-level tree, collapsing ignored directories."""

    lines: List[str] = [f"{root.name}/"]
    count = 0

    def walk(path: Path, prefix: str, depth: int) -> None:
        nonlocal count
        if depth > max_depth or count >= max_entries:
            return
        try:
            entries = sorted(
                path.iterdir(),
                key=lambda p: (p.is_file(), p.name.lower()),
            )
        except OSError:
            return
        entries = [e for e in entries
                   if not (e.is_dir() and (e.name in IGNORE_DIRS or e.name.startswith("."))
                           and e.name != ".github")]
        for entry in entries:
            if count >= max_entries:
                lines.append(f"{prefix}...")
                return
            count += 1
            if entry.is_dir():
                lines.append(f"{prefix}{entry.name}/")
                walk(entry, prefix + "  ", depth + 1)
            else:
                lines.append(f"{prefix}{entry.name}")

    walk(root, "  ", 1)
    return "\n".join(lines)


def _record_unknowns(facts: ProjectFacts) -> None:
    if not facts.summary:
        facts.unknowns.append("Project purpose/summary could not be determined.")
    if not facts.run_commands:
        facts.unknowns.append("No run/start command found.")
    if not facts.test_commands:
        facts.unknowns.append("No test command found.")
    if not facts.deployment_signals:
        facts.unknowns.append("No deployment configuration found in the repository.")
    if not facts.entry_points:
        facts.unknowns.append("No obvious application entry point found.")
