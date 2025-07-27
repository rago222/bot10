"""
Base Module - Classe base para todos os módulos do bot
"""

import logging
import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import numpy as np

class BaseModule(ABC):
    """Classe base para todos os módulos do bot"""
    
    def __init__(self, screen_capture, input_simulator, name: str):
        self.screen_capture = screen_capture
        self.input_simulator = input_simulator
        self.name = name
        self.logger = logging.getLogger(f"modules.{name}")
        
        # Configurações padrão
        self.config = {}
        self.enabled = False
        self.last_execution = 0
        self.execution_interval = 0.5  # Intervalo mínimo entre execuções
        
        self.logger.info(f"Módulo {name} inicializado")
    
    @abstractmethod
    def process(self, screen_image: np.ndarray) -> bool:
        """
        Processa uma imagem da tela e executa ações necessárias
        Retorna True se alguma ação foi executada
        """
        pass
    
    def can_execute(self) -> bool:
        """Verifica se o módulo pode ser executado agora"""
        current_time = time.time()
        return (current_time - self.last_execution) >= self.execution_interval
    
    def mark_execution(self):
        """Marca que o módulo foi executado"""
        self.last_execution = time.time()
    
    def get_config(self) -> Dict[str, Any]:
        """Retorna configuração atual do módulo"""
        return self.config.copy()
    
    def set_config(self, config: Dict[str, Any]):
        """Define nova configuração para o módulo"""
        self.config.update(config)
        self.logger.info(f"Configuração do módulo {self.name} atualizada")
    
    def is_enabled(self) -> bool:
        """Retorna se o módulo está habilitado"""
        return self.enabled
    
    def set_enabled(self, enabled: bool):
        """Habilita ou desabilita o módulo"""
        self.enabled = enabled
        self.logger.info(f"Módulo {self.name}: {'habilitado' if enabled else 'desabilitado'}")