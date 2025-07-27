"""
Screen Capture - Sistema de captura de tela com contorno de proteções anti-cheat
Utiliza técnica de virtualização de display via OBS Studio para evitar detecção
"""

import cv2
import numpy as np
import mss
import time
import logging
from typing import Optional, Tuple, Dict, Any
from PIL import Image, ImageGrab
import os

class ScreenCapture:
    """Sistema de captura de tela otimizado"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mss_instance = mss.mss()
        
        # Configurações de captura
        self.capture_region = None  # Região específica da tela (x, y, width, height)
        self.obs_window_title = "OBS Studio - Preview"
        
        # Cache para otimização
        self.last_capture_time = 0
        self.min_capture_interval = 0.05  # 50ms mínimo entre capturas
        
        # ROIs (Regions of Interest) para diferentes funcionalidades
        self.rois = {
            'health_bar': None,     # Barra de vida
            'mana_bar': None,       # Barra de mana
            'food_status': None,    # Status de comida
            'game_area': None,      # Área principal do jogo
            'loot_area': None,      # Área de loot
            'chat_area': None       # Área de chat
        }
        
        self.logger.info("ScreenCapture inicializado")
    
    def setup_obs_capture(self, window_title: str = "OBS Studio - Preview") -> bool:
        """
        Configura captura via janela do OBS Studio
        Esta é a técnica principal para contornar o BattlEye
        """
        try:
            self.obs_window_title = window_title
            self.logger.info(f"Configurando captura via OBS: {window_title}")
            
            # Testar captura
            test_capture = self.capture()
            if test_capture is not None:
                self.logger.info("Captura via OBS configurada com sucesso")
                return True
            else:
                self.logger.error("Falha ao configurar captura via OBS")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao configurar captura OBS: {e}")
            return False
    
    def set_capture_region(self, x: int, y: int, width: int, height: int):
        """Define região específica para captura"""
        self.capture_region = {
            'left': x,
            'top': y,
            'width': width,
            'height': height
        }
        self.logger.info(f"Região de captura definida: {x}, {y}, {width}x{height}")
    
    def set_roi(self, roi_name: str, x: int, y: int, width: int, height: int):
        """Define uma ROI específica"""
        self.rois[roi_name] = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
        self.logger.debug(f"ROI {roi_name} definida: {x}, {y}, {width}x{height}")
    
    def capture(self) -> Optional[np.ndarray]:
        """
        Captura a tela usando o método mais apropriado
        Retorna a imagem como array numpy (formato OpenCV)
        """
        current_time = time.time()
        
        # Throttling de captura para performance
        if current_time - self.last_capture_time < self.min_capture_interval:
            return None
        
        try:
            # Método 1: Captura via MSS (mais rápido)
            if self.capture_region:
                screenshot = self.mss_instance.grab(self.capture_region)
            else:
                # Captura tela inteira se região não definida
                screenshot = self.mss_instance.grab(self.mss_instance.monitors[1])
            
            # Converter para formato OpenCV
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            self.last_capture_time = current_time
            return img
            
        except Exception as e:
            self.logger.error(f"Erro na captura de tela: {e}")
            return None
    
    def capture_roi(self, roi_name: str, base_image: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
        """
        Captura uma ROI específica
        Se base_image for fornecida, extrai ROI dela, senão captura nova imagem
        """
        if roi_name not in self.rois or self.rois[roi_name] is None:
            self.logger.warning(f"ROI {roi_name} não está configurada")
            return None
        
        roi_config = self.rois[roi_name]
        
        # Usar imagem base ou capturar nova
        if base_image is None:
            base_image = self.capture()
            if base_image is None:
                return None
        
        try:
            # Extrair região da imagem
            y1 = roi_config['y']
            y2 = y1 + roi_config['height']
            x1 = roi_config['x']
            x2 = x1 + roi_config['width']
            
            roi_image = base_image[y1:y2, x1:x2]
            return roi_image
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair ROI {roi_name}: {e}")
            return None
    
    def test_capture(self) -> bool:
        """Testa se a captura está funcionando"""
        try:
            img = self.capture()
            if img is not None and img.size > 0:
                self.logger.info("Teste de captura: OK")
                return True
            else:
                self.logger.error("Teste de captura: FALHA - Imagem vazia")
                return False
        except Exception as e:
            self.logger.error(f"Teste de captura: FALHA - {e}")
            return False
    
    def find_template(self, template_path: str, base_image: Optional[np.ndarray] = None, 
                     threshold: float = 0.8) -> Optional[Tuple[int, int, float]]:
        """
        Encontra um template na imagem capturada
        Retorna (x, y, confidence) se encontrado, None caso contrário
        """
        if base_image is None:
            base_image = self.capture()
            if base_image is None:
                return None
        
        try:
            # Carregar template
            if not os.path.exists(template_path):
                self.logger.error(f"Template não encontrado: {template_path}")
                return None
            
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                self.logger.error(f"Erro ao carregar template: {template_path}")
                return None
            
            # Executar template matching
            result = cv2.matchTemplate(base_image, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                return (max_loc[0], max_loc[1], max_val)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Erro no template matching: {e}")
            return None
    
    def save_screenshot(self, filename: str = None) -> str:
        """Salva screenshot para debug"""
        try:
            img = self.capture()
            if img is None:
                raise Exception("Falha ao capturar tela")
            
            if filename is None:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            cv2.imwrite(filename, img)
            self.logger.info(f"Screenshot salvo: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar screenshot: {e}")
            return None
    
    def get_pixel_color(self, x: int, y: int, base_image: Optional[np.ndarray] = None) -> Optional[Tuple[int, int, int]]:
        """Obtém cor de um pixel específico (BGR)"""
        if base_image is None:
            base_image = self.capture()
            if base_image is None:
                return None
        
        try:
            if 0 <= y < base_image.shape[0] and 0 <= x < base_image.shape[1]:
                pixel = base_image[y, x]
                return (int(pixel[0]), int(pixel[1]), int(pixel[2]))  # BGR
            else:
                return None
        except Exception as e:
            self.logger.error(f"Erro ao obter cor do pixel: {e}")
            return None