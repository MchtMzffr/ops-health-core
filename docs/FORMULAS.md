# Ops-Health Core Formulas

## Sliding Window

### Event Count in Window

```
count = len([ts for ts in timestamps if now_ms - ts <= window_ms])
```

Prunes timestamps outside window before counting.

## Health Score

### Penalty Components

```
p_err = min(1, errors_in_window / max_errors_per_window)
p_429 = min(1, rate_limits_in_window / max_429_per_window)
p_rec = min(1, reconnects_in_window / max_reconnects_per_window)
p_lat = min(1, max(0, (p95_latency - max_p95_latency_ms) / max_p95_latency_ms))
```

### Weighted Score

```
score = 1 - (w1 * p_err + w2 * p_429 + w3 * p_rec + w4 * p_lat)
```

Where:
- `w1`: Weight for errors (default: 0.4)
- `w2`: Weight for rate limits (default: 0.3)
- `w3`: Weight for reconnects (default: 0.2)
- `w4`: Weight for latency (default: 0.1)

Score is clamped to [0.0, 1.0].

## Health State

### Thresholds

```
if score >= green_threshold (default: 0.6):
    state = "GREEN"
elif score >= yellow_threshold (default: 0.3):
    state = "YELLOW"
else:
    state = "RED"
```

## Kill Switch

### Activation

```
if state == "RED":
    deny_actions = True
    cooldown_until_ms = now_ms + cooldown_ms
else:
    deny_actions = False
    cooldown_until_ms = None
```

### Expiration

```
if now_ms >= cooldown_until_ms AND state == "GREEN":
    deny_actions = False
    cooldown_until_ms = None
```

Kill switch expires automatically when health returns to GREEN after cooldown period.

## Integration with DMC

### Context Conversion

```
context = {
    "ops_deny_actions": signal.deny_actions,
    "ops_state": signal.state.value,
    "ops_cooldown_until_ms": signal.cooldown_until_ms,
}
```

DMC ops-health guard checks these keys:
- `ops_deny_actions == True` → return STOP
- `ops_state == "RED"` → return STOP
- `now_ms < ops_cooldown_until_ms` → return STOP
