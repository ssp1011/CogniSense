# CogniSense — Environment Setup (Windows PowerShell)

Write-Host "🧠 CogniSense Environment Setup" -ForegroundColor Cyan
Write-Host "================================"

# Create Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install backend dependencies
Write-Host "📦 Installing backend dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r backend\requirements.txt

# Install ML dependencies
Write-Host "📦 Installing ML dependencies..." -ForegroundColor Yellow
pip install -r ml\requirements.txt

# Create logs directory
New-Item -ItemType Directory -Force -Path logs | Out-Null

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host "   Activate with: .\venv\Scripts\Activate.ps1"
Write-Host "   Run server:  cd backend; uvicorn app.main:app --reload"
Write-Host "   Run frontend: cd frontend; npm install; npm start"
