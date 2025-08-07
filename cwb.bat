@echo off
REM CWB Hub Hybrid AI System - Windows Batch Script
REM Criado por: David Simer

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale Python 3.8+ primeiro.
    echo 💡 Download: https://python.org/downloads/
    pause
    exit /b 1
)

REM Verificar se o arquivo CLI existe
if not exist "cwb_cli.py" (
    echo ❌ Arquivo cwb_cli.py não encontrado.
    echo 💡 Execute este script no diretório do CWB Hub.
    pause
    exit /b 1
)

REM Executar CLI com todos os argumentos passados
python cwb_cli.py %*

REM Pausar apenas se executado diretamente (não via linha de comando)
if "%1"=="" (
    echo.
    echo 💡 Para usar sem pausas, execute: cwb.bat [comando] [argumentos]
    echo 📖 Para ajuda: cwb.bat --help
    pause
)