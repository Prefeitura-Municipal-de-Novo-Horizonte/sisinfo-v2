from django.core.management.base import BaseCommand
import pdfplumber
import json
import re

class Command(BaseCommand):
    help = 'Extrai dados de licitação de um arquivo PDF'

    def add_arguments(self, parser):
        parser.add_argument('pdf_file', type=str, help='Caminho para o arquivo PDF')
        parser.add_argument('--output', type=str, help='Arquivo de saída JSON (opcional)')

    def handle(self, *args, **options):
        pdf_path = options['pdf_file']
        
        self.stdout.write(self.style.WARNING(f'\n=== Extraindo dados de: {pdf_path} ===\n'))
        
        data = {
            "pdf_file": pdf_path,
            "bidding_name": "",
            "materials": [],
            "suppliers": set(),
            "raw_text": ""
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                self.stdout.write(f'Total de páginas: {len(pdf.pages)}')
                
                # Extrair texto completo
                full_text = ""
                for i, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    full_text += page_text + "\n"
                    self.stdout.write(f'Página {i}: {len(page_text)} caracteres')
                
                data["raw_text"] = full_text
                
                # Extrair nome da licitação
                process_match = re.search(r'Processo\s+Licitatório\s+N?º?\s*(\d+/\d+)', full_text, re.IGNORECASE)
                if process_match:
                    data["bidding_name"] = f"Processo Licitatório {process_match.group(1)}"
                    self.stdout.write(self.style.SUCCESS(f'Licitação identificada: {data["bidding_name"]}'))
                
                # Extrair tabelas
                total_materials = 0
                for page_num, page in enumerate(pdf.pages, 1):
                    tables = page.extract_tables()
                    if tables:
                        self.stdout.write(f'\nPágina {page_num}: {len(tables)} tabela(s) encontrada(s)')
                        
                        for table_num, table in enumerate(tables, 1):
                            if not table or len(table) < 2:
                                continue
                            
                            self.stdout.write(f'  Tabela {table_num}: {len(table)} linhas')
                            
                            # Mostrar cabeçalho
                            if table[0]:
                                self.stdout.write(f'    Cabeçalho: {table[0]}')
                            
                            # Processar linhas
                            for row_num, row in enumerate(table[1:], 1):
                                if not row or len(row) < 2:
                                    continue
                                
                                # Mostrar primeiras 3 linhas como exemplo
                                if row_num <= 3:
                                    self.stdout.write(f'    Linha {row_num}: {row}')
                                
                                material_info = self._extract_material_from_row(row)
                                if material_info:
                                    data["materials"].append(material_info)
                                    total_materials += 1
                                    if material_info.get("supplier"):
                                        data["suppliers"].add(material_info["supplier"])
                
                # Converter set para list
                data["suppliers"] = list(data["suppliers"])
                
                # Resumo
                self.stdout.write(self.style.SUCCESS(f'\n=== RESUMO ==='))
                self.stdout.write(f'Licitação: {data["bidding_name"] or "NÃO IDENTIFICADA"}')
                self.stdout.write(f'Materiais encontrados: {total_materials}')
                self.stdout.write(f'Fornecedores únicos: {len(data["suppliers"])}')
                
                if data["suppliers"]:
                    self.stdout.write('\nFornecedores:')
                    for supplier in data["suppliers"]:
                        self.stdout.write(f'  - {supplier}')
                
                # Salvar JSON
                output_file = options.get('output')
                if output_file:
                    # Remover raw_text do output (muito grande)
                    output_data = {k: v for k, v in data.items() if k != 'raw_text'}
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(output_data, f, indent=2, ensure_ascii=False)
                    self.stdout.write(self.style.SUCCESS(f'\nDados salvos em: {output_file}'))
                else:
                    # Imprimir JSON (sem raw_text)
                    output_data = {k: v for k, v in data.items() if k != 'raw_text'}
                    self.stdout.write('\n' + json.dumps(output_data, indent=2, ensure_ascii=False))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nErro ao processar PDF: {e}'))
            import traceback
            traceback.print_exc()
    
    def _extract_material_from_row(self, row):
        """Extrai informações de material de uma linha da tabela."""
        material_info = {
            "description": "",
            "quantity": 0,
            "unit": "",
            "unit_price": 0.0,
            "supplier": "",
            "total": 0.0
        }
        
        for cell in row:
            if not cell:
                continue
            
            cell_str = str(cell).strip()
            
            # Preço (R$ X,XX ou X,XX)
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
            
            # Quantidade (número inteiro)
            if re.match(r'^\d+$', cell_str) and material_info["quantity"] == 0:
                try:
                    material_info["quantity"] = int(cell_str)
                except:
                    pass
            
            # Unidade (UN, PC, CX, etc)
            if re.match(r'^[A-Z]{2,4}$', cell_str) and not material_info["unit"]:
                material_info["unit"] = cell_str
            
            # Fornecedor (contém LTDA, S/A, ME, etc)
            if any(term in cell_str.upper() for term in ['LTDA', 'S/A', 'S.A.', 'ME', 'EPP', 'EIRELI']):
                material_info["supplier"] = cell_str
            
            # Descrição (texto longo sem padrões específicos)
            elif len(cell_str) > 15 and not price_match and not re.match(r'^\d+$', cell_str):
                if not material_info["description"]:
                    material_info["description"] = cell_str
        
        # Retornar apenas se tiver descrição e quantidade
        if material_info["description"] and material_info["quantity"] > 0:
            return material_info
        
        return None
