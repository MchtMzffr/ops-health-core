# Decision Ecosystem — ops-health-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Tests for integration helpers."""

from decision_schema.packet_v2 import PacketV2
from ops_health_core.integration import attach_to_packet, extract_from_packet
from ops_health_core.model import HealthState, OpsSignal
from decision_schema.types import Action


def test_attach_to_packet() -> None:
    """Verify attaching signal to packet."""
    packet = PacketV2(
        run_id="test",
        step=0,
        input={},
        external={},
        mdm={},
        final_action={},
        latency_ms=1,
    )

    signal = OpsSignal(
        score=0.5,
        state=HealthState.YELLOW,
        deny_actions=False,
        cooldown_until_ms=None,
        recommended_action=Action.HOLD,
    )

    new_packet = attach_to_packet(packet, signal)
    assert "ops_health" in new_packet.external
    assert new_packet.external["ops_health"]["ops_score"] == 0.5
    assert new_packet.external["ops_health"]["ops_state"] == "YELLOW"


def test_extract_from_packet() -> None:
    """Verify extracting signal from packet."""
    packet = PacketV2(
        run_id="test",
        step=0,
        input={},
        external={"ops_health": {"ops_score": 0.5, "ops_state": "YELLOW"}},
        mdm={},
        final_action={},
        latency_ms=1,
    )

    context = extract_from_packet(packet)
    assert context is not None
    assert context["ops_score"] == 0.5
    assert context["ops_state"] == "YELLOW"


def test_extract_from_packet_missing() -> None:
    """Verify extracting from packet without ops_health."""
    packet = PacketV2(
        run_id="test",
        step=0,
        input={},
        external={},
        mdm={},
        final_action={},
        latency_ms=1,
    )

    context = extract_from_packet(packet)
    assert context is None
