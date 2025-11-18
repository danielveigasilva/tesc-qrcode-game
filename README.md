# 🎮 QR Code Game - Jogo para 2 Jogadores

Um jogo interativo onde dois jogadores controlam seus personagens através de QR codes capturados pela câmera em tempo real. O objetivo é chegar ao destino primeiro!

## 📋 Descrição do Projeto

Este é um jogo educativo e divertido que utiliza QR codes para controlar personagens em um tabuleiro virtual. Cada jogador possui sua própria cartela com QR codes de movimentação e compete para chegar ao objetivo primeiro.

### 🎯 Características

- **2 Jogadores Simultâneos**: Cada jogador tem seu próprio personagem
- **Controle por QR Code**: Movimentação através de sequências de QR codes físicos
- **Sistema INICIO/FIM**: Sequências válidas devem começar com carta INICIO e terminar com carta FIM
- **Estabilização de Frames**: Detecção estável (5 frames consecutivos) para evitar leituras acidentais
- **Autofoco Automático**: Tentativa de ativar autofoco da câmera para melhor leitura
- **Tela Cheia**: Jogo abre em modo fullscreen automaticamente
- **Preview da Câmera**: Mini-preview da câmera no canto da tela para facilitar posicionamento

## 🎲 Como Jogar


### 1. Preparar Cartelas

**Recomendado: Imprimir os PDFs**
- Cada PDF tem 2 páginas:
  - Página 1: Cartas de movimento (Cima, Baixo, Esquerda, Direita)
  - Página 2: Cartas especiais (INICIO e FIM)
- Recorte as cartas seguindo as bordas
- Todas as cartas estão identificadas com "- Jogador X" para facilitar organização

### 2. Executar o Jogo

```bash
python main.py
```

O jogo abrirá em **tela cheia** automaticamente.

### 3. Como Montar uma Sequência

Para executar movimentos, cada jogador deve mostrar as cartas na seguinte ordem:

1. **INICIO** (obrigatório)
2. **Movimentos** (Cima, Baixo, Esquerda, Direita - quantos quiser)
3. **FIM** (obrigatório)

**Exemplo de sequência válida:**
```
INICIO → DIREITA → DIREITA → CIMA → CIMA → FIM
```

**Importante:**
- Mostre todas as cartas juntas para a câmera
- Mantenha-as estáveis por 5 segundos para detecção
- As cartas devem estar na ordem da esquerda para direita
- Sequências sem INICIO ou FIM não serão aceitas

### 5. Regras

- 🏁 Chegue ao **destino** (canto superior direito) primeiro
- 🏆 Primeiro jogador a chegar ao destino **vence**
- 📹 Posicione as cartas a ~50-80cm da câmera para melhor leitura
- ✨ Cada jogador executa sua sequência de forma independente
- ⏱️ Há um delay de 0.8s entre cada movimento para visualização
- 🎮 Pressione `q` para sair

### 6. Dicas para Melhor Detecção

- **Iluminação**: Use boa iluminação sobre as cartas
- **Distância**: Mantenha ~50-80cm da câmera (distância de videochamada)
- **Ângulo**: Cartas perpendiculares à câmera (90 graus)
- **Estabilidade**: Mantenha as cartas paradas por alguns segundos
- **Ordem**: Esquerda para direita (INICIO primeiro, FIM por último)

## 📁 Estrutura do Projeto

```
tesc-qrcode-game/
├── main.py                      # Jogo principal
├── gerar_recursos.py            # Script para gerar QR codes e PDFs
├── gerar_teste_foco.py          # Gera PDF para testar foco da câmera
├── recursos/                    # Pasta com recursos gerados
│   ├── Jogador1_Inicio.png
│   ├── Jogador1_Cima.png
│   ├── Jogador1_Baixo.png
│   ├── Jogador1_Esquerda.png
│   ├── Jogador1_Direita.png
│   ├── Jogador1_Fim.png
│   ├── Jogador2_*.png           # Mesmos para Jogador 2
│   ├── Cartelas_Jogador1.pdf    # 2 páginas
│   ├── Cartelas_Jogador2.pdf    # 2 páginas
│   └── Teste_Foco_Camera.pdf    # PDF para testar detecção
├── imagens/                     # Assets do jogo
│   ├── usuario1.png
│   ├── usuario2.png
│   ├── casa.png                 # Ícone de destino
│   └── fase1_background.png
└── README.md                    # Este arquivo
```

## 🛠️ Tecnologias Utilizadas

- **OpenCV**: Captura e processamento de vídeo
- **pyzbar**: Decodificação de QR codes
- **NumPy**: Manipulação de arrays e matrizes
- **qrcode**: Geração de QR codes
- **ReportLab**: Criação de PDFs
- **Pillow (PIL)**: Processamento de imagens

## � Instalação

```bash
# Clone o repositório
git clone https://github.com/danielveigasilva/tesc-qrcode-game.git
cd tesc-qrcode-game

# Instale as dependências
pip install opencv-python pyzbar numpy qrcode reportlab pillow

# Gere os recursos
python gerar_recursos.py --tudo

# Execute o jogo
python main.py
```

## 🎓 Créditos

**Desenvolvido por**: ... 
**Curso**: Tópicos Especiais em Sistemas Computacionais - UFF  
**Ano**: 2025

### Recursos de Arte Utilizados

- Personagens: [OpenGameArt - Mustached Gentleman & Big Eyes Boy](https://opengameart.org)
- Casa/Destino: [OpenGameArt - House Sets](https://opengameart.org/content/house-sets)

---

**Divirta-se jogando! 🎮🎉**
