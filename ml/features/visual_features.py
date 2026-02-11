"""
CogniSense — Visual Feature Extraction.

Derives cognitive-load-indicative features from a window of face
landmark frames. Computes blink statistics, eye aspect ratio metrics,
eyebrow position, mouth aspect ratio, head pose dynamics, and gaze
deviation.

Usage:
    from capture.webcam_capture import LandmarkFrame
    frames: List[LandmarkFrame] = [...]   # 5-sec window
    features = extract_visual_features(frames, fps=15)
"""

import logging
from typing import Dict, List

import numpy as np

logger = logging.getLogger(__name__)

# ── Landmark indices ─────────────────────────────────────────────────
# Eyebrows
LEFT_EYEBROW_IDX = [276, 283, 282, 295, 300]
RIGHT_EYEBROW_IDX = [46, 53, 52, 65, 70]

# Eyes (same as webcam_capture)
LEFT_EYE_IDX = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_IDX = [33, 160, 158, 133, 153, 144]

# Mouth
UPPER_LIP_IDX = [13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78, 191, 80, 81, 82]
LOWER_LIP_IDX = [14, 317, 402, 318, 324, 308, 415, 310, 311, 312, 13, 82, 81, 80, 191, 78, 95, 88, 178, 87]
MOUTH_TOP = 13
MOUTH_BOTTOM = 14
MOUTH_LEFT = 78
MOUTH_RIGHT = 308

# Iris (for gaze)
LEFT_IRIS_IDX = [468, 469, 470, 471, 472]
RIGHT_IRIS_IDX = [473, 474, 475, 476, 477]


def _mouth_aspect_ratio(landmarks: np.ndarray) -> float:
    """Compute Mouth Aspect Ratio (MAR) = vertical / horizontal."""
    vertical = np.linalg.norm(
        landmarks[MOUTH_TOP] - landmarks[MOUTH_BOTTOM]
    )
    horizontal = np.linalg.norm(
        landmarks[MOUTH_LEFT] - landmarks[MOUTH_RIGHT]
    )
    if horizontal == 0:
        return 0.0
    return vertical / horizontal


def _eyebrow_eye_distance(landmarks: np.ndarray) -> float:
    """Average vertical distance between eyebrow and eye center."""
    left_brow_y = np.mean([landmarks[i][1] for i in LEFT_EYEBROW_IDX])
    left_eye_y = np.mean([landmarks[i][1] for i in LEFT_EYE_IDX])
    right_brow_y = np.mean([landmarks[i][1] for i in RIGHT_EYEBROW_IDX])
    right_eye_y = np.mean([landmarks[i][1] for i in RIGHT_EYE_IDX])
    left_dist = abs(left_eye_y - left_brow_y)
    right_dist = abs(right_eye_y - right_brow_y)
    return (left_dist + right_dist) / 2.0


def _gaze_deviation(landmarks: np.ndarray) -> float:
    """
    Compute gaze deviation as distance of iris center from eye center.

    Uses iris landmarks (468-477) when available (refine_landmarks=True).
    Falls back to 0.0 if landmarks have fewer than 478 points.
    """
    if landmarks.shape[0] < 478:
        return 0.0

    left_iris_center = np.mean(landmarks[LEFT_IRIS_IDX], axis=0)[:2]
    left_eye_center = np.mean(landmarks[LEFT_EYE_IDX], axis=0)[:2]
    right_iris_center = np.mean(landmarks[RIGHT_IRIS_IDX], axis=0)[:2]
    right_eye_center = np.mean(landmarks[RIGHT_EYE_IDX], axis=0)[:2]

    left_dev = np.linalg.norm(left_iris_center - left_eye_center)
    right_dev = np.linalg.norm(right_iris_center - right_eye_center)
    return float((left_dev + right_dev) / 2.0)


