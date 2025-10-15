@echo off
title 🔍 Train Project - Docker Status Monitor
setlocal enabledelayedexpansion

set PROJECT_DIR=D:\Programs\train project
set LOG_FILE=%PROJECT_DIR%\docker_status_log.txt

echo ===================================================== > "%LOG_FILE%"
echo 🧠 Train Project - Docker Health Check (%date% %time%) >> "%LOG_FILE%"
echo ===================================================== >> "%LOG_FILE%"
echo.

cd /d "%PROJECT_DIR%"

echo =====================================================
echo 🔍 Checking Train Project Docker Environment
echo =====================================================

:: --- Step 1: Check if Docker is running ---
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running! Please start Docker Desktop.
    echo ❌ Docker not running! >> "%LOG_FILE%"
    pause
    exit /b
)
echo ✅ Docker is running.

:: --- Step 2: Show container statuses ---
echo -----------------------------------------------------
echo 🐳 Active Containers:
echo -----------------------------------------------------
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" >> "%LOG_FILE%"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

:: --- Step 3: Check individual container health ---
echo -----------------------------------------------------
echo 🩺 Checking individual container health...
for %%C in (train_booking_app train_db pgadmin) do (
    echo -----------------------------------------------------
    echo 🔍 %%C status:
    docker inspect -f "{{.State.Health.Status}}" %%C 2>nul
    docker inspect -f "{{.State.Health.Status}}" %%C >> "%LOG_FILE%" 2>&1
)

:: --- Step 4: Check FastAPI Health Endpoint ---
echo -----------------------------------------------------
echo 🌐 Checking FastAPI health endpoint...
curl -s http://localhost:8000/health | findstr /i "ok" >nul
if %errorlevel% neq 0 (
    echo ⚠️ FastAPI /health endpoint not responding.
    echo ⚠️ FastAPI not responding. >> "%LOG_FILE%"
) else (
    echo ✅ FastAPI /health endpoint is responding correctly!
    echo ✅ FastAPI health OK. >> "%LOG_FILE%"
)

:: --- Step 5: Check PostgreSQL connectivity ---
echo -----------------------------------------------------
echo 🧩 Checking PostgreSQL database connection...
docker exec -it train_db pg_isready -U admin -d train_db >> "%LOG_FILE%" 2>&1
docker exec -it train_db pg_isready -U admin -d train_db
if %errorlevel% neq 0 (
    echo ⚠️ Database connection check failed.
    echo ⚠️ DB connection failed. >> "%LOG_FILE%"
) else (
    echo ✅ PostgreSQL database is accepting connections!
    echo ✅ DB connection OK. >> "%LOG_FILE%"
)

:: --- Step 6: Display URLs ---
echo -----------------------------------------------------
echo 🌍 Access URLs:
echo   - FastAPI Docs:     http://localhost:8000/docs
echo   - pgAdmin Panel:    http://localhost:5050
echo   - PostgreSQL Port:  5432
echo -----------------------------------------------------

echo 🪵 Detailed log saved at: %LOG_FILE%
echo =====================================================
pause
