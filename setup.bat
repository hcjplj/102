@echo off
cd /d "%~dp0"

echo ===== Installing Required Python Packages =====

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo [ERROR] Python not found. When installing from https://www.python.org,
    echo         make sure to check "Add python.exe to PATH" and run this again.
    pause
    exit /b 1
)

%PY% -m pip install --upgrade pip
%PY% -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed. Please check the messages above.
    pause
    exit /b 1
)

echo.
echo Installation completed.
pause