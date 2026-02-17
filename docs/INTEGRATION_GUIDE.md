# Ops-Health Core Integration Guide

## Installation

```bash
pip install ops-health-core
```

Or from source:
```bash
pip install -e .
```

## Basic Usage

### Create Policy and State

```python
from ops_health_core.model import OpsPolicy, OpsState

policy = OpsPolicy(
    max_errors_per_window=10,
    max_429_per_window=5,
    max_reconnects_per_window=3,
    max_p95_latency_ms=1000,
    window_ms=60000,
    cooldown_ms=30000,
)

state = OpsState()
```

### Record Events

```python
now_ms = 1234567890

# Record errors
state.error_timestamps.append(now_ms - 5000)
state.error_timestamps.append(now_ms - 3000)

# Record rate limits
state.rate_limit_timestamps.append(now_ms - 2000)

# Record reconnects
state.reconnect_timestamps.append(now_ms - 1000)

# Record latency
state.p95_latency_ms = 1500
```

### Update Kill Switch

```python
from ops_health_core.kill_switch import update_kill_switch

signal = update_kill_switch(state, policy, now_ms)

# Check signal
if signal.deny_actions:
    print("Kill switch active - deny actions")
```

### Get DMC Context

```python
context = signal.to_context()
# Returns: {"ops_deny_actions": True, "ops_state": "RED", "ops_cooldown_until_ms": ...}
```

## DMC Integration

### Full Example

```python
from ops_health_core.model import OpsPolicy, OpsState
from ops_health_core.kill_switch import update_kill_switch
from dmc_core.dmc.modulator import modulate
from dmc_core.dmc.risk_policy import RiskPolicy
from decision_schema.types import Proposal, Action

# Create ops-health state
ops_state = OpsState()
ops_state.error_timestamps.append(now_ms - 1000)

# Update kill switch
ops_policy = OpsPolicy(max_errors_per_window=5, window_ms=60000, cooldown_ms=30000)
ops_signal = update_kill_switch(ops_state, ops_policy, now_ms)

# Build DMC context
context = {
    "now_ms": now_ms,
    "depth": 100.0,
    "spread_bps": 400.0,
    # ... other context ...
}
context.update(ops_signal.to_context())  # Adds ops-health keys

# DMC will check ops-health guard
proposal = Proposal(action=Action.ACT, confidence=0.8, reasons=["signal"])
final_action, mismatch = modulate(proposal, RiskPolicy(), context)

# If ops-health denies, final_action.action == Action.STOP
if mismatch.flags and "ops_health" in mismatch.flags:
    print(f"Ops-health denied: {mismatch.reason_codes}")
```

## PacketV2 Integration

### Attach to Packet

```python
from ops_health_core.integration import attach_to_packet
from decision_schema.packet_v2 import PacketV2

packet = PacketV2(...)
attach_to_packet(packet, ops_signal)
# Adds ops_signal to packet.external["ops_health"]
```

### Extract from Packet

```python
from ops_health_core.integration import extract_from_packet

signal = extract_from_packet(packet)
# Extracts OpsSignal from packet.external["ops_health"]
```

## Health Score Computation

```python
from ops_health_core.scorer import compute_health_score

score = compute_health_score(state, policy)
# Returns: HealthScore(score=0.5, state=HealthState.YELLOW)
```

## Configuration

### OpsPolicy Parameters

- `max_errors_per_window`: Maximum errors allowed in window
- `max_429_per_window`: Maximum rate limits allowed in window
- `max_reconnects_per_window`: Maximum reconnects allowed in window
- `max_p95_latency_ms`: Maximum p95 latency threshold
- `window_ms`: Time window for sliding window counters
- `cooldown_ms`: Cooldown period when kill switch activates
- `weight_errors`: Weight for error penalty (default: 0.4)
- `weight_429`: Weight for rate-limit penalty (default: 0.3)
- `weight_reconnects`: Weight for reconnect penalty (default: 0.2)
- `weight_latency`: Weight for latency penalty (default: 0.1)
- `green_threshold`: Score threshold for GREEN state (default: 0.6)
- `yellow_threshold`: Score threshold for YELLOW state (default: 0.3)

## Contract Compatibility

Ops-health core depends on `decision-schema>=0.1,<0.2` for PacketV2 integration.

See `ECOSYSTEM_CONTRACT_MATRIX.md` in decision-schema repo for version compatibility details.
