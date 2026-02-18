# Decision Ecosystem — ops-health-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Tests for sliding window."""

from ops_health_core.windows import count_in_window, prune_timestamps


def test_prune_timestamps() -> None:
    """Verify timestamp pruning."""
    timestamps = [1000, 2000, 3000, 4000, 5000]
    now_ms = 5000
    window_ms = 2000

    pruned = prune_timestamps(timestamps, now_ms, window_ms)
    assert pruned == [3000, 4000, 5000]  # Within [3000, 5000]


def test_count_in_window() -> None:
    """Verify count in window."""
    timestamps = [1000, 2000, 3000, 4000, 5000]
    now_ms = 5000
    window_ms = 2000

    count = count_in_window(timestamps, now_ms, window_ms)
    assert count == 3


def test_empty_window() -> None:
    """Verify empty window handling."""
    assert count_in_window([], 5000, 2000) == 0
    assert prune_timestamps([], 5000, 2000) == []
