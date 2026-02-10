#!/usr/bin/env bash
# CogniSense — Environment Setup (Linux/Mac)
set -e

echo "🧠 CogniSense Environment Setup"
echo "================================"

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Install ML dependencies
echo "📦 Installing ML dependencies..."
pip install -r ml/requirements.txt

# Create logs directory
mkdir -p logs

echo ""
echo "✅ Setup complete! Activate with: source venv/bin/activate"
echo "   Run server:  cd backend && uvicorn app.main:app --reload"
echo "   Run frontend: cd frontend && npm install && npm start"
