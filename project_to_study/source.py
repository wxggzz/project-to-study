"""Resolve a target spec (local path or remote Git URL) to a local directory.

Local paths are used in place. Remote Git URLs are shallow-cloned into a
temporary directory that is removed when the context manager exits. This keeps
the rest of the pipeline unaware of where the code came from.

Requires the ``git`` executable on PATH for remote specs; raises a clear
``RuntimeError`` if it is missing or the clone fails.
"""

from __future__ import annotations

import contextlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterator

# Matches https/http/ssh/git URLs, scp-style git@host:path, trailing .git,
# and the common "github.com/owner/repo" shorthand.
_REMOTE_RE = re.compile(
    r"^(https?|ssh|git)://"
    r"|^[\w.+-]+@[\w.-]+:"
    r"|\.git/?$"
    r"|^(github\.com|gitlab\.com|bitbucket\.org)/",
    re.IGNORECASE,
)

_SHORTHAND_HOSTS = ("github.com/", "gitlab.com/", "bitbucket.org/")


def is_remote(spec: str) -> bool:
    """Return True if ``spec`` should be cloned rather than read locally."""

    s = (spec or "").strip()
    if not s:
        return False
    # An existing local path always wins, even if the name looks URL-ish.
    if Path(s).expanduser().exists():
        return False
    return bool(_REMOTE_RE.search(s))


def _normalize(spec: str) -> str:
    s = spec.strip()
    if s.startswith(_SHORTHAND_HOSTS):
        return "https://" + s
    return s


@contextlib.contextmanager
def acquire(spec: str) -> Iterator[str]:
    """Yield a local directory for ``spec``.

    Local paths are yielded unchanged. Remote URLs are shallow-cloned to a temp
    directory that is deleted on exit.
    """

    if not is_remote(spec):
        yield str(Path(spec).expanduser())
        return

    url = _normalize(spec)
    tmp = tempfile.mkdtemp(prefix="tracedocs-")
    try:
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", url, tmp],
                check=True, capture_output=True, text=True,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "git is required to clone remote repositories but was not found "
                "on PATH."
            ) from exc
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or "").strip() or "unknown error"
            raise RuntimeError(f"git clone failed: {detail}") from exc
        yield tmp
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
