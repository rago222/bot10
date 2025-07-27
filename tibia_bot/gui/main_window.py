"""
Main Window - Janela principal da interface gráfica
Interface intuitiva para configuração e controle do bot
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from typing import Optional
import logging

from gui.status_panel import StatusPanel
from gui.config_panel import ConfigPanel
from gui.cavebot_panel import CavebotPanel
from gui.hotkey_panel import HotkeyPanel

class TibiaBotGUI:
    """Interface gráfica principal do Tibia Bot"""
    
    def __init__(self, root: tk.Tk, bot_manager):
        self.root = root
        self.bot_manager = bot_manager
        self.logger = logging.getLogger(__name__)
        
        # Estados da interface
        self.is_bot_running = False
        self.update_thread = None
        self.stop_update = False
        
        # Configurar janela principal
        self.setup_main_window()
        
        # Criar menu
        self.create_menu()
        
        # Criar interface
        self.create_widgets()
        
        # Iniciar thread de atualização
        self.start_update_thread()
        
        self.logger.info("Interface gráfica inicializada")
    
    def setup_main_window(self):
        """Configura janela principal"""
        self.root.title("Tibia Bot - Automação Avançada v1.0")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores personalizadas
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
    
    def create_menu(self):
        """Cria barra de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Carregar Configuração...", command=self.load_config)
        file_menu.add_command(label="Salvar Configuração...", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exportar Configuração...", command=self.export_config)
        file_menu.add_command(label="Importar Configuração...", command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        
        # Menu Ferramentas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)
        tools_menu.add_command(label="Capturar Tela", command=self.capture_screen)
        tools_menu.add_command(label="Configurar ROIs", command=self.configure_rois)
        tools_menu.add_command(label="Testar Captura", command=self.test_capture)
        tools_menu.add_separator()
        tools_menu.add_command(label="Logs do Sistema", command=self.show_logs)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Manual do Usuário", command=self.show_manual)
        help_menu.add_command(label="Configuração Inicial", command=self.show_setup_guide)
        help_menu.add_separator()
        help_menu.add_command(label="Sobre", command=self.show_about)
    
    def create_widgets(self):
        """Cria widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Tibia Bot - Automação Avançada", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Painel de controle principal
        control_frame = ttk.LabelFrame(main_frame, text="Controle Principal", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Botões principais
        self.start_stop_btn = ttk.Button(control_frame, text="Iniciar Bot", 
                                        command=self.toggle_bot, width=15)
        self.start_stop_btn.grid(row=0, column=0, pady=5)
        
        self.emergency_stop_btn = ttk.Button(control_frame, text="Parada de Emergência", 
                                           command=self.emergency_stop, width=20)
        self.emergency_stop_btn.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # Status do bot
        self.status_label = ttk.Label(control_frame, text="Bot Parado", 
                                     style='Status.TLabel')
        self.status_label.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Módulos de funcionalidade
        modules_frame = ttk.LabelFrame(control_frame, text="Módulos", padding="10")
        modules_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Checkboxes dos módulos
        self.module_vars = {}
        modules = [
            ('auto_heal', 'Auto Heal'),
            ('auto_mana', 'Auto Mana'),
            ('auto_food', 'Auto Food'),
            ('auto_loot', 'Auto Loot'),
            ('cavebot', 'Cavebot')
        ]
        
        for i, (module_id, module_name) in enumerate(modules):
            var = tk.BooleanVar()
            self.module_vars[module_id] = var
            
            checkbox = ttk.Checkbutton(modules_frame, text=module_name, 
                                     variable=var, 
                                     command=lambda m=module_id: self.toggle_module(m))
            checkbox.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=2)
        
        # Notebook para painéis
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Criar painéis
        self.create_panels()
    
    def create_panels(self):
        """Cria painéis do notebook"""
        # Painel de Status
        self.status_panel = StatusPanel(self.notebook, self.bot_manager)
        self.notebook.add(self.status_panel.frame, text="Status")
        
        # Painel de Configuração
        self.config_panel = ConfigPanel(self.notebook, self.bot_manager)
        self.notebook.add(self.config_panel.frame, text="Configurações")
        
        # Painel do Cavebot
        self.cavebot_panel = CavebotPanel(self.notebook, self.bot_manager)
        self.notebook.add(self.cavebot_panel.frame, text="Cavebot")
        
        # Painel de Hotkeys
        self.hotkey_panel = HotkeyPanel(self.notebook, self.bot_manager)
        self.notebook.add(self.hotkey_panel.frame, text="Hotkeys")
    
    def toggle_bot(self):
        """Inicia ou para o bot"""
        try:
            if self.is_bot_running:
                # Parar bot
                self.bot_manager.stop_bot()
                self.is_bot_running = False
                self.start_stop_btn.config(text="Iniciar Bot")
                self.status_label.config(text="Bot Parado", style='Status.TLabel')
                self.logger.info("Bot parado pelo usuário")
            else:
                # Iniciar bot
                self.bot_manager.start_bot()
                self.is_bot_running = True
                self.start_stop_btn.config(text="Parar Bot")
                self.status_label.config(text="Bot Executando", style='Success.TLabel')
                self.logger.info("Bot iniciado pelo usuário")
                
        except Exception as e:
            error_msg = f"Erro ao controlar bot: {e}"
            self.logger.error(error_msg)
            messagebox.showerror("Erro", error_msg)
    
    def emergency_stop(self):
        """Parada de emergência"""
        try:
            self.bot_manager.stop_all()
            self.is_bot_running = False
            self.start_stop_btn.config(text="Iniciar Bot")
            self.status_label.config(text="PARADA DE EMERGÊNCIA", style='Error.TLabel')
            
            # Desmarcar todos os módulos
            for var in self.module_vars.values():
                var.set(False)
            
            self.logger.warning("Parada de emergência acionada")
            messagebox.showwarning("Parada de Emergência", 
                                 "Bot parado em emergência! Todos os módulos foram desabilitados.")
            
        except Exception as e:
            self.logger.error(f"Erro na parada de emergência: {e}")
    
    def toggle_module(self, module_name: str):
        """Ativa/desativa um módulo"""
        try:
            enabled = self.module_vars[module_name].get()
            self.bot_manager.toggle_module(module_name, enabled)
            
            status = "ativado" if enabled else "desativado"
            self.logger.info(f"Módulo {module_name} {status}")
            
        except Exception as e:
            self.logger.error(f"Erro ao alternar módulo {module_name}: {e}")
    
    def start_update_thread(self):
        """Inicia thread de atualização da interface"""
        self.stop_update = False
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
    
    def update_loop(self):
        """Loop de atualização da interface"""
        while not self.stop_update:
            try:
                # Atualizar status do bot
                self.update_bot_status()
                
                # Atualizar painéis
                if hasattr(self, 'status_panel'):
                    self.status_panel.update_status()
                
                # Dormir por um tempo
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Erro no loop de atualização: {e}")
                time.sleep(1)
    
    def update_bot_status(self):
        """Atualiza status do bot na interface"""
        try:
            bot_status = self.bot_manager.get_status()
            
            # Atualizar estado dos módulos
            for module_name, var in self.module_vars.items():
                if hasattr(bot_status, f'{module_name}_enabled'):
                    enabled = getattr(bot_status, f'{module_name}_enabled')
                    if var.get() != enabled:
                        var.set(enabled)
            
            # Atualizar status geral
            if bot_status.running != self.is_bot_running:
                self.is_bot_running = bot_status.running
                if self.is_bot_running:
                    self.start_stop_btn.config(text="Parar Bot")
                    self.status_label.config(text="Bot Executando", style='Success.TLabel')
                else:
                    self.start_stop_btn.config(text="Iniciar Bot")
                    self.status_label.config(text="Bot Parado", style='Status.TLabel')
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar status do bot: {e}")
    
    # Métodos do menu
    def load_config(self):
        """Carrega configuração de arquivo"""
        try:
            filename = filedialog.askopenfilename(
                title="Carregar Configuração",
                filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
            )
            
            if filename:
                if self.bot_manager.config.import_config(filename):
                    messagebox.showinfo("Sucesso", "Configuração carregada com sucesso!")
                    self.refresh_all_panels()
                else:
                    messagebox.showerror("Erro", "Erro ao carregar configuração!")
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar configuração: {e}")
    
    def save_config(self):
        """Salva configuração atual"""
        try:
            if self.bot_manager.config.save_config():
                messagebox.showinfo("Sucesso", "Configuração salva com sucesso!")
            else:
                messagebox.showerror("Erro", "Erro ao salvar configuração!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configuração: {e}")
    
    def export_config(self):
        """Exporta configuração para arquivo"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Exportar Configuração",
                defaultextension=".json",
                filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
            )
            
            if filename:
                if self.bot_manager.config.export_config(filename):
                    messagebox.showinfo("Sucesso", "Configuração exportada com sucesso!")
                else:
                    messagebox.showerror("Erro", "Erro ao exportar configuração!")
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar configuração: {e}")
    
    def import_config(self):
        """Importa configuração de arquivo"""
        self.load_config()  # Mesmo processo
    
    def capture_screen(self):
        """Captura tela para debug"""
        try:
            filename = self.bot_manager.screen_capture.save_screenshot()
            if filename:
                messagebox.showinfo("Sucesso", f"Screenshot salvo: {filename}")
            else:
                messagebox.showerror("Erro", "Erro ao capturar tela!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao capturar tela: {e}")
    
    def configure_rois(self):
        """Abre ferramenta de configuração de ROIs"""
        try:
            # Implementar ferramenta de ROI (pode ser uma janela separada)
            messagebox.showinfo("Em Desenvolvimento", 
                              "Ferramenta de configuração de ROIs será implementada em breve!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir configuração de ROIs: {e}")
    
    def test_capture(self):
        """Testa captura de tela"""
        try:
            if self.bot_manager.screen_capture.test_capture():
                messagebox.showinfo("Sucesso", "Teste de captura: OK")
            else:
                messagebox.showerror("Erro", "Teste de captura: FALHA")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro no teste de captura: {e}")
    
    def show_logs(self):
        """Mostra logs do sistema"""
        try:
            # Implementar visualizador de logs
            messagebox.showinfo("Em Desenvolvimento", 
                              "Visualizador de logs será implementado em breve!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao mostrar logs: {e}")
    
    def show_manual(self):
        """Mostra manual do usuário"""
        manual_text = """
        TIBIA BOT - MANUAL DO USUÁRIO
        
        1. CONFIGURAÇÃO INICIAL:
           - Configure o OBS Studio para capturar a janela do Tibia
           - Defina as ROIs (Regiões de Interesse) para vida, mana, etc.
           - Configure as hotkeys para poções e magias
        
        2. MÓDULOS DISPONÍVEIS:
           - Auto Heal: Cura automática baseada no percentual de vida
           - Auto Mana: Restauração automática de mana
           - Auto Food: Consumo automático de comida
           - Auto Loot: Coleta automática de itens
           - Cavebot: Navegação e caça automática
        
        3. USO BÁSICO:
           - Ative os módulos desejados
           - Clique em "Iniciar Bot"
           - Use "Parada de Emergência" se necessário
        
        4. CONFIGURAÇÕES AVANÇADAS:
           - Ajuste thresholds de vida/mana
           - Configure listas de loot
           - Crie scripts de cavebot
        
        Para mais detalhes, consulte a documentação completa.
        """
        
        # Criar janela de manual
        manual_window = tk.Toplevel(self.root)
        manual_window.title("Manual do Usuário")
        manual_window.geometry("600x500")
        
        text_widget = tk.Text(manual_window, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(manual_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.insert(tk.END, manual_text)
        text_widget.config(state=tk.DISABLED)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def show_setup_guide(self):
        """Mostra guia de configuração inicial"""
        setup_text = """
        GUIA DE CONFIGURAÇÃO INICIAL
        
        PASSO 1: CONFIGURAR OBS STUDIO
        1. Baixe e instale o OBS Studio
        2. Crie uma nova cena
        3. Adicione fonte "Captura de Janela"
        4. Selecione a janela do Tibia
        5. Mantenha a janela de preview aberta
        
        PASSO 2: CONFIGURAR CLIENTE TIBIA
        1. Defina resolução recomendada: 1024x768
        2. Configure hotkeys:
           - F1: Poção de vida
           - F2: Poção de vida forte (emergência)
           - F3: Poção de mana
           - F4: Poção de mana forte (emergência)
           - F7: Comida
        3. Abra todos os painéis necessários (vida, mana, inventário)
        
        PASSO 3: CONFIGURAR BOT
        1. Teste a captura de tela
        2. Configure ROIs para vida e mana
        3. Ajuste thresholds conforme sua necessidade
        4. Teste cada módulo individualmente
        
        PASSO 4: PRIMEIRO USO
        1. Inicie com apenas Auto Heal ativo
        2. Observe o comportamento por alguns minutos
        3. Ative outros módulos gradualmente
        4. Crie scripts de cavebot conforme necessário
        
        DICAS IMPORTANTES:
        - Sempre teste em ambiente seguro primeiro
        - Monitore o bot periodicamente
        - Use a parada de emergência quando necessário
        - Mantenha backups de suas configurações
        """
        
        # Criar janela de setup
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Guia de Configuração Inicial")
        setup_window.geometry("700x600")
        
        text_widget = tk.Text(setup_window, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(setup_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.insert(tk.END, setup_text)
        text_widget.config(state=tk.DISABLED)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def show_about(self):
        """Mostra informações sobre o bot"""
        about_text = """
        Tibia Bot - Automação Avançada v1.0
        
        Desenvolvido para uso em servidores de teste privados (OT Server)
        
        Funcionalidades:
        • Auto Heal/Mana com detecção inteligente
        • Auto Food baseado em status visual
        • Auto Loot otimizado com filtragem
        • Cavebot com navegação por waypoints
        • Sistema anti-detecção com randomização
        
        Tecnologias utilizadas:
        • Python 3.11+
        • OpenCV para visão computacional
        • PyAutoGUI para simulação de input
        • Tkinter para interface gráfica
        
        Características de segurança:
        • Simulação humanizada de input
        • Randomização de timing e trajetórias
        • Contorno de proteções anti-cheat
        • Sistema de failsafe integrado
        
        Desenvolvido com foco em:
        ✓ Facilidade de uso
        ✓ Interface intuitiva
        ✓ Configuração flexível
        ✓ Detecção robusta
        ✓ Performance otimizada
        
        Para suporte técnico e atualizações,
        consulte a documentação oficial.
        """
        
        messagebox.showinfo("Sobre o Tibia Bot", about_text)
    
    def refresh_all_panels(self):
        """Atualiza todos os painéis"""
        try:
            if hasattr(self, 'config_panel'):
                self.config_panel.refresh()
            if hasattr(self, 'cavebot_panel'):
                self.cavebot_panel.refresh()
            if hasattr(self, 'hotkey_panel'):
                self.hotkey_panel.refresh()
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar painéis: {e}")
    
    def cleanup(self):
        """Limpeza ao fechar a aplicação"""
        self.stop_update = True
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)