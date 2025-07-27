"""
Auto Loot - Módulo de coleta automática de itens
Detecta monstros mortos e coleta itens valiosos automaticamente
"""

import cv2
import numpy as np
import time
from typing import List, Dict, Optional, Tuple
from modules.base_module import BaseModule
import json
import os

class AutoLoot(BaseModule):
    """Módulo de coleta automática otimizada"""
    
    def __init__(self, screen_capture, input_simulator):
        super().__init__(screen_capture, input_simulator, "auto_loot")
        
        # Configurações padrão
        self.config = {
            'enabled': True,
            'loot_radius': 150,      # Raio de coleta em pixels
            'loot_delay': 0.2,       # Delay entre coletas
            'use_optimized_loot': True,  # Usar lógica otimizada (coleta tudo, depois descarta)
            'auto_open_corpses': True,   # Abrir corpos automaticamente
            'pickup_all_items': False,   # Coletar todos os itens (ignora lista)
        }
        
        # Estados internos
        self.last_loot_time = 0
        self.loot_cooldown = 0.5
        self.corpses_processed = set()  # Cache de corpos já processados
        
        # Lista de itens valiosos (configurável)
        self.valuable_items = self._load_valuable_items()
        
        # Lista de itens descartáveis (para modo otimizado)
        self.trash_items = self._load_trash_items()
        
        # Templates para detecção
        self.corpse_templates = [
            'dead_monster.png',
            'corpse.png',
            'bones.png'
        ]
        
    def process(self, screen_image: np.ndarray) -> bool:
        """Processa detecção e coleta de loot"""
        if not self.can_execute():
            return False
        
        try:
            # Detectar corpos/loot na área
            loot_positions = self._detect_loot_opportunities(screen_image)
            
            if loot_positions and self._can_loot():
                # Processar cada posição de loot
                items_looted = 0
                for position in loot_positions[:3]:  # Limitar a 3 por ciclo
                    if self._process_loot_position(position, screen_image):
                        items_looted += 1
                        time.sleep(self.config['loot_delay'])
                
                if items_looted > 0:
                    self.mark_execution()
                    self.last_loot_time = time.time()
                    self.logger.info(f"Coletados {items_looted} grupos de itens")
                    
                    # Se usando modo otimizado, executar limpeza
                    if self.config['use_optimized_loot']:
                        self._optimize_inventory()
                    
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro no módulo auto_loot: {e}")
            return False
    
    def _detect_loot_opportunities(self, screen_image: np.ndarray) -> List[Tuple[int, int]]:
        """Detecta oportunidades de loot na tela"""
        try:
            loot_positions = []
            
            # Método 1: Detectar corpos usando templates
            corpse_positions = self._detect_corpses(screen_image)
            loot_positions.extend(corpse_positions)
            
            # Método 2: Detectar itens no chão por cor/brilho
            item_positions = self._detect_ground_items(screen_image)
            loot_positions.extend(item_positions)
            
            # Filtrar posições muito próximas (evitar duplicatas)
            filtered_positions = self._filter_nearby_positions(loot_positions, min_distance=30)
            
            # Filtrar por raio de coleta
            player_position = self._get_player_position(screen_image)
            if player_position:
                filtered_positions = self._filter_by_radius(
                    filtered_positions, player_position, self.config['loot_radius']
                )
            
            return filtered_positions
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de loot: {e}")
            return []
    
    def _detect_corpses(self, screen_image: np.ndarray) -> List[Tuple[int, int]]:
        """Detecta corpos de monstros usando template matching"""
        try:
            corpse_positions = []
            
            for template_name in self.corpse_templates:
                template_path = f"assets/templates/{template_name}"
                
                # Procurar template na tela
                result = self.screen_capture.find_template(template_path, screen_image, threshold=0.6)
                if result is not None:
                    x, y, confidence = result
                    
                    # Verificar se já processamos este corpo
                    corpse_id = f"{template_name}_{x}_{y}"
                    if corpse_id not in self.corpses_processed:
                        corpse_positions.append((x, y))
                        self.corpses_processed.add(corpse_id)
                        self.logger.debug(f"Corpo detectado: {template_name} em ({x}, {y})")
            
            # Limpar cache de corpos antigos
            if len(self.corpses_processed) > 50:
                self.corpses_processed.clear()
            
            return corpse_positions
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de corpos: {e}")
            return []
    
    def _detect_ground_items(self, screen_image: np.ndarray) -> List[Tuple[int, int]]:
        """Detecta itens no chão por análise de cor e brilho"""
        try:
            item_positions = []
            
            # Capturar área do jogo
            game_roi = self.screen_capture.capture_roi('game_area', screen_image)
            if game_roi is None:
                game_roi = screen_image
            
            # Converter para HSV
            hsv = cv2.cvtColor(game_roi, cv2.COLOR_BGR2HSV)
            
            # Definir ranges de cores comuns de itens valiosos
            # Dourado/amarelo (gold, coins)
            gold_lower = np.array([20, 100, 100])
            gold_upper = np.array([30, 255, 255])
            
            # Azul (itens mágicos)
            blue_lower = np.array([100, 100, 100])
            blue_upper = np.array([120, 255, 255])
            
            # Verde (itens raros)
            green_lower = np.array([40, 100, 100])
            green_upper = np.array([80, 255, 255])
            
            # Vermelho (itens especiais)
            red_lower1 = np.array([0, 100, 100])
            red_upper1 = np.array([10, 255, 255])
            red_lower2 = np.array([170, 100, 100])
            red_upper2 = np.array([180, 255, 255])
            
            # Criar máscaras
            gold_mask = cv2.inRange(hsv, gold_lower, gold_upper)
            blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
            red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
            
            combined_mask = gold_mask + blue_mask + green_mask + red_mask1 + red_mask2
            
            # Encontrar contornos
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filtrar contornos por tamanho (itens têm tamanho específico)
            for contour in contours:
                area = cv2.contourArea(contour)
                if 20 < area < 500:  # Tamanho típico de itens
                    x, y, w, h = cv2.boundingRect(contour)
                    center_x = x + w // 2
                    center_y = y + h // 2
                    item_positions.append((center_x, center_y))
            
            return item_positions
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de itens no chão: {e}")
            return []
    
    def _filter_nearby_positions(self, positions: List[Tuple[int, int]], min_distance: int) -> List[Tuple[int, int]]:
        """Remove posições muito próximas umas das outras"""
        if not positions:
            return []
        
        filtered = [positions[0]]
        
        for pos in positions[1:]:
            too_close = False
            for filtered_pos in filtered:
                distance = np.sqrt((pos[0] - filtered_pos[0])**2 + (pos[1] - filtered_pos[1])**2)
                if distance < min_distance:
                    too_close = True
                    break
            
            if not too_close:
                filtered.append(pos)
        
        return filtered
    
    def _filter_by_radius(self, positions: List[Tuple[int, int]], 
                         player_pos: Tuple[int, int], max_radius: int) -> List[Tuple[int, int]]:
        """Filtra posições que estão dentro do raio de coleta"""
        filtered = []
        
        for pos in positions:
            distance = np.sqrt((pos[0] - player_pos[0])**2 + (pos[1] - player_pos[1])**2)
            if distance <= max_radius:
                filtered.append(pos)
        
        return filtered
    
    def _get_player_position(self, screen_image: np.ndarray) -> Optional[Tuple[int, int]]:
        """Estima posição do jogador na tela (geralmente centro da tela)"""
        try:
            height, width = screen_image.shape[:2]
            # Assumir que jogador está no centro da tela
            return (width // 2, height // 2)
        except:
            return None
    
    def _process_loot_position(self, position: Tuple[int, int], screen_image: np.ndarray) -> bool:
        """Processa uma posição de loot específica"""
        try:
            x, y = position
            
            # Se configurado para coletar tudo, simplesmente clicar
            if self.config['pickup_all_items'] or self.config['use_optimized_loot']:
                return self._click_and_loot(x, y)
            else:
                # Analisar itens específicos na posição
                return self._selective_loot(x, y, screen_image)
            
        except Exception as e:
            self.logger.error(f"Erro ao processar posição de loot: {e}")
            return False
    
    def _click_and_loot(self, x: int, y: int) -> bool:
        """Clica na posição e tenta coletar tudo"""
        try:
            # Clique direito para abrir corpo ou item
            success = self.input_simulator.click(x, y, button='right', humanize=True)
            
            if success:
                time.sleep(0.1)  # Pequena pausa para interface carregar
                
                # Se modo otimizado, coletar tudo com Ctrl+A ou cliques múltiplos
                if self.config['use_optimized_loot']:
                    return self._loot_all_items()
                
                self.logger.debug(f"Loot executado em ({x}, {y})")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro no clique de loot: {e}")
            return False
    
    def _loot_all_items(self) -> bool:
        """Coleta todos os itens disponíveis"""
        try:
            # Método 1: Tentar Ctrl+A para selecionar tudo
            self.input_simulator.press_key('ctrl+a')
            time.sleep(0.1)
            
            # Método 2: Cliques múltiplos nas posições típicas de itens
            # (Implementar se Ctrl+A não funcionar)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar todos os itens: {e}")
            return False
    
    def _selective_loot(self, x: int, y: int, screen_image: np.ndarray) -> bool:
        """Coleta apenas itens específicos da lista de valiosos"""
        try:
            # Esta implementação seria mais complexa, envolvendo
            # análise detalhada dos itens disponíveis
            # Por simplicidade, usar método de coleta geral
            return self._click_and_loot(x, y)
            
        except Exception as e:
            self.logger.error(f"Erro no loot seletivo: {e}")
            return False
    
    def _optimize_inventory(self):
        """Remove itens indesejados do inventário (modo otimizado)"""
        try:
            # Percorrer slots do inventário e descartar itens de lixo
            for slot in range(1, 21):  # 20 slots do inventário
                if self._is_trash_item_in_slot(slot):
                    self._discard_item_from_slot(slot)
                    time.sleep(0.1)
            
        except Exception as e:
            self.logger.error(f"Erro na otimização do inventário: {e}")
    
    def _is_trash_item_in_slot(self, slot: int) -> bool:
        """Verifica se há item descartável no slot"""
        # Esta seria uma implementação complexa de reconhecimento de itens
        # Por enquanto, implementação simplificada
        return False
    
    def _discard_item_from_slot(self, slot: int):
        """Descarta item de um slot específico"""
        try:
            # Calcular posição do slot
            slot_pos = self._get_inventory_slot_position(slot)
            if slot_pos:
                x, y = slot_pos
                # Arrastar item para fora do inventário
                self.input_simulator.drag(x, y, x + 100, y + 100, duration=0.3)
        except Exception as e:
            self.logger.error(f"Erro ao descartar item do slot {slot}: {e}")
    
    def _get_inventory_slot_position(self, slot_number: int) -> Optional[Tuple[int, int]]:
        """Calcula posição de um slot do inventário (reutilizado do auto_food)"""
        try:
            if not (1 <= slot_number <= 20):
                return None
            
            # Configurações do inventário
            inventory_start_x = 600
            inventory_start_y = 300
            slot_width = 32
            slot_height = 32
            slot_spacing_x = 2
            slot_spacing_y = 2
            
            row = (slot_number - 1) // 4
            col = (slot_number - 1) % 4
            
            x = inventory_start_x + col * (slot_width + slot_spacing_x) + slot_width // 2
            y = inventory_start_y + row * (slot_height + slot_spacing_y) + slot_height // 2
            
            return (x, y)
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular posição do slot: {e}")
            return None
    
    def _can_loot(self) -> bool:
        """Verifica se pode executar loot (cooldown)"""
        current_time = time.time()
        return (current_time - self.last_loot_time) >= self.loot_cooldown
    
    def _load_valuable_items(self) -> List[str]:
        """Carrega lista de itens valiosos do arquivo de configuração"""
        try:
            config_path = "config/valuable_items.json"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                # Lista padrão
                return [
                    "gold coin", "platinum coin", "crystal coin",
                    "small ruby", "bag", "meat", "rope",
                    "magic plate armor", "crown armor", "legs"
                ]
        except Exception as e:
            self.logger.error(f"Erro ao carregar lista de itens valiosos: {e}")
            return []
    
    def _load_trash_items(self) -> List[str]:
        """Carrega lista de itens descartáveis"""
        try:
            config_path = "config/trash_items.json"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                # Lista padrão de itens de lixo
                return [
                    "torch", "candle", "bread", "roll",
                    "apple", "banana", "ham", "fish"
                ]
        except Exception as e:
            self.logger.error(f"Erro ao carregar lista de lixo: {e}")
            return []
    
    def add_valuable_item(self, item_name: str):
        """Adiciona item à lista de valiosos"""
        if item_name not in self.valuable_items:
            self.valuable_items.append(item_name)
            self.logger.info(f"Item adicionado à lista de valiosos: {item_name}")
    
    def remove_valuable_item(self, item_name: str):
        """Remove item da lista de valiosos"""
        if item_name in self.valuable_items:
            self.valuable_items.remove(item_name)
            self.logger.info(f"Item removido da lista de valiosos: {item_name}")
    
    def setup_loot_area_roi(self, x: int, y: int, width: int, height: int):
        """Configura ROI da área principal do jogo para loot"""
        self.screen_capture.set_roi('game_area', x, y, width, height)
        self.logger.info(f"ROI da área de loot configurada: {x}, {y}, {width}x{height}")