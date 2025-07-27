# Tibia Bot - Automação Avançada

Bot de automação completo para Tibia, desenvolvido especificamente para uso em servidores de teste privados (OT Server). 

## ⚠️ IMPORTANTE - LEIA ANTES DE USAR

**Este bot foi desenvolvido exclusivamente para uso em servidores de teste privados (OT Server) onde o uso de bots é permitido. O uso em servidores oficiais do Tibia pode resultar em banimento da conta. Use por sua própria conta e risco.**

## 🎯 Funcionalidades

### ✨ Principais Recursos
- **Auto Heal**: Cura automática inteligente baseada em percentual de vida
- **Auto Mana**: Gerenciamento automático de mana com suporte a emergência  
- **Auto Food**: Consumo automático de comida baseado em status visual
- **Auto Loot**: Sistema otimizado de coleta com filtragem inteligente
- **Cavebot**: Navegação automática com scripts de waypoints

### 🛡️ Recursos de Segurança
- **Anti-Detecção**: Simulação humanizada de input com randomização
- **Contorno BattlEye**: Técnica de virtualização via OBS Studio
- **Failsafe**: Sistema de parada de emergência integrado
- **Logging**: Sistema completo de logs para monitoramento

### 🎮 Interface Gráfica
- Interface intuitiva "plug-and-play"
- Configuração visual de todas as funcionalidades
- Monitor em tempo real do status do bot
- Editor visual de scripts de cavebot
- Sistema de hotkeys globais

## 📋 Requisitos do Sistema

### Software Necessário
- **Windows 10/11** (recomendado)
- **Python 3.11+** 
- **OBS Studio** (para captura de tela)
- **Cliente Tibia** configurado

### Hardware Mínimo
- CPU: Intel i3 ou AMD equivalente
- RAM: 4 GB
- Resolução: 1024x768 ou superior

## 🚀 Instalação Rápida

