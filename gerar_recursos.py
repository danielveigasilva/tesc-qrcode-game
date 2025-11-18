#!/usr/bin/env python3
"""
Script unificado para gerar recursos do jogo QR Code.

Uso:
    python gerar_recursos.py --qrcodes        # Gera apenas os QR codes
    python gerar_recursos.py --pdfs           # Gera apenas os PDFs
    python gerar_recursos.py --tudo           # Gera QR codes e PDFs
    python gerar_recursos.py --help           # Mostra ajuda
"""

import argparse
import os
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm


def gerar_qrcodes():
    """Gera os QR codes para 2 jogadores."""
    # Cria a pasta recursos se não existir
    os.makedirs("recursos", exist_ok=True)

    # Comandos para cada jogador (incluindo início e fim)
    comandos = ["inicio", "cima", "baixo", "direita", "esquerda", "fim"]
    jogadores = [1, 2]

    print("\n📱 Gerando QR codes para 2 jogadores...\n")

    for jogador in jogadores:
        print(f"Jogador {jogador}:")
        for comando in comandos:
            # Texto do QR code
            texto_qr = f"{jogador}-{comando}"
            
            # Cria o QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            qr.add_data(texto_qr)
            qr.make(fit=True)
            
            # Cria a imagem
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Nome do arquivo bem descritivo
            nome_arquivo = f"recursos/Jogador{jogador}_{comando.capitalize()}.png"
            img.save(nome_arquivo)
            print(f"  ✓ {nome_arquivo}")
        print()

    print("✅ Todos os QR codes foram criados na pasta 'recursos'!\n")


def criar_pdf_jogador(jogador_num):
    """Cria um PDF A4 com os QR codes de um jogador (2 páginas: controles + início/fim)."""
    
    # Nome do arquivo PDF
    pdf_filename = f"recursos/Cartelas_Jogador{jogador_num}.pdf"
    
    # Cria o canvas PDF (tamanho A4)
    c = canvas.Canvas(pdf_filename, pagesize=A4)
    largura, altura = A4  # 21cm x 29.7cm
    
    # ===== PÁGINA 1: CONTROLES DE MOVIMENTO =====
    
    # Cabeçalho grande
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(largura/2, altura - 3*cm, f"Controles - Jogador {jogador_num}")
    
    # Linha decorativa abaixo do cabeçalho
    c.setLineWidth(2)
    c.line(3*cm, altura - 4.2*cm, largura - 3*cm, altura - 4.2*cm)
    
    # Configurações dos QR codes
    qr_size = 5.5 * cm
    spacing_x = 1.5 * cm
    spacing_y = 2.5 * cm
    
    # Posições para os 4 QR codes (2x2)
    comandos = [
        ("Cima", 0, 0),
        ("Baixo", 1, 0),
        ("Esquerda", 0, 1),
        ("Direita", 1, 1)
    ]
    
    start_y = altura - 12*cm
    start_x = (largura - (2*qr_size + spacing_x)) / 2
    
    for comando, col, row in comandos:
        qr_path = f"recursos/Jogador{jogador_num}_{comando}.png"
        
        if os.path.exists(qr_path):
            x = start_x + col * (qr_size + spacing_x)
            y = start_y - row * (qr_size + spacing_y + 1*cm)
            
            c.setLineWidth(1)
            c.setStrokeColorRGB(0.7, 0.7, 0.7)
            c.rect(x - 0.3*cm, y - 0.3*cm, qr_size + 0.6*cm, qr_size + 1.4*cm, stroke=1, fill=0)
            
            c.drawImage(qr_path, x, y, width=qr_size, height=qr_size, preserveAspectRatio=True, mask='auto')
            
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(x + qr_size/2, y - 0.8*cm, f"{comando.upper()} - Jogador {jogador_num}")
    
    # Rodapé página 1
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(largura/2, 2*cm, "Use estas cartas para movimentar seu personagem")
    c.setFont("Helvetica", 9)
    c.drawCentredString(largura/2, 1.3*cm, "QR Code Game - Competição 2 Jogadores - Página 1/2")
    
    # ===== PÁGINA 2: INÍCIO E FIM =====
    c.showPage()
    
    # Cabeçalho página 2
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(largura/2, altura - 3*cm, f"Início/Fim - Jogador {jogador_num}")
    
    c.setLineWidth(2)
    c.line(3*cm, altura - 4.2*cm, largura - 3*cm, altura - 4.2*cm)
    
    # QR codes de início e fim (maiores, centralizados verticalmente)
    qr_size_grande = 7 * cm
    
    comandos_especiais = [
        ("Inicio", altura - 13*cm),
        ("Fim", altura - 23*cm)
    ]
    
    for comando, pos_y in comandos_especiais:
        qr_path = f"recursos/Jogador{jogador_num}_{comando}.png"
        
        if os.path.exists(qr_path):
            x = (largura - qr_size_grande) / 2
            y = pos_y
            
            # Borda mais destacada
            c.setLineWidth(2)
            c.setStrokeColorRGB(0.2, 0.5, 0.8)  # Azul
            c.rect(x - 0.4*cm, y - 0.4*cm, qr_size_grande + 0.8*cm, qr_size_grande + 1.6*cm, stroke=1, fill=0)
            
            c.drawImage(qr_path, x, y, width=qr_size_grande, height=qr_size_grande, preserveAspectRatio=True, mask='auto')
            
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(largura/2, y - 1*cm, f"{comando.upper()} - Jogador {jogador_num}")
    
    # Rodapé página 2
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(largura/2, 2.5*cm, "IMPORTANTE: Coloque INÍCIO antes e FIM depois das suas jogadas!")
    c.setFont("Helvetica", 9)
    c.drawCentredString(largura/2, 1.5*cm, "O jogo só executa quando detectar: INÍCIO → movimentos → FIM")
    c.drawCentredString(largura/2, 1*cm, "QR Code Game - Competição 2 Jogadores - Página 2/2")
    
    # Salva o PDF
    c.save()
    print(f"  ✓ {pdf_filename} (2 páginas)")


