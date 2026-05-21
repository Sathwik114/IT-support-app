@echo off
REM Deployment script for Windows LAN deployment
REM This script sets up and runs the Django application with Daphne

echo ========================================
echo LAN Chat System - Deployment Script
echo ========================================

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
if not exist "media" mkdir media
if not exist "staticfiles" mkdir staticfiles
if not exist "logs" mkdir logs

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput

REM Run migrations
echo Running migrations...
python manage.py migrate

REM Create superuser if needed (optional)
REM python manage.py createsuperuser

REM Start Redis (if not running)
echo Checking Redis...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Redis server...
    start redis-server
    timeout /t 3 /nobreak >nul
)

REM Start Celery worker (in background)
echo Starting Celery worker...
start /B celery -A chat_system worker -l info --logfile=logs\celery.log

REM Start the application with Daphne
echo Starting application with Daphne...
echo Server will be available at: http://0.0.0.0:8000
echo Press Ctrl+C to stop

daphne -b 0.0.0.0 -p 8000 chat_system.asgi:application

pause
