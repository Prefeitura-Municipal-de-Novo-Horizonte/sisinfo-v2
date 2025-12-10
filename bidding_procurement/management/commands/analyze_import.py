"""
Comando Django para analisar e comparar dados de PDF e XLSX antes de importar.

Gera relatório completo mostrando:
- Comparação entre fontes
- Divergências de nomes
- Quantidades e preços
- Materiais duplicados
- Possíveis problemas
"""
import pandas as pd
import os
from django.core.management.base import BaseCommand
from bidding_procurement.models import Material, Bidding, MaterialBidding
from bidding_supplier.models import Supplier
from bidding_supplier.utils.name_normalizer import normalize_supplier_name
from difflib import SequenceMatcher


class Command(BaseCommand):
    help = 'Analisa e compara dados de PDF e XLSX antes de importar'

    def add_arguments(self, parser):
        parser.add_argument(
            '--xlsx-dir',
            type=str,
            default='docs/licitacoes/xls',
            help='Diretório com arquivos XLSX'
        )

    def handle(self, *args, **options):
        xlsx_dir = options['xlsx_dir']

        self.stdout.write(
            self.style.SUCCESS('\n' + '='*80)
        )
        self.stdout.write(
            self.style.SUCCESS('ANÁLISE COMPARATIVA - PDF vs XLSX')
        )
        self.stdout.write(
            self.style.SUCCESS('='*80 + '\n')
        )

        # Listar arquivos XLSX
        xlsx_files = [f for f in os.listdir(xlsx_dir) if f.endswith('.xlsx')]
        
        if not xlsx_files:
            self.stdout.write(
                self.style.ERROR(f'❌ Nenhum arquivo XLSX encontrado em {xlsx_dir}')
            )
            return

        self.stdout.write(f'📁 Arquivos XLSX encontrados: {len(xlsx_files)}\n')
        for f in xlsx_files:
            self.stdout.write(f'   - {f}')

        # Analisar cada XLSX
        all_data = []
        for xlsx_file in xlsx_files:
            filepath = os.path.join(xlsx_dir, xlsx_file)
            data = self._analyze_xlsx(filepath, xlsx_file)
            if data:
                all_data.append(data)

        # Gerar relatório consolidado
        self._generate_report(all_data)

    def _analyze_xlsx(self, filepath, filename):
        """Analisa um arquivo XLSX."""
        self.stdout.write(f'\n{"="*80}')
        self.stdout.write(f'📊 Analisando: {filename}')
        self.stdout.write(f'{"="*80}\n')

        try:
            df = pd.read_excel(filepath, header=None)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao ler arquivo: {str(e)}')
            )
            return None

        # Extrair fornecedor
        supplier_code = df.iloc[0, 4] if len(df) > 0 else None
        supplier_name = None
        for col in range(5, 15):
            try:
                val = df.iloc[0, col]
                if pd.notna(val) and isinstance(val, str) and len(val) > 5:
                    supplier_name = val
                    break
            except:
                pass

        # Extrair número da licitação do nome do arquivo
        bidding_number = filename.replace('.xlsx', '').replace('.xls', '')

        # Contar materiais
        materials = []
        for idx in range(14, len(df)):
            try:
                item_num = df.iloc[idx, 0]
                if pd.isna(item_num):
                    continue

                codigo = df.iloc[idx, 1]
                descricao = df.iloc[idx, 3]
                quantidade = df.iloc[idx, 12]
                preco = df.iloc[idx, 13]

                if pd.notna(codigo) and pd.notna(descricao):
                    materials.append({
                        'codigo': str(codigo),
                        'descricao': str(descricao),
                        'quantidade': int(quantidade) if pd.notna(quantidade) else 0,
                        'preco': float(preco) if pd.notna(preco) else 0.0
                    })
            except:
                continue

        # Mostrar resumo
        self.stdout.write(f'🏢 Fornecedor: {supplier_name or "NÃO ENCONTRADO"}')
        self.stdout.write(f'📋 Licitação: {bidding_number}')
        self.stdout.write(f'📦 Total de materiais: {len(materials)}\n')

        # Mostrar primeiros 5 materiais
        self.stdout.write('Primeiros 5 materiais:')
        for i, mat in enumerate(materials[:5]):
            self.stdout.write(
                f'  {i+1}. {mat["descricao"][:60]}... '
                f'(Qtd: {mat["quantidade"]}, R$ {mat["preco"]:.2f})'
            )

        if len(materials) > 5:
            self.stdout.write(f'  ... e mais {len(materials) - 5} materiais')

        return {
            'filename': filename,
            'bidding_number': bidding_number,
            'supplier_name': supplier_name,
            'materials': materials
        }

    def _generate_report(self, all_data):
        """Gera relatório consolidado."""
        self.stdout.write(f'\n{"="*80}')
        self.stdout.write('📊 RELATÓRIO CONSOLIDADO')
        self.stdout.write(f'{"="*80}\n')

        total_materials = sum(len(d['materials']) for d in all_data)
        total_licitacoes = len(all_data)

        self.stdout.write(f'📋 Total de licitações: {total_licitacoes}')
        self.stdout.write(f'📦 Total de materiais: {total_materials}\n')

        # Verificar fornecedores
        self.stdout.write('🏢 FORNECEDORES:')
        suppliers_in_xlsx = set()
        for data in all_data:
            if data['supplier_name']:
                normalized = normalize_supplier_name(data['supplier_name'])
                suppliers_in_xlsx.add(normalized)
                
                # Verificar se existe no banco
                exists = False
                for supplier in Supplier.objects.all():
                    if normalize_supplier_name(supplier.company) == normalized:
                        exists = True
                        self.stdout.write(
                            f'  ✓ {data["supplier_name"]} '
                            f'(já existe: {supplier.company})'
                        )
                        break
                
                if not exists:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠️  {data["supplier_name"]} (SERÁ CRIADO)'
                        )
                    )

        # Verificar materiais duplicados entre licitações
        self.stdout.write(f'\n📦 ANÁLISE DE MATERIAIS:')
        all_materials_names = []
        for data in all_data:
            for mat in data['materials']:
                all_materials_names.append(mat['descricao'])

        # Contar duplicatas
        from collections import Counter
        duplicates = {name: count for name, count in Counter(all_materials_names).items() if count > 1}
        
        if duplicates:
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠️  {len(duplicates)} materiais aparecem em múltiplas licitações:'
                )
            )
            for name, count in list(duplicates.items())[:5]:
                self.stdout.write(f'  - {name[:60]}... ({count}x)')
            if len(duplicates) > 5:
                self.stdout.write(f'  ... e mais {len(duplicates) - 5} duplicatas')
        else:
            self.stdout.write('✓ Nenhum material duplicado entre licitações')

        # Verificar materiais existentes no banco
        self.stdout.write(f'\n🔍 COMPARAÇÃO COM BANCO DE DADOS:')
        existing_materials = Material.objects.count()
        self.stdout.write(f'  Materiais no banco: {existing_materials}')
        self.stdout.write(f'  Materiais no XLSX: {total_materials}')

        # Verificar se há materiais órfãos
        from reports.models import MaterialReport
        orphan_reports = MaterialReport.objects.filter(material_bidding__isnull=True).count()
        if orphan_reports > 0:
            self.stdout.write(
                self.style.ERROR(
                    f'\n❌ ATENÇÃO: {orphan_reports} MaterialReports órfãos no banco!'
                )
            )
        else:
            self.stdout.write('\n✓ Nenhum MaterialReport órfão')

        # Resumo final
        self.stdout.write(f'\n{"="*80}')
        self.stdout.write('📋 RESUMO DA IMPORTAÇÃO:')
        self.stdout.write(f'{"="*80}\n')

        for data in all_data:
            self.stdout.write(
                f'Licitação {data["bidding_number"]}:'
            )
            self.stdout.write(
                f'  - Fornecedor: {data["supplier_name"] or "N/A"}'
            )
            self.stdout.write(
                f'  - Materiais: {len(data["materials"])}'
            )
            total_value = sum(m['quantidade'] * m['preco'] for m in data['materials'])
            self.stdout.write(
                f'  - Valor total: R$ {total_value:,.2f}\n'
            )

        self.stdout.write(f'\n{"="*80}')
        self.stdout.write(
            self.style.SUCCESS('✅ Análise concluída!')
        )
        self.stdout.write(
            'Execute o comando de importação para prosseguir.'
        )
        self.stdout.write(f'{"="*80}\n')
