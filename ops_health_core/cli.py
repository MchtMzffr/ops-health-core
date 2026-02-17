"""CLI for ops-health-core (offline demo)."""

import argparse
import json
from pathlib import Path

from ops_health_core.contracts import check_schema_compatibility
from ops_health_core.kill_switch import update_kill_switch
from ops_health_core.model import OpsPolicy, OpsState


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Ops-Health Core Demo")
    parser.add_argument("--events", type=Path, help="JSON file with events: [{\"type\": \"error\", \"ts_ms\": 1000}, ...]")
    parser.add_argument("--policy", type=Path, help="JSON file with OpsPolicy config")

    args = parser.parse_args()

    # Check schema compatibility
    try:
        check_schema_compatibility()
    except RuntimeError as e:
        print(f"❌ Schema compatibility check failed: {e}")
        return

    # Load policy
    if args.policy:
        with open(args.policy, "r") as f:
            policy_data = json.load(f)
        policy = OpsPolicy(**policy_data)
    else:
        policy = OpsPolicy()

    # Load events
    if args.events:
        with open(args.events, "r") as f:
            events = json.load(f)
    else:
        # Demo events
        events = [
            {"type": "error", "ts_ms": 1000},
            {"type": "error", "ts_ms": 2000},
            {"type": "429", "ts_ms": 3000},
        ]

    # Process events
    state = OpsState()
    now_ms = max((e["ts_ms"] for e in events), default=1000)

    for event in events:
        event_type = event["type"]
        ts_ms = event["ts_ms"]

        if event_type == "error":
            state.error_timestamps.append(ts_ms)
        elif event_type == "429":
            state.rate_limit_timestamps.append(ts_ms)
        elif event_type == "reconnect":
            state.reconnect_timestamps.append(ts_ms)
        elif event_type == "latency":
            state.latency_samples.append(event.get("latency_ms", 0))

    # Update kill switch
    signal = update_kill_switch(state, policy, now_ms)

    # Print results
    print(f"Health Score: {signal.score:.3f}")
    print(f"State: {signal.state.value}")
    print(f"Deny Actions: {signal.deny_actions}")
    print(f"Recommended Action: {signal.recommended_action.value}")
    print(f"Reasons: {', '.join(signal.reasons)}")
    print(f"\nContext dict:\n{json.dumps(signal.to_context(), indent=2)}")


if __name__ == "__main__":
    main()
