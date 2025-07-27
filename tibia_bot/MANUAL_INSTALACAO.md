# 📋 MANUAL DE INSTALAÇÃO - TIBIA BOT

**Guia completo passo-a-passo para usuários sem conhecimento técnico**

---

## 🎯 ANTES DE COMEÇAR

### ⚠️ IMPORTANTE
Este bot é **EXCLUSIVAMENTE** para servidores de teste privados (OT Server) onde bots são permitidos. **NÃO USE em servidores oficiais** - risco de banimento!

### 📋 O QUE VOCÊ VAI PRECISAR
- Computador com Windows 10 ou 11
- Internet para download dos programas
- Cliente Tibia funcionando
- Aproximadamente 30 minutos para configuração completa

---

## 📥 PASSO 1: DOWNLOAD E INSTALAÇÃO DOS PROGRAMAS

### 1.1 Baixar Python
1. Acesse: https://www.python.org/downloads/
2. Clique no botão verde "Download Python 3.11.x"
3. Execute o arquivo baixado
4. **IMPORTANTE**: Marque a opção "Add Python to PATH"
5. Clique em "Install Now"
6. Aguarde a instalação concluir

### 1.2 Baixar OBS Studio  
1. Acesse: https://obsproject.com/
2. Clique em "Download OBS Studio"
3. Escolha "Windows"
4. Execute o arquivo baixado
5. Siga a instalação padrão (Next → Next → Install)

