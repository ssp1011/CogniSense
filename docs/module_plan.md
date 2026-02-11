# Phase 2 — Module-wise Implementation Plan

> Detailed breakdown of all 9 CogniSense modules.

---

## Module 1: Webcam Capture + Face Landmarks

| Attribute | Detail |
|-----------|--------|
| **File** | `capture/webcam_capture.py` |
| **Responsibilities** | Open camera stream, run MediaPipe Face Mesh per frame, extract 468 3D landmarks, compute head pose (pitch/yaw/roll), detect blinks via Eye Aspect Ratio |
| **Libraries** | `opencv-python`, `mediapipe` |
| **Est. LOC** | ~180 |

**Input Schema:**
```python
# Configuration
{ "camera_index": 0, "fps": 15, "resolution": [640, 480] }
```

**Output Schema:**
```python
{
  "timestamp": "2026-02-10T12:00:00",
  "landmarks": [[x, y, z], ...],     # 468 points
  "head_pose": { "pitch": 0.0, "yaw": 0.0, "roll": 0.0 },
  "left_ear": 0.32,                   # Eye Aspect Ratio
  "right_ear": 0.31,
  "blink_detected": false
}
```

**Dependencies:** None (standalone sensor)

---

## Module 2: Emotion / Stress Inference

| Attribute | Detail |
|-----------|--------|
| **File** | `ml/features/visual_features.py` |
| **Responsibilities** | Compute blink rate, EAR stats, eyebrow distance, mouth aspect ratio, head movement velocity, gaze deviation — all from landmarks over a time window |
| **Libraries** | `numpy`, `scipy` |
| **Est. LOC** | ~220 |

**Input:** Window of landmark frames from Module 1 (e.g., 5 sec × 15 fps = 75 frames)

**Output Schema:**
```python
{
  "blink_rate": 18.5,           # blinks/min
  "ear_mean": 0.29,
  "ear_std": 0.04,
  "eyebrow_distance_mean": 0.12,
  "mouth_aspect_ratio": 0.15,
  "head_pitch_std": 2.1,
  "head_yaw_std": 1.8,
  "gaze_deviation": 0.07,
  # ... ~20 features total
}
```

**Dependencies:** Module 1 output

---

## Module 3: Keystroke Dynamics Logger

| Attribute | Detail |
|-----------|--------|
| **File** | `capture/keystroke_logger.py` |
| **Responsibilities** | Capture key press/release with ms timestamps, compute dwell time (key hold), flight time (key-to-key), detect error keys (backspace/delete) |
| **Libraries** | `pynput` |
| **Est. LOC** | ~150 |

**Input:** System keyboard events (automatic via listener)

**Output Schema:**
```python
{
  "timestamp": "2026-02-10T12:00:00",
  "key": "a",
  "event": "press",            # press | release
  "time_ms": 1707556800123     # epoch ms
}
```

**Dependencies:** None (standalone sensor)

---

## Module 4: Mouse Movement Tracker

| Attribute | Detail |
|-----------|--------|
| **File** | `capture/mouse_tracker.py` |
| **Responsibilities** | Track mouse position, clicks, scrolls with timestamps. Buffer events for windowed feature extraction. |
| **Libraries** | `pynput` |
| **Est. LOC** | ~140 |

**Input:** System mouse events (automatic via listener)

**Output Schema:**
```python
{
  "timestamp": "2026-02-10T12:00:00",
  "event": "move",             # move | click | scroll
  "x": 512, "y": 384,
  "button": null,              # left | right | middle (for clicks)
  "scroll_dy": 0
}
```

**Dependencies:** None (standalone sensor)

---

## Module 5: Audio Stress Analyzer

| Attribute | Detail |
|-----------|--------|
| **File** | `capture/audio_capture.py` + `ml/features/audio_features.py` |
| **Responsibilities** | Record mic audio in chunks, extract pitch (F0), jitter, shimmer, MFCCs, spectral energy, speaking rate |
| **Libraries** | `sounddevice`, `librosa`, `numpy` |
| **Est. LOC** | ~200 (capture: 80, features: 120) |

**Input:** 1-second audio chunks at 16kHz

**Output Schema:**
```python
{
  "pitch_mean": 185.2,
  "pitch_std": 24.1,
  "jitter": 0.012,
  "shimmer": 0.035,
  "mfcc_1_mean": -12.5,
  # ... 13 MFCCs
  "spectral_centroid": 1850.0,
  "speaking_rate": 3.2         # syllables/sec
}
```

**Dependencies:** None (standalone sensor, always enabled)

---

