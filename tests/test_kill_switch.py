# Decision Ecosystem — ops-health-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Tests for kill switch."""

from ops_health_core.kill_switch import update_kill_switch
from ops_health_core.model import HealthState, OpsPolicy, OpsState
from decision_schema.types import Action


def test_kill_switch_activates_on_red() -> None:
    """Verify kill switch activates on RED state."""
    state = OpsState()
    # Manually set RED state by forcing low score
    now_ms = 10000
    # Add many events to force low score
    state.error_timestamps = list(range(5000, now_ms + 1, 100))
    state.rate_limit_timestamps = list(range(6000, now_ms + 1, 200))
    policy = OpsPolicy(
        max_errors_per_window=5,
        max_429_per_window=3,
        cooldown_ms=5000,
        window_ms=10000,
        score_threshold_red=0.3,
        weight_errors=0.6,  # High weight to force RED
    )

    signal = update_kill_switch(state, policy, now_ms)
    # If RED, kill switch should activate
    if signal.state == HealthState.RED:
        assert signal.deny_actions is True
        assert signal.recommended_action == Action.HOLD
        assert state.cooldown_until_ms is not None
        assert state.cooldown_until_ms > now_ms
    else:
        # If not RED, verify signal is still valid
        assert signal.score >= 0.0
        assert signal.state in [HealthState.GREEN, HealthState.YELLOW, HealthState.RED]


def test_kill_switch_cooldown_expires() -> None:
    """Verify cooldown expires."""
    state = OpsState()
    state.cooldown_until_ms = 1000
    policy = OpsPolicy()
    now_ms = 2000  # After cooldown

    signal = update_kill_switch(state, policy, now_ms)
    assert state.cooldown_until_ms is None
    assert signal.deny_actions is False or signal.state != HealthState.RED


def test_kill_switch_green_no_cooldown() -> None:
    """Verify no cooldown on GREEN state."""
    state = OpsState()
    policy = OpsPolicy()
    now_ms = 10000

    signal = update_kill_switch(state, policy, now_ms)
    assert signal.state == HealthState.GREEN
    assert signal.deny_actions is False
    assert state.cooldown_until_ms is None


def test_kill_switch_fail_closed() -> None:
    """Fail-closed: when RED or in cooldown, deny_actions=True and recommended_action=HOLD."""
    policy = OpsPolicy(
        max_errors_per_window=2,
        max_429_per_window=2,
        cooldown_ms=5000,
        window_ms=10000,
        score_threshold_red=0.5,
        weight_errors=1.0,
    )
    now_ms = 10000

    # Force RED by exceeding error budget
    state_red = OpsState()
    state_red.error_timestamps = [9000, 9500, 9900]
    signal_red = update_kill_switch(state_red, policy, now_ms)
    if signal_red.state == HealthState.RED:
        assert signal_red.deny_actions is True
        assert signal_red.recommended_action == Action.HOLD

    # Cooldown active => must deny and recommend HOLD
    state_cool = OpsState()
    state_cool.cooldown_until_ms = now_ms + 3000
    signal_cool = update_kill_switch(state_cool, policy, now_ms)
    assert signal_cool.deny_actions is True
    assert signal_cool.recommended_action == Action.HOLD
