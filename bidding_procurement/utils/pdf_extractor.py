"""
Utilitário para extração de dados de PDFs de licitação.
"""
import pdfplumber
import re
from datetime import datetime
from typing import Dict, List, Optional


class BiddingPDFExtractor:
    """Extrai dados estruturados de PDFs de licitação."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.data = {
            "administrative_process": "",
            "bidding_name": "",
            "modality": "",
            "modality_number": None,
            "validity_date": None,
            "object_description": "",
            "suppliers": [],
            "materials": []
        }
    
    def extract(self) -> Dict:
        """Extrai todos os dados do PDF."""
        with pdfplumber.open(self.pdf_path) as pdf:
            full_text = self._extract_full_text(pdf)
            
            # Extrair informações administrativas
            self._extract_administrative_info(full_text)
            
            # Extrair fornecedores
            self._extract_suppliers(full_text)
            
            # Extrair materiais (se houver tabelas)
            self._extract_materials(pdf)
        
        return self.data
    
    def _extract_full_text(self, pdf) -> str:
        """Extrai texto completo do PDF."""
        full_text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
        return full_text
    
    def _extract_administrative_info(self, text: str):
        """Extrai informações administrativas do cabeçalho."""
        # Processo Administrativo
        proc_admin = re.search(r'Proc\.\s*Administrativo\s*:\s*(\d+)', text)
        if proc_admin:
            proc_num = proc_admin.group(1)
            # Tentar extrair ano do processo licitatório
            proc_licit = re.search(r'Nº\s*Proc\.\s*Licitatório\s*:\s*\d+/(\d+)', text)
            year = proc_licit.group(1) if proc_licit else datetime.now().strftime('%y')
            self.data["administrative_process"] = f"{proc_num}/{year}"
            self.data["bidding_name"] = f"Processo Licitatório {proc_num}/{year}"
        
        # Modalidade
        modal_match = re.search(r'Modalidade\s*:\s*([^\n]+?)(?:Nº|$)', text, re.IGNORECASE)
        if modal_match:
            self.data["modality"] = modal_match.group(1).strip()
        
        # Número da Modalidade
        modal_num = re.search(r'Nº\s*Modalidade\s*Licit\.\s*:\s*(\d+)', text)
        if modal_num:
            self.data["modality_number"] = int(modal_num.group(1))
        
        # Data de Validade
        validity = re.search(r'Prazo\s*de\s*Validade\s*:\s*(\d{2}/\d{2}/\d{4})', text)
        if validity:
            try:
                self.data["validity_date"] = datetime.strptime(validity.group(1), '%d/%m/%Y').date()
            except:
                pass
        
        # Objeto/Descrição
        obj_match = re.search(r'Objeto\s*/\s*Descrição\s*:\s*([^\n]+)', text, re.IGNORECASE)
        if obj_match:
            self.data["object_description"] = obj_match.group(1).strip()
    
    def _extract_suppliers(self, text: str):
        """Extrai lista de fornecedores."""
        # Padrão: "Fornecedor / Proponente : NUMERO - NOME"
        suppliers = re.findall(
            r'Fornecedor\s*/?\s*Proponente\s*:\s*\d+\s*-\s*([^\n]+)',
            text,
            re.IGNORECASE
        )
        
        # Filtrar rodapé (Fiorilli)
        suppliers = [
            s.strip() 
            for s in suppliers 
            if 'fiorilli' not in s.lower() and s.strip()
        ]
        
        # Remover duplicatas mantendo ordem
        seen = set()
        unique_suppliers = []
        for supplier in suppliers:
            if supplier not in seen:
                seen.add(supplier)
                unique_suppliers.append(supplier)
        
        self.data["suppliers"] = unique_suppliers
    
    def _extract_materials(self, pdf):
        """Extrai materiais organizados por fornecedor."""
        full_text = self._extract_full_text(pdf)
        
        # Dividir por seções de fornecedores
        fornecedor_sections = re.split(r'Fornecedor\s*/?\s*Proponente\s*:', full_text)
        
        for section in fornecedor_sections[1:]:  # Pular cabeçalho
            # Extrair nome do fornecedor
            fornecedor_match = re.search(r'^\s*\d+\s*-\s*([^\n]+)', section)
            if not fornecedor_match:
                continue
            
            supplier_name = fornecedor_match.group(1).strip()
            if 'fiorilli' in supplier_name.lower():
                continue
            
            # Extrair materiais desta seção
            # Padrão melhorado: captura diferentes formatos de linhas
            # Formato: Item Código Descrição [Unidade] Qtd Preço_Unit Preço_Total
            lines = section.split('\n')
            
            for line in lines:
                # Procurar por linhas com código de material (XXX.XXX.XXX)
                codigo_match = re.search(r'(\d{3}\.\d{3}\.\d{3})', line)
                if not codigo_match:
                    continue
                
                codigo = codigo_match.group(1)
                
                # Extrair descrição (texto entre código e unidade)
                desc_match = re.search(r'\d{3}\.\d{3}\.\d{3}\s+(.+?)(?:UN|PC|CX|M|KG|L)\s+', line)
                if not desc_match:
                    # Tentar sem unidade explícita
                    desc_match = re.search(r'\d{3}\.\d{3}\.\d{3}\s+(.+?)\s+\d+\s+[\d,]+', line)
                
                if not desc_match:
                    continue
                
                descricao = desc_match.group(1).strip()
                
                # Extrair quantidade e preço
                # Padrão: UN/PC/etc Qtd Preço_Unit Preço_Total
                preco_match = re.search(r'(?:UN|PC|CX|M|KG|L)?\s+(\d+)\s+([\d.,]+)\s+([\d.,]+)', line)
                if not preco_match:
                    # Tentar sem unidade
                    preco_match = re.search(r'\s+(\d+)\s+([\d.,]+)\s+([\d.,]+)', line)
                
                if not preco_match:
                    continue
                
                qtd = preco_match.group(1)
                preco_unit = preco_match.group(2)
                
                # Extrair marca se houver
                marca = ""
                marca_match = re.search(r'MARCA\s+([A-Z\s]+)', descricao, re.IGNORECASE)
                if marca_match:
                    marca = marca_match.group(1).strip()
                
                # Converter preço
                try:
                    preco = float(preco_unit.replace('.', '').replace(',', '.'))
                except:
                    preco = 0.0
                
                # Limpar descrição
                desc_clean = descricao[:200]
                
                self.data["materials"].append({
                    "item": "",  # Item number não é crítico
                    "code": codigo,
                    "description": desc_clean,
                    "brand": marca,
                    "quantity": int(qtd),
                    "unit_price": preco,
                    "supplier": supplier_name
                })
    
    def get_summary(self) -> str:
        """Retorna um resumo dos dados extraídos."""
        summary = f"""
=== RESUMO DA EXTRAÇÃO ===
Licitação: {self.data['bidding_name']}
Processo Administrativo: {self.data['administrative_process']}
Modalidade: {self.data['modality']} Nº {self.data['modality_number']}
Validade: {self.data['validity_date']}
Objeto: {self.data['object_description'][:80]}...

Fornecedores ({len(self.data['suppliers'])}):
"""
        for supplier in self.data['suppliers']:
            summary += f"  - {supplier}\n"
        
        summary += f"\nMateriais: {len(self.data['materials'])} encontrados"
        
        return summary
