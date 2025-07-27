"""
Auto Food - Módulo de alimentação automática
Monitora status de fome e consome comida automaticamente
"""

import cv2
import numpy as np
import time
from typing import Optional, List
from modules.base_module import BaseModule

class AutoFood(BaseModule):
    """Módulo de alimentação automática"""
    
    def __init__(self, screen_capture, input_simulator):
        super().__init__(screen_capture, input_simulator, "auto_food")
        
        # Configurações padrão
        self.config = {
            'food_hotkey': 'F7',     # Tecla da comida
            'check_interval': 5.0,   # Verificar fome a cada 5 segundos
            'use_right_click': True, # Usar clique direito na comida
            'food_inventory_slot': 1, # Slot da comida no inventário (1-20)
        }
        
        # Estados internos
        self.last_food_time = 0
        self.food_cooldown = 5.0  # Cooldown mínimo entre uso de comida
        self.last_hunger_check = 0
        
        # Templates para detecção de fome
        self.hunger_indicators = [
            'hungry.png',    # Ícone de fome
            'starving.png'   # Ícone de muita fome
        ]
        
    def process(self, screen_image: np.ndarray) -> bool:
        """Processa verificação de fome e consome comida se necessário"""
        if not self.can_execute():
            return False
        
        try:
            # Verificar se está com fome
            is_hungry = self._check_hunger_status(screen_image)
            
            if is_hungry and self._can_eat():
                success = self._consume_food()
                if success:
                    self.mark_execution()
                    self.last_food_time = time.time()
                    self.logger.info("Comida consumida")
                return success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro no módulo auto_food: {e}")
            return False
    
    def _check_hunger_status(self, screen_image: np.ndarray) -> bool:
        """Verifica se o personagem está com fome"""
        try:
            # Método 1: Procurar ícones de fome na tela
            hunger_detected = self._detect_hunger_icons(screen_image)
            if hunger_detected:
                return True
            
            # Método 2: Verificar cor/brilho da área de status
            status_hungry = self._analyze_status_area(screen_image)
            if status_hungry:
                return True
            
            # Método 3: Verificar tempo desde última comida (fallback)
            time_since_food = time.time() - self.last_food_time
            if time_since_food > 180:  # 3 minutos sem comer
                self.logger.info("Detectado fome por tempo decorrido")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro na verificação de fome: {e}")
            return False
    
    def _detect_hunger_icons(self, screen_image: np.ndarray) -> bool:
        """Detecta ícones de fome na tela usando template matching"""
        try:
            for template_name in self.hunger_indicators:
                template_path = f"assets/templates/{template_name}"
                
                # Procurar template na tela
                result = self.screen_capture.find_template(template_path, screen_image, threshold=0.7)
                if result is not None:
                    x, y, confidence = result
                    self.logger.debug(f"Ícone de fome detectado: {template_name} "
                                    f"em ({x}, {y}) com confiança {confidence:.2f}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de ícones de fome: {e}")
            return False
    
    def _analyze_status_area(self, screen_image: np.ndarray) -> bool:
        """Analisa área de status para detectar fome por mudanças visuais"""
        try:
            # Capturar ROI da área de status
            status_roi = self.screen_capture.capture_roi('food_status', screen_image)
            if status_roi is None:
                return False
            
            # Converter para escala de cinza
            gray = cv2.cvtColor(status_roi, cv2.COLOR_BGR2GRAY)
            
            # Calcular brilho médio
            mean_brightness = np.mean(gray)
            
            # Se muito escuro, pode indicar fome (ícones ficam escuros quando com fome)
            if mean_brightness < 50:
                return True
            
            # Detectar cores específicas relacionadas à fome
            hsv = cv2.cvtColor(status_roi, cv2.COLOR_BGR2HSV)
            
            # Vermelho/laranja (cores típicas de alerta de fome)
            orange_lower = np.array([10, 100, 100])
            orange_upper = np.array([25, 255, 255])
            orange_mask = cv2.inRange(hsv, orange_lower, orange_upper)
            
            if cv2.countNonZero(orange_mask) > 50:  # Threshold mínimo de pixels
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro na análise da área de status: {e}")
            return False
    
    def _can_eat(self) -> bool:
        """Verifica se pode consumir comida (cooldown)"""
        current_time = time.time()
        return (current_time - self.last_food_time) >= self.food_cooldown
    
    def _consume_food(self) -> bool:
        """Consome comida usando método configurado"""
        try:
            if self.config['use_right_click']:
                # Método 1: Clique direito no slot da comida no inventário
                return self._right_click_food()
            else:
                # Método 2: Usar hotkey
                return self._use_food_hotkey()
            
        except Exception as e:
            self.logger.error(f"Erro ao consumir comida: {e}")
            return False
    
    def _right_click_food(self) -> bool:
        """Clica com botão direito na comida no inventário"""
        try:
            # Calcular posição do slot da comida no inventário
            slot_position = self._get_inventory_slot_position(self.config['food_inventory_slot'])
            if slot_position is None:
                self.logger.error("Posição do slot de comida não configurada")
                return False
            
            x, y = slot_position
            
            # Clicar com botão direito na comida
            success = self.input_simulator.click(x, y, button='right', humanize=True)
            
            if success:
                self.logger.debug(f"Clique direito na comida executado em ({x}, {y})")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro no clique direito da comida: {e}")
            return False
    
    def _use_food_hotkey(self) -> bool:
        """Usa hotkey configurada para consumir comida"""
        try:
            hotkey = self.config['food_hotkey']
            success = self.input_simulator.press_key(hotkey)
            
            if success:
                self.logger.debug(f"Hotkey de comida pressionada: {hotkey}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao usar hotkey de comida: {e}")
            return False
    
    def _get_inventory_slot_position(self, slot_number: int) -> Optional[tuple]:
        """
        Calcula posição de um slot do inventário
        Slots numerados de 1-20 (4 colunas x 5 linhas)
        """
        try:
            if not (1 <= slot_number <= 20):
                return None
            
            # Configurações do inventário (devem ser ajustadas conforme resolução)
            inventory_start_x = 600  # X inicial do inventário
            inventory_start_y = 300  # Y inicial do inventário
            slot_width = 32          # Largura de cada slot
            slot_height = 32         # Altura de cada slot
            slot_spacing_x = 2       # Espaçamento horizontal
            slot_spacing_y = 2       # Espaçamento vertical
            
            # Calcular linha e coluna (0-indexado)
            row = (slot_number - 1) // 4
            col = (slot_number - 1) % 4
            
            # Calcular posição central do slot
            x = inventory_start_x + col * (slot_width + slot_spacing_x) + slot_width // 2
            y = inventory_start_y + row * (slot_height + slot_spacing_y) + slot_height // 2
            
            return (x, y)
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular posição do slot: {e}")
            return None
    
    def setup_food_status_roi(self, x: int, y: int, width: int, height: int):
        """Configura ROI da área de status de comida"""
        self.screen_capture.set_roi('food_status', x, y, width, height)
        self.logger.info(f"ROI de status de comida configurada: {x}, {y}, {width}x{height}")
    
    def setup_inventory_position(self, start_x: int, start_y: int):
        """Configura posição inicial do inventário"""
        self.inventory_start_x = start_x
        self.inventory_start_y = start_y
        self.logger.info(f"Posição do inventário configurada: ({start_x}, {start_y})")