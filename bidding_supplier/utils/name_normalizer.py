"""
Utilitário para normalizar nomes de fornecedores.

Usado para detectar duplicatas e consolidar fornecedores.
"""
import unicodedata
import re


def normalize_supplier_name(name: str) -> str:
    """
    Normaliza nome de fornecedor para evitar duplicatas.
    
    Aplica as seguintes transformações:
    1. Converte para maiúsculas
    2. Remove acentos
    3. Remove pontuação extra
    4. Normaliza espaços
    5. Remove sufixos comuns (LTDA, ME, EPP, etc)
    
    Args:
        name: Nome do fornecedor
        
    Returns:
        Nome normalizado
        
    Examples:
        >>> normalize_supplier_name("Prosun Informática Ltda.")
        'PROSUN INFORMATICA'
        
        >>> normalize_supplier_name("PROSUN INFORMATICA LTDA")
        'PROSUN INFORMATICA'
    """
    if not name:
        return ''
    
    # Uppercase
    name = name.upper()
    
    # Remover acentos
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ASCII', 'ignore').decode('ASCII')
    
    # Remover pontuação extra
    name = re.sub(r'[.,\-]+', ' ', name)
    
    # Normalizar espaços
    name = ' '.join(name.split())
    
    # Remover sufixos comuns
    suffixes = ['LTDA', 'ME', 'EPP', 'EIRELI', 'S/A', 'SA', 'LTDA.', 'ME.']
    for suffix in suffixes:
        pattern = rf'\s+{suffix}$'
        name = re.sub(pattern, '', name)
    
    return name.strip()
