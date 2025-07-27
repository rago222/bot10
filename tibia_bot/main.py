#!/usr/bin/env python3
"""
Tibia Bot - Bot de Automação para Tibia
Desenvolvido para uso em servidores de teste privados (OT Server)

Funcionalidades:
- Auto-Heal (Autocura)
- Auto-Mana
- Auto-Food (Auto Comida)
- Auto-Loot (Coleta Automática)
- Cavebot (Caça Automática)
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import threading
import logging
from pathlib import Path

# Adicionar o diretório do projeto ao Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

from gui.main_window import TibiaBotGUI
from core.bot_manager import BotManager
from utils.logger import setup_logger

def main():
    """Função principal do bot"""
    try:
        # Configurar logging
        logger = setup_logger()
        logger.info("Iniciando Tibia Bot...")
        
        # Verificar se está executando no Windows (recomendado)
        if os.name != 'nt':
            logger.warning("Bot desenvolvido para Windows. Alguns recursos podem não funcionar adequadamente.")
        
        # Criar janela principal
        root = tk.Tk()
        root.title("Tibia Bot - Automação Avançada")
        root.geometry("800x600")
        root.resizable(True, True)
        
        # Definir ícone da aplicação (se existir)
        try:
            icon_path = project_dir / "assets" / "icon.ico"
            if icon_path.exists():
                root.iconbitmap(str(icon_path))
        except Exception as e:
            logger.warning(f"Não foi possível carregar o ícone: {e}")
        
        # Inicializar gerenciador do bot
        bot_manager = BotManager()
        
        # Criar interface gráfica
        app = TibiaBotGUI(root, bot_manager)
        
        # Configurar fechamento da aplicação
        def on_closing():
            if messagebox.askokcancel("Sair", "Deseja realmente sair do Tibia Bot?"):
                logger.info("Fechando aplicação...")
                bot_manager.stop_all()
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Iniciar loop principal
        logger.info("Interface gráfica iniciada com sucesso!")
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Erro crítico ao iniciar o bot: {e}"
        print(error_msg)
        if 'logger' in locals():
            logger.error(error_msg, exc_info=True)
        messagebox.showerror("Erro Crítico", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()