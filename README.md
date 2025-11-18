# 🎮 QR Code Game - Jogo para 2 Jogadores

Um jogo interativo onde dois jogadores controlam seus personagens através de QR codes capturados pela câmera em tempo real. O objetivo é chegar ao destino evitando os obstáculos!

## 📋 Descrição do Projeto

Este é um jogo educativo e divertido que utiliza QR codes e controla personagens em um tabuleiro virtual. Cada jogador possui sua própria cartela com QR codes de movimentação (cima, baixo, esquerda, direita) e compete para chegar ao objetivo primeiro.

### 🎯 Características

- **2 Jogadores Simultâneos**: Verde (Jogador 1) e Vermelho (Jogador 2)
- **Controle por QR Code**: Movimentação através de QR codes físicos
- **Objetivo**: Primeiro jogador a chegar ao destino vence

## 🎲 Como Jogar

### 1. Gerar Recursos do Jogo

Antes de jogar, você precisa gerar os QR codes e/ou PDFs para impressão:

Os recursos serão criados na pasta `recursos/`:
- **QR Codes PNG**: Imagens individuais de cada comando
- **PDFs Impressos**: Cartelas completas para cada jogador

### 2. Preparar Cartelas

Você pode:
- **Imprimir os PDFs**: `Cartelas_Jogador1.pdf` e `Cartelas_Jogador2.pdf`
- **Usar QR codes digitais**: Exibir as imagens PNG em dispositivos móveis ou monitores

### 3. Executar o Jogo

```bash
python main.py
```

### 4. Controles

Cada jogador mostra seu QR code para a câmera para mover seu personagem:


### 5. Regras

- ✅ Chegue ao **destino amarelo** (canto superior direito)
- 🏆 Primeiro jogador a chegar ao destino **vence**
- ⏱️ Há um delay de 1 segundo entre comandos para evitar movimentos acidentais
- 🎮 Pressione `q` ou clique no `X` para sair

## 📁 Estrutura do Projeto

```
tesc-qrcode-game/
├── main.py                 # Jogo principal
├── gerar_recursos.py       # Script para gerar QR codes e PDFs
├── recursos/               # Pasta com recursos gerados
│   ├── Jogador1_Cima.png
│   ├── Jogador1_Baixo.png
│   ├── Jogador1_Esquerda.png
│   ├── Jogador1_Direita.png
│   ├── Jogador2_Cima.png
│   ├── Jogador2_Baixo.png
│   ├── Jogador2_Esquerda.png
│   ├── Jogador2_Direita.png
│   ├── Cartelas_Jogador1.pdf
│   └── Cartelas_Jogador2.pdf
├── teste_qrcode.py         # Script de teste para detecção de QR
└── README.md               # Este arquivo
```

## 🛠️ Tecnologias Utilizadas

- **OpenCV**: Captura e processamento de vídeo
- **pyzbar**: Decodificação de QR codes
- **NumPy**: Manipulação de arrays e matrizes
- **qrcode**: Geração de QR codes
- **ReportLab**: Criação de PDFs
- **Pillow (PIL)**: Processamento de imagens

## 🔧 Solução de Problemas

### Câmera não é detectada

- Verifique as permissões de câmera em **Configurações do Sistema > Privacidade e Segurança > Câmera**
- Se usar câmera externa, ela geralmente é detectada em índice diferente (o código tenta automaticamente)


## 🎓 Créditos

Desenvolvido como parte do curso de Tópicos Especiais em Sistemas Computacionais da UFF.

## Recursos Utilizados:

https://opengameart.org/content/mustached-gentleman-game-character-sprites
https://opengameart.org/content/big-eyes-boy-game-character-sprites

---

**Divirta-se jogando! 🎮🎉**
