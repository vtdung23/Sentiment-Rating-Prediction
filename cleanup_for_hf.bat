@echo off
REM ============================================
REM Cleanup Script for Hugging Face Deployment
REM Removes unnecessary files before pushing to HF Space
REM ============================================

echo ========================================
echo Hugging Face Deployment Cleanup
echo ========================================
echo.

REM Create backup directory
if not exist "backup" mkdir backup
echo [INFO] Created backup directory

REM Backup important files
echo [INFO] Creating backups...
if exist ".env" copy ".env" "backup\.env" > nul
if exist "app\database\*.db" copy "app\database\*.db" "backup\" > nul

REM Remove Python cache
echo [INFO] Removing Python cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul

REM Remove virtual environments
echo [INFO] Removing virtual environments...
if exist "env" rd /s /q "env"
if exist "venv" rd /s /q "venv"
if exist ".venv" rd /s /q ".venv"

REM Remove local database files
echo [INFO] Removing local database files...
if exist "app\database\*.db" del /q "app\database\*.db"
if exist "app\database\*.sqlite" del /q "app\database\*.sqlite"
if exist "app\database\*.sqlite3" del /q "app\database\*.sqlite3"

REM Remove upload files
echo [INFO] Cleaning upload directories...
if exist "app\static\uploads\wordclouds\*.*" del /q "app\static\uploads\wordclouds\*.*"
if exist "app\static\uploads\*.csv" del /q "app\static\uploads\*.csv"

REM Remove IDE files
echo [INFO] Removing IDE files...
if exist ".vscode" rd /s /q ".vscode"
if exist ".idea" rd /s /q ".idea"

REM Remove logs
echo [INFO] Removing log files...
del /s /q *.log 2>nul

REM Remove .env files (secrets should be in HF Settings)
echo [WARNING] Removing .env file (use HF Secrets instead)
if exist ".env" del /q ".env"
if exist ".env.local" del /q ".env.local"

REM List files to be deployed
echo.
echo ========================================
echo Files ready for deployment:
echo ========================================
echo.
echo [CRITICAL FILES]
dir /b Dockerfile 2>nul && echo   - Dockerfile [OK] || echo   - Dockerfile [MISSING - ERROR!]
dir /b requirements.txt 2>nul && echo   - requirements.txt [OK] || echo   - requirements.txt [MISSING - ERROR!]
dir /b main.py 2>nul && echo   - main.py [OK] || echo   - main.py [MISSING - ERROR!]
dir /b .dockerignore 2>nul && echo   - .dockerignore [OK] || echo   - .dockerignore [OPTIONAL]
echo.

echo [DOCUMENTATION]
dir /b README_HF_SPACE.md 2>nul && echo   - README_HF_SPACE.md [OK] || echo   - README_HF_SPACE.md [MISSING]
dir /b HUGGING_FACE_DEPLOYMENT.md 2>nul && echo   - HUGGING_FACE_DEPLOYMENT.md [OK]
dir /b HF_ENV_VARIABLES.md 2>nul && echo   - HF_ENV_VARIABLES.md [OK]
echo.

echo [APPLICATION CODE]
if exist "app" (
    echo   - app/ directory [OK]
    dir /b app\*.py 2>nul | find /c /v "" > nul && echo   - Python files found [OK]
) else (
    echo   - app/ directory [MISSING - ERROR!]
)
echo.

echo ========================================
echo Cleanup Complete!
echo ========================================
echo.
echo NEXT STEPS:
echo 1. Rename README_HF_SPACE.md to README.md
echo 2. Test Docker build locally: docker build -t test .
echo 3. Push to Hugging Face Space repository
echo.
echo BACKUPS:
echo   Saved in ./backup/ directory
echo.
pause
