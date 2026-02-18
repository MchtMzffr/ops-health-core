<!--
Decision Ecosystem — ops-health-core
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# ops-health-core (Operational Safety & Kill-Switch)

This core produces operational safety signals and kill-switch decisions for the decision ecosystem.
Domain-agnostic; depends only on `decision-schema` (for PacketV2 interop).

## Responsibilities

- Health signal aggregation (latency, error rate, drift flags, saturation)
- Kill-switch evaluation (fail-closed)
- Rate-limiting recommendations

## Integration

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

# DMC can check ops_deny_actions flag
if context.get("ops_deny_actions"):
    # Deny actions during cooldown
    return FinalDecision(action=Action.HOLD, allowed=False, ...)
```

## Documentation

- `docs/ARCHITECTURE.md`: System architecture
- `docs/FORMULAS.md`: Health score formulas
- `docs/INTEGRATION_GUIDE.md`: DMC integration guide

## Installation

```bash
pip install -e .
```

Or from git:
```bash
pip install git+https://github.com/MchtMzffr/ops-health-core.git
```

## Tests

```bash
pytest tests/
```

## License

[Add your license]
