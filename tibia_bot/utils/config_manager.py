"""
Config Manager - Gerenciador de configurações
Salva e carrega configurações em arquivo JSON
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import logging

class ConfigManager:
    """Gerenciador de configurações do bot"""
    
    def __init__(self, config_file: str = "config/bot_config.json"):
        self.config_file = Path(config_file)
        self.logger = logging.getLogger(__name__)
        
        # Configurações padrão
        self.default_config = {
            'bot': {
                'cycle_delay': 0.1,
                'emergency_stop_key': 'F12',
                'debug_mode': False,
            },
            'screen_capture': {
                'obs_window_title': 'OBS Studio - Preview',
                'capture_region': None,
                'min_capture_interval': 0.05,
            },
            'input_simulator': {
                'mouse_speed_base': 0.5,
                'mouse_speed_variance': 0.3,
                'click_delay_base': 0.05,
                'click_delay_variance': 0.03,
                'humanize_by_default': True,
            },
            'auto_heal': {
                'health_threshold': 70,
                'emergency_threshold': 30,
                'use_potions': True,
                'use_spells': False,
                'potion_hotkey': 'F1',
                'spell_hotkey': 'F5',
                'emergency_hotkey': 'F2',
            },
            'auto_mana': {
                'mana_threshold': 60,
                'emergency_threshold': 20,
                'use_potions': True,
                'use_spells': False,
                'potion_hotkey': 'F3',
                'spell_hotkey': 'F6',
                'emergency_hotkey': 'F4',
            },
            'auto_food': {
                'food_hotkey': 'F7',
                'check_interval': 5.0,
                'use_right_click': True,
                'food_inventory_slot': 1,
            },
            'auto_loot': {
                'loot_radius': 150,
                'loot_delay': 0.2,
                'use_optimized_loot': True,
                'auto_open_corpses': True,
                'pickup_all_items': False,
            },
            'cavebot': {
                'attack_enabled': True,
                'walk_speed': 1.0,
                'attack_range': 5,
                'stuck_threshold': 5.0,
                'waypoint_precision': 10,
                'monster_priority': ['dragon', 'demon', 'hero'],
                'avoid_monsters': ['ancient scarab'],
            },
            'hotkeys': {
                'start_stop_bot': 'F9',
                'emergency_stop': 'F12',
                'toggle_auto_heal': 'Ctrl+F1',
                'toggle_auto_mana': 'Ctrl+F2',
                'toggle_auto_food': 'Ctrl+F3',
                'toggle_auto_loot': 'Ctrl+F4',
                'toggle_cavebot': 'Ctrl+F5',
            },
            'rois': {
                'health_bar': None,
                'mana_bar': None,
                'food_status': None,
                'game_area': None,
                'loot_area': None,
                'chat_area': None,
            }
        }
        
        self.config = self.default_config.copy()
        self.load_config()
    
    def load_config(self) -> bool:
        """Carrega configurações do arquivo"""
        try:
            if not self.config_file.exists():
                # Criar diretório e arquivo padrão
                self.config_file.parent.mkdir(parents=True, exist_ok=True)
                self.save_config()
                self.logger.info("Arquivo de configuração criado com valores padrão")
                return True
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # Mesclar com configurações padrão (para adicionar novas chaves)
            self.config = self._merge_configs(self.default_config, loaded_config)
            
            self.logger.info(f"Configurações carregadas de: {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
            self.config = self.default_config.copy()
            return False
    
    def save_config(self) -> bool:
        """Salva configurações no arquivo"""
        try:
            # Criar diretório se não existir
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configurações salvas em: {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor de configuração usando notação de ponto
        Exemplo: get('auto_heal.health_threshold')
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Define valor de configuração usando notação de ponto
        Exemplo: set('auto_heal.health_threshold', 80)
        """
        try:
            keys = key.split('.')
            config_ref = self.config
            
            # Navegar até o penúltimo nível
            for k in keys[:-1]:
                if k not in config_ref:
                    config_ref[k] = {}
                config_ref = config_ref[k]
            
            # Definir valor final
            config_ref[keys[-1]] = value
            
            self.logger.debug(f"Configuração atualizada: {key} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao definir configuração {key}: {e}")
            return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Obtém seção completa de configuração"""
        return self.config.get(section, {}).copy()
    
    def set_section(self, section: str, values: Dict[str, Any]) -> bool:
        """Define valores de uma seção completa"""
        try:
            if section not in self.config:
                self.config[section] = {}
            
            self.config[section].update(values)
            self.logger.info(f"Seção {section} atualizada")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar seção {section}: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Restaura configurações padrão"""
        try:
            self.config = self.default_config.copy()
            self.save_config()
            self.logger.info("Configurações restauradas para padrão")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao restaurar configurações: {e}")
            return False
    
    def export_config(self, export_path: str) -> bool:
        """Exporta configurações para arquivo"""
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configurações exportadas para: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar configurações: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """Importa configurações de arquivo"""
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                self.logger.error(f"Arquivo de importação não existe: {import_path}")
                return False
            
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Mesclar com configurações atuais
            self.config = self._merge_configs(self.config, imported_config)
            self.save_config()
            
            self.logger.info(f"Configurações importadas de: {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao importar configurações: {e}")
            return False
    
    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Mescla duas configurações recursivamente"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_hotkey(self, action: str) -> Optional[str]:
        """Obtém hotkey para uma ação específica"""
        return self.get(f'hotkeys.{action}')
    
    def set_hotkey(self, action: str, hotkey: str) -> bool:
        """Define hotkey para uma ação"""
        return self.set(f'hotkeys.{action}', hotkey)
    
    def get_roi(self, roi_name: str) -> Optional[Dict[str, int]]:
        """Obtém configuração de ROI"""
        return self.get(f'rois.{roi_name}')
    
    def set_roi(self, roi_name: str, x: int, y: int, width: int, height: int) -> bool:
        """Define ROI"""
        roi_config = {'x': x, 'y': y, 'width': width, 'height': height}
        return self.set(f'rois.{roi_name}', roi_config)
    
    def validate_config(self) -> List[str]:
        """Valida configuração atual e retorna lista de problemas"""
        issues = []
        
        try:
            # Validar hotkeys
            hotkeys = self.get_section('hotkeys')
            for action, hotkey in hotkeys.items():
                if not isinstance(hotkey, str) or not hotkey.strip():
                    issues.append(f"Hotkey inválida para {action}: {hotkey}")
            
            # Validar thresholds
            heal_threshold = self.get('auto_heal.health_threshold', 0)
            if not 0 < heal_threshold <= 100:
                issues.append(f"Threshold de vida inválido: {heal_threshold}")
            
            mana_threshold = self.get('auto_mana.mana_threshold', 0)
            if not 0 < mana_threshold <= 100:
                issues.append(f"Threshold de mana inválido: {mana_threshold}")
            
            # Validar delays
            cycle_delay = self.get('bot.cycle_delay', 0)
            if cycle_delay < 0.01:
                issues.append(f"Delay de ciclo muito baixo: {cycle_delay}")
            
        except Exception as e:
            issues.append(f"Erro na validação: {e}")
        
        return issues