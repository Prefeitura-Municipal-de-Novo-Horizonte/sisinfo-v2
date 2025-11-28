"""
Utilitário para matching fuzzy de nomes (fornecedores e materiais).
"""
from difflib import SequenceMatcher
from typing import List, Tuple, Optional


class FuzzyMatcher:
    """Detecta nomes similares para evitar duplicatas."""
    
    def __init__(self, threshold: float = 0.8):
        """
        Args:
            threshold: Similaridade mínima (0.0 a 1.0) para considerar match
        """
        self.threshold = threshold
    
    def similarity(self, str1: str, str2: str) -> float:
        """
        Calcula similaridade entre duas strings.
        
        Returns:
            Float entre 0.0 (totalmente diferente) e 1.0 (idêntico)
        """
        # Normalizar strings
        s1 = self._normalize(str1)
        s2 = self._normalize(str2)
        
        return SequenceMatcher(None, s1, s2).ratio()
    
    def find_similar(
        self, 
        name: str, 
        existing_names: List[str]
    ) -> List[Tuple[str, float]]:
        """
        Encontra nomes similares em uma lista.
        
        Args:
            name: Nome a procurar
            existing_names: Lista de nomes existentes
        
        Returns:
            Lista de tuplas (nome_similar, score) ordenada por similaridade
        """
        matches = []
        
        for existing in existing_names:
            score = self.similarity(name, existing)
            if score >= self.threshold:
                matches.append((existing, score))
        
        # Ordenar por score (maior primeiro)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def get_best_match(
        self, 
        name: str, 
        existing_names: List[str]
    ) -> Optional[Tuple[str, float]]:
        """
        Retorna o melhor match (mais similar).
        
        Returns:
            Tupla (nome, score) ou None se não houver match
        """
        matches = self.find_similar(name, existing_names)
        return matches[0] if matches else None
    
    def _normalize(self, text: str) -> str:
        """
        Normaliza texto para comparação.
        
        - Remove espaços extras
        - Converte para minúsculas
        - Remove pontuação comum
        """
        text = text.lower()
        text = text.replace('.', '')
        text = text.replace(',', '')
        text = text.replace('-', ' ')
        text = ' '.join(text.split())  # Remove espaços múltiplos
        
        return text
    
    def are_similar(self, str1: str, str2: str) -> bool:
        """Verifica se duas strings são similares (acima do threshold)."""
        return self.similarity(str1, str2) >= self.threshold


# Funções de conveniência
def find_similar_suppliers(
    supplier_name: str,
    existing_suppliers: List[str],
    threshold: float = 0.8
) -> List[Tuple[str, float]]:
    """
    Encontra fornecedores similares.
    
    Args:
        supplier_name: Nome do fornecedor a procurar
        existing_suppliers: Lista de fornecedores existentes
        threshold: Similaridade mínima
    
    Returns:
        Lista de tuplas (fornecedor, score)
    """
    matcher = FuzzyMatcher(threshold=threshold)
    return matcher.find_similar(supplier_name, existing_suppliers)


def find_similar_materials(
    material_name: str,
    existing_materials: List[str],
    threshold: float = 0.85
) -> List[Tuple[str, float]]:
    """
    Encontra materiais similares.
    
    Usa threshold mais alto (0.85) pois materiais precisam ser mais precisos.
    
    Args:
        material_name: Nome do material a procurar
        existing_materials: Lista de materiais existentes
        threshold: Similaridade mínima
    
    Returns:
        Lista de tuplas (material, score)
    """
    matcher = FuzzyMatcher(threshold=threshold)
    return matcher.find_similar(material_name, existing_materials)