### 1. Preparar Ambiente
```bash
# Clonar ou extrair o bot
cd tibia_bot

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar OBS Studio
1. Baixe e instale o [OBS Studio](https://obsproject.com/)
2. Crie uma nova cena
3. Adicione fonte "Captura de Janela"
4. Selecione a janela do Tibia
5. **IMPORTANTE**: Mantenha a janela de preview aberta

### 3. Configurar Cliente Tibia
1. Defina resolução: **1024x768** (recomendado)
2. Configure hotkeys:
   - **F1**: Poção de vida
   - **F2**: Poção de vida forte (emergência)  
   - **F3**: Poção de mana
   - **F4**: Poção de mana forte (emergência)
   - **F7**: Comida
3. Abra todos os painéis: vida, mana, inventário, chat

### 4. Executar o Bot
```bash
python main.py
```

## 📖 Guia de Uso

### Primeiro Uso
1. **Teste a Captura**: Menu → Ferramentas → Testar Captura
2. **Configure ROIs**: Defina áreas de vida e mana (será implementado)
3. **Ajuste Configurações**: Aba "Configurações" → ajuste thresholds
4. **Teste Módulos**: Ative apenas Auto Heal inicialmente
5. **Monitore**: Observe o comportamento por alguns minutos

### Configuração de Módulos

#### Auto Heal
- **Threshold**: Percentual de vida para usar cura (padrão: 70%)
- **Emergência**: Percentual crítico (padrão: 30%)
- **Métodos**: Poções e/ou magias de cura
- **Hotkeys**: Configuráveis por módulo

#### Auto Mana  
- **Threshold**: Percentual de mana para usar poção (padrão: 60%)
- **Emergência**: Percentual crítico (padrão: 20%)
- **Cooldown**: Tempo entre usos automáticos

#### Auto Food
- **Método**: Hotkey ou clique direito no inventário
- **Intervalo**: Verificação de fome a cada X segundos
- **Slot**: Posição da comida no inventário (1-20)

#### Auto Loot
- **Modo Otimizado**: Coleta tudo, depois descarta lixo (recomendado)
- **Raio**: Distância máxima para coleta (pixels)
- **Lista Valiosos**: Itens para manter
- **Lista Lixo**: Itens para descartar automaticamente

#### Cavebot
- **Scripts**: Arquivos JSON com waypoints
- **Tipos de Waypoint**: Walk, Attack, Stairs, Hole, Rope, Wait
- **Editor Visual**: Interface para criar/editar scripts
- **Gravação**: Grave waypoints em tempo real

### Hotkeys Globais
- **F9**: Iniciar/Parar Bot
- **F12**: Parada de Emergência
- **Ctrl+F1 a F5**: Toggle módulos individuais

## 🔧 Configurações Avançadas

### Arquivos de Configuração
- `config/bot_config.json`: Configurações gerais
- `config/valuable_items.json`: Lista de itens valiosos
- `config/trash_items.json`: Lista de itens descartáveis
- `scripts/*.json`: Scripts de cavebot

### Personalização
```json
{
  "auto_heal": {
    "health_threshold": 70,
    "emergency_threshold": 30,
    "use_potions": true,
    "potion_hotkey": "F1"
  },
  "screen_capture": {
    "obs_window_title": "OBS Studio - Preview",
    "min_capture_interval": 0.05
  }
}
```

### ROIs (Regiões de Interesse)
Configure áreas específicas da tela para otimizar detecção:
- **health_bar**: Barra de vida
- **mana_bar**: Barra de mana  
- **food_status**: Área de status de fome
- **game_area**: Área principal do jogo
- **loot_area**: Área para detecção de loot

## 📊 Monitoramento

### Logs
- `logs/tibia_bot.log`: Log geral
- `logs/errors.log`: Erros críticos
- Interface gráfica mostra log recente em tempo real

### Métricas
- FPS de captura
- Tempo de ciclo
- Uso de CPU/Memória
- Contadores de ação (curas, loots, etc.)

## 🛠️ Solução de Problemas

### Problemas Comuns

**Bot não detecta vida/mana**
- Verifique se OBS está capturando corretamente
- Configure ROIs manualmente
- Teste diferentes thresholds de cor

**Captura de tela falhando**
- Certifique-se que OBS Preview está aberto
- Verifique se janela do Tibia está visível
- Teste com "Capturar Tela" no menu

**Input não funciona**
- Execute como Administrador
- Verifique se hotkeys não conflitam
- Teste com "humanização" desabilitada

**Cavebot travando**
- Verifique waypoints por coordenadas incorretas
- Ajuste threshold de precisão
- Use função de destravar automático

### Mensagens de Erro

**"Não foi possível capturar a tela"**
- OBS não está configurado corretamente
- Janela de preview fechada
- Permissões insuficientes

**"Template não encontrado"**
- Arquivos de template ausentes na pasta `assets/`
- ROIs não configuradas
- Resolução de tela incompatível

## 🎯 Dicas de Otimização

### Performance
- Use ROIs específicas ao invés de tela completa
- Ajuste intervalo de captura conforme necessário
- Feche programas desnecessários durante uso

### Segurança  
- Sempre monitore o bot periodicamente
- Use em áreas seguras inicialmente
- Mantenha backups de configurações importantes
- Configure parada de emergência

### Eficiência
- Ajuste thresholds conforme seu personagem
- Use loot otimizado para máxima eficiência
- Crie scripts de cavebot específicos para cada hunt
- Configure hotkeys para controle rápido

## 📚 Scripts de Exemplo

### Script Básico de Cavebot
```json
{
  "name": "Hunt Simples",
  "waypoints": [
    {"x": 100, "y": 100, "type": "walk"},
    {"x": 120, "y": 100, "type": "attack"},
    {"x": 120, "y": 120, "type": "walk"},
    {"x": 100, "y": 120, "type": "walk"}
  ]
}
```

### Lista de Itens Valiosos
```json
[
  "gold coin",
  "platinum coin", 
  "crystal coin",
  "magic plate armor",
  "crown armor",
  "might ring",
  "power ring"
]
```

## ⚖️ Aspectos Legais

### Uso Permitido
- ✅ Servidores privados que permitem bots
- ✅ Ambiente de desenvolvimento/teste
- ✅ Uso educacional e aprendizado

### Uso Não Recomendado  
- ❌ Servidores oficiais do Tibia
- ❌ Servidores que proíbem automação
- ❌ Competições ou eventos oficiais

### Disclaimer
Este software é fornecido "como está" sem garantias. Os desenvolvedores não se responsabilizam por banimentos, perda de personagens ou qualquer consequência do uso inadequado.

## 🔄 Atualizações

### Versão Atual: 1.0.0
- Sistema completo de automação
- Interface gráfica intuitiva  
- Anti-detecção integrado
- Suporte a múltiplos módulos

### Próximas Versões
- [ ] Configurador visual de ROIs
- [ ] Sistema de plugins
- [ ] Suporte a múltiplos personagens
- [ ] Integração com Discord
- [ ] Machine Learning para detecção

## 📞 Suporte

Para dúvidas, problemas ou sugestões:
- Consulte este README primeiro
- Verifique os logs em `logs/`
- Teste em ambiente controlado
- Documente erros com detalhes

## 🏆 Créditos

Desenvolvido com foco em:
- **Facilidade de uso** para usuários leigos
- **Robustez** para uso contínuo  
- **Segurança** anti-detecção
- **Performance** otimizada
- **Flexibilidade** de configuração

---

**⚠️ Lembre-se: Use com responsabilidade e apenas onde permitido!**