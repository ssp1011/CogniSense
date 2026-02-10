# CogniSense — Deployment Guide

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- Git

### Quick Start (Windows)
```powershell
cd CogniSense
.\scripts\setup_env.ps1
cd backend
uvicorn app.main:app --reload
# In another terminal:
cd frontend
npm install
npm start
```

### Quick Start (Linux/Mac)
```bash
cd CogniSense
chmod +x scripts/setup_env.sh
./scripts/setup_env.sh
cd backend
uvicorn app.main:app --reload
# In another terminal:
cd frontend
npm install
npm start
```

## Docker

```bash
docker-compose up --build
```

## Production
See `configs/production.yaml` for production settings.