def extract_visual_features(
    frames: list, fps: int = 15
) -> Dict[str, float]:
    """
    Extract visual features from a window of LandmarkFrame objects.

    Computes 20 features across blink, EAR, eyebrow, mouth, head pose,
    and gaze categories.

    Args:
        frames: List of LandmarkFrame objects for a time window.
        fps: Frames per second (used for rate calculations).

    Returns:
        Dict of feature_name → value. Returns zeros if no valid frames.
    """
    # Filter to frames where face was detected
    valid = [f for f in frames if f.face_detected]

    if not valid:
        logger.debug("No valid face frames in window")
        return _zero_features()

    window_sec = len(frames) / max(fps, 1)

    # ── Blink features ───────────────────────────────────────────
    blinks = [f for f in valid if f.blink_detected]
    blink_count = len(blinks)
    blink_rate = (blink_count / window_sec) * 60 if window_sec > 0 else 0

    # ── EAR features ─────────────────────────────────────────────
    ears = [f.avg_ear for f in valid]
    ear_mean = float(np.mean(ears))
    ear_std = float(np.std(ears))
    ear_min = float(np.min(ears))
    ear_max = float(np.max(ears))
    ear_range = ear_max - ear_min

    # ── Eyebrow features ────────────────────────────────────────
    brow_dists = [_eyebrow_eye_distance(f.landmarks) for f in valid]
    eyebrow_dist_mean = float(np.mean(brow_dists))
    eyebrow_dist_std = float(np.std(brow_dists))

    # ── Mouth features ──────────────────────────────────────────
    mars = [_mouth_aspect_ratio(f.landmarks) for f in valid]
    mar_mean = float(np.mean(mars))
    mar_std = float(np.std(mars))

    # ── Head pose features ──────────────────────────────────────
    pitches = [f.head_pose["pitch"] for f in valid]
    yaws = [f.head_pose["yaw"] for f in valid]
    rolls = [f.head_pose["roll"] for f in valid]

    head_pitch_mean = float(np.mean(pitches))
    head_pitch_std = float(np.std(pitches))
    head_yaw_std = float(np.std(yaws))
    head_roll_std = float(np.std(rolls))

    # Head movement velocity (degree change per frame)
    if len(pitches) > 1:
        pitch_vel = np.diff(pitches)
        yaw_vel = np.diff(yaws)
        head_movement = float(
            np.mean(np.sqrt(np.array(pitch_vel)**2 + np.array(yaw_vel)**2))
        )
    else:
        head_movement = 0.0

    # ── Gaze features ───────────────────────────────────────────
    gaze_devs = [_gaze_deviation(f.landmarks) for f in valid]
    gaze_deviation_mean = float(np.mean(gaze_devs))
    gaze_deviation_std = float(np.std(gaze_devs))

    # ── Face detection ratio ────────────────────────────────────
    face_presence = len(valid) / max(len(frames), 1)

    features = {
        "blink_count": blink_count,
        "blink_rate": blink_rate,
        "ear_mean": ear_mean,
        "ear_std": ear_std,
        "ear_min": ear_min,
        "ear_range": ear_range,
        "eyebrow_dist_mean": eyebrow_dist_mean,
        "eyebrow_dist_std": eyebrow_dist_std,
        "mar_mean": mar_mean,
        "mar_std": mar_std,
        "head_pitch_mean": head_pitch_mean,
        "head_pitch_std": head_pitch_std,
        "head_yaw_std": head_yaw_std,
        "head_roll_std": head_roll_std,
        "head_movement": head_movement,
        "gaze_deviation_mean": gaze_deviation_mean,
        "gaze_deviation_std": gaze_deviation_std,
        "face_presence": face_presence,
    }

    logger.debug("Extracted %d visual features", len(features))
    return features


def _zero_features() -> Dict[str, float]:
    """Return a dict of all visual features set to 0.0."""
    keys = [
        "blink_count", "blink_rate",
        "ear_mean", "ear_std", "ear_min", "ear_range",
        "eyebrow_dist_mean", "eyebrow_dist_std",
        "mar_mean", "mar_std",
        "head_pitch_mean", "head_pitch_std",
        "head_yaw_std", "head_roll_std", "head_movement",
        "gaze_deviation_mean", "gaze_deviation_std",
        "face_presence",
    ]
    return {k: 0.0 for k in keys}
