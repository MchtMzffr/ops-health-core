"""INV-V1: Version single-source - pyproject version must match package __version__."""

import tomllib
from pathlib import Path

import ops_health_core


def test_version_single_source() -> None:
    """pyproject.toml version must equal ops_health_core.__version__ (no drift)."""
    repo_root = Path(__file__).resolve().parent.parent
    with (repo_root / "pyproject.toml").open("rb") as f:
        data = tomllib.load(f)
    pyproject_version = data["project"]["version"]
    assert ops_health_core.__version__ == pyproject_version, (
        "Version drift: pyproject.toml has %r, ops_health_core.__version__ is %r"
        % (pyproject_version, ops_health_core.__version__)
    )
