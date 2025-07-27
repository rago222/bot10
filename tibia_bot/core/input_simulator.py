"""
Input Simulator - Simulação de input com randomização para evitar detecção
Simula mouse e teclado de forma humanizada
"""

import pyautogui
import random
import time
import logging
import math
from typing import Tuple, List, Optional
from pynput import mouse, keyboard
import threading

class InputSimulator:
    """Simulador de input humanizado"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configurações de segurança do PyAutoGUI
        pyautogui.PAUSE = 0.01  # Pausa mínima entre comandos
        pyautogui.FAILSAFE = True  # Mover mouse para canto superior esquerdo para parar
        
        # Configurações de randomização
        self.mouse_speed_base = 0.5  # Velocidade base do mouse
        self.mouse_speed_variance = 0.3  # Variação na velocidade
        self.click_delay_base = 0.05  # Delay base entre cliques
        self.click_delay_variance = 0.03  # Variação no delay
        
        # Histórico para análise anti-detecção
        self.action_history = []
        self.max_history = 100
        
        self.logger.info("InputSimulator inicializado")
    
    def move_mouse(self, x: int, y: int, humanize: bool = True) -> bool:
        """
        Move o mouse para coordenadas específicas
        Se humanize=True, adiciona curva natural e velocidade variável
        """
        try:
            current_x, current_y = pyautogui.position()
            
            if humanize:
                # Calcular trajetória curva
                points = self._generate_curved_path(current_x, current_y, x, y)
                
                # Mover através dos pontos com velocidade variável
                for point_x, point_y in points:
                    pyautogui.moveTo(point_x, point_y)
                    # Delay aleatório pequeno
                    time.sleep(random.uniform(0.001, 0.005))
            else:
                # Movimento direto
                pyautogui.moveTo(x, y)
            
            self._record_action('mouse_move', {'x': x, 'y': y})
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao mover mouse: {e}")
            return False
    
    def click(self, x: int, y: int, button: str = 'left', humanize: bool = True) -> bool:
        """
        Clica em coordenadas específicas
        button pode ser 'left', 'right' ou 'middle'
        """
        try:
            # Mover mouse para posição
            if not self.move_mouse(x, y, humanize):
                return False
            
            # Adicionar jitter pequeno na posição final
            if humanize:
                jitter_x = random.randint(-2, 2)
                jitter_y = random.randint(-2, 2)
                pyautogui.moveTo(x + jitter_x, y + jitter_y)
            
            # Delay antes do clique
            if humanize:
                delay = self.click_delay_base + random.uniform(0, self.click_delay_variance)
                time.sleep(delay)
            
            # Executar clique
            pyautogui.click(button=button)
            
            # Delay após clique
            if humanize:
                delay = self.click_delay_base + random.uniform(0, self.click_delay_variance)
                time.sleep(delay)
            
            self._record_action('click', {'x': x, 'y': y, 'button': button})
            self.logger.debug(f"Clique executado: ({x}, {y}) - {button}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao clicar: {e}")
            return False
    
    def double_click(self, x: int, y: int, humanize: bool = True) -> bool:
        """Executa duplo clique"""
        try:
            if not self.move_mouse(x, y, humanize):
                return False
            
            # Primeiro clique
            pyautogui.click()
            
            # Delay entre cliques (humanizado)
            if humanize:
                delay = random.uniform(0.05, 0.15)
            else:
                delay = 0.05
            time.sleep(delay)
            
            # Segundo clique
            pyautogui.click()
            
            self._record_action('double_click', {'x': x, 'y': y})
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no duplo clique: {e}")
            return False
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
             duration: float = 0.5, humanize: bool = True) -> bool:
        """Arrasta de um ponto para outro"""
        try:
            # Mover para posição inicial
            if not self.move_mouse(start_x, start_y, humanize):
                return False
            
            # Executar drag
            if humanize:
                # Drag com curva natural
                pyautogui.drag(end_x - start_x, end_y - start_y, 
                              duration=duration + random.uniform(-0.1, 0.1))
            else:
                pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
            
            self._record_action('drag', {
                'start': (start_x, start_y), 
                'end': (end_x, end_y), 
                'duration': duration
            })
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no drag: {e}")
            return False
    
    def press_key(self, key: str, hold_time: float = None) -> bool:
        """
        Pressiona uma tecla
        key pode ser um caractere ou nome de tecla especial (enter, space, etc.)
        """
        try:
            if hold_time:
                pyautogui.keyDown(key)
                time.sleep(hold_time)
                pyautogui.keyUp(key)
            else:
                pyautogui.press(key)
            
            self._record_action('key_press', {'key': key, 'hold_time': hold_time})
            self.logger.debug(f"Tecla pressionada: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao pressionar tecla: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.05, humanize: bool = True) -> bool:
        """
        Digite texto com intervalo entre caracteres
        Se humanize=True, varia o intervalo e adiciona erros ocasionais
        """
        try:
            if humanize:
                # Digitação humanizada com variação de velocidade
                for char in text:
                    pyautogui.write(char)
                    # Intervalo variável
                    delay = interval + random.uniform(-0.02, 0.05)
                    time.sleep(max(0.01, delay))
                    
                    # Pequena chance de "erro de digitação" (mais realista)
                    if random.random() < 0.02:  # 2% de chance
                        # Pressionar backspace e reescrever caractere
                        time.sleep(0.1)
                        pyautogui.press('backspace')
                        time.sleep(0.1)
                        pyautogui.write(char)
            else:
                pyautogui.write(text, interval=interval)
            
            self._record_action('type_text', {'text': text, 'length': len(text)})
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao digitar texto: {e}")
            return False
    
    def scroll(self, x: int, y: int, clicks: int, direction: str = 'up') -> bool:
        """
        Scroll do mouse em posição específica
        direction pode ser 'up' ou 'down'
        clicks é o número de "cliques" do scroll
        """
        try:
            # Mover mouse para posição
            self.move_mouse(x, y)
            
            # Determinar direção
            scroll_clicks = clicks if direction == 'up' else -clicks
            
            # Executar scroll
            pyautogui.scroll(scroll_clicks)
            
            self._record_action('scroll', {
                'x': x, 'y': y, 
                'clicks': clicks, 
                'direction': direction
            })
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no scroll: {e}")
            return False
    
    def _generate_curved_path(self, start_x: int, start_y: int, 
                            end_x: int, end_y: int, num_points: int = 10) -> List[Tuple[int, int]]:
        """Gera trajetória curva natural entre dois pontos"""
        points = []
        
        # Calcular pontos de controle para curva Bézier
        control_x = (start_x + end_x) / 2 + random.randint(-50, 50)
        control_y = (start_y + end_y) / 2 + random.randint(-50, 50)
        
        for i in range(num_points + 1):
            t = i / num_points
            
            # Curva Bézier quadrática
            x = (1 - t) ** 2 * start_x + 2 * (1 - t) * t * control_x + t ** 2 * end_x
            y = (1 - t) ** 2 * start_y + 2 * (1 - t) * t * control_y + t ** 2 * end_y
            
            points.append((int(x), int(y)))
        
        return points
    
    def _record_action(self, action_type: str, data: dict):
        """Registra ação para análise anti-detecção"""
        action_record = {
            'timestamp': time.time(),
            'type': action_type,
            'data': data
        }
        
        self.action_history.append(action_record)
        
        # Manter histórico limitado
        if len(self.action_history) > self.max_history:
            self.action_history.pop(0)
    
    def get_action_statistics(self) -> dict:
        """Retorna estatísticas das ações para análise"""
        if not self.action_history:
            return {}
        
        stats = {
            'total_actions': len(self.action_history),
            'action_types': {},
            'time_span': 0,
            'average_interval': 0
        }
        
        # Contar tipos de ação
        for action in self.action_history:
            action_type = action['type']
            stats['action_types'][action_type] = stats['action_types'].get(action_type, 0) + 1
        
        # Calcular intervalos
        if len(self.action_history) > 1:
            timestamps = [action['timestamp'] for action in self.action_history]
            stats['time_span'] = timestamps[-1] - timestamps[0]
            
            intervals = []
            for i in range(1, len(timestamps)):
                intervals.append(timestamps[i] - timestamps[i-1])
            
            stats['average_interval'] = sum(intervals) / len(intervals)
        
        return stats
    
    def emergency_stop(self):
        """Para todas as ações de input imediatamente"""
        try:
            # Mover mouse para canto (ativa FAILSAFE do PyAutoGUI)
            pyautogui.moveTo(0, 0)
            self.logger.info("Parada de emergência ativada")
        except Exception as e:
            self.logger.error(f"Erro na parada de emergência: {e}")