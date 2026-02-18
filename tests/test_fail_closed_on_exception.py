# Decision Ecosystem — ops-health-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Fail-closed on exception: update_kill_switch must return deny_actions=True, recommended_action=HOLD."""

import pytest

from decision_schema.types import Action
from ops_health_core.kill_switch import update_kill_switch
from ops_health_core.model import OpsPolicy, OpsState


def test_fail_closed_on_exception() -> None:
    """When compute_health_score raises, update_kill_switch returns fail-closed signal."""
    from unittest.mock import patch

    state = OpsState()
    policy = OpsPolicy()
    now_ms = 10000

    with patch("ops_health_core.kill_switch.compute_health_score", side_effect=RuntimeError("simulated")):
        signal = update_kill_switch(state, policy, now_ms)

    assert signal.deny_actions is True
    assert signal.recommended_action == Action.HOLD
    assert "fail_closed_exception" in signal.reasons
