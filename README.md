# Ops-Health Core

**Ops-Health Core** produces operational safety signals: rate-limit & error budgets, reconnect budgets, latency watchdog, backoff recommendations, and kill-switch recommendations.

## Purpose

This core provides:
- **Sliding window counters**: Track errors, rate limits, reconnects within time windows
- **Health score computation**: Normalized score [0.0, 1.0] based on operational metrics
- **Health state**: GREEN / YELLOW / RED based on score thresholds
- **Kill switch**: Automatic cooldown recommendations when health is RED
- **DMC integration**: Convert signals to context dict for DMC guards

## Installation

```bash
pip install ops-health-core
```

Or from source:
```bash
pip install -e .
```

## Quick Start

### Basic Usage

```python
from ops_health_core.model import OpsPolicy, OpsState
from ops_health_core.kill_switch import update_kill_switch

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

# Update kill switch
signal = update_kill_switch(state, policy, now_ms=2000)

# Get context for DMC
context = signal.to_context()
```

### DMC Integration

```python
from ops_health_core.kill_switch import update_kill_switch
from ops_health_core.model import OpsPolicy, OpsState

# In your DMC context building:
signal = update_kill_switch(state, policy, now_ms)
context.update(signal.to_context())

# DMC can check:
if context.get("ops_deny_actions"):
    # Deny actions during cooldown
    return FinalDecision(action=Action.HOLD, allowed=False, ...)
```

## Health Score Formula

```
p_err = min(1, errors/max_errors)
p_429 = min(1, rate_limits/max_429)
p_rec = min(1, reconnects/max_reconnects)
p_lat = min(1, max(0, (p95_latency - max_p95_latency) / max_p95_latency))

score = 1 - (w1*p_err + w2*p_429 + w3*p_rec + w4*p_lat)
```

**State thresholds**:
- GREEN: score >= yellow_threshold (default 0.6)
- YELLOW: red_threshold <= score < yellow_threshold (default 0.3-0.6)
- RED: score < red_threshold (default 0.3)

## Kill Switch

When health state is RED:
- `cooldown_until_ms` is set to `now_ms + cooldown_ms`
- `deny_actions` is set to `True`
- `recommended_action` is set to `Action.HOLD`

During cooldown, actions are denied until cooldown expires.

## Dependencies

**Required**:
- `decision-schema>=0.1,<0.2` (contract dependency)

## Architecture

- **Contract-first**: Only depends on `decision-schema`
- **Non-invasive**: Does NOT modify decision-schema; adds to context/external dicts
- **Offline**: No network calls, all tests run offline
- **Domain-agnostic**: No trading/exchange-specific terms

## Documentation

- `docs/ARCHITECTURE.md`: System architecture
- `docs/FORMULAS.md`: Health score formulas
- `docs/INTEGRATION_GUIDE.md`: DMC integration guide
- `docs/PUBLIC_RELEASE_GUIDE.md`: Public release checklist

## License

[Add your license]
