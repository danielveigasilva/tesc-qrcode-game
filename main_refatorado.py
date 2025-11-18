"""
Jogo de QR Code para 2 Jogadores
Sistema de controle de personagens via QR codes detectados pela câmera.
"""

import cv2
import numpy as np
import time
from pyzbar.pyzbar import decode
from typing import Optional, Tuple, List


# ==================== CONSTANTES ====================
# Configurações da tela
LARGURA_TELA = 640
ALTURA_TELA = 480
TAMANHO_CELULA = 64

# Configurações do preview da câmera
PREVIEW_LARGURA = 160
PREVIEW_ALTURA = 120
PREVIEW_X = 10
PREVIEW_Y = 10

# Configurações de jogo
DELAY_LEITURA_QR = 1.0  # segundos entre leituras de QR

# Cores (BGR)
COR_JOGADOR1 = (0, 255, 0)  # Verde
COR_JOGADOR2 = (0, 0, 255)  # Vermelho
COR_JOGADOR1_DANO = (0, 100, 0)  # Verde escuro
COR_JOGADOR2_DANO = (0, 0, 150)  # Vermelho escuro
COR_AGUA = (255, 100, 100)  # Azul claro
COR_DESTINO = (0, 255, 255)  # Amarelo
COR_VITORIA = (0, 150, 0)  # Verde
COR_DERROTA = (0, 0, 255)  # Vermelho


# ==================== CLASSES ====================
class ConfiguracaoJogo:
    """Armazena as configurações do jogo."""
    
    def __init__(self):
        self.grid_cols = LARGURA_TELA // TAMANHO_CELULA
        self.grid_rows = ALTURA_TELA // TAMANHO_CELULA
        self.agua = [(2, 5), (3, 5), (4, 5)]
        self.destino = (self.grid_cols - 1, 0)  # Canto superior direito


class Jogador:
    """Representa um jogador no jogo."""
    
    def __init__(self, numero: int, x: int, y: int, cor: tuple, cor_dano: tuple):
        self.numero = numero
        self.x = x
        self.y = y
        self.cor = cor
        self.cor_dano = cor_dano
        self.morreu = False
    
    def mover(self, direcao: str, grid_cols: int, grid_rows: int) -> Tuple[int, int]:
        """Move o jogador na direção especificada e retorna a posição anterior."""
        pos_anterior = (self.x, self.y)
        
        if direcao == "direita":
            self.x = min(self.x + 1, grid_cols - 1)
        elif direcao == "esquerda":
            self.x = max(self.x - 1, 0)
        elif direcao == "cima":
            self.y = max(self.y - 1, 0)
        elif direcao == "baixo":
            self.y = min(self.y + 1, grid_rows - 1)
        
        return pos_anterior
    
    def esta_no_destino(self, destino: Tuple[int, int]) -> bool:
        """Verifica se o jogador alcançou o destino."""
        return (self.x, self.y) == destino
    
    def esta_na_agua(self, agua: List[Tuple[int, int]]) -> bool:
        """Verifica se o jogador está em uma célula de água."""
        return (self.x, self.y) in agua
    
    def get_posicao_pixel(self) -> Tuple[int, int]:
        """Retorna a posição do jogador em pixels."""
        return (self.x * TAMANHO_CELULA, self.y * TAMANHO_CELULA)


