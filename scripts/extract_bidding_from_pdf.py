#!/usr/bin/env python3
"""
Script para extrair dados de licitações de PDFs.
"""
import pdfplumber
import json
import sys
import re

def extract_bidding_data(pdf_path):
    """Extrai dados estruturados de um PDF de licitação."""
    
    data = {
        "pdf_file": pdf_path,
        "bidding_name": "",
        "materials": [],
        "suppliers": set(),
        "total_value": 0.0
    }
    
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        
        # Extrair texto de todas as páginas
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
        
        # Extrair nome da licitação
        process_match = re.search(r'Processo\s+Licitatório\s+N?º?\s*(\d+/\d+)', full_text, re.IGNORECASE)
        if process_match:
            data["bidding_name"] = f"Processo Licitatório {process_match.group(1)}"
        
        # Tentar extrair tabelas
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue
                
                # Processar cada linha da tabela
                for row in table:
                    if not row or len(row) < 3:
                        continue
                    
                    # Tentar identificar colunas de material
                    # Formato comum: [Item, Descrição, Qtd, Unidade, Preço Unit, Fornecedor, Total]
                    material_info = {
                        "description": "",
                        "quantity": 0,
                        "unit_price": 0.0,
                        "supplier": "",
                        "total": 0.0
                    }
                    
                    # Processar células
                    for i, cell in enumerate(row):
                        if cell:
                            cell_str = str(cell).strip()
                            
                            # Tentar identificar preço (formato: R$ X,XX ou X,XX)
                            price_match = re.search(r'R?\$?\s*([\d.]+,\d{2})', cell_str)
                            if price_match:
                                price_str = price_match.group(1).replace('.', '').replace(',', '.')
                                try:
                                    price = float(price_str)
                                    if material_info["unit_price"] == 0:
                                        material_info["unit_price"] = price
                                    else:
                                        material_info["total"] = price
                                except:
                                    pass
                            
                            # Tentar identificar quantidade
                            qty_match = re.search(r'^\d+$', cell_str)
                            if qty_match and material_info["quantity"] == 0:
                                try:
                                    material_info["quantity"] = int(cell_str)
                                except:
                                    pass
                            
                            # Descrição (células mais longas)
                            if len(cell_str) > 10 and not price_match and not qty_match:
                                if not material_info["description"]:
                                    material_info["description"] = cell_str
                                elif "LTDA" in cell_str.upper() or "S/A" in cell_str.upper() or "ME" in cell_str.upper():
                                    material_info["supplier"] = cell_str
                                    data["suppliers"].add(cell_str)
                    
                    # Adicionar material se tiver dados válidos
                    if material_info["description"] and material_info["quantity"] > 0:
                        data["materials"].append(material_info)
                        if material_info["total"] > 0:
                            data["total_value"] += material_info["total"]
        
        # Converter set para list para JSON
        data["suppliers"] = list(data["suppliers"])
        
        # Informações gerais
        print(f"\n=== Análise do PDF: {pdf_path} ===", file=sys.stderr)
        print(f"Licitação: {data['bidding_name']}", file=sys.stderr)
        print(f"Total de páginas: {len(pdf.pages)}", file=sys.stderr)
        print(f"Materiais encontrados: {len(data['materials'])}", file=sys.stderr)
        print(f"Fornecedores únicos: {len(data['suppliers'])}", file=sys.stderr)
        print(f"Valor total estimado: R$ {data['total_value']:.2f}", file=sys.stderr)
        
        return data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python extract_bidding_from_pdf.py <caminho_do_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    data = extract_bidding_data(pdf_path)
    
    # Imprimir JSON
    print(json.dumps(data, indent=2, ensure_ascii=False))
