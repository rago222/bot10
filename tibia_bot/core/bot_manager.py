"""
Bot Manager - Gerenciador principal do bot
Controla todos os módulos e funcionalidades
"""

import threading
import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from modules.auto_heal import AutoHeal
from modules.auto_mana import AutoMana
from modules.auto_food import AutoFood
from modules.auto_loot import AutoLoot
from modules.cavebot import Cavebot
from core.screen_capture import ScreenCapture
from core.input_simulator import InputSimulator
from utils.config_manager import ConfigManager

@dataclass
class BotStatus:
    """Status do bot"""
    running: bool = False
    auto_heal_enabled: bool = False
    auto_mana_enabled: bool = False
    auto_food_enabled: bool = False
    auto_loot_enabled: bool = False
    cavebot_enabled: bool = False

class BotManager:
    """Gerenciador principal do bot"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.status = BotStatus()
        self.config = ConfigManager()
        
        # Inicializar componentes core
        self.screen_capture = ScreenCapture()
        self.input_simulator = InputSimulator()
        
        # Inicializar módulos
        self.modules = {
            'auto_heal': AutoHeal(self.screen_capture, self.input_simulator),
            'auto_mana': AutoMana(self.screen_capture, self.input_simulator),
            'auto_food': AutoFood(self.screen_capture, self.input_simulator),
            'auto_loot': AutoLoot(self.screen_capture, self.input_simulator),
            'cavebot': Cavebot(self.screen_capture, self.input_simulator)
        }
        
        # Thread principal do bot
        self._bot_thread = None
        self._stop_event = threading.Event()
        
        self.logger.info("BotManager inicializado com sucesso")
    
    def start_bot(self):
        """Inicia o bot"""
        if self.status.running:
            self.logger.warning("Bot já está em execução")
            return
        
        try:
            # Verificar se a tela pode ser capturada
            if not self.screen_capture.test_capture():
                raise Exception("Não foi possível capturar a tela. Verifique as configurações do OBS Studio.")
            
            self.status.running = True
            self._stop_event.clear()
            
            # Iniciar thread principal
            self._bot_thread = threading.Thread(target=self._bot_loop, daemon=True)
            self._bot_thread.start()
            
            self.logger.info("Bot iniciado com sucesso")
            
        except Exception as e:
            self.status.running = False
            self.logger.error(f"Erro ao iniciar bot: {e}")
            raise
    
    def stop_bot(self):
        """Para o bot"""
        if not self.status.running:
            return
        
        self.logger.info("Parando bot...")
        self.status.running = False
        self._stop_event.set()
        
        if self._bot_thread and self._bot_thread.is_alive():
            self._bot_thread.join(timeout=5)
        
        self.logger.info("Bot parado")
    
    def stop_all(self):
        """Para todos os componentes do bot"""
        self.stop_bot()
        # Cleanup adicional se necessário
    
    def _bot_loop(self):
        """Loop principal do bot"""
        self.logger.info("Iniciando loop principal do bot")
        
        while not self._stop_event.is_set() and self.status.running:
            try:
                # Capturar tela uma vez por ciclo
                screen = self.screen_capture.capture()
                if screen is None:
                    time.sleep(0.5)
                    continue
                
                # Executar módulos habilitados na ordem de prioridade
                if self.status.auto_heal_enabled:
                    self.modules['auto_heal'].process(screen)
                
                if self.status.auto_mana_enabled:
                    self.modules['auto_mana'].process(screen)
                
                if self.status.auto_food_enabled:
                    self.modules['auto_food'].process(screen)
                
                if self.status.cavebot_enabled:
                    self.modules['cavebot'].process(screen)
                
                if self.status.auto_loot_enabled:
                    self.modules['auto_loot'].process(screen)
                
                # Pausa entre ciclos (configurável)
                time.sleep(self.config.get('bot.cycle_delay', 0.1))
                
            except Exception as e:
                self.logger.error(f"Erro no loop do bot: {e}", exc_info=True)
                time.sleep(1)
        
        self.logger.info("Loop do bot finalizado")
    
    def toggle_module(self, module_name: str, enabled: bool):
        """Ativa/desativa um módulo"""
        if module_name == 'auto_heal':
            self.status.auto_heal_enabled = enabled
        elif module_name == 'auto_mana':
            self.status.auto_mana_enabled = enabled
        elif module_name == 'auto_food':
            self.status.auto_food_enabled = enabled
        elif module_name == 'auto_loot':
            self.status.auto_loot_enabled = enabled
        elif module_name == 'cavebot':
            self.status.cavebot_enabled = enabled
        
        self.logger.info(f"Módulo {module_name}: {'ativado' if enabled else 'desativado'}")
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """Obtém configuração de um módulo"""
        if module_name in self.modules:
            return self.modules[module_name].get_config()
        return {}
    
    def set_module_config(self, module_name: str, config: Dict[str, Any]):
        """Define configuração de um módulo"""
        if module_name in self.modules:
            self.modules[module_name].set_config(config)
            self.logger.info(f"Configuração do módulo {module_name} atualizada")
    
    def get_status(self) -> BotStatus:
        """Retorna status atual do bot"""
        return self.status
    
    def load_cavebot_script(self, script_path: str) -> bool:
        """Carrega script do cavebot"""
        try:
            return self.modules['cavebot'].load_script(script_path)
        except Exception as e:
            self.logger.error(f"Erro ao carregar script do cavebot: {e}")
            return False