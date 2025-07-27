"""
Auto Mana - Módulo de gerenciamento automático de mana
Monitora a barra de mana e usa poções/magias para restaurar
"""

import cv2
import numpy as np
import time
from typing import Optional
from modules.base_module import BaseModule

class AutoMana(BaseModule):
    """Módulo de gerenciamento automático de mana"""
    
    def __init__(self, screen_capture, input_simulator):
        super().__init__(screen_capture, input_simulator, "auto_mana")
        
        # Configurações padrão
        self.config = {
            'mana_threshold': 60,    # Percentual de mana para usar poção
            'use_potions': True,     # Usar poções de mana
            'use_spells': False,     # Usar magias de mana
            'potion_hotkey': 'F3',   # Tecla da poção de mana
            'spell_hotkey': 'F6',    # Tecla da magia de mana
            'emergency_threshold': 20,  # Percentual crítico
            'emergency_hotkey': 'F4',   # Tecla de emergência
        }
        
        # Estados internos
        self.last_mana_check = 0
        self.mana_check_interval = 0.3  # Verificar mana a cada 300ms
        self.last_mana_time = 0
        self.mana_cooldown = 1.2  # Cooldown entre uso de mana
        
        self.last_mana_percentage = 100
        
    def process(self, screen_image: np.ndarray) -> bool:
        """Processa verificação de mana e executa ação se necessário"""
        if not self.can_execute():
            return False
        
        try:
            # Verificar mana atual
            mana_percentage = self._get_mana_percentage(screen_image)
            if mana_percentage is None:
                return False
            
            self.last_mana_percentage = mana_percentage
            
            # Determinar se precisa de mana
            needs_mana = False
            is_emergency = False
            
            if mana_percentage <= self.config['emergency_threshold']:
                needs_mana = True
                is_emergency = True
            elif mana_percentage <= self.config['mana_threshold']:
                needs_mana = True
            
            # Executar ação de mana se necessário
            if needs_mana and self._can_use_mana():
                success = self._execute_mana_action(is_emergency)
                if success:
                    self.mark_execution()
                    self.last_mana_time = time.time()
                    self.logger.info(f"Ação de mana executada - Mana: {mana_percentage}% "
                                   f"({'EMERGÊNCIA' if is_emergency else 'Normal'})")
                return success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro no módulo auto_mana: {e}")
            return False
    
    def _get_mana_percentage(self, screen_image: np.ndarray) -> Optional[float]:
        """Calcula percentual de mana atual analisando a barra de mana"""
        try:
            # Capturar ROI da barra de mana
            mana_roi = self.screen_capture.capture_roi('mana_bar', screen_image)
            if mana_roi is None:
                # Se ROI não configurada, tentar detectar automaticamente
                mana_roi = self._detect_mana_bar(screen_image)
                if mana_roi is None:
                    return None
            
            # Analisar barra de mana por cor
            mana_percentage = self._analyze_mana_bar(mana_roi)
            return mana_percentage
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular percentual de mana: {e}")
            return None
    
    def _detect_mana_bar(self, screen_image: np.ndarray) -> Optional[np.ndarray]:
        """Detecta automaticamente a barra de mana na tela"""
        try:
            # Converter para HSV
            hsv = cv2.cvtColor(screen_image, cv2.COLOR_BGR2HSV)
            
            # Definir range de cores azuis típicas da barra de mana
            blue_lower = np.array([100, 50, 50])
            blue_upper = np.array([130, 255, 255])
            
            # Azul claro/ciano
            cyan_lower = np.array([80, 50, 50])
            cyan_upper = np.array([100, 255, 255])
            
            # Criar máscaras
            blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
            cyan_mask = cv2.inRange(hsv, cyan_lower, cyan_upper)
            
            combined_mask = blue_mask + cyan_mask
            
            # Encontrar contornos
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filtrar contornos por tamanho e formato
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                area = cv2.contourArea(contour)
                
                # Barra de mana típica: larga e baixa, tamanho moderado
                if 3 < aspect_ratio < 15 and 500 < area < 5000:
                    # Extrair região da barra
                    mana_bar = screen_image[y:y+h, x:x+w]
                    return mana_bar
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro na detecção automática da barra de mana: {e}")
            return None
    
    def _analyze_mana_bar(self, mana_bar: np.ndarray) -> Optional[float]:
        """Analisa barra de mana e retorna percentual"""
        try:
            if mana_bar is None or mana_bar.size == 0:
                return None
            
            # Converter para HSV
            hsv = cv2.cvtColor(mana_bar, cv2.COLOR_BGR2HSV)
            
            # Definir cores de mana
            blue_lower = np.array([100, 50, 50])
            blue_upper = np.array([130, 255, 255])
            cyan_lower = np.array([80, 50, 50])
            cyan_upper = np.array([100, 255, 255])
            
            # Criar máscaras
            blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
            cyan_mask = cv2.inRange(hsv, cyan_lower, cyan_upper)
            
            mana_mask = blue_mask + cyan_mask
            
            # Calcular percentual baseado na área colorida vs área total
            total_pixels = mana_bar.shape[0] * mana_bar.shape[1]
            mana_pixels = cv2.countNonZero(mana_mask)
            
            if total_pixels > 0:
                percentage = (mana_pixels / total_pixels) * 100
                return min(100, max(0, percentage))
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro na análise da barra de mana: {e}")
            return None
    
    def _can_use_mana(self) -> bool:
        """Verifica se pode executar ação de mana (cooldown)"""
        current_time = time.time()
        return (current_time - self.last_mana_time) >= self.mana_cooldown
    
    def _execute_mana_action(self, is_emergency: bool = False) -> bool:
        """Executa ação de restauração de mana"""
        try:
            if is_emergency:
                # Usar restauração de emergência
                hotkey = self.config['emergency_hotkey']
                self.logger.info("Executando restauração de mana de EMERGÊNCIA")
            else:
                # Usar restauração normal
                if self.config['use_potions']:
                    hotkey = self.config['potion_hotkey']
                elif self.config['use_spells']:
                    hotkey = self.config['spell_hotkey']
                else:
                    self.logger.warning("Nenhum método de restauração de mana configurado")
                    return False
            
            # Pressionar tecla de mana
            success = self.input_simulator.press_key(hotkey)
            
            if success:
                self.logger.debug(f"Tecla de mana pressionada: {hotkey}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao executar ação de mana: {e}")
            return False
    
    def get_current_mana(self) -> float:
        """Retorna último percentual de mana calculado"""
        return self.last_mana_percentage
    
    def setup_mana_bar_roi(self, x: int, y: int, width: int, height: int):
        """Configura ROI da barra de mana manualmente"""
        self.screen_capture.set_roi('mana_bar', x, y, width, height)
        self.logger.info(f"ROI da barra de mana configurada: {x}, {y}, {width}x{height}")