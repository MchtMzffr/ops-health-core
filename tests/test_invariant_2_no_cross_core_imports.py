# Decision Ecosystem — ops-health-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""
INVARIANT 2: No cross-core imports.

ops_health_core/** must not import ami_engine, dmc_core, eval_calibration_core.
Only decision_schema is allowed as external ecosystem core.
"""

import ast
from pathlib import Path

FORBIDDEN = {"ami_engine", "dmc_core", "eval_calibration_core", "mdm_engine"}


def test_invariant_2_no_cross_core_imports() -> None:
    """AST scan: no cross-core imports in ops_health_core."""
    root = Path(__file__).resolve().parent.parent
    core_root = root / "ops_health_core"
    if not core_root.is_dir():
        return
    violations = []
    for py_path in core_root.rglob("*.py"):
        if "__pycache__" in str(py_path) or py_path.name.startswith("_"):
            continue
        try:
            tree = ast.parse(py_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        rel = py_path.relative_to(root)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in FORBIDDEN:
                        violations.append((str(rel), node.lineno or 0, alias.name))
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".")[0] in FORBIDDEN:
                    violations.append((str(rel), node.lineno or 0, node.module))
    assert not violations, "INVARIANT 2 violated: " + str(violations)