## Module 6: Feature Fusion Engine

| Attribute | Detail |
|-----------|--------|
| **File** | `ml/features/fusion.py` |
| **Responsibilities** | Merge visual, behavioral (keystroke + mouse), and audio features into a single vector. Apply normalization. Handle missing modalities (audio off). |
| **Libraries** | `numpy`, `scikit-learn` (StandardScaler) |
| **Est. LOC** | ~100 |

**Input:** Dicts from Modules 2, 3, 4, 5

**Output Schema:**
```python
{
  "vis_blink_rate": 18.5,
  "vis_ear_mean": 0.29,
  "beh_wpm": 62.3,
  "beh_dwell_mean": 95.2,
  "beh_mouse_velocity_mean": 450.0,
  "aud_pitch_mean": 185.2,     # null if audio off
  # ... 40-55 features total, prefixed by modality
}
```

**Dependencies:** Modules 2, 3 (features), 4 (features), 5 (optional)

---

## Module 7: Cognitive Load Classifier

| Attribute | Detail |
|-----------|--------|
| **Files** | `ml/models/random_forest.py`, `xgboost_clf.py`, `svm_clf.py`, `ensemble.py` |
| **Responsibilities** | Train on fused features → predict `low` / `medium` / `high`. Provide confidence scores and per-modality importance. |
| **Libraries** | `scikit-learn`, `xgboost`, `joblib` |
| **Est. LOC** | ~300 (4 files × ~75 each) |

**Input:** Fused feature vector (dict or numpy array)

**Output Schema:**
```python
{
  "load_level": "medium",
  "confidence": 0.82,
  "probabilities": { "low": 0.10, "medium": 0.82, "high": 0.08 },
  "feature_importance": { "vis_blink_rate": 0.12, "beh_wpm": 0.09, ... }
}
```

**Dependencies:** Module 6 output, trained model file in `ml/saved_models/`

---

## Module 8: Real-time Scoring API

| Attribute | Detail |
|-----------|--------|
| **Files** | `backend/app/api/v1/capture.py`, `load.py`, `interview.py`, `exam.py` + `backend/app/services/` |
| **Responsibilities** | REST endpoints for session control, live scoring (poll or WebSocket), historical queries, and scenario-specific analysis |
| **Libraries** | `fastapi`, `uvicorn`, `sqlalchemy`, `websockets` |
| **Est. LOC** | ~400 |

**Endpoints:**

| Endpoint | Method | Input | Output |
|----------|--------|-------|--------|
| `/capture/start` | POST | `{ scenario, webcam_enabled, audio_enabled }` | `{ session_id, started_at }` |
| `/capture/stop` | POST | `{ session_id }` | `{ duration_sec }` |
| `/load/live` | GET | — | `{ load_level, confidence, modality_scores }` |
| `/load/history` | GET | `?limit=100` | `{ predictions: [...], count }` |
| `/interview/analyze` | POST | `{ session_id }` | `{ avg_load, peak_moments, recommendations }` |
| `/exam/analyze` | POST | `{ session_id }` | `{ avg_load, anomalies, time_buckets }` |

**Dependencies:** Modules 1–7 (full pipeline)

---

## Module 9: Visualization Dashboard

| Attribute | Detail |
|-----------|--------|
| **Files** | `frontend/src/components/*.jsx`, `frontend/src/pages/*.jsx` |
| **Responsibilities** | Live cognitive load gauge, stress timeline (line chart), modality contribution (radar/bar chart), alerts when load exceeds threshold |
| **Libraries** | `react`, `chart.js`, `react-chartjs-2`, `axios` |
| **Est. LOC** | ~500 |

**Components:**

| Component | Data Source | Visualization |
|-----------|-----------|---------------|
| `CognitiveLoadMeter` | `/load/live` (poll 1s) | Gauge with color (green/yellow/red) |
| `StressTimeline` | `/load/history` | Line chart (load level over time) |
| `ModalityChart` | `/load/live` | Bar chart (visual/behavioral/audio scores) |
| `AlertsPanel` | Client-side threshold | List of alerts when load > threshold |

**Dependencies:** Module 8 (API)

---

## Integration Dependency Graph

```
Module 1 (Webcam) ───┐
Module 3 (Keystroke) ─┤
Module 4 (Mouse) ─────┼──▶ Module 6 (Fusion) ──▶ Module 7 (Classifier) ──▶ Module 8 (API) ──▶ Module 9 (Dashboard)
Module 5 (Audio) ─────┘          ▲
Module 2 (Visual Features) ──────┘
```

## Total Estimated LOC: ~2,200
