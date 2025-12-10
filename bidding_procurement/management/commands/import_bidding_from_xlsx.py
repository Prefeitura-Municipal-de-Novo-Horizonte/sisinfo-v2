"""
Comando Django para importar licitação completa de arquivo XLSX.

Importa:
- Material (código + descrição)
- MaterialBidding (fornecedor + quantidade + preço)
"""
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.template.defaultfilters import slugify
from bidding_procurement.models import Material, Bidding, MaterialBidding
from bidding_supplier.models import Supplier
from bidding_supplier.utils.name_normalizer import normalize_supplier_name


class Command(BaseCommand):
    help = 'Importa licitação completa de arquivo XLSX'

    def add_arguments(self, parser):
        parser.add_argument(
            '--xlsx',
            type=str,
            required=True,
            help='Caminho do arquivo XLSX'
        )
        parser.add_argument(
            '--bidding-number',
            type=str,
            required=True,
            help='Número da licitação (ex: 121/2025)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula execução sem fazer alterações'
        )

    def handle(self, *args, **options):
        xlsx_file = options['xlsx']
        bidding_number = options['bidding_number']
        dry_run = options['dry_run']

        self.stdout.write(
            self.style.SUCCESS(f'\n📊 Importando XLSX: {xlsx_file}\n')
        )

        # Ler XLSX
        try:
            df = pd.read_excel(xlsx_file, header=None)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao ler XLSX: {str(e)}')
            )
            return

        # Extrair fornecedor do cabeçalho (linha 0, coluna 4)
        supplier_code = df.iloc[0, 4]
        
        # Procurar nome do fornecedor nas colunas seguintes
        supplier_name = None
        for col in range(5, 15):
            val = df.iloc[0, col]
            if pd.notna(val) and isinstance(val, str) and len(val) > 5:
                supplier_name = val
                break
        
        if not supplier_name:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Fornecedor não encontrado no XLSX')
            )
            supplier = None
        else:
            # Normalizar nome do fornecedor
            supplier_normalized = normalize_supplier_name(supplier_name)
            
            # Buscar fornecedor existente por nome normalizado
            supplier = None
            for existing_supplier in Supplier.objects.all():
                if normalize_supplier_name(existing_supplier.company) == supplier_normalized:
                    supplier = existing_supplier
                    break
            
            # Se não encontrou, criar novo
            if not supplier:
                supplier = Supplier.objects.create(company=supplier_name)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Fornecedor criado: {supplier.company}')
                )
            else:
                self.stdout.write(
                    f'✓ Fornecedor encontrado: {supplier.company}'
                )

        # Buscar ou criar licitação
        bidding, created = Bidding.objects.get_or_create(
            administrative_process=bidding_number,
            defaults={
                'name': f'Licitação {bidding_number}',
                'slug': slugify(f'licitacao-{bidding_number}'),
                'status': '1'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Licitação criada: {bidding.name}')
            )
        else:
            self.stdout.write(
                f'✓ Licitação encontrada: {bidding.name}'
            )

        self.stdout.write('\n📦 Importando materiais...\n')

        # Processar materiais (a partir da linha 14)
        imported_count = 0
        updated_count = 0
        
        for idx in range(14, len(df)):
            # Verificar se linha tem dados
            item_num = df.iloc[idx, 0]
            if pd.isna(item_num):
                continue
            
            codigo = df.iloc[idx, 1]
            descricao = df.iloc[idx, 3]
            quantidade = df.iloc[idx, 12]
            preco = df.iloc[idx, 13]
            
            # Validar dados essenciais
            if pd.isna(codigo) or pd.isna(descricao):
                continue
            
            # Converter tipos
            try:
                quantidade = int(quantidade) if pd.notna(quantidade) else 0
                preco = float(preco) if pd.notna(preco) else 0.0
            except:
                quantidade = 0
                preco = 0.0
            
            # Criar ou atualizar Material
            slug = slugify(descricao)[:50]  # Limitar a 50 caracteres
            material, mat_created = Material.objects.get_or_create(
                name=descricao,
                defaults={'slug': slug}
            )
            
            # Criar ou atualizar MaterialBidding
            if not dry_run:
                mat_bidding, mb_created = MaterialBidding.objects.update_or_create(
                    material=material,
                    bidding=bidding,
                    defaults={
                        'supplier': supplier,
                        'quantity': quantidade,
                        'price': preco,
                        'status': '1'
                    }
                )
                
                if mb_created:
                    imported_count += 1
                    self.stdout.write(
                        f'  ✓ Importado: {descricao[:50]}... (Qtd: {quantidade}, R$ {preco})'
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        f'  ↻ Atualizado: {descricao[:50]}... (Qtd: {quantidade}, R$ {preco})'
                    )
            else:
                self.stdout.write(
                    f'  [DRY-RUN] {descricao[:50]}... (Qtd: {quantidade}, R$ {preco})'
                )
                imported_count += 1

        # Resumo
        self.stdout.write('\n' + '='*80)
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\n[DRY-RUN] {imported_count} materiais seriam importados\n')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Importação concluída!\n'
                    f'   Novos: {imported_count}\n'
                    f'   Atualizados: {updated_count}\n'
                )
            )
