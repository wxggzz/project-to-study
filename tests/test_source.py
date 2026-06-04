from pathlib import Path

import pytest

from project_to_study import source


@pytest.mark.parametrize("spec", [
    "https://github.com/owner/repo",
    "https://github.com/owner/repo.git",
    "http://example.com/owner/repo.git",
    "git@github.com:owner/repo.git",
    "ssh://git@host/owner/repo.git",
    "github.com/owner/repo",
    "gitlab.com/owner/repo",
])
def test_is_remote_true(spec):
    assert source.is_remote(spec) is True


@pytest.mark.parametrize("spec", [
    "/some/local/path",
    "relative/path",
    "",
    "   ",
])
def test_is_remote_false(spec):
    assert source.is_remote(spec) is False


def test_existing_local_path_is_never_remote(fixture_repo):
    # Even though the name is plain, an existing path wins.
    assert source.is_remote(fixture_repo) is False


def test_acquire_local_path_passthrough(tmp_path):
    (tmp_path / "marker").write_text("hi", encoding="utf-8")
    with source.acquire(str(tmp_path)) as resolved:
        assert resolved == str(tmp_path)


def test_acquire_remote_clones_and_cleans_up(monkeypatch):
    recorded = {}

    def fake_run(cmd, **kwargs):
        recorded["cmd"] = cmd
        # Simulate a successful clone by populating the target dir.
        Path(cmd[-1]).mkdir(parents=True, exist_ok=True)
        (Path(cmd[-1]) / "README.md").write_text("cloned", encoding="utf-8")

        class _Result:
            returncode = 0
            stderr = ""

        return _Result()

    monkeypatch.setattr(source.subprocess, "run", fake_run)

    seen_path = {}
    with source.acquire("https://github.com/owner/repo.git") as resolved:
        seen_path["path"] = resolved
        assert Path(resolved, "README.md").exists()

    assert recorded["cmd"][:4] == ["git", "clone", "--depth", "1"]
    # github.com shorthand-less URL passed through unchanged.
    assert recorded["cmd"][4] == "https://github.com/owner/repo.git"
    # Temp dir removed on exit.
    assert not Path(seen_path["path"]).exists()


def test_acquire_shorthand_is_normalized(monkeypatch):
    recorded = {}

    def fake_run(cmd, **kwargs):
        recorded["cmd"] = cmd
        Path(cmd[-1]).mkdir(parents=True, exist_ok=True)

        class _Result:
            returncode = 0
            stderr = ""

        return _Result()

    monkeypatch.setattr(source.subprocess, "run", fake_run)
    with source.acquire("github.com/owner/repo"):
        pass
    assert recorded["cmd"][4] == "https://github.com/owner/repo"


def test_acquire_clone_failure_raises(monkeypatch):
    import subprocess as _sp

    def fake_run(cmd, **kwargs):
        raise _sp.CalledProcessError(1, cmd, stderr="boom")

    monkeypatch.setattr(source.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="git clone failed"):
        with source.acquire("https://github.com/owner/repo.git"):
            pass
