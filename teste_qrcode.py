import cv2
from pyzbar.pyzbar import decode

# Testa detecção de QR code
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Não conseguiu abrir câmera")
        exit()

print("Câmera aberta! Mostre um QR code...")
print("Pressione 'q' para sair")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Tenta detectar QR codes
    codigos = decode(frame)
    
    if codigos:
        print(f"\n{'='*50}")
        print(f"DETECTOU {len(codigos)} QR CODE(S)!")
        for codigo in codigos:
            texto = codigo.data.decode("utf-8")
            print(f"Texto: '{texto}'")
            print(f"Tipo: {codigo.type}")
            
            # Desenha retângulo ao redor do QR code
            pontos = codigo.polygon
            if len(pontos) == 4:
                pts = [(p.x, p.y) for p in pontos]
                for i in range(4):
                    cv2.line(frame, pts[i], pts[(i+1)%4], (0, 255, 0), 3)
        print(f"{'='*50}\n")
    
    # Mostra o frame
    cv2.imshow("Teste QR Code - Pressione 'q' para sair", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Teste finalizado")
