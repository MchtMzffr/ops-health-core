<!--
Decision Ecosystem — ops-health-core
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# Integration Guide — ops-health-core

## Dependency

Pin schema version:
```toml
dependencies = ["decision-schema>=0.2,<0.3"]
```

## Basic Usage

```python
from ops_health_core.kill_switch import update_kill_switch
from ops_health_core.model import OpsPolicy, OpsState
from decision_schema.types import Action

# Create policy
policy = OpsPolicy(
    max_errors_per_window=10,
    max_429_per_window=5,
    cooldown_ms=30000,
)

# Create state
state = OpsState()

# Record events
state.error_timestamps.append(1000)
state.error_timestamps.append(2000)
state.rate_limit_timestamps.append(1500)

# Update kill switch
signal = update_kill_switch(state, policy, now_ms=2000)

# Get context for DMC
context = signal.to_context()
```

## DMC Integration (integration layer only)

**Note:** ops-health-core does **not** depend on DMC. The following is an example of how to use ops-health signals in your **integration layer** (e.g. when building the context dict passed to DMC).

```python
from ops_health_core.kill_switch import update_kill_switch
from ops_health_core.model import OpsPolicy, OpsState
# DMC is used only in your integration code, not as a dependency of ops-health-core:
# from dmc_core.dmc.modulator import modulate
# from dmc_core.dmc.risk_policy import RiskPolicy

# In your DMC context building (caller's code):
signal = update_kill_switch(state, policy, now_ms)
context.update(signal.to_context())

# DMC will check ops-health guard automatically
final_decision, mismatch = modulate(proposal, RiskPolicy(), context)

# DMC can check:
if context.get("ops_deny_actions"):
    # Deny actions during cooldown
    # (DMC ops-health guard handles this automatically)
    pass
```

## Health Score Monitoring

```python
signal = update_kill_switch(state, policy, now_ms)

print(f"Health score: {signal.health_score}")
print(f"Health state: {signal.health_state}")  # GREEN, YELLOW, or RED
print(f"Kill switch active: {signal.deny_actions}")
```

## Event Recording

Record events as they occur:

```python
state = OpsState()

# Record error
state.error_timestamps.append(now_ms)

# Record rate limit
state.rate_limit_timestamps.append(now_ms)

# Record reconnect
state.reconnect_timestamps.append(now_ms)
```

## Fail-Closed Behavior

On any error in `update_kill_switch()`:
- Returns signal with `deny_actions=True`
- `recommended_action=Action.HOLD`
- Logs error for debugging
