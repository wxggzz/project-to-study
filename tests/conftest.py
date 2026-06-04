import pathlib
import sys

import pytest

# Make the package importable without an editable install.
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FIXTURE = ROOT / "tests" / "fixtures" / "sample-node-app"
PY_FIXTURE = ROOT / "tests" / "fixtures" / "sample-py-api"


@pytest.fixture
def fixture_repo() -> str:
    return str(FIXTURE)


@pytest.fixture
def py_fixture_repo() -> str:
    return str(PY_FIXTURE)
