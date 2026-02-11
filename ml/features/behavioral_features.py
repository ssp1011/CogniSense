"""
CogniSense — Behavioral Feature Extraction.

Derives cognitive-load-indicative features from keystroke and mouse
event buffers. Computes typing speed, dwell/flight times, error rate,
mouse velocity, click patterns, and idle detection.

Usage:
    from capture.keystroke_logger import KeyEvent
    from capture.mouse_tracker import MouseEvent
    features = extract_keystroke_features(key_events, window_sec=5.0)
    features.update(extract_mouse_features(mouse_events, window_sec=5.0))
"""

import logging
from typing import Dict, List

import numpy as np

from capture.keystroke_logger import KeyEvent, KeyEventType
from capture.mouse_tracker import MouseEvent, MouseEventType

logger = logging.getLogger(__name__)


# ── Keystroke Features ───────────────────────────────────────────────

def extract_keystroke_features(
    events: List[KeyEvent], window_sec: float = 5.0
) -> Dict[str, float]:
    """
    Extract 10 keystroke-dynamics features from a window of key events.

    Features:
        - wpm: Approximate words per minute
        - key_count: Total key presses in window
        - dwell_mean, dwell_std: Key hold duration (press→release) stats
        - flight_mean, flight_std: Inter-key interval stats
        - error_rate: Fraction of error keys (backspace/delete)
        - burst_rate: Keys per second in active typing bursts
        - pause_count: Number of pauses > 1 second

    Args:
        events: List of KeyEvent from KeystrokeLogger.
        window_sec: Duration of the capture window in seconds.

    Returns:
        Dict of feature_name → value.
    """
    presses = [e for e in events if e.event_type == KeyEventType.PRESS]
    releases = [e for e in events if e.event_type == KeyEventType.RELEASE]

    if not presses:
        return _zero_keystroke_features()

    key_count = len(presses)

    # ── Words per minute (approx: 5 chars = 1 word) ─────────────
    wpm = (key_count / 5.0) / (window_sec / 60.0) if window_sec > 0 else 0.0

    # ── Dwell time (key hold duration) ──────────────────────────
    dwell_times = []
    release_map: Dict[str, float] = {}
    for r in releases:
        release_map.setdefault(r.key, []).append(r.timestamp) if hasattr(release_map.get(r.key, None), 'append') else release_map.update({r.key: [r.timestamp]})

    # Rebuild release_map properly
    rel_by_key: dict = {}
    for r in releases:
        rel_by_key.setdefault(r.key, []).append(r.timestamp)

    for p in presses:
        if p.key in rel_by_key and rel_by_key[p.key]:
            # Find the first release after this press
            for i, rt in enumerate(rel_by_key[p.key]):
                if rt >= p.timestamp:
                    dwell_times.append(rt - p.timestamp)
                    rel_by_key[p.key].pop(i)
                    break

    dwell_mean = float(np.mean(dwell_times)) if dwell_times else 0.0
    dwell_std = float(np.std(dwell_times)) if dwell_times else 0.0

    # ── Flight time (inter-key interval) ────────────────────────
    press_times = sorted([p.timestamp for p in presses])
    flight_times = np.diff(press_times).tolist() if len(press_times) > 1 else []

    flight_mean = float(np.mean(flight_times)) if flight_times else 0.0
    flight_std = float(np.std(flight_times)) if flight_times else 0.0

    # ── Error rate ──────────────────────────────────────────────
    error_count = sum(1 for p in presses if p.is_error_key)
    error_rate = error_count / key_count if key_count > 0 else 0.0

    # ── Burst rate (keys/sec during active periods) ─────────────
    if flight_times:
        active_flights = [f for f in flight_times if f < 1.0]  # < 1s = active
        if active_flights:
            burst_rate = 1.0 / np.mean(active_flights)
        else:
            burst_rate = 0.0
    else:
        burst_rate = 0.0

    # ── Pause count (gaps > 1 second) ───────────────────────────
    pause_count = sum(1 for f in flight_times if f > 1.0)

    features = {
        "wpm": wpm,
        "key_count": float(key_count),
        "dwell_mean": dwell_mean,
        "dwell_std": dwell_std,
        "flight_mean": flight_mean,
        "flight_std": flight_std,
        "error_rate": error_rate,
        "burst_rate": burst_rate,
        "pause_count": float(pause_count),
    }
    logger.debug("Extracted %d keystroke features", len(features))
    return features