# ==================== FUNÇÕES DE CÂMERA ====================
def inicializar_camera() -> Optional[cv2.VideoCapture]:
    """
    Tenta inicializar a câmera testando diferentes índices.
    Retorna o objeto VideoCapture ou None se falhar.
    """
    for camera_index in range(3):
        print(f"Tentando câmera no índice {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        
        if cap.isOpened():
            print(f"Câmera conectada no índice {camera_index}")
            time.sleep(2)  # Aguarda inicialização
            
            # Testa captura de frames
            frames_ok = 0
            for i in range(5):
                ret, _ = cap.read()
                if ret:
                    frames_ok += 1
                time.sleep(0.1)
            
            if frames_ok >= 3:
                print(f"✓ Câmera funcionando corretamente! ({frames_ok}/5 frames capturados)")
                return cap
            else:
                print(f"✗ Câmera no índice {camera_index} instável ({frames_ok}/5 frames). Tentando próxima...")
                cap.release()
        
        if cap is not None:
            cap.release()
    
    _mostrar_erro_camera()
    return None


def _mostrar_erro_camera() -> None:
    """Exibe mensagens de erro quando a câmera não pode ser inicializada."""
    print("\n❌ Não foi possível acessar nenhuma câmera.")
    print("Possíveis soluções:")
    print("1. Verifique as permissões em: Configurações do Sistema > Privacidade e Segurança > Câmera")
    print("2. Feche outras aplicações que possam estar usando a câmera (Zoom, FaceTime, etc)")
    print("3. Tente desconectar e reconectar a câmera")


def liberar_camera(cap: Optional[cv2.VideoCapture]) -> None:
    """Libera a câmera de forma segura."""
    print("\n✓ Encerrando jogo...")
    print("✓ Liberando câmera...")
    if cap is not None and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
    print("✓ Jogo encerrado com sucesso!\n")


# ==================== FUNÇÕES DE IMAGEM ====================
def criar_imagem_personagem(tamanho: int, cor: tuple) -> np.ndarray:
    """Cria uma imagem de personagem (círculo colorido com olhos)."""
    img = np.zeros((tamanho, tamanho, 4), dtype=np.uint8)
    centro = tamanho // 2
    raio = tamanho // 3
    
    # Corpo
    cv2.circle(img, (centro, centro), raio, (*cor, 255), -1)
    
    # Olhos
    cv2.circle(img, (centro - raio // 2, centro - raio // 3), raio // 5, (0, 0, 0, 255), -1)
    cv2.circle(img, (centro + raio // 2, centro - raio // 3), raio // 5, (0, 0, 0, 255), -1)
    
    return img


def criar_imagem_destino(tamanho: int) -> np.ndarray:
    """Cria uma imagem de destino (estrela amarela)."""
    img = np.zeros((tamanho, tamanho, 4), dtype=np.uint8)
    centro = tamanho // 2
    raio_ext = tamanho // 3
    raio_int = raio_ext // 2
    
    # Pontos da estrela
    pontos = []
    for i in range(10):
        angulo = (i * np.pi / 5) - np.pi / 2
        raio = raio_ext if i % 2 == 0 else raio_int
        x = int(centro + raio * np.cos(angulo))
        y = int(centro + raio * np.sin(angulo))
        pontos.append([x, y])
    
    pontos = np.array(pontos, dtype=np.int32)
    cv2.fillPoly(img, [pontos], (0, 255, 255, 255))
    
    return img


def carregar_ou_criar_imagem(caminho: str, tamanho: int, criar_funcao, *args) -> np.ndarray:
    """
    Tenta carregar uma imagem de arquivo, ou cria uma imagem padrão se falhar.
    """
    img = cv2.imread(caminho, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        print(f"Aviso: '{caminho}' não encontrado. Usando imagem padrão.")
        return criar_funcao(tamanho, *args)
    
    return cv2.resize(img, (tamanho, tamanho))


def overlay_image(fundo: np.ndarray, imagem: np.ndarray, x: int, y: int) -> None:
    """Desenha imagem PNG (com transparência) sobre o fundo."""
    h, w = imagem.shape[:2]
    
    if imagem.shape[2] == 4:  # Com canal alpha
        alpha_s = imagem[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        
        for c in range(3):
            fundo[y:y+h, x:x+w, c] = (alpha_s * imagem[:, :, c] +
                                      alpha_l * fundo[y:y+h, x:x+w, c])
    else:
        fundo[y:y+h, x:x+w] = imagem


# ==================== FUNÇÕES DE QR CODE ====================
def processar_qr_codes(codigos, ultimo_codigo: str, ultimo_tempo: float) -> Optional[Tuple[str, str, str, float]]:
    """
    Processa os QR codes detectados e retorna um comando válido.
    Retorna (jogador, direcao, texto, tempo) ou None.
    """
    if not codigos:
        return None
    
    print(f"✓ Detectou {len(codigos)} QR code(s)")
    
    # Ordena QR da direita para esquerda
    codigos_ordenados = sorted(codigos, key=lambda c: c.rect.left, reverse=True)
    
    for codigo in codigos_ordenados:
        texto = codigo.data.decode("utf-8").strip().lower()
        print(f"  Texto: '{texto}'")
        
        # Verifica formato: "N-direcao"
        if '-' not in texto:
            continue
        
        partes = texto.split('-')
        if len(partes) != 2:
            continue
        
        jogador, direcao = partes
        
        # Verifica delay
        if texto != ultimo_codigo or time.time() - ultimo_tempo > DELAY_LEITURA_QR:
            print(f"  ✓ Comando aceito: Jogador {jogador} - {direcao}")
            return (jogador, direcao, texto, time.time())
        else:
            print(f"  ✗ Ignorado (delay ou duplicado)")
    
    return None


# ==================== FUNÇÕES DE RENDERIZAÇÃO ====================
def criar_tela_base() -> np.ndarray:
    """Cria a tela base do jogo (fundo branco)."""
    return np.full((ALTURA_TELA, LARGURA_TELA, 3), 255, dtype=np.uint8)


def desenhar_agua(tela: np.ndarray, agua: List[Tuple[int, int]]) -> None:
    """Desenha as células de água na tela."""
    for (ax, ay) in agua:
        cv2.rectangle(
            tela,
            (ax * TAMANHO_CELULA, ay * TAMANHO_CELULA),
            ((ax + 1) * TAMANHO_CELULA, (ay + 1) * TAMANHO_CELULA),
            COR_AGUA,
            -1
        )


def desenhar_destino(tela: np.ndarray, destino: Tuple[int, int], destino_img: Optional[np.ndarray]) -> None:
    """Desenha o destino na tela."""
    dx, dy = destino
    x_destino = dx * TAMANHO_CELULA
    y_destino = dy * TAMANHO_CELULA
    
    # Retângulo amarelo de fundo
    cv2.rectangle(
        tela,
        (x_destino, y_destino),
        (x_destino + TAMANHO_CELULA, y_destino + TAMANHO_CELULA),
        COR_DESTINO,
        -1
    )
    
    # Estrela por cima (se disponível)
    if destino_img is not None:
        overlay_image(tela, destino_img, x_destino, y_destino)


def desenhar_jogador(tela: np.ndarray, jogador: Jogador, img_normal: np.ndarray, img_dano: np.ndarray) -> None:
    """Desenha o jogador na tela."""
    img = img_dano if jogador.morreu else img_normal
    x, y = jogador.get_posicao_pixel()
    overlay_image(tela, img, x, y)


def desenhar_mensagem(tela: np.ndarray, mensagem: str, cor: tuple) -> None:
    """Desenha mensagem na tela."""
    cv2.putText(tela, mensagem, (130, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.5, cor, 3)


def desenhar_preview_camera(tela: np.ndarray, frame: np.ndarray) -> None:
    """Desenha o preview da câmera no canto da tela."""
    frame_invertido = cv2.flip(frame, 1)
    preview = cv2.resize(frame_invertido, (PREVIEW_LARGURA, PREVIEW_ALTURA))
    tela[PREVIEW_Y:PREVIEW_Y+PREVIEW_ALTURA, PREVIEW_X:PREVIEW_X+PREVIEW_LARGURA] = preview


# ==================== FUNÇÕES DE LÓGICA DE JOGO ====================
def verificar_fim_de_jogo(jogador1: Jogador, jogador2: Jogador, config: ConfiguracaoJogo) -> Optional[str]:
    """
    Verifica condições de fim de jogo.
    Retorna mensagem de vitória/derrota ou None.
    """
    # Verifica vitória
    if jogador1.esta_no_destino(config.destino):
        return "Jogador 1 venceu!"
    if jogador2.esta_no_destino(config.destino):
        return "Jogador 2 venceu!"
    
    # Verifica morte
    if jogador1.morreu and jogador2.morreu:
        return "Ambos morreram!"
    if jogador1.morreu:
        return "Jogador 1 morreu!"
    if jogador2.morreu:
        return "Jogador 2 morreu!"
    
    return None


def processar_movimento_jogador(jogador: Jogador, jogador_id: str, direcao: str, config: ConfiguracaoJogo) -> None:
    """Processa o movimento de um jogador."""
    pos_anterior = jogador.mover(direcao, config.grid_cols, config.grid_rows)
    print(f"  Jogador {jogador_id} moveu de {pos_anterior} -> ({jogador.x}, {jogador.y})")


# ==================== FUNÇÃO PRINCIPAL ====================
def main():
    """Função principal do jogo."""
    # Inicializa câmera
    cap = inicializar_camera()
    if cap is None:
        return
    
    # Configurações
    config = ConfiguracaoJogo()
    
    # Cria jogadores
    jogador1 = Jogador(1, 0, config.grid_rows - 1, COR_JOGADOR1, COR_JOGADOR1_DANO)
    jogador2 = Jogador(2, 0, config.grid_rows - 1, COR_JOGADOR2, COR_JOGADOR2_DANO)
    
    # Carrega imagens
    jogador1_img = carregar_ou_criar_imagem("personagem.png", TAMANHO_CELULA, 
                                            criar_imagem_personagem, COR_JOGADOR1)
    jogador2_img = criar_imagem_personagem(TAMANHO_CELULA, COR_JOGADOR2)
    jogador1_dano_img = carregar_ou_criar_imagem("personagem_dano.png", TAMANHO_CELULA,
                                                 criar_imagem_personagem, COR_JOGADOR1_DANO)
    jogador2_dano_img = criar_imagem_personagem(TAMANHO_CELULA, COR_JOGADOR2_DANO)
    destino_img = carregar_ou_criar_imagem("destino.png", TAMANHO_CELULA, criar_imagem_destino)
    
    # Estado do jogo
    jogo_ativo = True
    ultimo_codigo = None
    ultimo_tempo = time.time()
    mensagem_fim = None
    
    # Prepara janela
    print("\n✓ Iniciando jogo...")
    print("✓ Pressione 'q' para sair\n")
    cv2.namedWindow("Jogo por QR Code - 2 Jogadores", cv2.WINDOW_NORMAL)
    
    # Loop principal
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar frame da câmera")
            break
        
        # Processa comandos QR
        if jogo_ativo:
            codigos = decode(frame)
            resultado = processar_qr_codes(codigos, ultimo_codigo, ultimo_tempo)
            
            if resultado:
                jogador_id, direcao, ultimo_codigo, ultimo_tempo = resultado
                
                # Move jogador correspondente
                if jogador_id == "1":
                    processar_movimento_jogador(jogador1, jogador_id, direcao, config)
                elif jogador_id == "2":
                    processar_movimento_jogador(jogador2, jogador_id, direcao, config)
            
            # Verifica colisões com água
            if jogador1.esta_na_agua(config.agua):
                jogador1.morreu = True
            if jogador2.esta_na_agua(config.agua):
                jogador2.morreu = True
            
            # Verifica fim de jogo
            mensagem_fim = verificar_fim_de_jogo(jogador1, jogador2, config)
            if mensagem_fim:
                jogo_ativo = False
        
        # Renderiza tela
        tela = criar_tela_base()
        desenhar_agua(tela, config.agua)
        desenhar_destino(tela, config.destino, destino_img)
        desenhar_jogador(tela, jogador1, jogador1_img, jogador1_dano_img)
        desenhar_jogador(tela, jogador2, jogador2_img, jogador2_dano_img)
        desenhar_preview_camera(tela, frame)
        
        # Desenha mensagem de fim de jogo
        if mensagem_fim:
            cor = COR_VITORIA if "venceu" in mensagem_fim else COR_DERROTA
            desenhar_mensagem(tela, mensagem_fim, cor)
        
        # Mostra tela
        cv2.imshow("Jogo por QR Code - 2 Jogadores", tela)
        
        # Verifica saída
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.getWindowProperty("Jogo por QR Code - 2 Jogadores", cv2.WND_PROP_VISIBLE) < 1:
            break
    
    # Limpeza
    liberar_camera(cap)


if __name__ == "__main__":
    main()
