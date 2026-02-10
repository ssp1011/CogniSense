# CogniSense — System Architecture

## High-Level Data Flow

```
┌──────────────┐     ┌────────────────┐     ┌──────────────┐
│   Sensors    │────▶│   Feature      │────▶│  Classifier  │
│  (capture/)  │     │  Extraction    │     │  (ml/models/) │
│              │     │  (ml/features/)│     │              │
└──────────────┘     └────────────────┘     └──────┬───────┘
  - Webcam                                         │
  - Keystroke                                      ▼
  - Mouse                               ┌──────────────────┐
  - Audio (opt)                          │  Scoring Service  │
                                         │  (backend/)       │
                                         └────────┬─────────┘
                                                  │
                                    ┌─────────────┼─────────────┐
                                    ▼             ▼             ▼
                              ┌──────────┐ ┌──────────┐ ┌──────────┐
                              │ REST API │ │ WebSocket│ │ Database │
                              │ /api/v1  │ │ (live)   │ │ (SQLite) │
                              └────┬─────┘ └────┬─────┘ └──────────┘
                                   │             │
                                   ▼             ▼
                              ┌──────────────────────┐
                              │   React Dashboard    │
                              │   (frontend/)        │
                              └──────────────────────┘
```

## Module Dependencies

| Module | Depends On |
|--------|-----------|
| `backend/` | `capture/`, `ml/features/`, `ml/models/` |
| `capture/` | OpenCV, MediaPipe, pynput, sounddevice |
| `ml/features/` | `capture/` output data |
| `ml/models/` | `ml/features/` output, scikit-learn, xgboost |
| `ml/training/` | `ml/features/`, `ml/models/`, `ml/data/` |
| `frontend/` | `backend/` REST API |
