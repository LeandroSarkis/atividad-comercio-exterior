@echo off
REM ─────────────────────────────────────────────────────────────────────────
REM  rodar_app.bat  –  Instala dependências e abre o App Comex (Windows)
REM  Duplo-clique neste arquivo para executar.
REM ─────────────────────────────────────────────────────────────────────────

echo ==========================================
echo   App Comex – Iniciando...
echo ==========================================

where python >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERRO] Python nao encontrado. Instale em https://www.python.org
    pause
    exit /b 1
)

pip install flet numpy --quiet
python main.py
pause
