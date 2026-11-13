@echo off
cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
    echo uv nao foi encontrado. Instale-o seguindo:
    echo https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

uv run main.py
if errorlevel 1 pause
