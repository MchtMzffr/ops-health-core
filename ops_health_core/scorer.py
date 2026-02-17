"""Health score computation."""

from ops_health_core.model import HealthState, OpsPolicy, OpsState


def compute_health_score(state: OpsState, policy: OpsPolicy, now_ms: int) -> tuple[float, HealthState]:
    """
    Compute health score and state.
    
    Formula:
        p_err = min(1, errors/max_errors)
        p_429 = min(1, rl/max_429)
        p_rec = min(1, rec/max_reconnects)
        p_lat = min(1, max(0, (p95_latency - max_p95_latency) / max_p95_latency))
        score = 1 - (w1*p_err + w2*p_429 + w3*p_rec + w4*p_lat)
    
    Args:
        state: Current ops state
        policy: Ops policy
        now_ms: Current time (ms)
    
    Returns:
        Tuple of (score [0.0, 1.0], HealthState)
    """
    from ops_health_core.windows import count_in_window

    # Count events in window
    errors = count_in_window(state.error_timestamps, now_ms, policy.window_ms)
    rate_limits = count_in_window(state.rate_limit_timestamps, now_ms, policy.window_ms)
    reconnects = count_in_window(state.reconnect_timestamps, now_ms, policy.window_ms)

    # Compute normalized penalties
    p_err = min(1.0, errors / policy.max_errors_per_window) if policy.max_errors_per_window > 0 else 0.0
    p_429 = min(1.0, rate_limits / policy.max_429_per_window) if policy.max_429_per_window > 0 else 0.0
    p_rec = min(1.0, reconnects / policy.max_reconnects_per_window) if policy.max_reconnects_per_window > 0 else 0.0

    # Latency penalty
    p_lat = 0.0
    if state.latency_samples:
        sorted_latencies = sorted(state.latency_samples)
        n = len(sorted_latencies)
        p95_idx = int(0.95 * n)
        p95_latency = sorted_latencies[min(p95_idx, n - 1)]
        if p95_latency > policy.max_p95_latency_ms:
            p_lat = min(1.0, (p95_latency - policy.max_p95_latency_ms) / policy.max_p95_latency_ms)

    # Weighted score
    score = 1.0 - (
        policy.weight_errors * p_err
        + policy.weight_429 * p_429
        + policy.weight_reconnects * p_rec
        + policy.weight_latency * p_lat
    )

    # Clamp to [0, 1]
    score = max(0.0, min(1.0, score))

    # Determine state
    if score >= policy.score_threshold_yellow:
        health_state = HealthState.GREEN
    elif score >= policy.score_threshold_red:
        health_state = HealthState.YELLOW
    else:
        health_state = HealthState.RED

    return score, health_state
