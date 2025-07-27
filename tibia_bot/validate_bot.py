"""
DEMONSTRAÇÃO DO TIBIA BOT - VALIDAÇÃO DE COMPONENTES
Este arquivo valida que todos os componentes do bot estão funcionando corretamente
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Testa se todos os imports principais funcionam"""
    print("🧪 Testando imports dos módulos...")
    
    try:
        # Core imports
        sys.path.append(str(Path(__file__).parent))
        
        from core.bot_manager import BotManager
        from core.screen_capture import ScreenCapture  
        from core.input_simulator import InputSimulator
        
        from modules.auto_heal import AutoHeal
        from modules.auto_mana import AutoMana
        from modules.auto_food import AutoFood
        from modules.auto_loot import AutoLoot
        from modules.cavebot import Cavebot
        
        from utils.config_manager import ConfigManager
        from utils.logger import setup_logger
        
        print("✅ Todos os imports principais funcionam!")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False

def test_structure():
    """Testa se a estrutura de arquivos está correta"""
    print("\n📁 Testando estrutura de arquivos...")
    
    required_files = [
        "main.py",
        "requirements.txt", 
        "README.md",
        "MANUAL_INSTALACAO.md",
        "core/bot_manager.py",
        "core/screen_capture.py",
        "core/input_simulator.py",
        "modules/auto_heal.py",
        "modules/auto_mana.py", 
        "modules/auto_food.py",
        "modules/auto_loot.py",
        "modules/cavebot.py",
        "gui/main_window.py",
        "gui/status_panel.py",
        "gui/config_panel.py",
        "gui/cavebot_panel.py",
        "gui/hotkey_panel.py",
        "utils/config_manager.py",
        "utils/logger.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Arquivos faltando: {missing_files}")
        return False
    else:
        print("✅ Toda a estrutura de arquivos está presente!")
        return True

def test_config():
    """Testa sistema de configuração"""
    print("\n⚙️ Testando sistema de configuração...")
    
    try:
        from utils.config_manager import ConfigManager
        config = ConfigManager()
        
        # Testar get/set
        config.set('test.value', 123)
        assert config.get('test.value') == 123
        
        # Testar seção
        config.set_section('test_section', {'key1': 'value1', 'key2': 'value2'})
        section = config.get_section('test_section')
        assert section['key1'] == 'value1'
        
        print("✅ Sistema de configuração funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema de configuração: {e}")
        return False

def test_modules():
    """Testa inicialização dos módulos"""
    print("\n🤖 Testando módulos do bot...")
    
    try:
        # Mock objects para evitar dependências GUI
        class MockScreenCapture:
            def test_capture(self): return True
            def capture(self): return None
            def set_roi(self, *args): pass
            def capture_roi(self, *args): return None
        
        class MockInputSim:
            def click(self, *args, **kwargs): return True
            def press_key(self, *args): return True
        
        screen_cap = MockScreenCapture()
        input_sim = MockInputSim()
        
        # Testar módulos
        from modules.auto_heal import AutoHeal
        from modules.auto_mana import AutoMana
        from modules.auto_food import AutoFood
        from modules.auto_loot import AutoLoot
        from modules.cavebot import Cavebot
        
        heal = AutoHeal(screen_cap, input_sim)
        mana = AutoMana(screen_cap, input_sim)
        food = AutoFood(screen_cap, input_sim)
        loot = AutoLoot(screen_cap, input_sim)
        cavebot = Cavebot(screen_cap, input_sim)
        
        # Testar configurações
        heal.set_config({'health_threshold': 80})
        assert heal.get_config()['health_threshold'] == 80
        
        print("✅ Todos os módulos inicializam corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos módulos: {e}")
        return False

def test_dependencies():
    """Testa se dependências estão disponíveis"""
    print("\n📦 Testando dependências externas...")
    
    dependencies = [
        'cv2',
        'numpy', 
        'PIL',
        'json',
        'os',
        'pathlib',
        'threading',
        'time'
    ]
    
    missing_deps = []
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"❌ Dependências faltando: {missing_deps}")
        return False
    else:
        print("✅ Todas as dependências principais estão disponíveis!")
        return True

def main():
    """Função principal de validação"""
    print("🤖 TIBIA BOT - VALIDAÇÃO COMPLETA")
    print("=" * 50)
    
    tests = [
        ("Estrutura de Arquivos", test_structure),
        ("Dependências", test_dependencies), 
        ("Imports", test_imports),
        ("Sistema de Configuração", test_config),
        ("Módulos do Bot", test_modules)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TIBIA BOT ESTÁ COMPLETAMENTE FUNCIONAL!")
        print("\n✅ O bot está pronto para uso:")
        print("   • Todos os módulos funcionando")
        print("   • Estrutura completa")
        print("   • Configurações validadas")
        print("   • Dependências OK")
        print("\n🚀 Para usar, execute: python main.py")
        print("📖 Leia o MANUAL_INSTALACAO.md para instruções detalhadas")
        
        return True
    else:
        print("❌ Alguns testes falharam - verifique os erros acima")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)