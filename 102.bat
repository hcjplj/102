@echo off
chcp 65001 >nul
cd /d "%~dp0"
where pythonw >nul 2>nul && (start "" pythonw main.py & exit /b)
where pyw >nul 2>nul && (start "" pyw -3 main.py & exit /b)
echo [오류] 파이썬을 찾을 수 없습니다. 먼저 setup.bat 을 실행하거나 파이썬을 설치하세요.
pause
