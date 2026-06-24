@echo off
:: MED.MIX OS - Quick Start Script
:: ---------------------------------
echo.
echo ======================================
echo    MED.MIX OS - تشغيل المشروع
echo ======================================
echo.

:: Check Docker
docker ps >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [1/4] تشغيل Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo ننتظر Docker...
    :wait_docker
    timeout /t 3 /nobreak >nul
    docker ps >nul 2>&1
    if %ERRORLEVEL% NEQ 0 goto wait_docker
    echo Docker جاهز
) else (
    echo [1/4] Docker شغال ✅
)

:: Clean any old containers from other projects
echo [2/4] تنظيف حاويات مشاريع أخرى...
docker rm -f docker-postgres-1 docker-redis-1 docker-minio-1 docker-backend-1 docker-frontend-1 2>nul
docker rm -f $(docker ps -aq --filter "name=supabase") 2>nul
docker rm -f $(docker ps -aq --filter "name=ooai") 2>nul

:: Start MED MIX containers
echo [3/4] تشغيل MED MIX...
cd /d "%~dp0infrastructure\docker"
docker compose -p medmix up -d
echo.

:: Wait for backend
echo [4/4] انتظار الباكند...
:wait_backend
timeout /t 3 /nobreak >nul
curl -s http://localhost:8000/api/health >nul 2>&1
if %ERRORLEVEL% NEQ 0 goto wait_backend

echo.
echo ===================================================================
echo    ✅ MED.MIX OS شغال بالكامل! ✅
echo ===================================================================
echo.
echo    الواجهة:  http://localhost:3000
echo    API:      http://localhost:8000/api
echo    Swagger:  http://localhost:8000/docs
echo.
echo    دخول:    admin@medmix.com / admin123
echo    Vercel:  https://frontend-steel-three-58.vercel.app
echo.
echo    ملاحظة: فقط حاويات MED MIX شغالة (medmix-*)
echo    لا يوجد أي تداخل مع مشاريع أخرى
echo.
echo ===================================================================
pause
