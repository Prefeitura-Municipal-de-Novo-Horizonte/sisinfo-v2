"""
Parser de respostas do OCR.

Este módulo contém funções para parsear a resposta JSON
retornada pelo Gemini Vision em objetos estruturados.
"""
import re
import json
from typing import Optional

from .ocr_types import InvoiceProduct, ExtractedInvoiceData


def parse_br_float(value) -> float:
    """
    Converte strings numéricas pt-BR para float.
    
    Exemplos:
        "1.000,00" -> 1000.00
        "10,5" -> 10.5
        "100" -> 100.0
    
    Args:
        value: Valor a converter (str, int ou float)
        
    Returns:
        float: Valor convertido
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Remove pontos de milhar e troca vírgula decimal por ponto
        clean = value.replace('.', '').replace(',', '.')
        try:
            return float(clean)
        except ValueError:
            return 0.0
    return 0.0


def clean_response_text(response_text: str) -> str:
    """
    Limpa texto de resposta do Gemini, removendo markdown e comentários.
    
    Args:
        response_text: Texto bruto da resposta
        
    Returns:
        str: JSON limpo
    """
    clean_text = response_text.strip()
    
    # Remover delimitadores de código markdown
    if "```json" in clean_text:
        clean_text = clean_text.split("```json")[1]
    elif "```" in clean_text:
        clean_text = clean_text.split("```")[1]
        
    if "```" in clean_text:
        clean_text = clean_text.split("```")[0]
    
    # Remover comentários de linha (//)
    clean_text = re.sub(r'^\s*//.*$', '', clean_text, flags=re.MULTILINE)
        
    return clean_text.strip()


def parse_ocr_response(response_text: str) -> ExtractedInvoiceData:
    """
    Parseia a resposta do modelo em ExtractedInvoiceData.
    
    Args:
        response_text: Texto JSON retornado pelo Gemini
        
    Returns:
        ExtractedInvoiceData: Dados estruturados extraídos
    """
    try:
        clean_text = clean_response_text(response_text)
        data = json.loads(clean_text)
        
        # Normalizar chaves (suporte a variações do Gemini)
        nf_data = data.get('nota_fiscal') or data.get('documento') or data
        emit_data = data.get('emitente') or data.get('fornecedor') or data
        items_data = (
            data.get('itens') or 
            data.get('produtos') or 
            data.get('products') or 
            data.get('produtos_servicos') or 
            []
        )
        totals_data = data.get('valores_totais') or data.get('calculo_imposto') or data
        
        # Converter produtos
        products = []
        for p in items_data:
            products.append(InvoiceProduct(
                code=str(p.get('codigo') or p.get('code') or ''),
                description=str(p.get('descricao') or p.get('description') or ''),
                quantity=parse_br_float(p.get('quantidade') or p.get('quantity')),
                unit=str(p.get('unidade') or p.get('unit') or 'UN'),
                unit_price=parse_br_float(p.get('valor_unitario') or p.get('unit_price')),
                total_price=parse_br_float(p.get('valor_total') or p.get('total_price')),
            ))
        
        # Limpar CNPJ (apenas números)
        raw_cnpj = str(emit_data.get('cnpj') or emit_data.get('supplier_cnpj') or '')
        cnpj = re.sub(r'\D', '', raw_cnpj)
        
        # Limpar chave de acesso
        raw_key = str(
            nf_data.get('chave_acesso') or 
            nf_data.get('chave_de_acesso') or 
            nf_data.get('access_key') or 
            ''
        )
        access_key = re.sub(r'\D', '', raw_key)
        
        # Extrair observações
        observations = ""
        if 'dados_adicionais' in data:
            dados = data['dados_adicionais']
            if isinstance(dados, dict):
                observations = dados.get('informacoes_complementares', '')
            elif isinstance(dados, str):
                observations = dados

        # Extrair dados principais
        number = str(nf_data.get('numero') or nf_data.get('number') or '')
        series = str(nf_data.get('serie') or nf_data.get('series') or '')
        issue_date = str(nf_data.get('data_emissao') or nf_data.get('issue_date') or '')
        supplier_name = str(emit_data.get('razao_social') or emit_data.get('supplier_name') or '')
        
        # Valor total
        total_val = parse_br_float(
            totals_data.get('valor_total_nota') or 
            totals_data.get('total_value') or 
            data.get('total_value')
        )

        return ExtractedInvoiceData(
            number=number,
            series=series,
            access_key=access_key,
            issue_date=issue_date,
            supplier_name=supplier_name,
            supplier_cnpj=cnpj,
            total_value=total_val,
            products=products,
            observations=observations,
            confidence=float(data.get('confidence', 0) or 1.0),
            raw_text=response_text,
        )
        
    except json.JSONDecodeError as e:
        return ExtractedInvoiceData(
            error=f"Erro ao parsear resposta: {e}",
            raw_text=response_text
        )
    except Exception as e:
        return ExtractedInvoiceData(
            error=f"Erro inesperado: {e}",
            raw_text=response_text
        )
