"""
Serviço de busca de fornecedores.

Este módulo contém funções para buscar fornecedores no banco
a partir de dados extraídos pelo OCR (CNPJ, nome).
"""
import re
from django.db.models import Q


def validate_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ pelos dígitos verificadores.
    Usa a biblioteca validate_docbr.
    
    Args:
        cnpj: CNPJ a validar (apenas números)
        
    Returns:
        bool: True se válido
    """
    from validate_docbr import CNPJ
    
    cnpj_validator = CNPJ()
    return cnpj_validator.validate(cnpj)


def count_different_digits(cnpj1: str, cnpj2: str) -> int:
    """
    Conta quantos dígitos são diferentes entre dois CNPJs.
    Usa distância de Hamming (comparação caractere a caractere).
    
    Args:
        cnpj1: Primeiro CNPJ
        cnpj2: Segundo CNPJ
        
    Returns:
        int: Número de dígitos diferentes
    """
    if len(cnpj1) != len(cnpj2):
        return 99  # Tamanhos diferentes = muito diferentes
    
    return sum(1 for a, b in zip(cnpj1, cnpj2) if a != b)


def find_supplier_by_cnpj(cnpj: str, supplier_name: str = None, max_digit_diff: int = 2):
    """
    Busca fornecedor pelo CNPJ ou pelo nome.
    
    Estratégia de busca:
    1. Busca exata por CNPJ completo
    2. Se CNPJ inválido ou não encontrado, busca CNPJ similar
    3. Busca pelo nome do fornecedor (razão social ou nome fantasia)
    
    Args:
        cnpj: CNPJ detectado pelo OCR
        supplier_name: Nome do fornecedor detectado pelo OCR
        max_digit_diff: Máximo de dígitos diferentes para considerar match
        
    Returns:
        Supplier | None: Fornecedor encontrado ou None
    """
    from bidding_supplier.models import Supplier
    
    cnpj_clean = re.sub(r'\D', '', cnpj) if cnpj else ''
    
    # 1. Busca exata por CNPJ completo
    if len(cnpj_clean) == 14:
        supplier = Supplier.objects.filter(cnpj=cnpj_clean).first()
        
        if supplier:
            return supplier
        
        # 2. Busca por CNPJ similar (até max_digit_diff dígitos diferentes)
        is_valid = validate_cnpj(cnpj_clean)
        
        # Filtrar por prefixo para otimização
        prefix = cnpj_clean[:4]
        candidates = Supplier.objects.filter(
            Q(cnpj__startswith=prefix) |
            Q(cnpj__startswith=cnpj_clean[:2])
        )
        
        best_match = None
        best_diff = max_digit_diff + 1
        
        for candidate in candidates:
            if len(candidate.cnpj) == 14:
                diff = count_different_digits(cnpj_clean, candidate.cnpj)
                
                if diff <= max_digit_diff and diff < best_diff:
                    # Se CNPJ detectado é inválido E o candidato é válido
                    if not is_valid and validate_cnpj(candidate.cnpj):
                        return candidate  # Match imediato!
                    
                    best_match = candidate
                    best_diff = diff
        
        if best_match:
            return best_match
    
    # 3. Busca pelo nome do fornecedor (fallback)
    if supplier_name:
        name_clean = supplier_name.upper().strip()
        
        # Remover sufixos comuns
        for suffix in [' - ME', ' - EPP', ' - EIRELI', ' LTDA', ' S/A', ' S.A.']:
            name_clean = name_clean.replace(suffix, '')
        
        name_clean = name_clean.strip()
        
        if name_clean:
            supplier = Supplier.objects.filter(
                Q(company__icontains=name_clean) |
                Q(trade__icontains=name_clean)
            ).first()
            
            if supplier:
                return supplier
            
            # Tentar primeira palavra significativa
            words = [w for w in name_clean.split() if len(w) > 2]
            if words:
                first_word = words[0]
                supplier = Supplier.objects.filter(
                    Q(company__icontains=first_word) |
                    Q(trade__icontains=first_word)
                ).first()
                
                if supplier:
                    return supplier
    
    return None


def find_similar_materials(product_description: str, supplier_id: int, limit: int = 5):
    """
    Busca materiais similares no banco de dados para um produto da nota.
    
    Args:
        product_description: Descrição do produto
        supplier_id: ID do fornecedor
        limit: Máximo de resultados
        
    Returns:
        QuerySet de MaterialBidding
    """
    from bidding_procurement.models import MaterialBidding
    
    words = product_description.upper().split()
    words = [w for w in words if len(w) > 2]
    
    if not words:
        return MaterialBidding.objects.none()
    
    query = Q()
    for word in words[:5]:
        query |= Q(material__name__icontains=word)
    
    return MaterialBidding.objects.filter(
        query,
        supplier_id=supplier_id,
        status='1'
    ).select_related('material', 'bidding').distinct()[:limit]
