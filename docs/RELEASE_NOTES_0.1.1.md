<!--
Decision Ecosystem — ops-health-core
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# Release Notes — ops-health-core 0.1.1

**Release Date:** 2026-02-17  
**Type:** Patch Release (backward-compatible)

---

## Summary

This patch release fixes unbounded growth in timestamp lists by implementing in-place pruning, ensuring memory usage remains bounded over time.

---

## Changes

### ✅ F2 — Unbounded Growth Fix

**Problem:** `count_in_window()` pruned timestamps but didn't mutate state, causing `error_timestamps`, `rate_limit_timestamps`, and `reconnect_timestamps` to grow unbounded.

**Solution:** Added in-place pruning:
- `prune_timestamps_inplace()` function
- Called in `update_kill_switch()` before `compute_health_score()`
- Ensures timestamp lists remain bounded within window

**Files Changed:**
- `ops_health_core/windows.py`: Added `prune_timestamps_inplace()`
- `ops_health_core/kill_switch.py`: Call in-place prune before health score computation
- `ops_health_core/scorer.py`: Added TODO for latency_timestamps (future enhancement)

**Invariant:** `∀ts∈timestamps: ts ≥ now_ms - window_ms` (window bounded)

---

## Backward Compatibility

✅ **Fully backward-compatible:**
- No API changes
- Behavior improvement (memory efficiency)
- Existing code continues to work without modification

---

## Migration Guide

**No migration needed.** Existing code continues to work.

**Note:** Timestamp lists now automatically prune in-place, reducing memory usage over time.

---

## Testing

- ✅ All existing tests pass (23/23)
- ✅ Memory boundedness verified
- ✅ Window pruning behavior tested

---

## Future Enhancements

**TODO (P1):** Add `latency_timestamps` to `OpsState` for proper window-based latency pruning. Currently `latency_samples` is timestamp-less.

---

## References

- **Issue:** F2 from static analysis report
- **Performance:** Memory usage now bounded

---

**Upgrade Path:** `pip install "ops-health-core>=0.1.1,<0.2"`
