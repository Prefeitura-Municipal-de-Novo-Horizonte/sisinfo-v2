"""
Tipos de dados para o serviço de OCR.

Este módulo contém as dataclasses usadas para representar
dados extraídos de notas fiscais.
"""
from dataclasses import dataclass, field


@dataclass
class InvoiceProduct:
    """
    Produto extraído da nota fiscal.
    
    Attributes:
        code: Código do produto
        description: Descrição do produto
        quantity: Quantidade
        unit: Unidade (UN, KG, etc)
        unit_price: Preço unitário
        total_price: Preço total (quantity * unit_price)
    """
    code: str = ""
    description: str = ""
    quantity: float = 0.0
    unit: str = "UN"
    unit_price: float = 0.0
    total_price: float = 0.0


@dataclass
class ExtractedInvoiceData:
    """
    Dados extraídos da nota fiscal.
    
    Attributes:
        number: Número da nota fiscal
        series: Série da nota fiscal
        access_key: Chave de acesso (44 dígitos)
        issue_date: Data de emissão (DD/MM/AAAA)
        supplier_name: Razão social do fornecedor
        supplier_cnpj: CNPJ do fornecedor (apenas números)
        total_value: Valor total da nota
        products: Lista de produtos
        observations: Informações complementares
        raw_text: Texto bruto retornado pelo OCR
        confidence: Nível de confiança da extração
        error: Mensagem de erro, se houver
    """
    number: str = ""
    series: str = ""
    access_key: str = ""
    issue_date: str = ""
    supplier_name: str = ""
    supplier_cnpj: str = ""
    total_value: float = 0.0
    products: list = field(default_factory=list)
    observations: str = ""
    raw_text: str = ""
    confidence: float = 0.0
    error: str = ""
    
    @property
    def has_error(self) -> bool:
        """Verifica se houve erro na extração."""
        return bool(self.error)
    
    @property
    def has_products(self) -> bool:
        """Verifica se há produtos extraídos."""
        return len(self.products) > 0
