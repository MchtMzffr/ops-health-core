<!--
Decision Ecosystem — ops-health-core
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# Architecture — ops-health-core

## Role in the ecosystem

ops-health-core provides **operational safety signals** and kill-switch recommendations.

## Data flow

```
Events -> OpsState -> update_kill_switch() -> KillSwitchSignal -> context dict
```

## Health score computation

Health score is computed from:
- Error rate
- Rate-limit event frequency
- Reconnect frequency
- Latency percentiles

## Kill-switch logic

When health state is RED:
- `cooldown_until_ms` is set
- `deny_actions` is set to `True`
- `recommended_action` is set to `Action.HOLD`

## Contracts

- Output: Context dictionary (for DMC integration)
- Uses `decision_schema.types.Action` for recommended actions
- Integrates with `PacketV2` for operational signals

## Components

### 1. Kill Switch (`ops_health_core/kill_switch.py`)

**Function**: `update_kill_switch(state: OpsState, policy: OpsPolicy, now_ms: int) -> KillSwitchSignal`

- Computes health score
- Evaluates kill-switch conditions
- Returns signal with context dict

### 2. Ops State (`ops_health_core/model.py`)

**Class**: `OpsState`

- Tracks error timestamps
- Tracks rate-limit event timestamps
- Tracks reconnect timestamps
- Sliding window counters

### 3. Ops Policy (`ops_health_core/model.py`)

**Class**: `OpsPolicy`

- Configurable thresholds
- Cooldown duration
- Health state thresholds

## Safety invariants

- **Fail-closed**: On errors, recommend `Action.HOLD`
- **Deterministic**: Same inputs → same outputs
- **Non-invasive**: Does not modify `decision-schema`; adds to context dicts
