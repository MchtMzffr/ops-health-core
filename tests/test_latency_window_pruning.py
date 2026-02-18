"""Tests for latency window-based pruning (P1 fix)."""

import pytest
from ops_health_core.kill_switch import update_kill_switch
from ops_health_core.model import OpsPolicy, OpsState


def test_latency_samples_pruned_by_window() -> None:
    """Latency samples outside window are pruned."""
    state = OpsState()
    policy = OpsPolicy(window_ms=1000, max_p95_latency_ms=100)
    now_ms = 5000

    # Add latency samples: old (outside window) and new (inside window)
    state.latency_samples = [200, 150, 50]  # Old samples
    state.latency_timestamps = [1000, 2000, 3000]  # Outside window (now_ms - window_ms = 4000)

    state.latency_samples.extend([80, 60])  # New samples
    state.latency_timestamps.extend([4500, 4800])  # Inside window

    # Update kill switch (prunes timestamps and syncs samples)
    signal = update_kill_switch(state, policy, now_ms)

    # After pruning: only samples within window should remain
    assert len(state.latency_samples) == len(state.latency_timestamps)
    assert len(state.latency_samples) == 2  # Only [80, 60] remain
    assert all(ts >= 4000 for ts in state.latency_timestamps)  # All within window


def test_latency_samples_synced_with_timestamps() -> None:
    """Latency samples and timestamps must have same length."""
    state = OpsState()
    policy = OpsPolicy(window_ms=1000)
    now_ms = 5000

    # Mismatched lengths (should be synced during pruning)
    state.latency_samples = [100, 200, 300]
    state.latency_timestamps = [4500, 4800]  # One less timestamp

    signal = update_kill_switch(state, policy, now_ms)

    # After sync: lengths must match
    assert len(state.latency_samples) == len(state.latency_timestamps)


def test_latency_window_based_p95() -> None:
    """P95 latency computed only on windowed samples."""
    state = OpsState()
    policy = OpsPolicy(window_ms=1000, max_p95_latency_ms=100, weight_latency=1.0)
    now_ms = 5000

    # Old high latency (outside window) should not affect score
    state.latency_samples = [500]  # Very high latency
    state.latency_timestamps = [1000]  # Outside window

    # New low latency (inside window)
    state.latency_samples.extend([50, 60, 70])
    state.latency_timestamps.extend([4500, 4600, 4700])

    signal = update_kill_switch(state, policy, now_ms)

    # Score should be based on windowed samples only (50, 60, 70)
    # p95 of [50, 60, 70] = 70, which is < max_p95_latency_ms (100)
    # So p_lat should be 0.0, score should be high
    assert signal.score > 0.9  # High score (no latency penalty)


def test_latency_empty_after_pruning() -> None:
    """If all samples are outside window, latency lists become empty."""
    state = OpsState()
    policy = OpsPolicy(window_ms=1000)
    now_ms = 5000

    # All samples outside window
    state.latency_samples = [100, 200]
    state.latency_timestamps = [1000, 2000]  # Both < 4000 (cutoff)

    signal = update_kill_switch(state, policy, now_ms)

    # After pruning: empty lists
    assert len(state.latency_samples) == 0
    assert len(state.latency_timestamps) == 0
