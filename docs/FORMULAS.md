<!--
Decision Ecosystem — ops-health-core
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# Formulas — ops-health-core

## Health Score

```
p_err = min(1, errors/max_errors)
p_rate_limit = min(1, rate_limit_events/max_rate_limit_events)
p_rec = min(1, reconnects/max_reconnects)
p_lat = min(1, max(0, (p95_latency - max_p95_latency) / max_p95_latency))

score = 1 - (w1*p_err + w2*p_rate_limit + w3*p_rec + w4*p_lat)
```

Where `p_*` are normalized penalty factors [0, 1].

## State thresholds

- **GREEN**: score >= yellow_threshold (default 0.6)
- **YELLOW**: red_threshold <= score < yellow_threshold (default 0.3-0.6)
- **RED**: score < red_threshold (default 0.3)

## Kill-switch condition

```
kill_switch_active = (score < red_threshold) OR (now_ms < cooldown_until_ms)
```

When kill-switch is active:
- `deny_actions = True`
- `recommended_action = Action.HOLD`
- `cooldown_until_ms = now_ms + cooldown_ms`

## Sliding window

Events are tracked in sliding windows:
- Window size: `window_ms` (default: 60000 = 1 minute)
- Events outside window are discarded

## Invariants

- **Fail-closed**: On errors, recommend `Action.HOLD`
- **Deterministic**: Same inputs → same outputs
- **Bounded**: Score always in [0, 1]
