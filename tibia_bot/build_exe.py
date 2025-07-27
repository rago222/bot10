"""
Script para criar executável do Tibia Bot usando PyInstaller
Execute este script para gerar um arquivo .exe standalone
"""

import subprocess
import sys
import os
from pathlib import Path

def install_pyinstaller():
    """Instala PyInstaller se não estiver instalado"""
    try:
        import PyInstaller
        print("PyInstaller já está instalado")
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_executable():
    """Constrói o executável"""
    print("Construindo executável do Tibia Bot...")
    
    # Comandos do PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",                    # Arquivo único
        "--windowed",                   # Sem console (GUI)
        "--name=TibiaBot",              # Nome do executável
        "--icon=assets/icon.ico",       # Ícone (se existir)
        "--add-data=config;config",     # Incluir pasta config
        "--add-data=assets;assets",     # Incluir pasta assets
        "--add-data=scripts;scripts",   # Incluir pasta scripts
        "--hidden-import=cv2",          # Imports ocultos
        "--hidden-import=numpy",
        "--hidden-import=PIL",
        "--hidden-import=pyautogui",
        "--hidden-import=mss",
        "--hidden-import=tkinter",
        "main.py"                       # Arquivo principal
    ]
    
    try:
        # Verificar se arquivo icon existe
        if not Path("assets/icon.ico").exists():
            # Remover parâmetro do ícone se não existir
            cmd = [c for c in cmd if not c.startswith("--icon=")]
        
        subprocess.run(cmd, check=True)
        print("\n✅ Executável criado com sucesso!")
        print("📁 Localização: dist/TibiaBot.exe")
        print("\n📋 Para distribuir:")
        print("1. Copie o arquivo TibiaBot.exe da pasta 'dist'")
        print("2. Copie as pastas 'config', 'assets' e 'scripts'")
        print("3. Inclua o manual MANUAL_INSTALACAO.md")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar executável: {e}")
        return False
    
    return True

def create_installer():
    """Cria script de instalação simples"""
    installer_content = '''@echo off
echo =================================
echo    TIBIA BOT - INSTALADOR
echo =================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo Por favor, instale Python 3.11+ primeiro
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python encontrado!
echo.

echo Instalando dependências...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Erro ao instalar dependências
    pause
    exit /b 1
)

echo ✅ Instalação concluída!
echo.
echo Para executar o bot, use:
echo python main.py
echo.
pause
'''
    
    with open("instalar.bat", "w", encoding="utf-8") as f:
        f.write(installer_content)
    
    print("✅ Arquivo 'instalar.bat' criado!")

def main():
    """Função principal"""
    print("🤖 TIBIA BOT - CONSTRUTOR DE EXECUTÁVEL")
    print("=" * 50)
    
    opcao = input("\nEscolha uma opção:\n"
                  "1. Criar executável (.exe)\n"
                  "2. Criar instalador (.bat)\n"
                  "3. Ambos\n"
                  "Opção (1-3): ")
    
    if opcao in ["1", "3"]:
        install_pyinstaller()
        if not build_executable():
            return
    
    if opcao in ["2", "3"]:
        create_installer()
    
    print("\n🎉 Processo concluído!")
    print("\n📋 Próximos passos:")
    print("1. Teste o executável antes de distribuir")
    print("2. Inclua todos os arquivos necessários")
    print("3. Teste em outro computador")

if __name__ == "__main__":
    main()