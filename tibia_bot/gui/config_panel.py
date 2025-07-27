"""
Config Panel - Painel de configurações
Interface para ajustar todas as configurações do bot
"""

import tkinter as tk
from tkinter import ttk, messagebox

class ConfigPanel:
    """Painel de configurações do bot"""
    
    def __init__(self, parent, bot_manager):
        self.parent = parent
        self.bot_manager = bot_manager
        
        self.frame = ttk.Frame(parent, padding="10")
        self.create_widgets()
        
        # Variáveis de configuração
        self.config_vars = {}
        self.load_current_config()
    
    def create_widgets(self):
        """Cria widgets do painel de configurações"""
        # Notebook para organizar configurações
        self.config_notebook = ttk.Notebook(self.frame)
        self.config_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        # Abas de configuração
        self.create_general_tab()
        self.create_heal_tab()
        self.create_mana_tab()
        self.create_food_tab()
        self.create_loot_tab()
        
        # Botões de controle
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=1, column=0, pady=(10, 0))
        
        ttk.Button(button_frame, text="Aplicar", 
                  command=self.apply_config).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Salvar", 
                  command=self.save_config).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Restaurar Padrão", 
                  command=self.restore_defaults).grid(row=0, column=2, padx=(5, 0))
    
    def create_general_tab(self):
        """Cria aba de configurações gerais"""
        general_frame = ttk.Frame(self.config_notebook, padding="10")
        self.config_notebook.add(general_frame, text="Geral")
        
        # Configurações do bot
        bot_frame = ttk.LabelFrame(general_frame, text="Bot", padding="10")
        bot_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(bot_frame, text="Delay entre ciclos (s):").grid(row=0, column=0, sticky=tk.W)
        self.config_vars['cycle_delay'] = tk.DoubleVar(value=0.1)
        cycle_delay_spin = ttk.Spinbox(bot_frame, from_=0.01, to=1.0, increment=0.01, 
                                      width=10, textvariable=self.config_vars['cycle_delay'])
        cycle_delay_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Configurações de captura
        capture_frame = ttk.LabelFrame(general_frame, text="Captura de Tela", padding="10")
        capture_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(capture_frame, text="Janela OBS:").grid(row=0, column=0, sticky=tk.W)
        self.config_vars['obs_window'] = tk.StringVar(value="OBS Studio - Preview")
        obs_entry = ttk.Entry(capture_frame, width=30, textvariable=self.config_vars['obs_window'])
        obs_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(capture_frame, text="Intervalo mín. captura (s):").grid(row=1, column=0, sticky=tk.W)
        self.config_vars['capture_interval'] = tk.DoubleVar(value=0.05)
        capture_spin = ttk.Spinbox(capture_frame, from_=0.01, to=0.2, increment=0.01, 
                                  width=10, textvariable=self.config_vars['capture_interval'])
        capture_spin.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Configurações de input
        input_frame = ttk.LabelFrame(general_frame, text="Simulação de Input", padding="10")
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.config_vars['humanize_input'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(input_frame, text="Humanizar input (recomendado)", 
                       variable=self.config_vars['humanize_input']).grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(input_frame, text="Velocidade base do mouse:").grid(row=1, column=0, sticky=tk.W)
        self.config_vars['mouse_speed'] = tk.DoubleVar(value=0.5)
        mouse_speed_spin = ttk.Spinbox(input_frame, from_=0.1, to=2.0, increment=0.1, 
                                      width=10, textvariable=self.config_vars['mouse_speed'])
        mouse_speed_spin.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
    
    def create_heal_tab(self):
        """Cria aba de configurações de cura"""
        heal_frame = ttk.Frame(self.config_notebook, padding="10")
        self.config_notebook.add(heal_frame, text="Auto Heal")
        
        # Configurações básicas
        basic_frame = ttk.LabelFrame(heal_frame, text="Configurações Básicas", padding="10")
        basic_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(basic_frame, text="Percentual de vida para curar:").grid(row=0, column=0, sticky=tk.W)
        self.config_vars['health_threshold'] = tk.IntVar(value=70)
        health_spin = ttk.Spinbox(basic_frame, from_=1, to=99, width=10, 
                                 textvariable=self.config_vars['health_threshold'])
        health_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Label(basic_frame, text="%").grid(row=0, column=2, sticky=tk.W)
        
        ttk.Label(basic_frame, text="Percentual de emergência:").grid(row=1, column=0, sticky=tk.W)
        self.config_vars['emergency_threshold'] = tk.IntVar(value=30)
        emergency_spin = ttk.Spinbox(basic_frame, from_=1, to=99, width=10, 
                                    textvariable=self.config_vars['emergency_threshold'])
        emergency_spin.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Label(basic_frame, text="%").grid(row=1, column=2, sticky=tk.W)
        
        # Métodos de cura
        methods_frame = ttk.LabelFrame(heal_frame, text="Métodos de Cura", padding="10")
        methods_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.config_vars['use_heal_potions'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(methods_frame, text="Usar poções de vida", 
                       variable=self.config_vars['use_heal_potions']).grid(row=0, column=0, sticky=tk.W)
        
        self.config_vars['use_heal_spells'] = tk.BooleanVar(value=False)
        ttk.Checkbutton(methods_frame, text="Usar magias de cura", 
                       variable=self.config_vars['use_heal_spells']).grid(row=1, column=0, sticky=tk.W)
        
        # Hotkeys
        hotkeys_frame = ttk.LabelFrame(heal_frame, text="Hotkeys", padding="10")
        hotkeys_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(hotkeys_frame, text="Poção de vida:").grid(row=0, column=0, sticky=tk.W)
        self.config_vars['heal_potion_key'] = tk.StringVar(value="F1")
        ttk.Entry(hotkeys_frame, width=10, textvariable=self.config_vars['heal_potion_key']).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(hotkeys_frame, text="Emergência:").grid(row=1, column=0, sticky=tk.W)
        self.config_vars['heal_emergency_key'] = tk.StringVar(value="F2")
        ttk.Entry(hotkeys_frame, width=10, textvariable=self.config_vars['heal_emergency_key']).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(hotkeys_frame, text="Magia de cura:").grid(row=2, column=0, sticky=tk.W)
        self.config_vars['heal_spell_key'] = tk.StringVar(value="F5")
        ttk.Entry(hotkeys_frame, width=10, textvariable=self.config_vars['heal_spell_key']).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
    
    def create_mana_tab(self):
        """Cria aba de configurações de mana"""
        mana_frame = ttk.Frame(self.config_notebook, padding="10")
        self.config_notebook.add(mana_frame, text="Auto Mana")
        
        # Configurações básicas
        basic_frame = ttk.LabelFrame(mana_frame, text="Configurações Básicas", padding="10")
        basic_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(basic_frame, text="Percentual de mana para usar:").grid(row=0, column=0, sticky=tk.W)
        self.config_vars['mana_threshold'] = tk.IntVar(value=60)
        mana_spin = ttk.Spinbox(basic_frame, from_=1, to=99, width=10, 
                               textvariable=self.config_vars['mana_threshold'])
        mana_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Label(basic_frame, text="%").grid(row=0, column=2, sticky=tk.W)
        
        ttk.Label(basic_frame, text="Percentual de emergência:").grid(row=1, column=0, sticky=tk.W)
        self.config_vars['mana_emergency_threshold'] = tk.IntVar(value=20)
        mana_emergency_spin = ttk.Spinbox(basic_frame, from_=1, to=99, width=10, 
                                         textvariable=self.config_vars['mana_emergency_threshold'])
        mana_emergency_spin.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Label(basic_frame, text="%").grid(row=1, column=2, sticky=tk.W)
        
        # Métodos de mana
        methods_frame = ttk.LabelFrame(mana_frame, text="Métodos de Restauração", padding="10")
        methods_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.config_vars['use_mana_potions'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(methods_frame, text="Usar poções de mana", 
                       variable=self.config_vars['use_mana_potions']).grid(row=0, column=0, sticky=tk.W)
        
        self.config_vars['use_mana_spells'] = tk.BooleanVar(value=False)
        ttk.Checkbutton(methods_frame, text="Usar magias de mana", 
                       variable=self.config_vars['use_mana_spells']).grid(row=1, column=0, sticky=tk.W)
        
        # Hotkeys
        hotkeys_frame = ttk.LabelFrame(mana_frame, text="Hotkeys", padding="10")
        hotkeys_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(hotkeys_frame, text="Poção de mana:").grid(row=0, column=0, sticky=tk.W)
        self.config_vars['mana_potion_key'] = tk.StringVar(value="F3")
        ttk.Entry(hotkeys_frame, width=10, textvariable=self.config_vars['mana_potion_key']).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(hotkeys_frame, text="Emergência:").grid(row=1, column=0, sticky=tk.W)
        self.config_vars['mana_emergency_key'] = tk.StringVar(value="F4")
        ttk.Entry(hotkeys_frame, width=10, textvariable=self.config_vars['mana_emergency_key']).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
    
    def create_food_tab(self):
        """Cria aba de configurações de comida"""
        food_frame = ttk.Frame(self.config_notebook, padding="10")
        self.config_notebook.add(food_frame, text="Auto Food")
        
        # Configurações básicas
        basic_frame = ttk.LabelFrame(food_frame, text="Configurações Básicas", padding="10")
        basic_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(basic_frame, text="Intervalo de verificação (s):").grid(row=0, column=0, sticky=tk.W)
        self.config_vars['food_check_interval'] = tk.DoubleVar(value=5.0)
        food_interval_spin = ttk.Spinbox(basic_frame, from_=1.0, to=30.0, increment=1.0, 
                                        width=10, textvariable=self.config_vars['food_check_interval'])
        food_interval_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Método de uso
        method_frame = ttk.LabelFrame(food_frame, text="Método de Uso", padding="10")
        method_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.config_vars['food_use_hotkey'] = tk.BooleanVar(value=False)
        ttk.Radiobutton(method_frame, text="Usar hotkey", 
                       variable=self.config_vars['food_use_hotkey'], value=False).grid(row=0, column=0, sticky=tk.W)
        
        self.config_vars['food_use_click'] = tk.BooleanVar(value=True)
        ttk.Radiobutton(method_frame, text="Clique direito no inventário", 
                       variable=self.config_vars['food_use_hotkey'], value=True).grid(row=1, column=0, sticky=tk.W)
        
        # Configurações
        config_frame = ttk.LabelFrame(food_frame, text="Configurações", padding="10")
        config_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(config_frame, text="Hotkey da comida:").grid(row=0, column=0, sticky=tk.W)
        self.config_vars['food_hotkey'] = tk.StringVar(value="F7")
        ttk.Entry(config_frame, width=10, textvariable=self.config_vars['food_hotkey']).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(config_frame, text="Slot da comida (1-20):").grid(row=1, column=0, sticky=tk.W)
        self.config_vars['food_slot'] = tk.IntVar(value=1)
        food_slot_spin = ttk.Spinbox(config_frame, from_=1, to=20, width=10, 
                                    textvariable=self.config_vars['food_slot'])
        food_slot_spin.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
    
    def create_loot_tab(self):
        """Cria aba de configurações de loot"""
        loot_frame = ttk.Frame(self.config_notebook, padding="10")
        self.config_notebook.add(loot_frame, text="Auto Loot")
        
        # Configurações básicas
        basic_frame = ttk.LabelFrame(loot_frame, text="Configurações Básicas", padding="10")
        basic_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(basic_frame, text="Raio de coleta (pixels):").grid(row=0, column=0, sticky=tk.W)
        self.config_vars['loot_radius'] = tk.IntVar(value=150)
        loot_radius_spin = ttk.Spinbox(basic_frame, from_=50, to=300, increment=10, 
                                      width=10, textvariable=self.config_vars['loot_radius'])
        loot_radius_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(basic_frame, text="Delay entre coletas (s):").grid(row=1, column=0, sticky=tk.W)
        self.config_vars['loot_delay'] = tk.DoubleVar(value=0.2)
        loot_delay_spin = ttk.Spinbox(basic_frame, from_=0.1, to=2.0, increment=0.1, 
                                     width=10, textvariable=self.config_vars['loot_delay'])
        loot_delay_spin.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Opções de loot
        options_frame = ttk.LabelFrame(loot_frame, text="Opções de Loot", padding="10")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.config_vars['loot_optimized'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Usar loot otimizado (recomendado)", 
                       variable=self.config_vars['loot_optimized']).grid(row=0, column=0, sticky=tk.W)
        
        self.config_vars['loot_auto_open'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Abrir corpos automaticamente", 
                       variable=self.config_vars['loot_auto_open']).grid(row=1, column=0, sticky=tk.W)
        
        self.config_vars['loot_pickup_all'] = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Coletar todos os itens (ignora lista)", 
                       variable=self.config_vars['loot_pickup_all']).grid(row=2, column=0, sticky=tk.W)
        
        # Lista de itens valiosos
        items_frame = ttk.LabelFrame(loot_frame, text="Itens Valiosos", padding="10")
        items_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Lista
        items_list_frame = ttk.Frame(items_frame)
        items_list_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.items_listbox = tk.Listbox(items_list_frame, height=6)
        items_scrollbar = ttk.Scrollbar(items_list_frame, orient=tk.VERTICAL, command=self.items_listbox.yview)
        self.items_listbox.configure(yscrollcommand=items_scrollbar.set)
        
        self.items_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        items_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        items_list_frame.columnconfigure(0, weight=1)
        items_list_frame.rowconfigure(0, weight=1)
        
        # Controles da lista
        list_controls_frame = ttk.Frame(items_frame)
        list_controls_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        self.item_entry = ttk.Entry(list_controls_frame, width=20)
        self.item_entry.grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(list_controls_frame, text="Adicionar", 
                  command=self.add_valuable_item).grid(row=0, column=1, padx=5)
        ttk.Button(list_controls_frame, text="Remover", 
                  command=self.remove_valuable_item).grid(row=0, column=2, padx=(5, 0))
        
        # Configurar expansão
        loot_frame.rowconfigure(2, weight=1)
        items_frame.columnconfigure(0, weight=1)
        items_frame.rowconfigure(0, weight=1)
    
    def load_current_config(self):
        """Carrega configuração atual do bot"""
        try:
            config = self.bot_manager.config
            
            # Carregar valores nas variáveis
            self.config_vars['cycle_delay'].set(config.get('bot.cycle_delay', 0.1))
            self.config_vars['obs_window'].set(config.get('screen_capture.obs_window_title', 'OBS Studio - Preview'))
            self.config_vars['capture_interval'].set(config.get('screen_capture.min_capture_interval', 0.05))
            self.config_vars['humanize_input'].set(config.get('input_simulator.humanize_by_default', True))
            self.config_vars['mouse_speed'].set(config.get('input_simulator.mouse_speed_base', 0.5))
            
            # Auto Heal
            self.config_vars['health_threshold'].set(config.get('auto_heal.health_threshold', 70))
            self.config_vars['emergency_threshold'].set(config.get('auto_heal.emergency_threshold', 30))
            self.config_vars['use_heal_potions'].set(config.get('auto_heal.use_potions', True))
            self.config_vars['use_heal_spells'].set(config.get('auto_heal.use_spells', False))
            self.config_vars['heal_potion_key'].set(config.get('auto_heal.potion_hotkey', 'F1'))
            self.config_vars['heal_emergency_key'].set(config.get('auto_heal.emergency_hotkey', 'F2'))
            self.config_vars['heal_spell_key'].set(config.get('auto_heal.spell_hotkey', 'F5'))
            
            # Auto Mana
            self.config_vars['mana_threshold'].set(config.get('auto_mana.mana_threshold', 60))
            self.config_vars['mana_emergency_threshold'].set(config.get('auto_mana.emergency_threshold', 20))
            self.config_vars['use_mana_potions'].set(config.get('auto_mana.use_potions', True))
            self.config_vars['use_mana_spells'].set(config.get('auto_mana.use_spells', False))
            self.config_vars['mana_potion_key'].set(config.get('auto_mana.potion_hotkey', 'F3'))
            self.config_vars['mana_emergency_key'].set(config.get('auto_mana.emergency_hotkey', 'F4'))
            
            # Auto Food
            self.config_vars['food_check_interval'].set(config.get('auto_food.check_interval', 5.0))
            self.config_vars['food_use_hotkey'].set(not config.get('auto_food.use_right_click', True))
            self.config_vars['food_hotkey'].set(config.get('auto_food.food_hotkey', 'F7'))
            self.config_vars['food_slot'].set(config.get('auto_food.food_inventory_slot', 1))
            
            # Auto Loot
            self.config_vars['loot_radius'].set(config.get('auto_loot.loot_radius', 150))
            self.config_vars['loot_delay'].set(config.get('auto_loot.loot_delay', 0.2))
            self.config_vars['loot_optimized'].set(config.get('auto_loot.use_optimized_loot', True))
            self.config_vars['loot_auto_open'].set(config.get('auto_loot.auto_open_corpses', True))
            self.config_vars['loot_pickup_all'].set(config.get('auto_loot.pickup_all_items', False))
            
            # Lista de itens valiosos
            self.load_valuable_items()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar configurações: {e}")
    
    def apply_config(self):
        """Aplica configurações ao bot"""
        try:
            config = self.bot_manager.config
            
            # Aplicar configurações gerais
            config.set('bot.cycle_delay', self.config_vars['cycle_delay'].get())
            config.set('screen_capture.obs_window_title', self.config_vars['obs_window'].get())
            config.set('screen_capture.min_capture_interval', self.config_vars['capture_interval'].get())
            config.set('input_simulator.humanize_by_default', self.config_vars['humanize_input'].get())
            config.set('input_simulator.mouse_speed_base', self.config_vars['mouse_speed'].get())
            
            # Auto Heal
            heal_config = {
                'health_threshold': self.config_vars['health_threshold'].get(),
                'emergency_threshold': self.config_vars['emergency_threshold'].get(),
                'use_potions': self.config_vars['use_heal_potions'].get(),
                'use_spells': self.config_vars['use_heal_spells'].get(),
                'potion_hotkey': self.config_vars['heal_potion_key'].get(),
                'emergency_hotkey': self.config_vars['heal_emergency_key'].get(),
                'spell_hotkey': self.config_vars['heal_spell_key'].get(),
            }
            self.bot_manager.set_module_config('auto_heal', heal_config)
            
            # Auto Mana
            mana_config = {
                'mana_threshold': self.config_vars['mana_threshold'].get(),
                'emergency_threshold': self.config_vars['mana_emergency_threshold'].get(),
                'use_potions': self.config_vars['use_mana_potions'].get(),
                'use_spells': self.config_vars['use_mana_spells'].get(),
                'potion_hotkey': self.config_vars['mana_potion_key'].get(),
                'emergency_hotkey': self.config_vars['mana_emergency_key'].get(),
            }
            self.bot_manager.set_module_config('auto_mana', mana_config)
            
            # Auto Food
            food_config = {
                'check_interval': self.config_vars['food_check_interval'].get(),
                'use_right_click': not self.config_vars['food_use_hotkey'].get(),
                'food_hotkey': self.config_vars['food_hotkey'].get(),
                'food_inventory_slot': self.config_vars['food_slot'].get(),
            }
            self.bot_manager.set_module_config('auto_food', food_config)
            
            # Auto Loot
            loot_config = {
                'loot_radius': self.config_vars['loot_radius'].get(),
                'loot_delay': self.config_vars['loot_delay'].get(),
                'use_optimized_loot': self.config_vars['loot_optimized'].get(),
                'auto_open_corpses': self.config_vars['loot_auto_open'].get(),
                'pickup_all_items': self.config_vars['loot_pickup_all'].get(),
            }
            self.bot_manager.set_module_config('auto_loot', loot_config)
            
            messagebox.showinfo("Sucesso", "Configurações aplicadas com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar configurações: {e}")
    
    def save_config(self):
        """Salva configurações no arquivo"""
        try:
            self.apply_config()  # Aplicar primeiro
            if self.bot_manager.config.save_config():
                messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            else:
                messagebox.showerror("Erro", "Erro ao salvar configurações!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")
    
    def restore_defaults(self):
        """Restaura configurações padrão"""
        try:
            if messagebox.askyesno("Confirmar", "Deseja restaurar todas as configurações para os valores padrão?"):
                self.bot_manager.config.reset_to_defaults()
                self.load_current_config()
                messagebox.showinfo("Sucesso", "Configurações restauradas para padrão!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao restaurar configurações: {e}")
    
    def load_valuable_items(self):
        """Carrega lista de itens valiosos"""
        try:
            self.items_listbox.delete(0, tk.END)
            
            # Obter lista do módulo auto_loot
            if hasattr(self.bot_manager.modules['auto_loot'], 'valuable_items'):
                items = self.bot_manager.modules['auto_loot'].valuable_items
                for item in items:
                    self.items_listbox.insert(tk.END, item)
                    
        except Exception as e:
            pass  # Silencioso se módulo não estiver disponível
    
    def add_valuable_item(self):
        """Adiciona item à lista de valiosos"""
        try:
            item_name = self.item_entry.get().strip()
            if item_name:
                self.items_listbox.insert(tk.END, item_name)
                self.item_entry.delete(0, tk.END)
                
                # Adicionar ao módulo
                if hasattr(self.bot_manager.modules['auto_loot'], 'add_valuable_item'):
                    self.bot_manager.modules['auto_loot'].add_valuable_item(item_name)
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar item: {e}")
    
    def remove_valuable_item(self):
        """Remove item da lista de valiosos"""
        try:
            selection = self.items_listbox.curselection()
            if selection:
                item_name = self.items_listbox.get(selection[0])
                self.items_listbox.delete(selection[0])
                
                # Remover do módulo
                if hasattr(self.bot_manager.modules['auto_loot'], 'remove_valuable_item'):
                    self.bot_manager.modules['auto_loot'].remove_valuable_item(item_name)
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover item: {e}")
    
    def refresh(self):
        """Atualiza painel com configurações atuais"""
        self.load_current_config()