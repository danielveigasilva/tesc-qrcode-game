import cv2
import numpy as np
import time
from pyzbar.pyzbar import decode


def criar_imagem_personagem(tamanho, cor):
    """Cria uma imagem simples para o personagem (círculo colorido)."""
    img = np.zeros((tamanho, tamanho, 4), dtype=np.uint8)
    centro = tamanho // 2
    raio = tamanho // 3
    cv2.circle(img, (centro, centro), raio, (*cor, 255), -1)
    # Adiciona olhos
    cv2.circle(img, (centro - raio // 2, centro - raio // 3), raio // 5, (0, 0, 0, 255), -1)
    cv2.circle(img, (centro + raio // 2, centro - raio // 3), raio // 5, (0, 0, 0, 255), -1)
    return img


def criar_imagem_destino(tamanho):
    """Cria uma imagem simples para o destino (estrela amarela)."""
    img = np.zeros((tamanho, tamanho, 4), dtype=np.uint8)
    centro = tamanho // 2
    raio_ext = tamanho // 3
    raio_int = raio_ext // 2
    
    # Cria pontos da estrela
    pontos = []
    for i in range(10):
        angulo = (i * np.pi / 5) - np.pi / 2
        raio = raio_ext if i % 2 == 0 else raio_int
        x = int(centro + raio * np.cos(angulo))
        y = int(centro + raio * np.sin(angulo))
        pontos.append([x, y])
    
    pontos = np.array(pontos, dtype=np.int32)
    cv2.fillPoly(img, [pontos], (0, 255, 255, 255))  # Amarelo
    return img


def redimensionar_com_proporcao(img, tamanho_alvo):
    """Redimensiona imagem mantendo a proporção e centralizando em um quadrado."""
    h, w = img.shape[:2]
    
    # Calcula escala mantendo proporção
    scale = min(tamanho_alvo / w, tamanho_alvo / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    # Redimensiona mantendo proporção
    img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Cria canvas transparente quadrado
    if img.shape[2] == 4:  # Com canal alpha
        canvas = np.zeros((tamanho_alvo, tamanho_alvo, 4), dtype=np.uint8)
    else:
        canvas = np.zeros((tamanho_alvo, tamanho_alvo, 3), dtype=np.uint8)
    
    # Centraliza a imagem no canvas
    y_offset = (tamanho_alvo - new_h) // 2
    x_offset = (tamanho_alvo - new_w) // 2
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized
    
    return canvas


def carregar_ou_criar_imagem(caminho, tamanho, funcao_criar, mensagem_aviso):
    """Carrega imagem de arquivo ou cria uma padrão se não existir."""
    img = cv2.imread(caminho, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Aviso: '{caminho}' não encontrado. {mensagem_aviso}")
        return funcao_criar()
    return redimensionar_com_proporcao(img, tamanho)


def processar_sequencia_comandos(codigos_ordenados, mostrar_console=True, cartas_anteriores_j1=None, cartas_anteriores_j2=None):
    """
    Processa os QR codes detectados e extrai sequências válidas por jogador.
    Retorna um dicionário com as sequências de comandos para cada jogador que
    tenha uma sequência completa (inicio -> comandos -> fim).
    
    Formato de retorno: {"1": ["cima", "direita"], "2": ["esquerda", "baixo"]}
    """
    if cartas_anteriores_j1 is None:
        cartas_anteriores_j1 = []
    if cartas_anteriores_j2 is None:
        cartas_anteriores_j2 = []
    
    # Extrai todos os textos dos QR codes
    textos = []
    for codigo in codigos_ordenados:
        texto = codigo.data.decode("utf-8").strip().lower()
        textos.append(texto)
    
    # Separa as cartas detectadas por usuário
    cartas_usuario1 = [t for t in textos if t.startswith("1-")]
    cartas_usuario2 = [t for t in textos if t.startswith("2-")]
    
    # Verifica se houve mudança nas cartas detectadas
    mudou_j1 = set(cartas_usuario1) != set(cartas_anteriores_j1)
    mudou_j2 = set(cartas_usuario2) != set(cartas_anteriores_j2)
    
    # Mostra no console apenas se houve mudança E se mostrar_console=True
    if mostrar_console and (mudou_j1 or mudou_j2):
        print("\n" + "="*60)
        
        # Mostra usuário 1 (se houver cartas)
        if cartas_usuario1:
            comandos_legivel = [c.split('-')[1].capitalize() for c in cartas_usuario1 if '-' in c]
            print(f"Usuario 1: {', '.join(comandos_legivel)}")
        
        # Mostra usuário 2 (se houver cartas)
        if cartas_usuario2:
            comandos_legivel = [c.split('-')[1].capitalize() for c in cartas_usuario2 if '-' in c]
            print(f"Usuario 2: {', '.join(comandos_legivel)}")
    
    sequencias = {}
    
    # Processa cada jogador
    for jogador in ["1", "2"]:
        inicio_marker = f"{jogador}-inicio"
        fim_marker = f"{jogador}-fim"
        
        cartas_atuais = cartas_usuario1 if jogador == "1" else cartas_usuario2
        mudou = mudou_j1 if jogador == "1" else mudou_j2
        
        # Verifica se há início e fim
        if inicio_marker in textos and fim_marker in textos:
            idx_inicio = textos.index(inicio_marker)
            idx_fim = textos.index(fim_marker)
            
            # VALIDAÇÃO DE ORDEM: Início deve ser a primeira carta do jogador, Fim a última
            if cartas_atuais:
                primeira_carta = cartas_atuais[0]
                ultima_carta = cartas_atuais[-1]
                
                # Verifica se a ordem está correta
                ordem_correta = (primeira_carta == inicio_marker and ultima_carta == fim_marker)
                
                if not ordem_correta:
                    # Não aceita a sequência se a ordem estiver incorreta
                    continue  # Pula para o próximo jogador
            
            # Garante que sempre processamos do menor índice pro maior
            idx_menor = min(idx_inicio, idx_fim)
            idx_maior = max(idx_inicio, idx_fim)
            
            # Calcula quantas cartas há entre início e fim
            quantidade_entre = idx_maior - idx_menor - 1
            
            # Extrai comandos entre as duas cartas (início e fim)
            comandos = []
            comandos_encontrados = []  # Para debug
            for i in range(idx_menor + 1, idx_maior):
                texto = textos[i]
                # Verifica se é um comando válido para este jogador
                if texto.startswith(f"{jogador}-"):
                    comandos_encontrados.append(texto)
                    partes = texto.split('-')
                    if len(partes) == 2:
                        direcao = partes[1]
                        if direcao in ["cima", "baixo", "esquerda", "direita"]:
                            comandos.append(direcao)
            
            # Adiciona se houver comandos
            if comandos:
                sequencias[jogador] = comandos
        elif mostrar_console and mudou and cartas_atuais:
            # Silencioso - não mostra nada se faltar início ou fim
            pass
    
    if mostrar_console and (mudou_j1 or mudou_j2):
        print("="*60)
    
    return sequencias, cartas_usuario1, cartas_usuario2


def main():
    # Tenta diferentes índices de câmera (útil para câmeras externas no macOS)
    cap = None
    for camera_index in range(3):  # Tenta índices 0, 1, 2
        print(f"Tentando câmera no índice {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            print(f"Câmera conectada no índice {camera_index}")
            # Aguarda mais tempo para a câmera inicializar
            time.sleep(2)
            # Tenta ler múltiplos frames para garantir que a câmera está realmente funcionando
            frames_ok = 0
            for i in range(5):
                ret, _ = cap.read()
                if ret:
                    frames_ok += 1
                time.sleep(0.1)
            
            if frames_ok >= 3:
                print(f"✓ Câmera funcionando corretamente! ({frames_ok}/5 frames capturados)")
                break
            else:
                print(f"✗ Câmera no índice {camera_index} instável ({frames_ok}/5 frames). Tentando próxima...")
                cap.release()
                cap = None
        else:
            if cap is not None:
                cap.release()
            cap = None
    
    if cap is None or not cap.isOpened():
        print("\n❌ Não foi possível acessar nenhuma câmera.")
        print("Possíveis soluções:")
        print("1. Verifique as permissões em: Configurações do Sistema > Privacidade e Segurança > Câmera")
        print("2. Feche outras aplicações que possam estar usando a câmera (Zoom, FaceTime, etc)")
        print("3. Tente desconectar e reconectar a câmera")
        return

    # Configurações do jogo
    largura, altura = 1280, 960  # Resolução maior (2x do original)
    tamanho_celula = 128  # Células maiores para acompanhar
    grid_cols = largura // tamanho_celula
    grid_rows = altura // tamanho_celula
    
    # Configurações do preview da câmera
    PREVIEW_LARGURA = 320  # Dobrado também
    PREVIEW_ALTURA = 240
    PREVIEW_X = 20
    PREVIEW_Y = 20

    # Posições iniciais dos 2 jogadores (em coordenadas de grid)
    # Ambos os jogadores começam no canto inferior ESQUERDO
    pos1_x, pos1_y = 0, grid_rows - 1
    pos2_x, pos2_y = 0, grid_rows - 1

    # Carrega todas as imagens com a função auxiliar
    personagem1_img = carregar_ou_criar_imagem(
        "imagens/usuario1.png", 
        tamanho_celula,
        lambda: criar_imagem_personagem(tamanho_celula, (0, 255, 0)),
        "Usando imagem padrão verde."
    )
    
    personagem2_img = carregar_ou_criar_imagem(
        "imagens/usuario2.png",
        tamanho_celula,
        lambda: criar_imagem_personagem(tamanho_celula, (0, 0, 255)),
        "Usando imagem padrão vermelha."
    )
    
    personagem1_dano = carregar_ou_criar_imagem(
        "personagem_dano.png",
        tamanho_celula,
        lambda: criar_imagem_personagem(tamanho_celula, (0, 100, 0)),
        "Usando imagem padrão verde escuro."
    )
    
    personagem2_dano = criar_imagem_personagem(tamanho_celula, (0, 0, 150))
    
    destino_img = carregar_ou_criar_imagem(
        "destino.png",
        tamanho_celula,
        lambda: criar_imagem_destino(tamanho_celula),
        "Usando estrela padrão."
    )

    # Carrega imagem de fundo
    fundo_img = cv2.imread("imagens/fase1_background.png")
    if fundo_img is not None:
        fundo_img = cv2.resize(fundo_img, (largura, altura))
        print("✓ Fundo carregado!")
    else:
        print("⚠️ Aviso: 'imagens/fase1_background.png' não encontrado. Usando fundo branco.")
        fundo_img = np.full((altura, largura, 3), 255, dtype=np.uint8)

    # Células de água (lista de tuplas)
    agua = [(2, 5), (3, 5), (4, 5)]

    # Célula destino (canto superior DIREITO)
    destino = (grid_cols - 1, 0)

    # Controle de leitura de QR e sequências
    sequencia_j1_processada = False  # Flag para processar apenas uma vez
    sequencia_j2_processada = False
    aguardando_ambas_sequencias = True  # Aguarda ambas as sequências serem detectadas
    
    # Filas de comandos para cada jogador
    fila_comandos_j1 = []
    fila_comandos_j2 = []
    tempo_ultimo_movimento = time.time()
    delay_movimento = 0.8  # segundos entre cada movimento da fila
    
    # Controle de atualização do console
    tempo_ultima_atualizacao_console = time.time()
    delay_console = 5.0  # segundos entre cada atualização do console
    
    # Controle de cartas detectadas anteriormente (para evitar repetir no console)
    cartas_anteriores_j1 = []
    cartas_anteriores_j2 = []
    
    # Sistema de estabilização para evitar oscilação
    cartas_estavel_j1 = []
    cartas_estavel_j2 = []
    contagem_estavel_j1 = 0
    contagem_estavel_j2 = 0
    FRAMES_NECESSARIOS = 3  # Precisa detectar a mesma coisa 3 vezes seguidas
    
    # Controle de execução sequencial
    executando_j1 = False
    executando_j2 = False
    j1_completo = False

    jogo_ativo = True
    morreu1 = False
    morreu2 = False
    
    print("\n✓ Iniciando jogo...")
    print("✓ Pressione 'q' para sair\n")
    
    # Cria a janela antes do loop
    cv2.namedWindow("Jogo por QR Code - 2 Jogadores", cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar frame da câmera")
            break

        # Detecta QR codes no frame original (não invertido)
        codigos = decode(frame)
        
        # Inverte frame apenas para exibição
        frame_invertido = cv2.flip(frame, 1)

        # Processa sequências de comandos (apenas uma vez por jogador)
        if jogo_ativo and codigos and aguardando_ambas_sequencias:
            # Ordena QR da esquerda para direita (ordem natural de leitura)
            codigos_ordenados = sorted(codigos, key=lambda c: c.rect.left)
            
            # Verifica se deve atualizar o console (a cada 5 segundos)
            tempo_atual = time.time()
            mostrar_no_console = (tempo_atual - tempo_ultima_atualizacao_console) >= delay_console
            
            # Processa sequências válidas (SEM mostrar no console ainda)
            sequencias, cartas_usuario1, cartas_usuario2 = processar_sequencia_comandos(
                codigos_ordenados, 
                mostrar_console=False,  # Não mostra ainda - vamos estabilizar primeiro
                cartas_anteriores_j1=cartas_anteriores_j1,
                cartas_anteriores_j2=cartas_anteriores_j2
            )
            
            # Sistema de estabilização - Usuario 1
            if set(cartas_usuario1) == set(cartas_estavel_j1):
                contagem_estavel_j1 += 1
            else:
                cartas_estavel_j1 = cartas_usuario1
                contagem_estavel_j1 = 1
            
            # Sistema de estabilização - Usuario 2
            if set(cartas_usuario2) == set(cartas_estavel_j2):
                contagem_estavel_j2 += 1
            else:
                cartas_estavel_j2 = cartas_usuario2
                contagem_estavel_j2 = 1
            
            # Só atualiza e mostra se estiver estável E na hora de mostrar
            if mostrar_no_console:
                mudou_j1 = set(cartas_estavel_j1) != set(cartas_anteriores_j1) and contagem_estavel_j1 >= FRAMES_NECESSARIOS
                mudou_j2 = set(cartas_estavel_j2) != set(cartas_anteriores_j2) and contagem_estavel_j2 >= FRAMES_NECESSARIOS
                
                if mudou_j1 or mudou_j2:
                    # Mostra no console
                    print("\n" + "="*60)
                    
                    if cartas_estavel_j1:
                        comandos_legivel = [c.split('-')[1].capitalize() for c in cartas_estavel_j1 if '-' in c]
                        print(f"Usuario 1: {', '.join(comandos_legivel)}")
                    
                    if cartas_estavel_j2:
                        comandos_legivel = [c.split('-')[1].capitalize() for c in cartas_estavel_j2 if '-' in c]
                        print(f"Usuario 2: {', '.join(comandos_legivel)}")
                    
                    print("="*60)
                    
                    # Atualiza as cartas anteriores
                    cartas_anteriores_j1 = cartas_estavel_j1.copy()
                    cartas_anteriores_j2 = cartas_estavel_j2.copy()
                
                tempo_ultima_atualizacao_console = tempo_atual
            
            # Adiciona comandos às filas dos jogadores (APENAS UMA VEZ)
            if "1" in sequencias and not sequencia_j1_processada:
                fila_comandos_j1 = sequencias["1"].copy()
                sequencia_j1_processada = True
                print(f"✓ Sequência completa capturada do Usuario 1: {sequencias['1']}")
            
            if "2" in sequencias and not sequencia_j2_processada:
                fila_comandos_j2 = sequencias["2"].copy()
                sequencia_j2_processada = True
                print(f"✓ Sequência completa capturada do Usuario 2: {sequencias['2']}")
            
            # Verifica se AMBAS as sequências foram capturadas
            if sequencia_j1_processada and sequencia_j2_processada:
                aguardando_ambas_sequencias = False
                executando_j1 = True
                print("\n🎬 Iniciando execução dos movimentos...")
        
        # Executa comandos das filas (J1 primeiro, depois J2)
        if jogo_ativo and time.time() - tempo_ultimo_movimento > delay_movimento:
            moveu = False
            
            # Executa Jogador 1 PRIMEIRO
            if executando_j1 and fila_comandos_j1:
                direcao = fila_comandos_j1.pop(0)
                pos_anterior = (pos1_x, pos1_y)
                
                if direcao == "direita":
                    pos1_x = min(pos1_x + 1, grid_cols - 1)
                elif direcao == "esquerda":
                    pos1_x = max(pos1_x - 1, 0)
                elif direcao == "cima":
                    pos1_y = max(pos1_y - 1, 0)
                elif direcao == "baixo":
                    pos1_y = min(pos1_y + 1, grid_rows - 1)
                
                moveu = True
                
                # Se terminou os comandos do J1, passa para o J2
                if not fila_comandos_j1:
                    executando_j1 = False
                    j1_completo = True
                    executando_j2 = True
            
            # Executa Jogador 2 DEPOIS (só se J1 completou)
            elif executando_j2 and fila_comandos_j2:
                direcao = fila_comandos_j2.pop(0)
                pos_anterior = (pos2_x, pos2_y)
                
                if direcao == "direita":
                    pos2_x = min(pos2_x + 1, grid_cols - 1)
                elif direcao == "esquerda":
                    pos2_x = max(pos2_x - 1, 0)
                elif direcao == "cima":
                    pos2_y = max(pos2_y - 1, 0)
                elif direcao == "baixo":
                    pos2_y = min(pos2_y + 1, grid_rows - 1)
                
                moveu = True
            
            if moveu:
                tempo_ultimo_movimento = time.time()

        # Cria tela copiando o fundo
        tela = fundo_img.copy()
        
        # Mostra mensagem de aguardo ou execução
        if aguardando_ambas_sequencias:
            # Mostra quais sequências faltam
            if not sequencia_j1_processada or not sequencia_j2_processada:
                msg_parts = []
                if not sequencia_j1_processada:
                    msg_parts.append("Jogador 1")
                if not sequencia_j2_processada:
                    msg_parts.append("Jogador 2")
                
                # Fundo semi-transparente
                overlay = tela.copy()
                cv2.rectangle(overlay, (0, 30), (largura, 150), (50, 50, 50), -1)
                cv2.addWeighted(overlay, 0.8, tela, 0.2, 0, tela)
                
                cv2.putText(tela, "Aguardando sequencias:", (50, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 4)
                cv2.putText(tela, " e ".join(msg_parts), (50, 130), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 200, 0), 4)
        
        elif executando_j1:
            # Fundo semi-transparente para a mensagem
            overlay = tela.copy()
            cv2.rectangle(overlay, (0, altura//2 - 100), (largura, altura//2 + 100), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, tela, 0.3, 0, tela)
            
            # Texto grande centralizado verticalmente e horizontalmente
            texto1 = "Analisando caminho"
            texto2 = "Usuario 1"
            
            # Calcula tamanho dos textos
            (w1, h1), _ = cv2.getTextSize(texto1, cv2.FONT_HERSHEY_SIMPLEX, 2.5, 6)
            (w2, h2), _ = cv2.getTextSize(texto2, cv2.FONT_HERSHEY_SIMPLEX, 2.5, 6)
            
            # Centraliza horizontalmente e verticalmente
            y_centro = altura // 2
            cv2.putText(tela, texto1, ((largura - w1) // 2, y_centro - 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 6)
            cv2.putText(tela, texto2, ((largura - w2) // 2, y_centro + 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 255, 0), 6)
        
        elif executando_j2:
            # Fundo semi-transparente para a mensagem
            overlay = tela.copy()
            cv2.rectangle(overlay, (0, altura//2 - 100), (largura, altura//2 + 100), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, tela, 0.3, 0, tela)
            
            # Texto grande centralizado verticalmente e horizontalmente
            texto1 = "Analisando caminho"
            texto2 = "Usuario 2"
            
            # Calcula tamanho dos textos
            (w1, h1), _ = cv2.getTextSize(texto1, cv2.FONT_HERSHEY_SIMPLEX, 2.5, 6)
            (w2, h2), _ = cv2.getTextSize(texto2, cv2.FONT_HERSHEY_SIMPLEX, 2.5, 6)
            
            # Centraliza horizontalmente e verticalmente
            y_centro = altura // 2
            cv2.putText(tela, texto1, ((largura - w1) // 2, y_centro - 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 6)
            cv2.putText(tela, texto2, ((largura - w2) // 2, y_centro + 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 100, 255), 6)

        # Desenha água
        for (ax, ay) in agua:
            cv2.rectangle(
                tela,
                (ax * tamanho_celula, ay * tamanho_celula),
                ((ax + 1) * tamanho_celula, (ay + 1) * tamanho_celula),
                (255, 100, 100),
                -1,
            )

        # Desenha destino PRIMEIRO (para ficar atrás dos personagens)
        dx, dy = destino
        x_destino = dx * tamanho_celula
        y_destino = dy * tamanho_celula
        
        # Desenha um retângulo amarelo brilhante para o destino
        cv2.rectangle(
            tela,
            (x_destino, y_destino),
            (x_destino + tamanho_celula, y_destino + tamanho_celula),
            (0, 255, 255),  # Amarelo brilhante em BGR
            -1  # Preenchido
        )
        
        # Tenta desenhar a estrela por cima (se disponível)
        if destino_img is not None:
            overlay_image(tela, destino_img, x_destino, y_destino)

        # Verifica e desenha Jogador 1
        if (pos1_x, pos1_y) in agua:
            morreu1 = True
            personagem1_atual = personagem1_dano
        else:
            personagem1_atual = personagem1_img

        x1, y1 = pos1_x * tamanho_celula, pos1_y * tamanho_celula
        # Só desenha se não estiver na mesma posição do destino (para ver ambos)
        overlay_image(tela, personagem1_atual, x1, y1)
        
        # Verifica e desenha Jogador 2
        if (pos2_x, pos2_y) in agua:
            morreu2 = True
            personagem2_atual = personagem2_dano
        else:
            personagem2_atual = personagem2_img

        x2, y2 = pos2_x * tamanho_celula, pos2_y * tamanho_celula
        overlay_image(tela, personagem2_atual, x2, y2)

        # Verifica vitória
        vencedor = None
        if jogo_ativo and (pos1_x, pos1_y) == destino:
            jogo_ativo = False
            vencedor = "Jogador 1"
        elif jogo_ativo and (pos2_x, pos2_y) == destino:
            jogo_ativo = False
            vencedor = "Jogador 2"
        
        if vencedor:
            cv2.putText(tela, f"{vencedor} venceu!", (300, 480), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 150, 0), 6)

        # Verifica morte
        if (morreu1 or morreu2) and jogo_ativo:
            jogo_ativo = False
            if morreu1 and morreu2:
                cv2.putText(tela, "Ambos morreram!", (300, 480), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 6)
            elif morreu1:
                cv2.putText(tela, "Jogador 1 morreu!", (260, 480), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 6)
            else:
                cv2.putText(tela, "Jogador 2 morreu!", (260, 480), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 6)

        # Mostra preview da câmera
        preview = cv2.resize(frame_invertido, (PREVIEW_LARGURA, PREVIEW_ALTURA))
        tela[PREVIEW_Y:PREVIEW_Y+PREVIEW_ALTURA, PREVIEW_X:PREVIEW_X+PREVIEW_LARGURA] = preview

        cv2.imshow("Jogo por QR Code - 2 Jogadores", tela)

        # Verifica se a janela foi fechada ou se 'q' foi pressionado
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        # Verifica se a janela foi fechada pelo botão X
        if cv2.getWindowProperty("Jogo por QR Code - 2 Jogadores", cv2.WND_PROP_VISIBLE) < 1:
            break

    # Sempre libera a câmera e fecha as janelas
    print("\n✓ Encerrando jogo...")
    print("✓ Liberando câmera...")
    if cap is not None and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
    print("✓ Jogo encerrado com sucesso!\n")


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
