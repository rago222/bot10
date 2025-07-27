"""
Status Panel - Painel de status e monitoramento
Exibe informações em tempo real sobre o funcionamento do bot
"""

import tkinter as tk
from tkinter import ttk
import time
from typing import Optional

class StatusPanel:
    """Painel de status do bot"""
    
    def __init__(self, parent, bot_manager):
        self.parent = parent
        self.bot_manager = bot_manager
        
        self.frame = ttk.Frame(parent, padding="10")
        self.create_widgets()
        
        # Variáveis de status
        self.last_update = 0
        self.update_interval = 1.0  # Atualizar a cada segundo
    
    def create_widgets(self):
        """Cria widgets do painel de status"""
        # Status geral
        general_frame = ttk.LabelFrame(self.frame, text="Status Geral", padding="10")
        general_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Labels de status geral
        ttk.Label(general_frame, text="Status do Bot:").grid(row=0, column=0, sticky=tk.W)
        self.bot_status_label = ttk.Label(general_frame, text="Parado", foreground="red")
        self.bot_status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(general_frame, text="Tempo Ativo:").grid(row=1, column=0, sticky=tk.W)
        self.uptime_label = ttk.Label(general_frame, text="00:00:00")
        self.uptime_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(general_frame, text="Última Ação:").grid(row=2, column=0, sticky=tk.W)
        self.last_action_label = ttk.Label(general_frame, text="Nenhuma")
        self.last_action_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Status dos módulos
        modules_frame = ttk.LabelFrame(self.frame, text="Status dos Módulos", padding="10")
        modules_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Auto Heal
        heal_frame = ttk.Frame(modules_frame)
        heal_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Label(heal_frame, text="Auto Heal:", width=12).grid(row=0, column=0, sticky=tk.W)
        self.heal_status = ttk.Label(heal_frame, text="Desabilitado")
        self.heal_status.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        self.heal_health = ttk.Label(heal_frame, text="Vida: ---%")
        self.heal_health.grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # Auto Mana
        mana_frame = ttk.Frame(modules_frame)
        mana_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Label(mana_frame, text="Auto Mana:", width=12).grid(row=0, column=0, sticky=tk.W)
        self.mana_status = ttk.Label(mana_frame, text="Desabilitado")
        self.mana_status.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        self.mana_mana = ttk.Label(mana_frame, text="Mana: ---%")
        self.mana_mana.grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # Auto Food
        food_frame = ttk.Frame(modules_frame)
        food_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Label(food_frame, text="Auto Food:", width=12).grid(row=0, column=0, sticky=tk.W)
        self.food_status = ttk.Label(food_frame, text="Desabilitado")
        self.food_status.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Auto Loot
        loot_frame = ttk.Frame(modules_frame)
        loot_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Label(loot_frame, text="Auto Loot:", width=12).grid(row=0, column=0, sticky=tk.W)
        self.loot_status = ttk.Label(loot_frame, text="Desabilitado")
        self.loot_status.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Cavebot
        cavebot_frame = ttk.Frame(modules_frame)
        cavebot_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Label(cavebot_frame, text="Cavebot:", width=12).grid(row=0, column=0, sticky=tk.W)
        self.cavebot_status = ttk.Label(cavebot_frame, text="Desabilitado")
        self.cavebot_status.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        self.cavebot_waypoint = ttk.Label(cavebot_frame, text="Waypoint: --")
        self.cavebot_waypoint.grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # Estatísticas
        stats_frame = ttk.LabelFrame(self.frame, text="Estatísticas", padding="10")
        stats_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Contadores
        ttk.Label(stats_frame, text="Curas Realizadas:").grid(row=0, column=0, sticky=tk.W)
        self.heal_count_label = ttk.Label(stats_frame, text="0")
        self.heal_count_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(stats_frame, text="Manas Usadas:").grid(row=1, column=0, sticky=tk.W)
        self.mana_count_label = ttk.Label(stats_frame, text="0")
        self.mana_count_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(stats_frame, text="Itens Coletados:").grid(row=2, column=0, sticky=tk.W)
        self.loot_count_label = ttk.Label(stats_frame, text="0")
        self.loot_count_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(stats_frame, text="Monstros Mortos:").grid(row=3, column=0, sticky=tk.W)
        self.kill_count_label = ttk.Label(stats_frame, text="0")
        self.kill_count_label.grid(row=3, column=1, sticky=tk.W, padx=(10, 0))
        
        # Performance
        performance_frame = ttk.LabelFrame(self.frame, text="Performance", padding="10")
        performance_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(performance_frame, text="FPS Captura:").grid(row=0, column=0, sticky=tk.W)
        self.fps_label = ttk.Label(performance_frame, text="0.0")
        self.fps_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(performance_frame, text="Tempo Ciclo:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.cycle_time_label = ttk.Label(performance_frame, text="0ms")
        self.cycle_time_label.grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(performance_frame, text="Memória:").grid(row=1, column=0, sticky=tk.W)
        self.memory_label = ttk.Label(performance_frame, text="0 MB")
        self.memory_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(performance_frame, text="CPU:").grid(row=1, column=2, sticky=tk.W, padx=(20, 0))
        self.cpu_label = ttk.Label(performance_frame, text="0%")
        self.cpu_label.grid(row=1, column=3, sticky=tk.W, padx=(10, 0))
        
        # Log recente
        log_frame = ttk.LabelFrame(self.frame, text="Log Recente", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Text widget para log
        self.log_text = tk.Text(log_frame, height=8, width=70, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Configurar expansão
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(3, weight=1)
    
    def update_status(self):
        """Atualiza status do painel"""
        try:
            current_time = time.time()
            if current_time - self.last_update < self.update_interval:
                return
            
            self.last_update = current_time
            
            # Obter status do bot
            bot_status = self.bot_manager.get_status()
            
            # Atualizar status geral
            if bot_status.running:
                self.bot_status_label.config(text="Executando", foreground="green")
            else:
                self.bot_status_label.config(text="Parado", foreground="red")
            
            # Atualizar status dos módulos
            self._update_module_status("auto_heal", self.heal_status, bot_status.auto_heal_enabled)
            self._update_module_status("auto_mana", self.mana_status, bot_status.auto_mana_enabled)
            self._update_module_status("auto_food", self.food_status, bot_status.auto_food_enabled)
            self._update_module_status("auto_loot", self.loot_status, bot_status.auto_loot_enabled)
            self._update_module_status("cavebot", self.cavebot_status, bot_status.cavebot_enabled)
            
            # Atualizar informações específicas
            self._update_health_mana_info()
            self._update_cavebot_info()
            self._update_performance_info()
            
        except Exception as e:
            # Log silencioso do erro
            pass
    
    def _update_module_status(self, module_name: str, label: ttk.Label, enabled: bool):
        """Atualiza status de um módulo específico"""
        if enabled:
            label.config(text="Ativo", foreground="green")
        else:
            label.config(text="Desabilitado", foreground="gray")
    
    def _update_health_mana_info(self):
        """Atualiza informações de vida e mana"""
        try:
            # Obter percentuais atuais
            if hasattr(self.bot_manager.modules['auto_heal'], 'get_current_health'):
                health = self.bot_manager.modules['auto_heal'].get_current_health()
                self.heal_health.config(text=f"Vida: {health:.0f}%")
            
            if hasattr(self.bot_manager.modules['auto_mana'], 'get_current_mana'):
                mana = self.bot_manager.modules['auto_mana'].get_current_mana()
                self.mana_mana.config(text=f"Mana: {mana:.0f}%")
                
        except Exception:
            pass
    
    def _update_cavebot_info(self):
        """Atualiza informações do cavebot"""
        try:
            if hasattr(self.bot_manager.modules['cavebot'], 'get_status'):
                cavebot_status = self.bot_manager.modules['cavebot'].get_status()
                current_wp = cavebot_status.get('current_waypoint', 0)
                total_wp = cavebot_status.get('total_waypoints', 0)
                self.cavebot_waypoint.config(text=f"Waypoint: {current_wp}/{total_wp}")
                
        except Exception:
            pass
    
    def _update_performance_info(self):
        """Atualiza informações de performance"""
        try:
            # Estas informações seriam obtidas do sistema de monitoramento
            # Por enquanto, valores simulados
            self.fps_label.config(text="20.0")
            self.cycle_time_label.config(text="50ms")
            self.memory_label.config(text="45 MB")
            self.cpu_label.config(text="15%")
            
        except Exception:
            pass
    
    def add_log_entry(self, message: str, level: str = "INFO"):
        """Adiciona entrada ao log"""
        try:
            timestamp = time.strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {level}: {message}\n"
            
            # Adicionar ao texto
            self.log_text.insert(tk.END, log_entry)
            
            # Scroll para o final
            self.log_text.see(tk.END)
            
            # Limitar número de linhas (manter últimas 100)
            lines = self.log_text.get(1.0, tk.END).split('\n')
            if len(lines) > 100:
                self.log_text.delete(1.0, f"{len(lines)-100}.0")
                
        except Exception:
            pass