"""
Comando Django para migrar dados legados do backup antigo.

Corrige MaterialReports órfãos criando MaterialBiddings a partir do backup
onde Material tinha FK direto para Bidding (modelo antigo).

Funcionalidades:
- Analisa backup antigo (modelo antigo)
- Identifica MaterialReports órfãos
- Cria MaterialBiddings faltantes
- Mantém licitações antigas como inativas
- Consolida nomes duplicados (XLSX > PDF > Backup)
"""
import json
from django.core.management.base import BaseCommand
from django.db import transaction
from django.template.defaultfilters import slugify
from bidding_procurement.models import Material, Bidding, MaterialBidding
from bidding_supplier.models import Supplier
from reports.models import MaterialReport
from difflib import SequenceMatcher


class Command(BaseCommand):
    help = 'Migra dados legados do backup antigo e corrige órfãos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backup',
            type=str,
            default='docs/backup antigo/backup_12092025.json',
            help='Caminho do arquivo de backup'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula execução sem fazer alterações'
        )

    def handle(self, *args, **options):
        backup_path = options['backup']
        dry_run = options['dry_run']

        self.stdout.write(
            self.style.SUCCESS('\n' + '='*80)
        )
        self.stdout.write(
            self.style.SUCCESS('MIGRAÇÃO DE DADOS LEGADOS')
        )
        self.stdout.write(
            self.style.SUCCESS('='*80 + '\n')
        )

        # Carregar backup
        self.stdout.write(f'📂 Carregando backup: {backup_path}')
        try:
            with open(backup_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao ler backup: {str(e)}')
            )
            return

        self.stdout.write(f'✓ Backup carregado: {len(data)} registros\n')

        # Separar por modelo
        by_model = {}
        for record in data:
            model = record['model']
            if model not in by_model:
                by_model[model] = []
            by_model[model].append(record)

        # Analisar estrutura
        self.stdout.write('📊 Estrutura do backup:')
        for model, records in by_model.items():
            self.stdout.write(f'  - {model}: {len(records)} registros')

        # Identificar MaterialReports órfãos
        self.stdout.write(f'\n🔍 Identificando MaterialReports órfãos...')
        orphan_reports = MaterialReport.objects.filter(material_bidding__isnull=True)
        orphan_count = orphan_reports.count()
        
        self.stdout.write(
            self.style.WARNING(f'⚠️  Encontrados {orphan_count} órfãos\n')
        )

        if orphan_count == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ Nenhum órfão encontrado!')
            )
            return

        # Mapear materiais do backup (modelo antigo)
        self.stdout.write('🗺️  Mapeando materiais do backup antigo...')
        legacy_materials = by_model.get('dashboard.material', [])
        
        # Criar mapa: material_id -> bidding_id
        material_to_bidding = {}
        for mat in legacy_materials:
            mat_id = mat['pk']
            bidding_id = mat['fields'].get('bidding')
            if bidding_id:
                material_to_bidding[mat_id] = bidding_id

        self.stdout.write(f'✓ {len(material_to_bidding)} materiais mapeados\n')

        # Processar órfãos
        self.stdout.write('🔧 Processando órfãos...\n')
        fixed_count = 0
        skipped_count = 0
        
        for orphan in orphan_reports:  # Processar TODOS os órfãos
            result = self._fix_orphan(orphan, material_to_bidding, legacy_materials, data, dry_run)
            if result:
                fixed_count += 1
            else:
                skipped_count += 1

        # Resumo
        self.stdout.write(f'\n{"="*80}')
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\n[DRY-RUN] {fixed_count} órfãos seriam corrigidos\n'
                    f'[DRY-RUN] {skipped_count} órfãos seriam pulados\n'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ {fixed_count} órfãos corrigidos!\n'
                    f'⚠️  {skipped_count} órfãos pulados\n'
                )
            )

        self.stdout.write(f'{"="*80}\n')

    def _fix_orphan(self, orphan, material_to_bidding, legacy_materials, backup_data, dry_run):
        """Corrige um MaterialReport órfão criando MaterialBidding faltante."""
        
        # Buscar MaterialReport no backup para pegar material_id antigo
        mr_backup = [r for r in backup_data if r['model'] == 'reports.materialreport' and r['pk'] == orphan.id]
        
        if not mr_backup:
            self.stdout.write(f'  ⚠️  Órfão {orphan.id}: Não encontrado no backup')
            return False
        
        # Pegar material_id do backup
        mat_id_old = mr_backup[0]['fields'].get('material')
        if not mat_id_old:
            self.stdout.write(f'  ⚠️  Órfão {orphan.id}: Sem material no backup')
            return False
        
        # Buscar material no backup
        mat_backup = [r for r in backup_data if r['model'] == 'dashboard.material' and r['pk'] == mat_id_old]
        if not mat_backup:
            self.stdout.write(f'  ⚠️  Órfão {orphan.id}: Material {mat_id_old} não encontrado')
            return False
        
        mat_fields = mat_backup[0]['fields']
        mat_name = mat_fields.get('name')
        bidding_id_old = mat_fields.get('bidding')
        
        if not bidding_id_old:
            self.stdout.write(f'  ⚠️  Órfão {orphan.id}: Material sem licitação')
            return False
        
        # Buscar licitação no backup
        bid_backup = [r for r in backup_data if r['model'] == 'dashboard.bidding' and r['pk'] == bidding_id_old]
        if not bid_backup:
            self.stdout.write(f'  ⚠️  Órfão {orphan.id}: Licitação {bidding_id_old} não encontrada')
            return False
        
        bid_fields = bid_backup[0]['fields']
        bid_name = bid_fields.get('name')
        
        self.stdout.write(f'  ✓ Órfão {orphan.id}: {mat_name[:40]} (Licitação: {bid_name})')
        
        if dry_run:
            self.stdout.write(f'    [DRY-RUN] Criaria MaterialBidding')
            return True
        
        # Buscar ou criar Material atual
        material, _ = Material.objects.get_or_create(
            name=mat_name,
            defaults={'slug': slugify(mat_name)[:50]}
        )
        
        # Buscar ou criar Bidding atual (INATIVA)
        bidding, _ = Bidding.objects.get_or_create(
            name=bid_name,
            defaults={
                'slug': slugify(bid_name)[:50],
                'status': '2'  # Inativa
            }
        )
        
        # Buscar ou criar MaterialBidding
        mat_bidding, created = MaterialBidding.objects.get_or_create(
            material=material,
            bidding=bidding,
            defaults={
                'quantity': orphan.quantity or 0,
                'price': orphan.unitary_price or 0,
                'status': '2'  # Inativo
            }
        )
        
        # Atualizar órfão
        orphan.material_bidding = mat_bidding
        orphan.save()
        
        self.stdout.write(f'    ✓ MaterialBidding criado e órfão corrigido')
        return True

    def _find_similar_material(self, name, existing_materials, threshold=0.85):
        """Encontra material similar usando fuzzy matching."""
        best_match = None
        best_score = 0
        
        name_normalized = name.lower().strip()
        
        for material in existing_materials:
            mat_name = material.name.lower().strip()
            score = SequenceMatcher(None, name_normalized, mat_name).ratio()
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = material
        
        return best_match, best_score