### 1.3 Baixar o Bot
1. Extraia os arquivos do bot em uma pasta (ex: `C:\TibiaBot\`)
2. Certifique-se que todos os arquivos estão na pasta

---

## 🔧 PASSO 2: CONFIGURAR O OBS STUDIO

### 2.1 Primeira Configuração do OBS
1. Abra o OBS Studio
2. Na primeira vez, clique em "Cancelar" no assistente
3. Você verá uma tela preta - isso é normal

### 2.2 Adicionar Captura do Tibia
1. Na área "Fontes" (parte inferior), clique no **+**
2. Selecione **"Captura de Janela"**
3. Clique em **"OK"** (mantenha o nome padrão)
4. Na nova janela:
   - **Janela**: Escolha a janela do Tibia (deve aparecer na lista)
   - **Método de Captura**: "Windows Graphics Capture"
   - Clique em **"OK"**

### 2.3 Verificar Captura
1. Você deve ver a tela do Tibia no OBS
2. Se aparecer tela preta:
   - Feche o Tibia
   - Abra o Tibia DEPOIS do OBS
   - Repita o processo de captura

### 2.4 IMPORTANTE - Manter Preview Aberto
**🚨 CRÍTICO**: A janela do OBS deve ficar SEMPRE ABERTA enquanto usar o bot!

---

## 🎮 PASSO 3: CONFIGURAR O CLIENTE TIBIA

### 3.1 Configurações Básicas
1. Abra o Tibia
2. Vá em **Options → General**
3. Configure:
   - **Resolution**: 1024x768 (recomendado)
   - **Interface**: "Classic" ou "Modern" (sua preferência)

### 3.2 Configurar Hotkeys OBRIGATÓRIAS
**Esta é a parte mais importante! Anote suas configurações:**

1. Vá em **Options → Hotkeys**
2. Configure EXATAMENTE assim:

| Função | Tecla | Como Configurar |
|--------|-------|-----------------|
| Poção de Vida | **F1** | Coloque sua poção de vida no slot F1 |
| Poção Vida Forte | **F2** | Coloque uma poção mais forte no F2 |
| Poção de Mana | **F3** | Coloque sua poção de mana no F3 |
| Poção Mana Forte | **F4** | Coloque uma poção de mana forte no F4 |
| Comida | **F7** | Coloque comida no F7 |

### 3.3 Organizar Interface
1. Deixe visíveis:
   - ✅ Barra de vida (health bar)
   - ✅ Barra de mana (mana bar)  
   - ✅ Inventário (inventory)
   - ✅ Chat (opcional, mas recomendado)

2. Posicione as barras de vida e mana em local fixo e visível

---

## 🚀 PASSO 4: INSTALAR E EXECUTAR O BOT

### 4.1 Instalar Dependências
1. Abra o **Prompt de Comando**:
   - Pressione **Windows + R**
   - Digite **cmd**
   - Pressione **Enter**

2. Navegue até a pasta do bot:
   ```
   cd C:\TibiaBot
   ```
   (substitua pelo caminho onde você extraiu o bot)

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
   
4. Aguarde a instalação (pode demorar alguns minutos)

### 4.2 Executar o Bot
1. No mesmo Prompt de Comando, digite:
   ```
   python main.py
   ```

2. A interface gráfica do bot deve abrir

---

## ⚙️ PASSO 5: CONFIGURAÇÃO INICIAL DO BOT

### 5.1 Primeiro Teste
1. Com o bot aberto, vá em **Menu → Ferramentas → Testar Captura**
2. Deve aparecer "Teste de captura: OK"
3. Se der erro, volte ao Passo 2 (OBS Studio)

### 5.2 Configurar Auto Heal (Primeira Funcionalidade)
1. Clique na aba **"Configurações"**
2. Clique na sub-aba **"Auto Heal"**
3. Configure:
   - **Percentual de vida para curar**: 70% (ajuste conforme necessário)
   - **Percentual de emergência**: 30%
   - Marque **"Usar poções de vida"**
   - **Hotkey da poção**: F1
   - **Hotkey de emergência**: F2

4. Clique em **"Aplicar"** e depois **"Salvar"**

### 5.3 Primeiro Uso
1. Volte para a aba **"Status"** 
2. Marque apenas **"Auto Heal"** (deixe os outros desmarcados)
3. Clique em **"Iniciar Bot"**
4. No Tibia, tome algum dano para testar
5. O bot deve usar poção automaticamente quando a vida baixar

---

## 🔍 PASSO 6: CONFIGURAÇÕES AVANÇADAS

### 6.1 Configurar Auto Mana
1. Aba **"Configurações"** → **"Auto Mana"**
2. Configure similar ao Auto Heal:
   - **Percentual de mana**: 60%
   - **Hotkey**: F3
   - **Emergência**: F4

### 6.2 Configurar Auto Food
1. Aba **"Configurações"** → **"Auto Food"**
2. Configure:
   - **Método**: "Clique direito no inventário"
   - **Slot da comida**: 1 (primeiro slot do inventário)
   - Ou use **Hotkey**: F7

### 6.3 Configurar Auto Loot
1. Aba **"Configurações"** → **"Auto Loot"**
2. Marque **"Usar loot otimizado"** (recomendado)
3. Configure **"Raio de coleta"**: 150 pixels
4. Adicione itens valiosos na lista

---

## 🎛️ PASSO 7: USANDO O CAVEBOT

### 7.1 Carregar Script de Exemplo
1. Clique na aba **"Cavebot"**
2. Clique em **"Carregar"**
3. Selecione o arquivo `example_thais_rats.json`
4. Clique em **"Iniciar Cavebot"**

### 7.2 Criar Seu Próprio Script
1. Na aba **"Cavebot"**, clique em **"Novo"**
2. Use o **"Editor de Waypoints"** para adicionar pontos:
   - **Tipo**: "walk" para caminhar
   - **X, Y**: Coordenadas do jogo
   - **Ação**: Deixe vazio para movimento normal
3. Clique **"Adicionar"** para cada waypoint
4. Clique **"Salvar"** quando terminar

---

## 🆘 SOLUÇÃO DE PROBLEMAS

### ❌ "Não foi possível capturar a tela"
**Solução:**
1. Certifique-se que o OBS está aberto
2. Verifique se a captura do Tibia está funcionando no OBS
3. Reinicie o OBS e tente novamente

### ❌ "Bot não está curando"
**Solução:**
1. Verifique se F1 está configurado corretamente no Tibia
2. Certifique-se que há poções no inventário
3. Ajuste o percentual de vida nas configurações

### ❌ "Python não é reconhecido"
**Solução:**
1. Reinstale o Python
2. Marque "Add Python to PATH" na instalação
3. Reinicie o computador

### ❌ "Tela preta no OBS"
**Solução:**
1. Feche o Tibia
2. Abra o OBS primeiro
3. Depois abra o Tibia
4. Reconfigure a captura de janela

### ❌ "Bot não clica direito"
**Solução:**
1. Execute o bot como Administrador
2. Vá em Configurações → Geral
3. Marque "Humanizar input"

---

## 🎯 DICAS IMPORTANTES

### ✅ Para Usar com Segurança
- **Sempre monitore o bot** - não deixe 100% sozinho
- **Comece devagar** - teste cada função individualmente  
- **Use em áreas seguras** - longe de PKs
- **Tenha sempre poções** - bot não funciona sem supplies

### ✅ Para Melhor Performance
- **Feche programas desnecessários** durante o uso
- **Use resolução 1024x768** no Tibia
- **Mantenha OBS sempre aberto**
- **Configure hotkeys corretamente**

### ✅ Configuração Ideal para Iniciantes
1. **Primeiro**: Só Auto Heal
2. **Depois**: Auto Heal + Auto Mana  
3. **Depois**: Adicionar Auto Food
4. **Por último**: Auto Loot e Cavebot

---

## 🚨 AVISOS FINAIS

### ⚠️ LEMBRE-SE
- Este bot é para **OT Server apenas**
- **Monitore sempre** o funcionamento
- **Pare imediatamente** se algo der errado
- **Use F12** para parada de emergência

### 📞 Se Precisar de Ajuda
1. Leia este manual novamente
2. Verifique os logs na pasta `logs/`
3. Teste cada passo isoladamente
4. Anote o erro exato que aparece

---

**🎉 Pronto! Seu bot está configurado e funcionando!**

**Divirta-se e use com responsabilidade! 🎮**