# Decision Ecosystem — ops-health-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""INV-OPS-DOC-1: ops-health docs/FORMULAS.md must not use deprecated param names."""

from pathlib import Path


def test_inv_ops_formulas_no_legacy_param_names() -> None:
    """FORMULAS.md must not contain max_rate_limit_events; must use max_429_per_window."""
    repo_root = Path(__file__).resolve().parent.parent
    formulas = repo_root / "docs" / "FORMULAS.md"
    assert formulas.exists(), "docs/FORMULAS.md missing"
    text = formulas.read_text(encoding="utf-8")
    # INV-OPS-DOC-1: legacy names forbidden
    forbidden = ["max_rate_limit_events", "max_rate_limit_events_per_window"]
    for bad in forbidden:
        assert bad not in text, f"INV-OPS-DOC-1: FORMULAS.md must not contain {bad!r}"
    # Code-aligned param must appear
    assert (
        "max_429_per_window" in text
    ), "INV-OPS-DOC-1: FORMULAS.md should document max_429_per_window"