def _zero_keystroke_features() -> Dict[str, float]:
    """Return zero-valued keystroke features."""
    return {k: 0.0 for k in [
        "wpm", "key_count", "dwell_mean", "dwell_std",
        "flight_mean", "flight_std", "error_rate", "burst_rate",
        "pause_count",
    ]}


# ── Mouse Features ───────────────────────────────────────────────────

def extract_mouse_features(
    events: List[MouseEvent], window_sec: float = 5.0
) -> Dict[str, float]:
    """
    Extract 11 mouse-dynamics features from a window of mouse events.

    Features:
        - mouse_distance: Total cursor distance (pixels)
        - mouse_velocity_mean, mouse_velocity_std: Speed stats
        - mouse_acceleration_mean: Rate of speed change
        - click_count: Total clicks
        - click_rate: Clicks per second
        - left_click_ratio: Fraction of left clicks
        - scroll_total: Total scroll distance
        - direction_changes: Number of direction reversals
        - idle_time: Total time cursor was stationary > 0.5s
        - movement_straightness: Ratio of displacement to distance

    Args:
        events: List of MouseEvent from MouseTracker.
        window_sec: Duration of the capture window in seconds.

    Returns:
        Dict of feature_name → value.
    """
    moves = [e for e in events if e.event_type == MouseEventType.MOVE]
    clicks = [e for e in events if e.event_type == MouseEventType.CLICK and e.pressed]
    scrolls = [e for e in events if e.event_type == MouseEventType.SCROLL]

    if not moves:
        return _zero_mouse_features()

    # ── Distance & velocity ─────────────────────────────────────
    positions = np.array([[m.x, m.y] for m in moves], dtype=np.float64)
    timestamps = np.array([m.timestamp for m in moves])

    diffs = np.diff(positions, axis=0)
    distances = np.linalg.norm(diffs, axis=1)
    dt = np.diff(timestamps)
    dt[dt == 0] = 1e-6  # avoid division by zero

    velocities = distances / dt
    mouse_distance = float(np.sum(distances))
    mouse_velocity_mean = float(np.mean(velocities))
    mouse_velocity_std = float(np.std(velocities))

    # ── Acceleration ────────────────────────────────────────────
    if len(velocities) > 1:
        acc = np.diff(velocities) / dt[1:]
        mouse_acceleration_mean = float(np.mean(np.abs(acc)))
    else:
        mouse_acceleration_mean = 0.0

    # ── Clicks ──────────────────────────────────────────────────
    click_count = len(clicks)
    click_rate = click_count / window_sec if window_sec > 0 else 0.0
    left_clicks = sum(1 for c in clicks if c.button == "left")
    left_click_ratio = left_clicks / click_count if click_count > 0 else 0.0

    # ── Scroll ──────────────────────────────────────────────────
    scroll_total = float(sum(abs(s.scroll_dy) for s in scrolls))

    # ── Direction changes ───────────────────────────────────────
    if len(diffs) > 1:
        angles = np.arctan2(diffs[:, 1], diffs[:, 0])
        angle_diffs = np.abs(np.diff(angles))
        direction_changes = float(np.sum(angle_diffs > np.pi / 4))
    else:
        direction_changes = 0.0

    # ── Idle time (gaps > 0.5s between moves) ───────────────────
    idle_time = float(np.sum(dt[dt > 0.5]))

    # ── Movement straightness ───────────────────────────────────
    displacement = np.linalg.norm(positions[-1] - positions[0])
    straightness = displacement / mouse_distance if mouse_distance > 0 else 1.0

    features = {
        "mouse_distance": mouse_distance,
        "mouse_velocity_mean": mouse_velocity_mean,
        "mouse_velocity_std": mouse_velocity_std,
        "mouse_acceleration_mean": mouse_acceleration_mean,
        "click_count": float(click_count),
        "click_rate": click_rate,
        "left_click_ratio": left_click_ratio,
        "scroll_total": scroll_total,
        "direction_changes": direction_changes,
        "idle_time": idle_time,
        "movement_straightness": straightness,
    }
    logger.debug("Extracted %d mouse features", len(features))
    return features


def _zero_mouse_features() -> Dict[str, float]:
    """Return zero-valued mouse features."""
    return {k: 0.0 for k in [
        "mouse_distance", "mouse_velocity_mean", "mouse_velocity_std",
        "mouse_acceleration_mean", "click_count", "click_rate",
        "left_click_ratio", "scroll_total", "direction_changes",
        "idle_time", "movement_straightness",
    ]}
