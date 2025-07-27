"""
Cavebot - Módulo de navegação automática e caça
Sistema de waypoints, ataque de monstros e navegação inteligente
"""

import cv2
import numpy as np
import time
import json
import os
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from modules.base_module import BaseModule

class WaypointType(Enum):
    """Tipos de waypoint"""
    WALK = "walk"
    ATTACK = "attack"
    USE_STAIRS = "stairs"
    USE_HOLE = "hole"
    USE_ROPE = "rope"
    USE_SHOVEL = "shovel"
    WAIT = "wait"
    LABEL = "label"
    GOTO_LABEL = "goto_label"

@dataclass
class Waypoint:
    """Ponto de navegação"""
    x: int
    y: int
    type: WaypointType
    action: str = ""
    delay: float = 0.0
    condition: str = ""

class CavebotState(Enum):
    """Estados do cavebot"""
    STOPPED = "stopped"
    WALKING = "walking"
    FIGHTING = "fighting"
    USING_STAIRS = "using_stairs"
    WAITING = "waiting"
    STUCK = "stuck"

class Cavebot(BaseModule):
    """Sistema de navegação automática e caça"""
    
    def __init__(self, screen_capture, input_simulator):
        super().__init__(screen_capture, input_simulator, "cavebot")
        
        # Configurações padrão
        self.config = {
            'enabled': False,
            'attack_enabled': True,
            'walk_speed': 1.0,           # Velocidade de movimento
            'attack_range': 5,           # Alcance de ataque em SQMs
            'monster_priority': [],      # Lista de prioridade de monstros
            'avoid_monsters': [],        # Monstros para evitar
            'stuck_threshold': 5.0,      # Tempo para considerar travado
            'waypoint_precision': 10,    # Precisão para considerar waypoint alcançado
        }
        
        # Estados internos
        self.state = CavebotState.STOPPED
        self.waypoints: List[Waypoint] = []
        self.current_waypoint_index = 0
        self.script_loaded = False
        self.script_path = ""
        
        # Navegação
        self.last_position = None
        self.position_check_time = 0
        self.stuck_start_time = None
        self.last_movement_time = 0
        
        # Combate
        self.current_target = None
        self.last_attack_time = 0
        self.attack_cooldown = 1.5
        self.monsters_on_screen = []
        
        # Templates para detecção
        self.monster_templates = self._load_monster_templates()
        self.navigation_templates = {
            'stairs_up': 'stairs_up.png',
            'stairs_down': 'stairs_down.png',
            'hole': 'hole.png',
            'rope_spot': 'rope_spot.png'
        }
        
    def process(self, screen_image: np.ndarray) -> bool:
        """Processa lógica principal do cavebot"""
        if not self.can_execute() or not self.script_loaded:
            return False
        
        try:
            # Atualizar estado atual
            self._update_position(screen_image)
            self._update_monsters(screen_image)
            
            # Máquina de estados
            action_taken = False
            
            if self.state == CavebotState.STOPPED:
                if self.config['enabled']:
                    self.state = CavebotState.WALKING
                    action_taken = True
            
            elif self.state == CavebotState.WALKING:
                action_taken = self._process_walking_state(screen_image)
            
            elif self.state == CavebotState.FIGHTING:
                action_taken = self._process_fighting_state(screen_image)
            
            elif self.state == CavebotState.USING_STAIRS:
                action_taken = self._process_stairs_state(screen_image)
            
            elif self.state == CavebotState.WAITING:
                action_taken = self._process_waiting_state()
            
            elif self.state == CavebotState.STUCK:
                action_taken = self._process_stuck_state(screen_image)
            
            if action_taken:
                self.mark_execution()
            
            return action_taken
            
        except Exception as e:
            self.logger.error(f"Erro no módulo cavebot: {e}")
            return False
    
    def _process_walking_state(self, screen_image: np.ndarray) -> bool:
        """Processa estado de caminhada"""
        try:
            # Verificar se há monstros para atacar
            if self.config['attack_enabled']:
                target_monster = self._find_priority_monster()
                if target_monster:
                    self.current_target = target_monster
                    self.state = CavebotState.FIGHTING
                    self.logger.info(f"Alvo encontrado: {target_monster['name']}")
                    return True
            
            # Verificar se chegou no waypoint atual
            current_waypoint = self._get_current_waypoint()
            if current_waypoint is None:
                self.logger.info("Script finalizado, reiniciando")
                self.current_waypoint_index = 0
                return False
            
            if self._reached_waypoint(current_waypoint):
                return self._execute_waypoint(current_waypoint, screen_image)
            
            # Mover em direção ao waypoint
            return self._move_to_waypoint(current_waypoint)
            
        except Exception as e:
            self.logger.error(f"Erro no estado de caminhada: {e}")
            return False
    
    def _process_fighting_state(self, screen_image: np.ndarray) -> bool:
        """Processa estado de combate"""
        try:
            if not self.current_target:
                self.state = CavebotState.WALKING
                return False
            
            # Verificar se alvo ainda está visível
            if not self._is_monster_visible(self.current_target):
                self.current_target = None
                self.state = CavebotState.WALKING
                self.logger.info("Alvo perdido, retornando à navegação")
                return False
            
            # Executar ataque
            if self._can_attack():
                success = self._attack_monster(self.current_target)
                if success:
                    self.last_attack_time = time.time()
                    self.logger.debug(f"Atacando {self.current_target['name']}")
                return success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro no estado de combate: {e}")
            return False
    
    def _process_stairs_state(self, screen_image: np.ndarray) -> bool:
        """Processa uso de escadas/buracos"""
        try:
            # Implementar lógica específica para escadas
            # Por enquanto, apenas avançar waypoint
            self._advance_waypoint()
            self.state = CavebotState.WALKING
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no estado de escadas: {e}")
            return False
    
    def _process_waiting_state(self) -> bool:
        """Processa estado de espera"""
        try:
            current_waypoint = self._get_current_waypoint()
            if current_waypoint and current_waypoint.delay > 0:
                if time.time() - self.last_movement_time >= current_waypoint.delay:
                    self._advance_waypoint()
                    self.state = CavebotState.WALKING
                    return True
            else:
                self.state = CavebotState.WALKING
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro no estado de espera: {e}")
            return False
    
    def _process_stuck_state(self, screen_image: np.ndarray) -> bool:
        """Processa estado de travamento"""
        try:
            # Tentar destravar com movimentos aleatórios
            import random
            directions = ['up', 'down', 'left', 'right']
            random_direction = random.choice(directions)
            
            self._move_direction(random_direction)
            
            # Após tentativa, voltar ao estado normal
            self.state = CavebotState.WALKING
            self.stuck_start_time = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no estado de travamento: {e}")
            return False
    
    def _update_position(self, screen_image: np.ndarray):
        """Atualiza posição atual do jogador"""
        try:
            # Detectar posição do jogador na tela
            # Por simplicidade, assumir centro da tela
            height, width = screen_image.shape[:2]
            current_position = (width // 2, height // 2)
            
            # Verificar se está travado
            if self.last_position:
                if self._positions_equal(current_position, self.last_position):
                    if self.stuck_start_time is None:
                        self.stuck_start_time = time.time()
                    elif time.time() - self.stuck_start_time > self.config['stuck_threshold']:
                        if self.state != CavebotState.STUCK:
                            self.state = CavebotState.STUCK
                            self.logger.warning("Jogador travado detectado")
                else:
                    self.stuck_start_time = None
            
            self.last_position = current_position
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar posição: {e}")
    
    def _update_monsters(self, screen_image: np.ndarray):
        """Atualiza lista de monstros visíveis"""
        try:
            self.monsters_on_screen = []
            
            # Detectar monstros usando templates
            for monster_name, template_path in self.monster_templates.items():
                results = self._find_all_templates(template_path, screen_image, threshold=0.7)
                
                for x, y, confidence in results:
                    monster = {
                        'name': monster_name,
                        'x': x,
                        'y': y,
                        'confidence': confidence,
                        'distance': self._calculate_distance_to_player(x, y)
                    }
                    self.monsters_on_screen.append(monster)
            
            # Ordenar por prioridade e distância
            self.monsters_on_screen.sort(key=lambda m: (
                self._get_monster_priority(m['name']),
                m['distance']
            ))
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar monstros: {e}")
    
    def _find_priority_monster(self) -> Optional[Dict]:
        """Encontra monstro de maior prioridade para atacar"""
        try:
            for monster in self.monsters_on_screen:
                # Verificar se não está na lista de evitar
                if monster['name'] in self.config['avoid_monsters']:
                    continue
                
                # Verificar distância
                if monster['distance'] <= self.config['attack_range'] * 32:  # 32px por SQM
                    return monster
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao encontrar monstro prioritário: {e}")
            return None
    
    def _get_current_waypoint(self) -> Optional[Waypoint]:
        """Retorna waypoint atual"""
        if 0 <= self.current_waypoint_index < len(self.waypoints):
            return self.waypoints[self.current_waypoint_index]
        return None
    
    def _reached_waypoint(self, waypoint: Waypoint) -> bool:
        """Verifica se chegou no waypoint"""
        if not self.last_position:
            return False
        
        distance = np.sqrt(
            (self.last_position[0] - waypoint.x) ** 2 +
            (self.last_position[1] - waypoint.y) ** 2
        )
        
        return distance <= self.config['waypoint_precision']
    
    def _execute_waypoint(self, waypoint: Waypoint, screen_image: np.ndarray) -> bool:
        """Executa ação do waypoint"""
        try:
            if waypoint.type == WaypointType.WALK:
                self._advance_waypoint()
                return True
            
            elif waypoint.type == WaypointType.USE_STAIRS:
                return self._use_stairs(waypoint, screen_image)
            
            elif waypoint.type == WaypointType.USE_HOLE:
                return self._use_hole(waypoint, screen_image)
            
            elif waypoint.type == WaypointType.USE_ROPE:
                return self._use_rope(waypoint, screen_image)
            
            elif waypoint.type == WaypointType.WAIT:
                self.state = CavebotState.WAITING
                self.last_movement_time = time.time()
                return True
            
            elif waypoint.type == WaypointType.GOTO_LABEL:
                return self._goto_label(waypoint.action)
            
            else:
                self._advance_waypoint()
                return True
            
        except Exception as e:
            self.logger.error(f"Erro ao executar waypoint: {e}")
            return False
    
    def _move_to_waypoint(self, waypoint: Waypoint) -> bool:
        """Move em direção ao waypoint"""
        try:
            if not self.last_position:
                return False
            
            # Calcular direção
            dx = waypoint.x - self.last_position[0]
            dy = waypoint.y - self.last_position[1]
            
            # Determinar direção principal
            if abs(dx) > abs(dy):
                direction = 'right' if dx > 0 else 'left'
            else:
                direction = 'down' if dy > 0 else 'up'
            
            return self._move_direction(direction)
            
        except Exception as e:
            self.logger.error(f"Erro ao mover para waypoint: {e}")
            return False
    
    def _move_direction(self, direction: str) -> bool:
        """Move em uma direção específica"""
        try:
            direction_keys = {
                'up': 'Up',
                'down': 'Down',
                'left': 'Left',
                'right': 'Right'
            }
            
            if direction in direction_keys:
                key = direction_keys[direction]
                success = self.input_simulator.press_key(key)
                if success:
                    self.last_movement_time = time.time()
                return success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao mover na direção {direction}: {e}")
            return False
    
    def _attack_monster(self, monster: Dict) -> bool:
        """Ataca um monstro"""
        try:
            # Clicar no monstro para atacar
            success = self.input_simulator.click(monster['x'], monster['y'], humanize=True)
            
            if success:
                self.logger.debug(f"Atacando monstro em ({monster['x']}, {monster['y']})")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao atacar monstro: {e}")
            return False
    
    def _can_attack(self) -> bool:
        """Verifica se pode atacar (cooldown)"""
        return (time.time() - self.last_attack_time) >= self.attack_cooldown
    
    def _advance_waypoint(self):
        """Avança para próximo waypoint"""
        self.current_waypoint_index += 1
        if self.current_waypoint_index >= len(self.waypoints):
            self.current_waypoint_index = 0  # Reiniciar script
    
    def load_script(self, script_path: str) -> bool:
        """Carrega script de waypoints"""
        try:
            if not os.path.exists(script_path):
                self.logger.error(f"Script não encontrado: {script_path}")
                return False
            
            with open(script_path, 'r', encoding='utf-8') as f:
                script_data = json.load(f)
            
            # Converter dados para waypoints
            self.waypoints = []
            for wp_data in script_data.get('waypoints', []):
                waypoint = Waypoint(
                    x=wp_data['x'],
                    y=wp_data['y'],
                    type=WaypointType(wp_data.get('type', 'walk')),
                    action=wp_data.get('action', ''),
                    delay=wp_data.get('delay', 0.0),
                    condition=wp_data.get('condition', '')
                )
                self.waypoints.append(waypoint)
            
            self.script_path = script_path
            self.script_loaded = True
            self.current_waypoint_index = 0
            
            self.logger.info(f"Script carregado: {script_path} ({len(self.waypoints)} waypoints)")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar script: {e}")
            return False
    
    def save_script(self, script_path: str) -> bool:
        """Salva script atual"""
        try:
            script_data = {
                'name': os.path.basename(script_path),
                'created': time.strftime('%Y-%m-%d %H:%M:%S'),
                'waypoints': []
            }
            
            for wp in self.waypoints:
                wp_data = {
                    'x': wp.x,
                    'y': wp.y,
                    'type': wp.type.value,
                    'action': wp.action,
                    'delay': wp.delay,
                    'condition': wp.condition
                }
                script_data['waypoints'].append(wp_data)
            
            with open(script_path, 'w', encoding='utf-8') as f:
                json.dump(script_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Script salvo: {script_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar script: {e}")
            return False
    
    def add_waypoint(self, x: int, y: int, wp_type: WaypointType = WaypointType.WALK, 
                    action: str = "", delay: float = 0.0):
        """Adiciona waypoint ao script"""
        waypoint = Waypoint(x, y, wp_type, action, delay)
        self.waypoints.append(waypoint)
        self.logger.info(f"Waypoint adicionado: ({x}, {y}) - {wp_type.value}")
    
    def clear_waypoints(self):
        """Limpa todos os waypoints"""
        self.waypoints.clear()
        self.current_waypoint_index = 0
        self.script_loaded = False
        self.logger.info("Waypoints limpos")
    
    def start_cavebot(self):
        """Inicia o cavebot"""
        if self.script_loaded:
            self.config['enabled'] = True
            self.state = CavebotState.WALKING
            self.logger.info("Cavebot iniciado")
        else:
            self.logger.error("Nenhum script carregado")
    
    def stop_cavebot(self):
        """Para o cavebot"""
        self.config['enabled'] = False
        self.state = CavebotState.STOPPED
        self.current_target = None
        self.logger.info("Cavebot parado")
    
    def _load_monster_templates(self) -> Dict[str, str]:
        """Carrega templates de monstros"""
        try:
            # Templates padrão
            return {
                'rat': 'monsters/rat.png',
                'spider': 'monsters/spider.png',
                'skeleton': 'monsters/skeleton.png',
                'orc': 'monsters/orc.png',
                'troll': 'monsters/troll.png'
            }
        except Exception as e:
            self.logger.error(f"Erro ao carregar templates de monstros: {e}")
            return {}
    
    def _get_monster_priority(self, monster_name: str) -> int:
        """Retorna prioridade do monstro (menor = maior prioridade)"""
        try:
            if monster_name in self.config['monster_priority']:
                return self.config['monster_priority'].index(monster_name)
            return 999  # Baixa prioridade para monstros não listados
        except:
            return 999
    
    def _calculate_distance_to_player(self, x: int, y: int) -> float:
        """Calcula distância até o jogador"""
        if not self.last_position:
            return float('inf')
        
        return np.sqrt(
            (x - self.last_position[0]) ** 2 +
            (y - self.last_position[1]) ** 2
        )
    
    def _positions_equal(self, pos1: Tuple[int, int], pos2: Tuple[int, int], threshold: int = 5) -> bool:
        """Verifica se duas posições são iguais (com threshold)"""
        return abs(pos1[0] - pos2[0]) <= threshold and abs(pos1[1] - pos2[1]) <= threshold
    
    def _is_monster_visible(self, monster: Dict) -> bool:
        """Verifica se monstro ainda está visível"""
        # Verificar se monstro ainda está na lista atual
        for current_monster in self.monsters_on_screen:
            if (current_monster['name'] == monster['name'] and
                abs(current_monster['x'] - monster['x']) <= 20 and
                abs(current_monster['y'] - monster['y']) <= 20):
                return True
        return False
    
    def _find_all_templates(self, template_path: str, screen_image: np.ndarray, 
                          threshold: float = 0.8) -> List[Tuple[int, int, float]]:
        """Encontra todas as ocorrências de um template"""
        try:
            if not os.path.exists(template_path):
                return []
            
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                return []
            
            result = cv2.matchTemplate(screen_image, template, cv2.TM_CCOEFF_NORMED)
            
            # Encontrar todos os matches acima do threshold
            locations = np.where(result >= threshold)
            matches = []
            
            for pt in zip(*locations[::-1]):
                matches.append((pt[0], pt[1], result[pt[1], pt[0]]))
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Erro no template matching múltiplo: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status atual do cavebot"""
        return {
            'state': self.state.value,
            'script_loaded': self.script_loaded,
            'current_waypoint': self.current_waypoint_index,
            'total_waypoints': len(self.waypoints),
            'monsters_visible': len(self.monsters_on_screen),
            'current_target': self.current_target['name'] if self.current_target else None
        }