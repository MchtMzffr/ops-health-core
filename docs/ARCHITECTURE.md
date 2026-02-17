# Ops-Health Core Architecture

## Purpose

**Ops-Health Core** produces operational safety signals: rate-limit budgets, error budgets, reconnect budgets, latency watchdog, backoff recommendations, and kill-switch recommendations.

## Data Flow

```
Events → Sliding Windows → Health Score → Health State → Kill Switch → OpsSignal → DMC Context
```

## Components

### 1. Sliding Windows (`ops_health_core/windows.py`)

**Function**: `count_in_window(timestamps: list[int], window_ms: int, now_ms: int) -> int`

Tracks events within a time window:
- Prunes timestamps outside window
- Counts events within window
- Used for errors, rate limits, reconnects

### 2. Health Score (`ops_health_core/scorer.py`)

**Function**: `compute_health_score(state: OpsState, policy: OpsPolicy) -> HealthScore`

Computes normalized health score [0.0, 1.0]:
- Error rate penalty
- Rate-limit penalty
- Reconnect penalty
- Latency penalty

**Health State**:
- GREEN: score >= 0.6
- YELLOW: 0.3 <= score < 0.6
- RED: score < 0.3

### 3. Kill Switch (`ops_health_core/kill_switch.py`)

**Function**: `update_kill_switch(state: OpsState, policy: OpsPolicy, now_ms: int) -> OpsSignal`

Determines:
- `deny_actions`: Whether to deny all actions
- `cooldown_until_ms`: Cooldown expiration timestamp
- `recommended_action`: Recommended action (if any)

**Activation**:
- RED health state → activate kill switch
- Cooldown period enforced
- Auto-expires when health returns to GREEN

### 4. Integration Helpers (`ops_health_core/integration.py`)

**Functions**:
- `attach_to_packet()`: Attach OpsSignal to PacketV2.external
- `extract_from_packet()`: Extract OpsSignal from PacketV2
- `to_context()`: Convert OpsSignal to DMC context dict

### 5. Model (`ops_health_core/model.py`)

**Types**:
- `OpsPolicy`: Configuration (thresholds, weights, cooldown)
- `OpsState`: Runtime state (error timestamps, rate-limit timestamps, etc.)
- `OpsSignal`: Output signal (deny_actions, state, cooldown)

## Integration Points

### Input: Events

Ops-health core tracks:
- Errors (timestamps)
- Rate limits (429 responses, timestamps)
- Reconnects (timestamps)
- Latency (p95 latency)

### Output: OpsSignal

OpsSignal provides:
- `deny_actions`: Boolean flag for DMC guard
- `ops_state`: Health state string ("GREEN", "YELLOW", "RED")
- `ops_cooldown_until_ms`: Cooldown expiration timestamp

### DMC Integration

OpsSignal converts to DMC context:

```python
signal = update_kill_switch(state, policy, now_ms)
context.update(signal.to_context())
# Adds: ops_deny_actions, ops_state, ops_cooldown_until_ms
```

DMC ops-health guard checks these context keys.

## Design Principles

1. **Contract-first**: Only depends on `decision-schema` (for PacketV2 integration)
2. **Fail-closed**: RED state → deny actions
3. **Automatic recovery**: Cooldown expires when health returns to GREEN
4. **Domain-agnostic**: No trading/exchange-specific logic
5. **Configurable**: All thresholds in OpsPolicy

## Non-Goals

- **Not a monitoring system**: Does not collect events (user provides timestamps)
- **Not domain-specific**: Generic operational safety signals
- **Not a circuit breaker**: Focuses on health scoring and kill-switch, not circuit patterns
