from project_to_study.model import Confidence
from project_to_study.scanner import scan


def test_scanner_extracts_core_facts(fixture_repo):
    facts = scan(fixture_repo)

    assert facts.name == "sample-node-app"
    assert "JavaScript" in facts.languages
    assert "npm" in facts.package_managers

    # Commands map from package.json scripts.
    run_cmds = {c.command for c in facts.run_commands}
    assert "npm run dev" in run_cmds
    test_cmds = {c.command for c in facts.test_commands}
    assert "npm run test" in test_cmds

    # Framework / data store / integration inference.
    assert "Express" in facts.frameworks
    assert "PostgreSQL" in facts.data_stores
    assert "Stripe" in facts.integrations

    # Deployment signal from Dockerfile.
    assert any("Docker" in d.purpose for d in facts.deployment_signals)

    assert facts.has_tests


def test_scanner_records_env_var_names_without_values(fixture_repo):
    facts = scan(fixture_repo)
    names = {e.name for e in facts.env_vars}

    # Names from .env.example and source references.
    assert {"PORT", "DATABASE_URL", "STRIPE_SECRET_KEY"} <= names

    # No value is ever stored on the EnvVar model.
    for env in facts.env_vars:
        assert not hasattr(env, "value")
        assert "=" not in env.name


def test_scanner_emits_verified_claims(fixture_repo):
    facts = scan(fixture_repo)
    assert facts.claims
    assert any(c.confidence == Confidence.VERIFIED for c in facts.claims)