def gerar_pdfs():
    """Gera PDFs com cartelas de QR codes."""
    print("\n📄 Gerando PDFs com cartelas de QR codes...\n")
    
    for jogador in [1, 2]:
        criar_pdf_jogador(jogador)
    
    print("\n✅ PDFs criados com sucesso na pasta 'recursos'!")
    print("   - Cartelas_Jogador1.pdf")
    print("   - Cartelas_Jogador2.pdf")
    print("\n🖨️  Agora você pode imprimir e distribuir para os jogadores!\n")


def main():
    parser = argparse.ArgumentParser(
        description="Gera recursos (QR codes e/ou PDFs) para o jogo QR Code de 2 jogadores.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python gerar_recursos.py --qrcodes        Gera apenas os QR codes
  python gerar_recursos.py --pdfs           Gera apenas os PDFs
  python gerar_recursos.py --tudo           Gera QR codes e PDFs
  python gerar_recursos.py -t               Atalho para --tudo
        """
    )
    
    parser.add_argument(
        '--qrcodes',
        action='store_true',
        help='Gera os QR codes PNG para os 2 jogadores'
    )
    
    parser.add_argument(
        '--pdfs',
        action='store_true',
        help='Gera os PDFs com cartelas impressas dos QR codes'
    )
    
    parser.add_argument(
        '--tudo', '-t',
        action='store_true',
        help='Gera tanto QR codes quanto PDFs (atalho: -t)'
    )
    
    args = parser.parse_args()
    
    # Se nenhuma opção foi escolhida, mostra ajuda
    if not (args.qrcodes or args.pdfs or args.tudo):
        parser.print_help()
        return
    
    # Executa as funções conforme solicitado
    if args.tudo:
        gerar_qrcodes()
        gerar_pdfs()
    else:
        if args.qrcodes:
            gerar_qrcodes()
        if args.pdfs:
            gerar_pdfs()
    
    print("✨ Concluído!\n")


if __name__ == "__main__":
    main()
