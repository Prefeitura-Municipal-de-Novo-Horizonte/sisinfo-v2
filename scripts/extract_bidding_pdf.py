#!/usr/bin/env python3
"""
Script para extrair dados de licitações de PDFs usando Gemini Vision API.
Extrai: materiais, quantidades, unidades, preços e fornecedores.
"""

import os
import sys
import json
import base64
from pathlib import Path

# Adicionar o projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

import django
django.setup()

from decouple import config
import google.generativeai as genai
import time

# Obter todas as chaves Gemini e modelo
GEMINI_KEYS = [k.strip() for k in config('GEMINI_API_KEY', default='').split(',') if k.strip()]
GEMINI_MODEL = config('GEMINI_MODEL', default='gemini-flash-latest')
current_key_index = 0

print(f"🤖 Usando modelo: {GEMINI_MODEL}")


def get_next_key():
    """Retorna a próxima chave disponível usando rotação."""
    global current_key_index
    if not GEMINI_KEYS:
        raise ValueError("Nenhuma chave GEMINI_API_KEY configurada!")
    key = GEMINI_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(GEMINI_KEYS)
    return key


def configure_gemini(key_index=None):
    """Configura o Gemini com uma chave específica."""
    if key_index is not None:
        key = GEMINI_KEYS[key_index % len(GEMINI_KEYS)]
    else:
        key = get_next_key()
    genai.configure(api_key=key)
    return key


def extract_pdf_data(pdf_path: str) -> dict:
    """
    Extrai dados de um PDF de licitação usando Gemini Vision.
    Usa rotação de chaves em caso de quota esgotada.
    """
    print(f"\n{'='*60}")
    print(f"Processando: {pdf_path}")
    print(f"{'='*60}")
    
    # Ler o PDF como bytes
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    # Converter para base64
    pdf_base64 = base64.standard_b64encode(pdf_bytes).decode('utf-8')
    
    # Prompt para extração estruturada
    prompt = """
Analise este documento PDF de licitação e extraia TODAS as informações em formato JSON estruturado.

IMPORTANTE: Este é um documento de Ata de Registro de Preços onde CADA ITEM pode ter um FORNECEDOR DIFERENTE.

Retorne EXATAMENTE neste formato JSON (sem markdown, sem ```):
{
    "numero_licitacao": "XXX/2025",
    "modalidade": "Pregão Eletrônico/Presencial/etc",
    "objeto": "Descrição do objeto da licitação",
    "orgao": "Nome do órgão",
    "data_homologacao": "DD/MM/YYYY",
    "itens": [
        {
            "item": 1,
            "descricao": "Nome COMPLETO do material/produto",
            "unidade": "UN/CX/PC/M/L/KG/etc",
            "quantidade": 100,
            "valor_unitario": 10.50,
            "marca": "Marca se especificada",
            "fornecedor": {
                "razao_social": "Nome da empresa vencedora DESTE ITEM",
                "cnpj": "XX.XXX.XXX/XXXX-XX"
            }
        }
    ],
    "valor_total_licitacao": 0.00
}

REGRAS CRÍTICAS:

1. **CADA ITEM TEM SEU PRÓPRIO FORNECEDOR** - Extraia o fornecedor específico de cada item

2. **NUNCA inclua a unidade no final da descrição**:
   - ERRADO: "CABO ADAPTADOR DE REDE USB 3.0 PARA RJ45 F3, 10/1un"
   - CORRETO: "CABO ADAPTADOR DE REDE USB 3.0 PARA RJ45 F3, 10/100/1000MBPS"

3. **Se a descrição parecer truncada, COMPLETE usando seu conhecimento**:
   - Se terminar em "COM 1 CONECTOF" → "COM 1 CONECTOR VGA E 1 CONECTOR HDMI"
   - Se terminar em "GIGABIT DA MAUN" → "GIGABIT DA MARCA UBIQUITI"

4. **Unidades válidas**: UN, PC, CX, M, KG, L, ML, G, PA (par)

5. **Mantenha especificações técnicas completas**:
   - Exemplo: "PLACA DE VÍDEO, 12GB GDDR6, 02 (DUAS) VENTOINHAS"

6. **Use números decimais com ponto** (ex: 10.50, não 10,50)

7. **Se algum campo não existir, use null**

8. **Retorne APENAS o JSON, sem texto adicional**
"""
    
    # Tentar com múltiplas chaves
    max_retries = len(GEMINI_KEYS)
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Configurar com próxima chave
            key_used = configure_gemini()
            print(f"   Tentativa {attempt + 1}/{max_retries}")
            
            # Criar o modelo
            model = genai.GenerativeModel(GEMINI_MODEL)
            
            # Enviar para o Gemini
            response = model.generate_content([
                {
                    'mime_type': 'application/pdf',
                    'data': pdf_base64
                },
                prompt
            ])
            
            # Processar resposta
            response_text = response.text.strip()
            
            # Limpar possíveis blocos de código markdown
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                # Remover primeira linha (```json) e última (```)
                response_text = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])
            
            data = json.loads(response_text)
            print(f"\n✅ Extração bem-sucedida!")
            print(f"   Licitação: {data.get('numero_licitacao', 'N/A')}")
            print(f"   Fornecedor: {data.get('fornecedor_vencedor', {}).get('razao_social', 'N/A')}")
            print(f"   Total de itens: {len(data.get('itens', []))}")
            return data
            
        except Exception as e:
            last_error = e
            error_str = str(e)
            if '429' in error_str or 'quota' in error_str.lower():
                print(f"   ⚠️ Quota esgotada, tentando próxima chave...")
                time.sleep(2)  # Pequena pausa
            else:
                print(f"   ❌ Erro: {error_str[:100]}...")
                break
    
    # Se todas as tentativas falharam
    print(f"\n❌ Todas as tentativas falharam!")
    return {"error": str(last_error)}


