"""
Auto Heal - Módulo de autocura
Monitora a barra de vida e usa poções/magias de cura
"""

import cv2
import numpy as np
import time
from typing import Optional, Tuple
from modules.base_module import BaseModule

class AutoHeal(BaseModule):
    """Módulo de autocura automática"""
    
    def __init__(self, screen_capture, input_simulator):
        super().__init__(screen_capture, input_simulator, "auto_heal")
        
        # Configurações padrão
        self.config = {
            'health_threshold': 70,  # Percentual de vida para usar cura
            'use_potions': True,     # Usar poções
            'use_spells': False,     # Usar magias
            'potion_hotkey': 'F1',   # Tecla da poção
            'spell_hotkey': 'F5',    # Tecla da magia
            'emergency_threshold': 30,  # Percentual crítico
            'emergency_hotkey': 'F2',   # Tecla de emergência
        }
        
        # Estados internos
        self.last_health_check = 0
        self.health_check_interval = 0.2  # Verificar vida a cada 200ms
        self.last_heal_time = 0
        self.heal_cooldown = 1.0  # Cooldown entre curas
        
        # Cache de imagens para otimização
        self.health_bar_template = None
        self.last_health_percentage = 100
        
    def process(self, screen_image: np.ndarray) -> bool:
        """Processa verificação de vida e executa cura se necessário"""
        if not self.can_execute():
            return False
        
        try:
            # Verificar vida atual
            health_percentage = self._get_health_percentage(screen_image)
            if health_percentage is None:
                return False
            
            self.last_health_percentage = health_percentage
            
            # Determinar se precisa de cura
            needs_healing = False
            is_emergency = False
            
            if health_percentage <= self.config['emergency_threshold']:
                needs_healing = True
                is_emergency = True
            elif health_percentage <= self.config['health_threshold']:
                needs_healing = True
            
            # Executar cura se necessário
            if needs_healing and self._can_heal():
                success = self._execute_heal(is_emergency)
                if success:
                    self.mark_execution()
                    self.last_heal_time = time.time()
                    self.logger.info(f"Cura executada - Vida: {health_percentage}% "
                                   f"({'EMERGÊNCIA' if is_emergency else 'Normal'})")
                return success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro no módulo auto_heal: {e}")
            return False
    
    def _get_health_percentage(self, screen_image: np.ndarray) -> Optional[float]:
        """Calcula percentual de vida atual analisando a barra de vida"""
        try:
            # Capturar ROI da barra de vida
            health_roi = self.screen_capture.capture_roi('health_bar', screen_image)
            if health_roi is None:
                # Se ROI não configurada, tentar detectar automaticamente
                health_roi = self._detect_health_bar(screen_image)
                if health_roi is None:
                    return None
            
            # Analisar barra de vida por cor
            health_percentage = self._analyze_health_bar(health_roi)
            return health_percentage
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular percentual de vida: {e}")
            return None
    
    def _detect_health_bar(self, screen_image: np.ndarray) -> Optional[np.ndarray]:
        """Detecta automaticamente a barra de vida na tela"""
        try:
            # Converter para HSV para melhor detecção de cor
            hsv = cv2.cvtColor(screen_image, cv2.COLOR_BGR2HSV)
            
            # Definir range de cores vermelhas/verdes típicas da barra de vida
            # Vermelho (vida baixa)
            red_lower1 = np.array([0, 50, 50])
            red_upper1 = np.array([10, 255, 255])
            red_lower2 = np.array([170, 50, 50])
            red_upper2 = np.array([180, 255, 255])
            
            # Verde (vida alta)
            green_lower = np.array([40, 50, 50])
            green_upper = np.array([80, 255, 255])
            
            # Criar máscaras
            red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
            red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            
            combined_mask = red_mask1 + red_mask2 + green_mask
            
            # Encontrar contornos
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filtrar contornos por tamanho e formato (barras são retangulares)
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                area = cv2.contourArea(contour)
                
                # Barra de vida típica: larga e baixa, tamanho moderado
                if 3 < aspect_ratio < 15 and 500 < area < 5000:
                    # Extrair região da barra
                    health_bar = screen_image[y:y+h, x:x+w]
                    return health_bar
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro na detecção automática da barra de vida: {e}")
            return None
    
    def _analyze_health_bar(self, health_bar: np.ndarray) -> Optional[float]:
        """Analisa barra de vida e retorna percentual"""
        try:
            if health_bar is None or health_bar.size == 0:
                return None
            
            # Converter para HSV
            hsv = cv2.cvtColor(health_bar, cv2.COLOR_BGR2HSV)
            
            # Definir cores de vida
            red_lower1 = np.array([0, 50, 50])
            red_upper1 = np.array([10, 255, 255])
            red_lower2 = np.array([170, 50, 50])
            red_upper2 = np.array([180, 255, 255])
            green_lower = np.array([40, 50, 50])
            green_upper = np.array([80, 255, 255])
            
            # Criar máscaras
            red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
            red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            
            health_mask = red_mask1 + red_mask2 + green_mask
            
            # Calcular percentual baseado na área colorida vs área total
            total_pixels = health_bar.shape[0] * health_bar.shape[1]
            health_pixels = cv2.countNonZero(health_mask)
            
            if total_pixels > 0:
                percentage = (health_pixels / total_pixels) * 100
                return min(100, max(0, percentage))
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro na análise da barra de vida: {e}")
            return None
    
    def _can_heal(self) -> bool:
        """Verifica se pode executar cura (cooldown)"""
        current_time = time.time()
        return (current_time - self.last_heal_time) >= self.heal_cooldown
    
    def _execute_heal(self, is_emergency: bool = False) -> bool:
        """Executa ação de cura"""
        try:
            if is_emergency:
                # Usar cura de emergência
                hotkey = self.config['emergency_hotkey']
                self.logger.info("Executando cura de EMERGÊNCIA")
            else:
                # Usar cura normal
                if self.config['use_potions']:
                    hotkey = self.config['potion_hotkey']
                elif self.config['use_spells']:
                    hotkey = self.config['spell_hotkey']
                else:
                    self.logger.warning("Nenhum método de cura configurado")
                    return False
            
            # Pressionar tecla de cura
            success = self.input_simulator.press_key(hotkey)
            
            if success:
                self.logger.debug(f"Tecla de cura pressionada: {hotkey}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao executar cura: {e}")
            return False
    
    def get_current_health(self) -> float:
        """Retorna último percentual de vida calculado"""
        return self.last_health_percentage
    
    def setup_health_bar_roi(self, x: int, y: int, width: int, height: int):
        """Configura ROI da barra de vida manualmente"""
        self.screen_capture.set_roi('health_bar', x, y, width, height)
        self.logger.info(f"ROI da barra de vida configurada: {x}, {y}, {width}x{height}")