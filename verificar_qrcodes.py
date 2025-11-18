#!/usr/bin/env python3
"""
Script para verificar o conteúdo dos QR codes gerados.
"""

import os
from pyzbar.pyzbar import decode
from PIL import Image

def verificar_qrcodes():
    """Verifica todos os QR codes na pasta recursos."""
    
    pasta = "recursos"
    
    if not os.path.exists(pasta):
        print("❌ Pasta 'recursos' não encontrada!")
        return
    
    print("\n🔍 Verificando QR codes...\n")
    print("="*70)
    
    # Lista de arquivos PNG
    arquivos = sorted([f for f in os.listdir(pasta) if f.endswith('.png')])
    
    erros = []
    sucesso = []
    
    for arquivo in arquivos:
        caminho = os.path.join(pasta, arquivo)
        
        try:
            # Abre a imagem
            img = Image.open(caminho)
            
            # Decodifica o QR code
            codigos = decode(img)
            
            if codigos:
                # Pega o primeiro código (deve haver apenas um por imagem)
                codigo = codigos[0]
                conteudo = codigo.data.decode('utf-8')
                
                # Extrai o esperado do nome do arquivo
                # Formato: Jogador1_Cima.png -> espera "1-cima"
                partes = arquivo.replace('.png', '').split('_')
                if len(partes) == 2:
                    jogador = partes[0].replace('Jogador', '')
                    comando = partes[1].lower()
                    esperado = f"{jogador}-{comando}"
                    
                    if conteudo.lower() == esperado:
                        print(f"✅ {arquivo:30s} → Conteúdo: '{conteudo}'")
                        sucesso.append(arquivo)
                    else:
                        print(f"❌ {arquivo:30s} → Esperado: '{esperado}', Encontrado: '{conteudo}'")
                        erros.append((arquivo, esperado, conteudo))
                else:
                    print(f"⚠️  {arquivo:30s} → Nome de arquivo inesperado")
            else:
                print(f"❌ {arquivo:30s} → QR code não detectado!")
                erros.append((arquivo, "QR válido", "Não detectado"))
                
        except Exception as e:
            print(f"❌ {arquivo:30s} → Erro ao processar: {e}")
            erros.append((arquivo, "Processamento OK", f"Erro: {e}"))
    
    print("="*70)
    print(f"\n📊 Resumo:")
    print(f"   ✅ Corretos: {len(sucesso)}/{len(arquivos)}")
    print(f"   ❌ Erros: {len(erros)}/{len(arquivos)}")
    
    if erros:
        print(f"\n⚠️  Problemas encontrados:")
        for arquivo, esperado, encontrado in erros:
            print(f"   • {arquivo}: esperado '{esperado}', encontrado '{encontrado}'")
    else:
        print(f"\n🎉 Todos os QR codes estão corretos!")
    
    print()

if __name__ == "__main__":
    verificar_qrcodes()