def save_results(data: dict, output_path: str):
    """Salva os resultados em arquivo JSON."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Salvo em: {output_path}")


def main():
    """Função principal."""
    # Diretório dos PDFs
    pdf_dir = Path(__file__).parent.parent / 'docs' / 'licitacoes-ativas'
    output_dir = Path(__file__).parent.parent / 'docs' / 'licitacoes-extraidas'
    output_dir.mkdir(exist_ok=True)
    
    # PDFs a processar
    pdfs = [
        'licitacao-121-2025.pdf',
        'licitacao-223-2025.pdf',
    ]
    
    all_results = {}
    
    for pdf_file in pdfs:
        pdf_path = pdf_dir / pdf_file
        if not pdf_path.exists():
            print(f"⚠️ Arquivo não encontrado: {pdf_path}")
            continue
        
        # Extrair dados
        data = extract_pdf_data(str(pdf_path))
        all_results[pdf_file] = data
        
        # Salvar resultado individual
        output_file = output_dir / f"{pdf_file.replace('.pdf', '.json')}"
        save_results(data, str(output_file))
    
    # Salvar resultado consolidado
    consolidated_path = output_dir / 'licitacoes_consolidadas.json'
    save_results(all_results, str(consolidated_path))
    
    # Resumo
    print(f"\n{'='*60}")
    print("📋 RESUMO DA EXTRAÇÃO")
    print(f"{'='*60}")
    
    for pdf_file, data in all_results.items():
        if 'error' not in data:
            print(f"\n📄 {pdf_file}")
            print(f"   Licitação: {data.get('numero_licitacao', 'N/A')}")
            print(f"   Objeto: {data.get('objeto', 'N/A')[:60]}...")
            
            fornecedor = data.get('fornecedor_vencedor', {})
            print(f"   Fornecedor: {fornecedor.get('razao_social', 'N/A')}")
            print(f"   CNPJ: {fornecedor.get('cnpj', 'N/A')}")
            
            itens = data.get('itens', [])
            print(f"   Itens: {len(itens)}")
            
            for item in itens[:5]:  # Mostrar primeiros 5
                print(f"      - {item.get('descricao', 'N/A')[:40]}... (Qtd: {item.get('quantidade', 'N/A')})")
            
            if len(itens) > 5:
                print(f"      ... e mais {len(itens) - 5} itens")


if __name__ == '__main__':
    main()
