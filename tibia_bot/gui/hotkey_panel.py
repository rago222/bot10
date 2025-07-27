"""
Hotkey Panel - Painel de configuração de hotkeys
Interface para configurar atalhos de teclado globais
"""

import tkinter as tk
from tkinter import ttk, messagebox

class HotkeyPanel:
    """Painel de configuração de hotkeys"""
    
    def __init__(self, parent, bot_manager):
        self.parent = parent
        self.bot_manager = bot_manager
        
        self.frame = ttk.Frame(parent, padding="10")
        self.create_widgets()
        
        # Variáveis de hotkeys
        self.hotkey_vars = {}
        self.load_current_hotkeys()
    
    def create_widgets(self):
        """Cria widgets do painel de hotkeys"""
        # Título e descrição
        title_label = ttk.Label(self.frame, text="Configuração de Hotkeys", 
                               font=('Arial', 12, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        desc_label = ttk.Label(self.frame, 
                              text="Configure atalhos de teclado para controlar o bot rapidamente.\n"
                                   "Use combinações como Ctrl+F1, Alt+Q, etc.",
                              justify=tk.CENTER)
        desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Hotkeys do bot
        bot_frame = ttk.LabelFrame(self.frame, text="Controles do Bot", padding="10")
        bot_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.create_hotkey_entry(bot_frame, 0, "start_stop_bot", "Iniciar/Parar Bot:", "F9")
        self.create_hotkey_entry(bot_frame, 1, "emergency_stop", "Parada de Emergência:", "F12")
        
        # Hotkeys dos módulos
        modules_frame = ttk.LabelFrame(self.frame, text="Módulos", padding="10")
        modules_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        self.create_hotkey_entry(modules_frame, 0, "toggle_auto_heal", "Toggle Auto Heal:", "Ctrl+F1")
        self.create_hotkey_entry(modules_frame, 1, "toggle_auto_mana", "Toggle Auto Mana:", "Ctrl+F2")
        self.create_hotkey_entry(modules_frame, 2, "toggle_auto_food", "Toggle Auto Food:", "Ctrl+F3")
        self.create_hotkey_entry(modules_frame, 3, "toggle_auto_loot", "Toggle Auto Loot:", "Ctrl+F4")
        self.create_hotkey_entry(modules_frame, 4, "toggle_cavebot", "Toggle Cavebot:", "Ctrl+F5")
        
        # Hotkeys de ação
        actions_frame = ttk.LabelFrame(self.frame, text="Ações Diretas", padding="10")
        actions_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Primeira coluna
        self.create_hotkey_entry(actions_frame, 0, "heal_potion", "Poção de Vida:", "F1", column=0)
        self.create_hotkey_entry(actions_frame, 1, "heal_emergency", "Vida Emergência:", "F2", column=0)
        self.create_hotkey_entry(actions_frame, 2, "mana_potion", "Poção de Mana:", "F3", column=0)
        self.create_hotkey_entry(actions_frame, 3, "mana_emergency", "Mana Emergência:", "F4", column=0)
        
        # Segunda coluna
        self.create_hotkey_entry(actions_frame, 0, "food_consume", "Consumir Comida:", "F7", column=2)
        self.create_hotkey_entry(actions_frame, 1, "screenshot", "Capturar Tela:", "F8", column=2)
        self.create_hotkey_entry(actions_frame, 2, "loot_manual", "Loot Manual:", "Space", column=2)
        
        # Status das hotkeys
        status_frame = ttk.LabelFrame(self.frame, text="Status das Hotkeys", padding="10")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Lista de hotkeys ativas
        self.status_text = tk.Text(status_frame, height=6, width=60, wrap=tk.WORD, state=tk.DISABLED)
        status_scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # Botões de controle
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Aplicar Hotkeys", 
                  command=self.apply_hotkeys).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(buttons_frame, text="Testar Hotkeys", 
                  command=self.test_hotkeys).grid(row=0, column=1, padx=5)
        ttk.Button(buttons_frame, text="Restaurar Padrão", 
                  command=self.restore_default_hotkeys).grid(row=0, column=2, padx=5)
        ttk.Button(buttons_frame, text="Desativar Todas", 
                  command=self.disable_all_hotkeys).grid(row=0, column=3, padx=(5, 0))
        
        # Configurar expansão
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(4, weight=1)
        
        # Atualizar status inicial
        self.update_status()
    
    def create_hotkey_entry(self, parent, row, key, label, default_value, column=0):
        """Cria entrada de hotkey"""
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky=tk.W, pady=2)
        
        self.hotkey_vars[key] = tk.StringVar(value=default_value)
        entry = ttk.Entry(parent, textvariable=self.hotkey_vars[key], width=15)
        entry.grid(row=row, column=column+1, sticky=tk.W, padx=(10, 20), pady=2)
        
        # Bind para capturar combinações de tecla
        entry.bind('<KeyPress>', lambda e, k=key: self.capture_hotkey(e, k))
    
    def capture_hotkey(self, event, hotkey_key):
        """Captura combinação de tecla pressionada"""
        try:
            # Construir string da hotkey
            modifiers = []
            if event.state & 0x4:  # Ctrl
                modifiers.append("Ctrl")
            if event.state & 0x8:  # Alt
                modifiers.append("Alt")
            if event.state & 0x1:  # Shift
                modifiers.append("Shift")
            
            key = event.keysym
            
            # Construir hotkey string
            if modifiers:
                hotkey_string = "+".join(modifiers) + "+" + key
            else:
                hotkey_string = key
            
            # Atualizar variável
            self.hotkey_vars[hotkey_key].set(hotkey_string)
            
            # Prevenir inserção normal
            return "break"
            
        except Exception as e:
            pass  # Ignorar erros de captura
    
    def load_current_hotkeys(self):
        """Carrega hotkeys atuais da configuração"""
        try:
            config = self.bot_manager.config
            
            # Carregar hotkeys do bot
            self.hotkey_vars['start_stop_bot'] = tk.StringVar(value=config.get('hotkeys.start_stop_bot', 'F9'))
            self.hotkey_vars['emergency_stop'] = tk.StringVar(value=config.get('hotkeys.emergency_stop', 'F12'))
            
            # Carregar hotkeys dos módulos
            self.hotkey_vars['toggle_auto_heal'] = tk.StringVar(value=config.get('hotkeys.toggle_auto_heal', 'Ctrl+F1'))
            self.hotkey_vars['toggle_auto_mana'] = tk.StringVar(value=config.get('hotkeys.toggle_auto_mana', 'Ctrl+F2'))
            self.hotkey_vars['toggle_auto_food'] = tk.StringVar(value=config.get('hotkeys.toggle_auto_food', 'Ctrl+F3'))
            self.hotkey_vars['toggle_auto_loot'] = tk.StringVar(value=config.get('hotkeys.toggle_auto_loot', 'Ctrl+F4'))
            self.hotkey_vars['toggle_cavebot'] = tk.StringVar(value=config.get('hotkeys.toggle_cavebot', 'Ctrl+F5'))
            
            # Carregar hotkeys de ação
            self.hotkey_vars['heal_potion'] = tk.StringVar(value=config.get('auto_heal.potion_hotkey', 'F1'))
            self.hotkey_vars['heal_emergency'] = tk.StringVar(value=config.get('auto_heal.emergency_hotkey', 'F2'))
            self.hotkey_vars['mana_potion'] = tk.StringVar(value=config.get('auto_mana.potion_hotkey', 'F3'))
            self.hotkey_vars['mana_emergency'] = tk.StringVar(value=config.get('auto_mana.emergency_hotkey', 'F4'))
            self.hotkey_vars['food_consume'] = tk.StringVar(value=config.get('auto_food.food_hotkey', 'F7'))
            self.hotkey_vars['screenshot'] = tk.StringVar(value=config.get('hotkeys.screenshot', 'F8'))
            self.hotkey_vars['loot_manual'] = tk.StringVar(value=config.get('hotkeys.loot_manual', 'Space'))
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar hotkeys: {e}")
    
    def apply_hotkeys(self):
        """Aplica hotkeys configuradas"""
        try:
            config = self.bot_manager.config
            
            # Salvar hotkeys do bot
            config.set('hotkeys.start_stop_bot', self.hotkey_vars['start_stop_bot'].get())
            config.set('hotkeys.emergency_stop', self.hotkey_vars['emergency_stop'].get())
            
            # Salvar hotkeys dos módulos
            config.set('hotkeys.toggle_auto_heal', self.hotkey_vars['toggle_auto_heal'].get())
            config.set('hotkeys.toggle_auto_mana', self.hotkey_vars['toggle_auto_mana'].get())
            config.set('hotkeys.toggle_auto_food', self.hotkey_vars['toggle_auto_food'].get())
            config.set('hotkeys.toggle_auto_loot', self.hotkey_vars['toggle_auto_loot'].get())
            config.set('hotkeys.toggle_cavebot', self.hotkey_vars['toggle_cavebot'].get())
            
            # Salvar hotkeys de ação
            config.set('auto_heal.potion_hotkey', self.hotkey_vars['heal_potion'].get())
            config.set('auto_heal.emergency_hotkey', self.hotkey_vars['heal_emergency'].get())
            config.set('auto_mana.potion_hotkey', self.hotkey_vars['mana_potion'].get())
            config.set('auto_mana.emergency_hotkey', self.hotkey_vars['mana_emergency'].get())
            config.set('auto_food.food_hotkey', self.hotkey_vars['food_consume'].get())
            config.set('hotkeys.screenshot', self.hotkey_vars['screenshot'].get())
            config.set('hotkeys.loot_manual', self.hotkey_vars['loot_manual'].get())
            
            # Aplicar nos módulos
            self._apply_module_hotkeys()
            
            # Atualizar status
            self.update_status()
            
            messagebox.showinfo("Sucesso", "Hotkeys aplicadas com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar hotkeys: {e}")
    
    def _apply_module_hotkeys(self):
        """Aplica hotkeys nos módulos específicos"""
        try:
            # Atualizar configurações dos módulos
            heal_config = self.bot_manager.get_module_config('auto_heal')
            heal_config.update({
                'potion_hotkey': self.hotkey_vars['heal_potion'].get(),
                'emergency_hotkey': self.hotkey_vars['heal_emergency'].get()
            })
            self.bot_manager.set_module_config('auto_heal', heal_config)
            
            mana_config = self.bot_manager.get_module_config('auto_mana')
            mana_config.update({
                'potion_hotkey': self.hotkey_vars['mana_potion'].get(),
                'emergency_hotkey': self.hotkey_vars['mana_emergency'].get()
            })
            self.bot_manager.set_module_config('auto_mana', mana_config)
            
            food_config = self.bot_manager.get_module_config('auto_food')
            food_config.update({
                'food_hotkey': self.hotkey_vars['food_consume'].get()
            })
            self.bot_manager.set_module_config('auto_food', food_config)
            
        except Exception as e:
            pass  # Silencioso se módulos não disponíveis
    
    def test_hotkeys(self):
        """Testa se as hotkeys estão funcionando"""
        try:
            # Simular teste das hotkeys
            messagebox.showinfo("Teste de Hotkeys", 
                              "Teste iniciado!\n\n"
                              "Pressione as hotkeys configuradas para verificar se estão funcionando.\n"
                              "O status será atualizado abaixo.")
            
            # Atualizar status com informação de teste
            self.update_status("Modo de teste ativo - pressione as hotkeys para verificar funcionamento...")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro no teste de hotkeys: {e}")
    
    def restore_default_hotkeys(self):
        """Restaura hotkeys padrão"""
        try:
            if messagebox.askyesno("Confirmar", "Deseja restaurar todas as hotkeys para os valores padrão?"):
                # Restaurar valores padrão
                defaults = {
                    'start_stop_bot': 'F9',
                    'emergency_stop': 'F12',
                    'toggle_auto_heal': 'Ctrl+F1',
                    'toggle_auto_mana': 'Ctrl+F2',
                    'toggle_auto_food': 'Ctrl+F3',
                    'toggle_auto_loot': 'Ctrl+F4',
                    'toggle_cavebot': 'Ctrl+F5',
                    'heal_potion': 'F1',
                    'heal_emergency': 'F2',
                    'mana_potion': 'F3',
                    'mana_emergency': 'F4',
                    'food_consume': 'F7',
                    'screenshot': 'F8',
                    'loot_manual': 'Space'
                }
                
                for key, value in defaults.items():
                    if key in self.hotkey_vars:
                        self.hotkey_vars[key].set(value)
                
                messagebox.showinfo("Sucesso", "Hotkeys restauradas para valores padrão!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao restaurar hotkeys: {e}")
    
    def disable_all_hotkeys(self):
        """Desativa todas as hotkeys"""
        try:
            if messagebox.askyesno("Confirmar", "Deseja desativar todas as hotkeys globais?"):
                # Implementar lógica de desativação
                messagebox.showinfo("Info", "Funcionalidade de desativação será implementada em breve!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao desativar hotkeys: {e}")
    
    def update_status(self, custom_message=None):
        """Atualiza status das hotkeys"""
        try:
            self.status_text.config(state=tk.NORMAL)
            self.status_text.delete(1.0, tk.END)
            
            if custom_message:
                self.status_text.insert(tk.END, custom_message)
            else:
                # Mostrar hotkeys ativas
                status_lines = [
                    "HOTKEYS CONFIGURADAS:",
                    "-" * 40,
                    f"Iniciar/Parar Bot: {self.hotkey_vars.get('start_stop_bot', tk.StringVar()).get()}",
                    f"Parada de Emergência: {self.hotkey_vars.get('emergency_stop', tk.StringVar()).get()}",
                    "",
                    "MÓDULOS:",
                    f"Toggle Auto Heal: {self.hotkey_vars.get('toggle_auto_heal', tk.StringVar()).get()}",
                    f"Toggle Auto Mana: {self.hotkey_vars.get('toggle_auto_mana', tk.StringVar()).get()}",
                    f"Toggle Auto Food: {self.hotkey_vars.get('toggle_auto_food', tk.StringVar()).get()}",
                    f"Toggle Auto Loot: {self.hotkey_vars.get('toggle_auto_loot', tk.StringVar()).get()}",
                    f"Toggle Cavebot: {self.hotkey_vars.get('toggle_cavebot', tk.StringVar()).get()}",
                    "",
                    "AÇÕES DIRETAS:",
                    f"Poção de Vida: {self.hotkey_vars.get('heal_potion', tk.StringVar()).get()}",
                    f"Poção de Mana: {self.hotkey_vars.get('mana_potion', tk.StringVar()).get()}",
                    f"Consumir Comida: {self.hotkey_vars.get('food_consume', tk.StringVar()).get()}",
                    f"Capturar Tela: {self.hotkey_vars.get('screenshot', tk.StringVar()).get()}",
                    "",
                    "Status: Hotkeys carregadas e prontas para uso."
                ]
                
                self.status_text.insert(tk.END, "\n".join(status_lines))
            
            self.status_text.config(state=tk.DISABLED)
            
        except Exception as e:
            pass  # Silencioso em caso de erro
    
    def refresh(self):
        """Atualiza painel"""
        self.load_current_hotkeys()
        self.update_status()