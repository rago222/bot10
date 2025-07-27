@echo off
title Tibia Bot - Iniciador
color 0A

echo.
echo ========================================
echo          TIBIA BOT v1.0
echo    Automacao Avancada para Tibia
echo ========================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python nao encontrado!
    echo.
    echo Por favor, instale Python 3.11+ primeiro:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Marque "Add Python to PATH" na instalacao
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado!
echo.

echo Verificando dependencias...
pip show opencv-python >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Dependencias nao instaladas.
    echo Instalando automaticamente...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Erro ao instalar dependencias!
        echo.
        echo Tente executar manualmente:
        echo pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo ✅ Dependencias OK!
echo.

echo Verificando estrutura de arquivos...
if not exist "config" (
    echo ⚠️  Criando pasta config...
    mkdir config
)
if not exist "logs" (
    echo ⚠️  Criando pasta logs...
    mkdir logs
)
if not exist "scripts" (
    echo ⚠️  Criando pasta scripts...
    mkdir scripts
)
if not exist "assets" (
    echo ⚠️  Criando pasta assets...
    mkdir assets
    mkdir assets\templates
)

echo ✅ Estrutura de arquivos OK!
echo.

echo 🚀 Iniciando Tibia Bot...
echo.
echo ⚠️  LEMBRETE IMPORTANTE:
echo    - Certifique-se que o OBS Studio esta aberto
echo    - Configure a captura da janela do Tibia
echo    - Use apenas em servidores OT permitidos
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ❌ O bot foi fechado com erro!
    echo Verifique os logs na pasta 'logs' para mais detalhes.
    echo.
    pause
)

echo.
echo 👋 Bot finalizado. Ate logo!
pause