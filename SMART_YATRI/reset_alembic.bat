@echo off
title 🔄 Reset Alembic & Rebuild Docker (Windows)
color 0A

echo ============================================
echo 🚀 FASTAPI + POSTGRES + ALEMBIC RESET SCRIPT
echo ============================================

echo.
echo 🔻 Stopping and removing all containers and volumes...
docker compose down -v

echo.
echo 🧹 Cleaning old Alembic migration files...
if exist Alembic\versions (
    rmdir /s /q Alembic\versions
)
mkdir Alembic\versions
echo ✅ Old migrations removed.

echo.
echo 🐳 Rebuilding Docker containers (no cache)...
docker compose build --no-cache
docker compose up -d

echo.
echo ⏳ Waiting 25 seconds for database to initialize...
timeout /t 25 /nobreak >nul

echo.
echo 🚪 Running Alembic migrations inside backend container...
docker exec -i train_booking_app bash -c "alembic revision --autogenerate -m 'initial db setup' && alembic upgrade head"

echo.
echo 🔍 Checking container health status...
set healthyCount=0
for /f "tokens=1,2" %%A in ('docker ps --format "{{.Names}} {{.Status}}"') do (
    echo %%A - %%B
    echo %%B | find /I "healthy" >nul
    if not errorlevel 1 (
        set /a healthyCount+=1
    )
)

echo.
if %healthyCount% GEQ 2 (
    color 0A
    echo ✅ SUCCESS: All containers are up and healthy!
    echo 🌐 Opening pgAdmin and FastAPI docs in browser...
    start http://localhost:5050
    start http://localhost:8000/docs
) else (
    color 0C
    echo ❌ WARNING: One or more containers are not healthy.
    echo 🩺 Please check logs with:
    echo     docker ps
    echo     docker logs train_booking_app --tail 50
)

echo.
echo ============================================
echo 🎉 RESET COMPLETE! SYSTEM IS READY.
echo ============================================

pause
