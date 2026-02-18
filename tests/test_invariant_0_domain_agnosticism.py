# Decision Ecosystem — ops-health-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""
INVARIANT 0: Domain-agnosticism in public surface.

Public surface: README.md, docs/** (excluding docs/examples), ops_health_core/**.
No domain-specific lexemes in public surface.
"""

import re
from pathlib import Path

FORBIDDEN_TERMS = {
    "trade", "trading", "trader", "market", "marketplace",
    "orderbook", "bid", "ask", "quote", "fill", "exchange",
    "portfolio", "pnl", "slippage", "spread", "liquidity",
    "inventory", "exposure", "drawdown", "flatten", "cancel_all",
}

PUBLIC_SURFACE_PATHS = ["README.md", "docs/", "ops_health_core/"]
EXCLUDE_PATTERNS = [r"docs[/\\]examples[/\\]", r"tests/.*"]


def _find_files(repo_root: Path) -> list[Path]:
    files = []
    for path_pattern in PUBLIC_SURFACE_PATHS:
        path = repo_root / path_pattern
        if not path.exists():
            continue
        if path.is_file():
            files.append(path)
        else:
            for f in path.rglob("*"):
                if f.is_file() and f.suffix in (".md", ".py", ".rst", ".txt"):
                    rel = str(f.relative_to(repo_root)).replace("\\", "/")
                    if not any(re.search(p, rel, re.IGNORECASE) for p in EXCLUDE_PATTERNS):
                        files.append(f)
    return files


def _check_file(file_path: Path) -> list[tuple[int, str, str]]:
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return violations
    for i, line in enumerate(content.splitlines(), 1):
        lower = line.lower()
        for term in FORBIDDEN_TERMS:
            if term in lower and not lower.strip().startswith("#"):
                violations.append((i, term, line.strip()[:80]))
    return violations


def test_invariant_0_domain_agnosticism() -> None:
    """Public surface must not contain domain vocabulary (DLS == 0)."""
    repo_root = Path(__file__).resolve().parent.parent
    all_violations = []
    for f in _find_files(repo_root):
        for line_no, term, snippet in _check_file(f):
            all_violations.append((str(f.relative_to(repo_root)), line_no, term, snippet))
    assert not all_violations, "INVARIANT 0 violated: " + str(all_violations[:15])
