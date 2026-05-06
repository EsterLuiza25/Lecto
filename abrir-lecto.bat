@echo off
setlocal

cd /d "%~dp0"
title Lecto - servidor local

set "PYTHON_EXE=python"
if defined VIRTUAL_ENV set "PYTHON_EXE=%VIRTUAL_ENV%\Scripts\python.exe"
if not defined VIRTUAL_ENV if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" if exist "C:\Python312\python.exe" set "PYTHON_EXE=C:\Python312\python.exe"

echo.
echo ==========================================
echo   Lecto - servidor local
echo ==========================================
echo.
echo Pasta: %CD%
echo URL: http://127.0.0.1:8000/
echo Python: %PYTHON_EXE%
echo.
echo Quando aparecer "Watching for file changes" ou "Starting development server", abra:
echo http://127.0.0.1:8000/
echo.
echo Mantenha esta janela aberta. Se ela fechar, o site sai do ar.
echo.

"%PYTHON_EXE%" manage.py check
if errorlevel 1 (
    echo.
    echo O Django encontrou um erro. Veja a mensagem acima.
    pause
    exit /b 1
)

echo.
echo Aplicando migrations pendentes...
"%PYTHON_EXE%" manage.py migrate --noinput
if errorlevel 1 (
    echo.
    echo Nao foi possivel atualizar o banco de dados. Veja a mensagem acima.
    pause
    exit /b 1
)

echo.
echo Iniciando Django...
echo Abrindo o navegador automaticamente...
start "" cmd /c "timeout /t 3 /nobreak >nul & start "" http://127.0.0.1:8000/"
"%PYTHON_EXE%" -u manage.py runserver 127.0.0.1:8000

echo.
echo O servidor foi encerrado.
pause
