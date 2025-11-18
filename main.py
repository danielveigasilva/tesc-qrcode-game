import cv2
import numpy as np
import time
from pyzbar.pyzbar import decode


def carregar_imagem(caminho, tamanho):
    """Carrega e redimensiona imagem."""
    img = cv2.imread(caminho, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"❌ Erro: '{caminho}' não encontrado!")
        return None
    return cv2.resize(img, (tamanho, tamanho))


def extrair_textos_qr(codigos):
    """Extrai textos dos QR codes."""
    return [codigo.data.decode("utf-8").strip().lower() for codigo in codigos]


def extrair_comandos_jogador(textos, jogador):
    """Extrai comandos válidos de um jogador (entre inicio e fim)."""
    cartas = [t for t in textos if t.startswith(f"{jogador}-")]
    
    # Valida ordem: inicio primeiro, fim último
    if not cartas or cartas[0] != f"{jogador}-inicio" or cartas[-1] != f"{jogador}-fim":
        return []
    
    # Extrai apenas direções válidas (entre inicio e fim)
    comandos = []
    for carta in cartas[1:-1]:  # Pula inicio e fim
        direcao = carta.split('-')[1]
        if direcao in ["cima", "baixo", "esquerda", "direita"]:
            comandos.append(direcao)
    
    return comandos


def processar_sequencia_comandos(codigos_ordenados, mostrar_console=True, 
                                cartas_anteriores_j1=None, cartas_anteriores_j2=None):
    """Processa QR codes e retorna sequências válidas."""
    cartas_anteriores_j1 = cartas_anteriores_j1 or []
    cartas_anteriores_j2 = cartas_anteriores_j2 or []
    
    # Extrai textos
    textos = extrair_textos_qr(codigos_ordenados)
    
    # Separa por usuário
    cartas_usuario1 = [t for t in textos if t.startswith("1-")]
    cartas_usuario2 = [t for t in textos if t.startswith("2-")]
    
    # Mostra no console se mudou
    if mostrar_console:
        if (set(cartas_usuario1) != set(cartas_anteriores_j1) or 
            set(cartas_usuario2) != set(cartas_anteriores_j2) or 
            (not cartas_usuario1 and not cartas_usuario2)):
            print("\nCartas que estão na tela:")
            for usuario, cartas in [("1", cartas_usuario1), ("2", cartas_usuario2)]:
                comandos = [c.split('-')[1].capitalize() for c in cartas if '-' in c] if cartas else ["Nenhuma"]
                print(f"Usuario {usuario} - {', '.join(comandos)}")
            print("="*60)
    
    # Extrai sequências válidas
    sequencias = {}
    for jogador in ["1", "2"]:
        comandos = extrair_comandos_jogador(textos, jogador)
        if comandos:
            sequencias[jogador] = comandos
    
    return sequencias, cartas_usuario1, cartas_usuario2


