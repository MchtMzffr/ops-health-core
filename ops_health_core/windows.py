# Decision Ecosystem — ops-health-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Sliding window counters."""


def prune_timestamps(timestamps: list[int], now_ms: int, window_ms: int) -> list[int]:
    """
    Prune timestamps outside the sliding window.
    
    Args:
        timestamps: List of event timestamps (ms)
        now_ms: Current time (ms)
        window_ms: Window duration (ms)
    
    Returns:
        Pruned list of timestamps within [now_ms - window_ms, now_ms]
    """
    cutoff_ms = now_ms - window_ms
    return [ts for ts in timestamps if ts >= cutoff_ms]


def prune_timestamps_inplace(timestamps: list[int], now_ms: int, window_ms: int) -> None:
    """
    Prune timestamps in-place (mutates list to avoid unbounded growth).
    
    Args:
        timestamps: List of event timestamps (ms) - will be modified
        now_ms: Current time (ms)
        window_ms: Window duration (ms)
    """
    cutoff_ms = now_ms - window_ms
    # Remove items before cutoff (in-place, efficient)
    timestamps[:] = [ts for ts in timestamps if ts >= cutoff_ms]


def count_in_window(timestamps: list[int], now_ms: int, window_ms: int) -> int:
    """
    Count events within sliding window.
    
    Args:
        timestamps: List of event timestamps (ms)
        now_ms: Current time (ms)
        window_ms: Window duration (ms)
    
    Returns:
        Count of events within window
    """
    pruned = prune_timestamps(timestamps, now_ms, window_ms)
    return len(pruned)
