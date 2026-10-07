@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ===== 필요한 파이썬 패키지 설치 =====

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo [오류] 파이썬을 찾을 수 없습니다. https://www.python.org 에서 설치할 때
    echo        "Add python.exe to PATH" 를 체크한 뒤 다시 실행하세요.
    pause
    exit /b 1
)

%PY% -m pip install --upgrade pip
%PY% -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [오류] 설치에 실패했습니다. 위 메시지를 확인하세요.
    pause
    exit /b 1
)

echo.
echo 설치가 끝났습니다.
pause