def inicializar_camera():
    """Tenta inicializar a câmera em diferentes índices."""
    for camera_index in range(3):
        print(f"Tentando câmera no índice {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        
        if cap.isOpened():
            print(f"Câmera conectada no índice {camera_index}")
            
            # Configura autofoco (se disponível)
            try:
                cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Ativa autofoco
                cap.set(cv2.CAP_PROP_FOCUS, 0)      # Reset para autofoco automático
                print("✓ Autofoco ativado")
            except:
                print("⚠️ Autofoco não disponível nesta câmera")
            
            time.sleep(2)
            
            # Testa estabilidade da câmera
            frames_ok = sum(1 for _ in range(5) if cap.read()[0] or not time.sleep(0.1))
            
            if frames_ok >= 3:
                print(f"✓ Câmera funcionando corretamente! ({frames_ok}/5 frames capturados)")
                return cap
            
            print(f"✗ Câmera no índice {camera_index} instável ({frames_ok}/5 frames). Tentando próxima...")
            cap.release()
    
    print("\n❌ Não foi possível acessar nenhuma câmera.")
    print("Possíveis soluções:")
    print("1. Verifique as permissões em: Configurações do Sistema > Privacidade e Segurança > Câmera")
    print("2. Feche outras aplicações que possam estar usando a câmera (Zoom, FaceTime, etc)")
    print("3. Tente desconectar e reconectar a câmera")
    return None


def liberar_camera(cap):
    """Libera recursos da câmera."""
    print("\n✓ Encerrando jogo...")
    print("✓ Liberando câmera...")
    if cap is not None and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
    print("✓ Jogo encerrado com sucesso!\n")


def carregar_recursos(tamanho_celula, largura, altura):
    """Carrega todas as imagens e recursos do jogo."""
    recursos = {
        'personagem1': carregar_imagem("imagens/usuario1.png", tamanho_celula),
        'personagem2': carregar_imagem("imagens/usuario2.png", tamanho_celula),
        'personagem1_dano': carregar_imagem("imagens/usuario1_dano.png", tamanho_celula),
        'personagem2_dano': carregar_imagem("imagens/usuario2_dano.png", tamanho_celula),
        'destino': carregar_imagem("imagens/casa.png", tamanho_celula)
    }
    
    # Carrega fundo
    fundo = cv2.imread("imagens/fase1_background.png")
    if fundo is not None:
        recursos['fundo'] = cv2.resize(fundo, (largura, altura))
        print("✓ Fundo carregado!")
    else:
        print("⚠️ Aviso: 'imagens/fase1_background.png' não encontrado. Usando fundo branco.")
        recursos['fundo'] = np.full((altura, largura, 3), 255, dtype=np.uint8)
    
    return recursos


def desenhar_mensagem_executando(tela, largura, altura, usuario, cor):
    """Desenha mensagem de execução centralizada na tela."""
    overlay = tela.copy()
    cv2.rectangle(overlay, (0, altura//2 - 100), (largura, altura//2 + 100), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, tela, 0.3, 0, tela)
    
    texto1, texto2 = "Analisando caminho", f"Usuario {usuario}"
    (w1, _), _ = cv2.getTextSize(texto1, cv2.FONT_HERSHEY_SIMPLEX, 2.5, 6)
    (w2, _), _ = cv2.getTextSize(texto2, cv2.FONT_HERSHEY_SIMPLEX, 2.5, 6)
    
    y_centro = altura // 2
    cv2.putText(tela, texto1, ((largura - w1) // 2, y_centro - 40), 
               cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 6)
    cv2.putText(tela, texto2, ((largura - w2) // 2, y_centro + 60), 
               cv2.FONT_HERSHEY_SIMPLEX, 2.5, cor, 6)


def desenhar_cenario(tela, agua, destino, destino_img, tamanho_celula):
    """Desenha água e destino no cenário."""
    # Desenha água
    for (ax, ay) in agua:
        cv2.rectangle(tela, (ax * tamanho_celula, ay * tamanho_celula),
                     ((ax + 1) * tamanho_celula, (ay + 1) * tamanho_celula),
                     (255, 100, 100), -1)
    
    # Desenha destino (apenas a imagem, sem quadrado amarelo)
    if destino_img is not None:
        dx, dy = destino
        x_destino, y_destino = dx * tamanho_celula, dy * tamanho_celula
        overlay_image(tela, destino_img, x_destino, y_destino)


def executar_movimento(pos_x, pos_y, direcao, grid_cols, grid_rows):
    """Executa um movimento e retorna nova posição."""
    if direcao == "direita":
        return min(pos_x + 1, grid_cols - 1), pos_y
    elif direcao == "esquerda":
        return max(pos_x - 1, 0), pos_y
    elif direcao == "cima":
        return pos_x, max(pos_y - 1, 0)
    elif direcao == "baixo":
        return pos_x, min(pos_y + 1, grid_rows - 1)
    return pos_x, pos_y


def main():
    # Inicializa câmera
    cap = inicializar_camera()
    if cap is None:
        return

    # Configurações do jogo
    LARGURA, ALTURA = 1280, 960
    TAMANHO_CELULA = 128
    grid_cols, grid_rows = LARGURA // TAMANHO_CELULA, ALTURA // TAMANHO_CELULA
    
    # Preview da câmera
    PREVIEW_CONFIG = {'largura': 320, 'altura': 240, 'x': 20, 'y': 20}
    
    # Carrega recursos
    recursos = carregar_recursos(TAMANHO_CELULA, LARGURA, ALTURA)
    
    # Configuração do cenário
    agua = [(2, 5), (3, 5), (4, 5)]
    destino = (grid_cols - 1, 0)
    
    # Posições iniciais
    pos1 = [0, grid_rows - 1]
    pos2 = [0, grid_rows - 1]
    
    # Estado do jogo
    estado = {
        'sequencia_j1_processada': False,
        'sequencia_j2_processada': False,
        'aguardando_ambas': True,
        'executando_j1': False,
        'executando_j2': False,
        'jogo_ativo': True,
        'morreu1': False,
        'morreu2': False,
        'vencedor': None
    }
    
    # Filas de comandos
    fila_j1, fila_j2 = [], []
    tempo_ultimo_movimento = time.time()
    
    # Controle de console e estabilização
    tempo_ultima_atualizacao_console = time.time()
    cartas_anteriores_j1, cartas_anteriores_j2 = [], []
    cartas_estavel_j1, cartas_estavel_j2 = [], []
    contagem_estavel_j1, contagem_estavel_j2 = 0, 0
    FRAMES_NECESSARIOS = 5
    
    print("\n✓ Iniciando jogo...")
    print("✓ Pressione 'q' para sair\n")
    cv2.namedWindow("Jogo por QR Code - 2 Jogadores", cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar frame da câmera")
            break

        codigos = decode(frame)
        frame_invertido = cv2.flip(frame, 1)

        # Processa QR codes
        if estado['jogo_ativo'] and codigos and estado['aguardando_ambas']:
            codigos_ordenados = sorted(codigos, key=lambda c: c.rect.left)
            tempo_atual = time.time()
            mostrar_no_console = (tempo_atual - tempo_ultima_atualizacao_console) >= 1.0
            
            sequencias, cartas_u1, cartas_u2 = processar_sequencia_comandos(
                codigos_ordenados, False, cartas_anteriores_j1, cartas_anteriores_j2)
            
            # Estabilização
            contagem_estavel_j1 = contagem_estavel_j1 + 1 if set(cartas_u1) == set(cartas_estavel_j1) else 1
            contagem_estavel_j2 = contagem_estavel_j2 + 1 if set(cartas_u2) == set(cartas_estavel_j2) else 1
            cartas_estavel_j1, cartas_estavel_j2 = cartas_u1, cartas_u2
            
            # Atualiza console se estável
            if mostrar_no_console:
                mudou_j1 = set(cartas_estavel_j1) != set(cartas_anteriores_j1) and contagem_estavel_j1 >= FRAMES_NECESSARIOS
                mudou_j2 = set(cartas_estavel_j2) != set(cartas_anteriores_j2) and contagem_estavel_j2 >= FRAMES_NECESSARIOS
                
                if mudou_j1 or mudou_j2:
                    print("\nCartas que estão na tela:")
                    for i, cartas in enumerate([cartas_estavel_j1, cartas_estavel_j2], 1):
                        cmd = [c.split('-')[1].capitalize() for c in cartas if '-' in c] if cartas else ["Nenhuma"]
                        print(f"Usuario {i} - {', '.join(cmd)}")
                    print("="*60)
                    cartas_anteriores_j1, cartas_anteriores_j2 = cartas_estavel_j1.copy(), cartas_estavel_j2.copy()
                
                tempo_ultima_atualizacao_console = tempo_atual
            
            # Captura sequências
            if "1" in sequencias and not estado['sequencia_j1_processada']:
                fila_j1 = sequencias["1"].copy()
                estado['sequencia_j1_processada'] = True
                print(f"✓ Sequência completa capturada do Usuario 1: {sequencias['1']}")
            
            if "2" in sequencias and not estado['sequencia_j2_processada']:
                fila_j2 = sequencias["2"].copy()
                estado['sequencia_j2_processada'] = True
                print(f"✓ Sequência completa capturada do Usuario 2: {sequencias['2']}")
            
            if estado['sequencia_j1_processada'] and estado['sequencia_j2_processada']:
                estado['aguardando_ambas'] = False
                estado['executando_j1'] = True
                print("\n🎬 Iniciando execução dos movimentos...")
        
        # Executa movimentos
        if estado['jogo_ativo'] and time.time() - tempo_ultimo_movimento > 0.8:
            if estado['executando_j1'] and fila_j1:
                pos1[0], pos1[1] = executar_movimento(pos1[0], pos1[1], fila_j1.pop(0), grid_cols, grid_rows)
                tempo_ultimo_movimento = time.time()
                if not fila_j1:
                    estado['executando_j1'], estado['executando_j2'] = False, True
            
            elif estado['executando_j2'] and fila_j2:
                pos2[0], pos2[1] = executar_movimento(pos2[0], pos2[1], fila_j2.pop(0), grid_cols, grid_rows)
                tempo_ultimo_movimento = time.time()

        # Renderiza tela
        tela = recursos['fundo'].copy()
        
        # Mensagens
        if estado['aguardando_ambas']:
            pass  # Removido: desenhar_mensagem_aguardando
        elif estado['executando_j1']:
            desenhar_mensagem_executando(tela, LARGURA, ALTURA, "1", (0, 255, 0))
        elif estado['executando_j2']:
            desenhar_mensagem_executando(tela, LARGURA, ALTURA, "2", (0, 100, 255))

        # Cenário
        desenhar_cenario(tela, agua, destino, recursos['destino'], TAMANHO_CELULA)
        
        # Personagens
        if tuple(pos1) in agua:
            estado['morreu1'] = True
        if tuple(pos2) in agua:
            estado['morreu2'] = True
        
        img1 = recursos['personagem1_dano'] if estado['morreu1'] else recursos['personagem1']
        img2 = recursos['personagem2_dano'] if estado['morreu2'] else recursos['personagem2']
        
        overlay_image(tela, img1, pos1[0] * TAMANHO_CELULA, pos1[1] * TAMANHO_CELULA)
        overlay_image(tela, img2, pos2[0] * TAMANHO_CELULA, pos2[1] * TAMANHO_CELULA)

        # Vitória/Morte
        if estado['jogo_ativo']:
            if tuple(pos1) == destino:
                estado['jogo_ativo'], estado['vencedor'] = False, "Jogador 1"
            elif tuple(pos2) == destino:
                estado['jogo_ativo'], estado['vencedor'] = False, "Jogador 2"
        
        if estado['vencedor']:
            cv2.putText(tela, f"{estado['vencedor']} venceu!", (300, 480), 
                       cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 150, 0), 6)
        
        if (estado['morreu1'] or estado['morreu2']) and estado['jogo_ativo']:
            estado['jogo_ativo'] = False
            msg = "Ambos morreram!" if estado['morreu1'] and estado['morreu2'] else \
                  f"Jogador {'1' if estado['morreu1'] else '2'} morreu!"
            cv2.putText(tela, msg, (260 if "Jogador" in msg else 300, 480), 
                       cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 6)

        # Preview da câmera
        preview = cv2.resize(frame_invertido, (PREVIEW_CONFIG['largura'], PREVIEW_CONFIG['altura']))
        y, x = PREVIEW_CONFIG['y'], PREVIEW_CONFIG['x']
        tela[y:y+PREVIEW_CONFIG['altura'], x:x+PREVIEW_CONFIG['largura']] = preview

        cv2.imshow("Jogo por QR Code - 2 Jogadores", tela)

        if cv2.waitKey(1) & 0xFF == ord('q') or \
           cv2.getWindowProperty("Jogo por QR Code - 2 Jogadores", cv2.WND_PROP_VISIBLE) < 1:
            break

    liberar_camera(cap)


def overlay_image(fundo, imagem, x, y):
    """Desenha imagem PNG (com transparência) sobre o fundo."""
    h, w = imagem.shape[:2]
    if imagem.shape[2] == 4:
        alpha_s = imagem[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s

        for c in range(3):
            fundo[y:y+h, x:x+w, c] = (alpha_s * imagem[:, :, c] +
                                      alpha_l * fundo[y:y+h, x:x+w, c])
    else:
        fundo[y:y+h, x:x+w] = imagem


if __name__ == "__main__":
    main()
