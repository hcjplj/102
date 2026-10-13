@echo off
cd /d "%~dp0"
where pythonw >nul 2>nul && (start "" pythonw main.py & exit /b)
where pyw >nul 2>nul && (start "" pyw -3 main.py & exit /b)
echo [ERROR] Python not found. Please run setup.bat first or install Python.
pause