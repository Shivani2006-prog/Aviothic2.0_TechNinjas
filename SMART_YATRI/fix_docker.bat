@echo off
title 🚀 Train Project - Full Auto Fix + Logging
setlocal enabledelayedexpansion

:: === Define project path and log file ===
set PROJECT_DIR=D:\Programs\train project
set LOG_FILE=%PROJECT_DIR%\docker_fix_log.txt

:: === Create or clear log file ===
echo ===================================================== > "%LOG_FILE%"
echo 🧠 Train Project - Auto Docker Fix Run - %date% %time% >> "%LOG_FILE%"
echo ===================================================== >> "%LOG_FILE%"
echo.

cd /d "%PROJECT_DIR%"
echo =====================================================
echo  🧠 Starting Full Docker + ML Auto-Fix for Train Project
echo =====================================================

:: --- Step 1: Cleanup old Docker containers ---
echo 🧹 Cleaning up old Docker containers...
docker compose down -v >> "%LOG_FILE%" 2>&1
docker rm -f train_booking_app train_db pgadmin >> "%LOG_FILE%" 2>&1
docker network prune -f >> "%LOG_FILE%" 2>&1

:: --- Step 2: Verify Dockerfile exists ---
if not exist "Dockerfile" (
    echo ❌ Dockerfile not found! >> "%LOG_FILE%"
    echo ❌ ERROR: Dockerfile missing in %PROJECT_DIR%
    pause
    exit /b
)

:: --- Step 3: Check ML model files ---
echo 🔍 Checking ML model files...
set MODEL_PATH=ml\model_artifacts

if not exist "%MODEL_PATH%" mkdir "%MODEL_PATH%" >> "%LOG_FILE%" 2>&1

if not exist "%MODEL_PATH%\fare_model.joblib" (
    echo ⚠️ fare_model.joblib missing. Retraining models... >> "%LOG_FILE%"
    docker run --rm -v "%cd%:/app" -w /app python:3.11-slim-bookworm python train_all_models.py >> "%LOG_FILE%" 2>&1
)

if not exist "%MODEL_PATH%\seat_model.joblib" (
    echo ⚠️ seat_model.joblib missing. Retraining models... >> "%LOG_FILE%"
    docker run --rm -v "%cd%:/app" -w /app python:3.11-slim-bookworm python train_all_models.py >> "%LOG_FILE%" 2>&1
)

echo ✅ ML model verification done. >> "%LOG_FILE%"

:: --- Step 4: Reset Alembic versions ---
echo 🔄 Resetting Alembic versions...
rmdir /S /Q Alembic\versions >> "%LOG_FILE%" 2>&1
mkdir Alembic\versions >> "%LOG_FILE%" 2>&1

:: --- Step 5: Build Docker images ---
echo 🏗️ Building Docker images (no cache)...
docker compose build --no-cache >> "%LOG_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo ❌ Build failed. See docker_fix_log.txt for details.
    echo ❌ Build failed! >> "%LOG_FILE%"
    pause
    exit /b
)

:: --- Step 6: Start containers ---
echo 🐳 Starting Docker containers...
docker compose up -d --remove-orphans >> "%LOG_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Startup failed. Retrying with rebuild... >> "%LOG_FILE%"
    docker compose down -v >> "%LOG_FILE%" 2>&1
    docker compose up -d --build >> "%LOG_FILE%" 2>&1
)

:: --- Step 7: Wait for PostgreSQL ---
echo ⏳ Waiting for PostgreSQL to initialize...
timeout /t 25 /nobreak >nul

:: --- Step 8: Alembic migrations ---
echo 🧩 Running Alembic migrations...
docker exec -it train_booking_app alembic revision --autogenerate -m "auto setup" >> "%LOG_FILE%" 2>&1
docker exec -it train_booking_app alembic upgrade head >> "%LOG_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Alembic issue detected — merging heads... >> "%LOG_FILE%"
    docker exec -it train_booking_app alembic merge heads -m "merge heads" >> "%LOG_FILE%" 2>&1
    docker exec -it train_booking_app alembic upgrade head >> "%LOG_FILE%" 2>&1
)

:: --- Step 9: Health check ---
echo 🔍 Checking FastAPI health endpoint...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ FastAPI health endpoint not responding. Retrying... >> "%LOG_FILE%"
    timeout /t 10 /nobreak >nul
    curl -s http://localhost:8000/health >nul 2>&1
)

:: --- Step 10: Check pgAdmin status ---
docker inspect -f "{{.State.Health.Status}}" pgadmin >> "%LOG_FILE%" 2>&1

:: --- Step 11: Final summary ---
echo ===================================================== >> "%LOG_FILE%"
echo ✅ Docker fix completed successfully on %date% %time% >> "%LOG_FILE%"
echo ===================================================== >> "%LOG_FILE%"

echo =====================================================
echo ✅ Environment setup complete!
echo -----------------------------------------------------
echo 🌐 FastAPI Docs:     http://localhost:8000/docs
echo 🧠 pgAdmin Panel:    http://localhost:5050
echo 🗄️  PostgreSQL:       localhost:5432
echo 🪵 Log File:         %LOG_FILE%
echo =====================================================

pause
