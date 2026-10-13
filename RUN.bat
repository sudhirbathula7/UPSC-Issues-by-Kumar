
@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo             UPSC ANCHOR BY KUMAR
echo               PRODUCTION PIPELINE
echo ========================================================
echo.

if exist ".venv\Scripts\python.exe" (
    set "PYTHON=.venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)

echo Starting production pipeline...
echo.

"%PYTHON%" -u "run.py"

if errorlevel 1 (
    echo.
    echo ========================================================
    echo              PRODUCTION FAILED
    echo ========================================================
    pause
    exit /b 1
)

echo.
echo ========================================================
echo           PRODUCTION COMPLETED SUCCESSFULLY
echo ========================================================
pause
exit /b 0
