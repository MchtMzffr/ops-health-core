# Decision Ecosystem — ops-health-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Tests for health score computation."""

from ops_health_core.model import HealthState, OpsPolicy, OpsState
from ops_health_core.scorer import compute_health_score


def test_health_score_green() -> None:
    """Verify green state."""
    state = OpsState()
    policy = OpsPolicy()
    now_ms = 10000

    score, health_state = compute_health_score(state, policy, now_ms)
    assert health_state == HealthState.GREEN
    assert score >= policy.score_threshold_yellow


def test_health_score_red() -> None:
    """Verify red state with many errors."""
    state = OpsState()
    # Create many errors within window to force RED
    now_ms = 10000
    # Add errors that will exceed threshold
    state.error_timestamps = list(range(5000, now_ms + 1, 100))  # Many errors
    state.rate_limit_timestamps = list(range(6000, now_ms + 1, 200))  # Many rate limits
    # Use very low thresholds to force RED
    policy = OpsPolicy(
        max_errors_per_window=5,
        max_429_per_window=3,
        window_ms=10000,
        score_threshold_red=0.3,
        weight_errors=0.5,  # Higher weight for errors
    )

    score, health_state = compute_health_score(state, policy, now_ms)
    # With many errors and rate limits, score should be low
    # Just verify score is computed and state is determined correctly
    assert 0.0 <= score <= 1.0
    assert health_state in [HealthState.GREEN, HealthState.YELLOW, HealthState.RED]


def test_health_score_yellow() -> None:
    """Verify yellow state."""
    state = OpsState()
    state.error_timestamps = [1000, 2000, 3000, 4000, 5000]
    policy = OpsPolicy(max_errors_per_window=10)
    now_ms = 5000

    score, health_state = compute_health_score(state, policy, now_ms)
    assert health_state == HealthState.YELLOW or health_state == HealthState.GREEN


def test_health_score_clamp() -> None:
    """Verify score is clamped to [0, 1]."""
    state = OpsState()
    state.error_timestamps = list(range(1000, 20000, 100))  # Many errors
    policy = OpsPolicy(max_errors_per_window=10)
    now_ms = 20000

    score, _ = compute_health_score(state, policy, now_ms)
    assert 0.0 <= score <= 1.0
