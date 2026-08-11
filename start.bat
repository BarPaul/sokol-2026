@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   Sokol-2026 (СтудСемья) - launcher
echo ============================================
echo.

if not exist "backend\.venv\Scripts\python.exe" (
    echo [ERROR] Backend venv not found. Create it first:
    echo   cd backend
    echo   python -m venv .venv
    echo   .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo [ERROR] Frontend dependencies not found. Run:
    echo   cd frontend
    echo   npm install
    pause
    exit /b 1
)

echo [1/3] Applying database migrations...
pushd backend
.venv\Scripts\python.exe -m alembic upgrade head
if errorlevel 1 (
    echo [ERROR] Migration failed.
    pause
    exit /b 1
)
popd

echo.
echo [2/3] Starting backend API  (http://127.0.0.1:8000) ...
start "Sokol-2026 backend (FastAPI)" cmd /k "cd /d %~dp0backend && .venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

echo.
echo [3/3] Starting frontend (http://127.0.0.1:3000) ...
start "Sokol-2026 frontend (Nuxt)" cmd /k "cd /d %~dp0frontend && node node_modules\nuxt\bin\nuxt.mjs dev --port 3000 --host 127.0.0.1"

echo.
echo All services are launching. Open http://127.0.0.1:3000
echo Close the two new terminal windows to stop the services.
echo.
pause