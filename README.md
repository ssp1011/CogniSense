# 🧠 CogniSense

**Multimodal Cognitive Load Detection System Using Behavioral, Visual, and Audio Biometrics**

> Real-time cognitive load estimation (low / medium / high) using webcam facial cues, keystroke dynamics, mouse activity, and optional voice stress signals.

---

## ✨ Features

- **Face Analysis** — Blink rate, eye aspect ratio, head pose, emotion proxies via MediaPipe
- **Keystroke Dynamics** — Typing speed, dwell/flight time, error rate, rhythm consistency
- **Mouse Tracking** — Velocity, acceleration, click patterns, idle detection
- **Audio Stress** *(optional)* — Pitch, jitter, shimmer, MFCCs via Librosa
- **Real-time Dashboard** — Live cognitive load meter, stress timeline, modality charts
- **Multiple Scenarios** — Coding sessions, proctored exams, interview simulations

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy, SQLite |
| ML | Scikit-learn, XGBoost, OpenCV, MediaPipe |
| Audio | Librosa, sounddevice |
| Frontend | React, Chart.js, Axios |
| DevOps | Docker, GitHub Actions |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+

### Windows
```powershell
git clone https://github.com/yourusername/CogniSense.git
cd CogniSense
.\scripts\setup_env.ps1
cd backend
uvicorn app.main:app --reload
```

### Linux / Mac
```bash
git clone https://github.com/yourusername/CogniSense.git
cd CogniSense
./scripts/setup_env.sh
cd backend
uvicorn app.main:app --reload
```

### Frontend (separate terminal)
```bash
cd frontend
npm install
npm start
```

## 📁 Project Structure

```
CogniSense/
├── backend/          # FastAPI app, API routes, services, ORM models
├── capture/          # Real-time sensor modules (webcam, keyboard, mouse, audio)
├── ml/               # ML pipeline (features, models, training, data, notebooks)
├── frontend/         # React dashboard
├── configs/          # YAML configuration files
├── scripts/          # Setup and utility scripts
├── docs/             # Architecture, API reference, feature catalog
├── logs/             # Runtime logs (git-ignored)
├── docker-compose.yml
└── README.md
```

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/capture/start` | Start capture session |
| POST | `/api/v1/capture/stop` | Stop capture session |
| GET | `/api/v1/load/live` | Live cognitive load score |
| GET | `/api/v1/load/history` | Historical predictions |
| POST | `/api/v1/interview/analyze` | Interview analysis |
| POST | `/api/v1/exam/analyze` | Exam proctoring analysis |

## 🧪 Testing

```bash
pytest backend/tests/ -v
```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.