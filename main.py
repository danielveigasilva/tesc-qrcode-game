import cv2
import numpy as np
import time
from pyzbar.pyzbar import decode

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Não foi possível acessar a câmera.")
        return

    # Configurações do jogo
    largura, altura = 640, 480
    tamanho_celula = 64
    grid_cols = largura // tamanho_celula
    grid_rows = altura // tamanho_celula

    # Posições iniciais (em coordenadas de grid)
    pos_x, pos_y = 0, grid_rows - 1

    # Carrega imagens
    personagem_img = cv2.imread("personagem.png", cv2.IMREAD_UNCHANGED)
    personagem_dano = cv2.imread("personagem_dano.png", cv2.IMREAD_UNCHANGED)
    destino_img = cv2.imread("destino.png", cv2.IMREAD_UNCHANGED)

    # Redimensiona imagens para o tamanho da célula
    personagem_img = cv2.resize(personagem_img, (tamanho_celula, tamanho_celula))
    personagem_dano = cv2.resize(personagem_dano, (tamanho_celula, tamanho_celula))
    destino_img = cv2.resize(destino_img, (tamanho_celula, tamanho_celula))

    # Células de água (lista de tuplas)
    agua = [(2, 5), (3, 5), (4, 5)]

    # Célula destino
    destino = (grid_cols - 1, 0)

    # Controle de leitura de QR
    ultimo_codigo = None
    ultimo_tempo = time.time()
    delay_leitura = 1.0  # segundos entre leituras

    jogo_ativo = True
    morreu = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_invertido = cv2.flip(frame, 1)
        codigos = decode(frame_invertido)
        comando = None

        if jogo_ativo and codigos:
            # Ordena QR da direita para esquerda
            codigos_ordenados = sorted(codigos, key=lambda c: c.rect.left, reverse=True)
            for codigo in codigos_ordenados:
                texto = codigo.data.decode("utf-8").strip().lower()
                if texto and (texto != ultimo_codigo or time.time() - ultimo_tempo > delay_leitura):
                    comando = texto
                    ultimo_codigo = texto
                    ultimo_tempo = time.time()
                    print(f"Comando detectado: {texto}")
                    break

        # Atualiza posição com base no comando
        if jogo_ativo and comando:
            if comando == "direita":
                pos_x = min(pos_x + 1, grid_cols - 1)
            elif comando == "esquerda":
                pos_x = max(pos_x - 1, 0)
            elif comando == "cima":
                pos_y = max(pos_y - 1, 0)
            elif comando == "baixo":
                pos_y = min(pos_y + 1, grid_rows - 1)

        # Cria tela
        tela = np.full((altura, largura, 3), 255, dtype=np.uint8)

        # Desenha água
        for (ax, ay) in agua:
            cv2.rectangle(
                tela,
                (ax * tamanho_celula, ay * tamanho_celula),
                ((ax + 1) * tamanho_celula, (ay + 1) * tamanho_celula),
                (255, 100, 100),
                -1,
            )

        # Desenha destino
        dx, dy = destino
        y1, y2 = dy * tamanho_celula, (dy + 1) * tamanho_celula
        x1, x2 = dx * tamanho_celula, (dx + 1) * tamanho_celula
        overlay_image(tela, destino_img, x1, y1)

        # Verifica se caiu na água
        if (pos_x, pos_y) in agua:
            morreu = True
            personagem_atual = personagem_dano
        else:
            personagem_atual = personagem_img

        # Desenha personagem
        x, y = pos_x * tamanho_celula, pos_y * tamanho_celula
        overlay_image(tela, personagem_atual, x, y)

        # Verifica vitória
        if jogo_ativo and (pos_x, pos_y) == destino:
            jogo_ativo = False
            cv2.putText(tela, "Você venceu!", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 150, 0), 3)

        # Verifica morte
        if morreu and jogo_ativo:
            jogo_ativo = False
            cv2.putText(tela, "Você morreu!", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

        # Mostra preview da câmera
        preview = cv2.resize(frame_invertido, (160, 120))
        tela[10:130, 10:170] = preview

        cv2.imshow("Jogo por QR Code", tela)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


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
