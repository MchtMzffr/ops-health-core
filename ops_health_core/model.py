# Decision Ecosystem — ops-health-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Ops-Health data models."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from decision_schema.types import Action


class HealthState(str, Enum):
    """Health state levels."""

    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


@dataclass
class OpsPolicy:
    """Operational health policy configuration."""

    window_ms: int = 60_000  # Sliding window duration
    max_errors_per_window: int = 10
    max_429_per_window: int = 5  # Rate limit (429) events
    max_reconnects_per_window: int = 3
    max_p95_latency_ms: int = 1000
    cooldown_ms: int = 30_000  # Kill switch duration
    score_threshold_red: float = 0.3
    score_threshold_yellow: float = 0.6
    # Weights for score computation
    weight_errors: float = 0.4
    weight_429: float = 0.3
    weight_reconnects: float = 0.2
    weight_latency: float = 0.1


@dataclass
class OpsState:
    """Current operational state."""

    error_timestamps: list[int] = field(default_factory=list)
    rate_limit_timestamps: list[int] = field(default_factory=list)
    reconnect_timestamps: list[int] = field(default_factory=list)
    latency_samples: list[int] = field(default_factory=list)
    latency_timestamps: list[int] = field(default_factory=list)
    cooldown_until_ms: int | None = None


@dataclass
class OpsSignal:
    """Operational health signal."""

    score: float  # [0.0, 1.0]
    state: HealthState
    deny_actions: bool
    cooldown_until_ms: int | None
    recommended_action: Action
    reasons: list[str] = field(default_factory=list)

    def to_context(self) -> dict[str, Any]:
        """
        Convert to context dict for DMC integration.
        
        Returns:
            Dict with ops_health fields
        """
        return {
            "ops_score": self.score,
            "ops_state": self.state.value,
            "ops_deny_actions": self.deny_actions,
            "ops_cooldown_until_ms": self.cooldown_until_ms,
            "ops_reasons": self.reasons,
        }
