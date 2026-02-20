# Decision Ecosystem — ops-health-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Integration helpers for DMC and PacketV2."""

from typing import Any

from decision_schema.packet_v2 import PacketV2
from ops_health_core.model import OpsSignal


def attach_to_packet(packet: PacketV2, signal: OpsSignal) -> PacketV2:
    """
    Attach ops signal to PacketV2.external dict.

    Does NOT modify decision-schema itself; only adds to external dict.

    Args:
        packet: PacketV2 instance
        signal: OpsSignal instance

    Returns:
        New PacketV2 with ops_health in external dict
    """
    # Create new external dict with ops_health
    new_external = packet.external.copy()
    new_external["ops_health"] = signal.to_context()

    # Create new packet with updated external
    return PacketV2(
        run_id=packet.run_id,
        step=packet.step,
        input=packet.input,
        external=new_external,
        mdm=packet.mdm,
        final_action=packet.final_action,
        latency_ms=packet.latency_ms,
        mismatch=packet.mismatch,
        schema_version=packet.schema_version,
    )


def extract_from_packet(packet: PacketV2) -> dict[str, Any] | None:
    """
    Extract ops_health from PacketV2.external dict.

    Args:
        packet: PacketV2 instance

    Returns:
        Ops health context dict or None if not present
    """
    return packet.external.get("ops_health")
