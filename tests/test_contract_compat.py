"""Contract compatibility tests."""

import pytest

from ops_health_core.contracts import check_schema_compatibility, get_schema_version


def test_schema_version_import() -> None:
    """Verify schema version can be imported."""
    version = get_schema_version()
    assert isinstance(version, str)
    assert version.count(".") == 2


def test_schema_compatibility() -> None:
    """Verify schema compatibility check."""
    check_schema_compatibility(expected_minor=1)
