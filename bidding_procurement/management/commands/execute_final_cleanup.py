"""
Comando final para executar limpeza baseada no CSV editado.

Lê coluna 'equivale á' e executa:
- MERGE_COM_ID_X: Consolidar com material X
- NAO_USADO: Deletar (se sem laudos)
- DELETE: Deletar forçado
- Normaliza nomes para maiúsculo
"""
import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from bidding_procurement.models import Material, MaterialBidding
from reports.models import MaterialReport


class Command(BaseCommand):
    help = 'Executa limpeza final baseada no CSV'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=str, default='relatorio_materiais_detalhado.csv')
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--uppercase', action='store_true', help='Normalizar nomes para maiúsculo')

    def handle(self, *args, **options):
        csv_file = options['csv']
        dry_run = options['dry_run']
        uppercase = options['uppercase']

        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('LIMPEZA FINAL'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))

        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY-RUN MODE]\n'))

        # Ler CSV
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        merged = 0
        deleted = 0
        uppercased = 0

        with transaction.atomic():
            # Fase 1: Merges
            for row in rows:
                acao = (row.get('mudancas_sugeridas') or '').strip()
                
                if 'MERGE_COM_ID_' in acao:
                    # Extrair ID do merge
                    import re
                    match = re.search(r'MERGE_COM_ID_(\d+)', acao)
                    if match:
                        target_id = match.group(1)
                        result = self._merge_material(row['id'], target_id, dry_run)
                        if result:
                            merged += 1

            # Fase 2: Deletar não usados
            for row in rows:
                acao = (row.get('mudancas_sugeridas') or '').strip()
                
                if 'EXCLUIR' in acao or acao == 'NAO_USADO' or acao == 'DELETE':
                    result = self._delete_if_safe(row['id'], dry_run)
                    if result:
                        deleted += 1

            # Fase 3: Normalizar para maiúsculo
            if uppercase:
                for material in Material.objects.all():
                    if material.name != material.name.upper():
                        if not dry_run:
                            material.name = material.name.upper()
                            material.save()
                        uppercased += 1

        # Resumo
        self.stdout.write('\n' + '='*80)
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'\n[DRY-RUN] {merged} materiais seriam consolidados\n'
                f'[DRY-RUN] {deleted} materiais seriam deletados\n'
                f'[DRY-RUN] {uppercased} nomes seriam normalizados\n'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ {merged} materiais consolidados!\n'
                f'✅ {deleted} materiais deletados!\n'
                f'✅ {uppercased} nomes normalizados!\n'
            ))
        self.stdout.write('='*80 + '\n')

    def _merge_material(self, source_id, target_id, dry_run):
        """Consolida source em target."""
        source = Material.objects.filter(id=source_id).first()
        target = Material.objects.filter(id=target_id).first()

        if not source or not target:
            self.stdout.write(f'⚠️  Material {source_id} ou {target_id} não encontrado')
            return False

        self.stdout.write(f'\n🔄 Consolidando:')
        self.stdout.write(f'  {source.name} (ID {source.id})')
        self.stdout.write(f'  → {target.name} (ID {target.id})')

        if not dry_run:
            # Reatribuir MaterialBiddings
            mbs = MaterialBidding.objects.filter(material=source)
            for mb in mbs:
                # Verificar se já existe
                existing = MaterialBidding.objects.filter(
                    material=target,
                    bidding=mb.bidding
                ).first()

                if existing:
                    # Reatribuir laudos
                    MaterialReport.objects.filter(material_bidding=mb).update(
                        material_bidding=existing
                    )
                    mb.delete()
                else:
                    mb.material = target
                    mb.save()

            # Deletar source
            source.delete()
            self.stdout.write(self.style.SUCCESS('  ✓ Consolidado!'))
            return True
        else:
            self.stdout.write('  [DRY-RUN] Seria consolidado')
            return True

    def _delete_if_safe(self, material_id, dry_run):
        """Deleta material se não tiver laudos."""
        material = Material.objects.filter(id=material_id).first()
        if not material:
            return False

        # Verificar laudos
        laudos = MaterialReport.objects.filter(
            material_bidding__material=material
        ).count()

        if laudos > 0:
            self.stdout.write(f'⚠️  Material {material.id} tem {laudos} laudos - NÃO deletado')
            return False

        # Verificar MaterialBiddings
        mbs = MaterialBidding.objects.filter(material=material).count()

        if mbs > 0:
            self.stdout.write(f'⚠️  Material {material.id} tem {mbs} licitações - NÃO deletado')
            return False

        self.stdout.write(f'\n🗑️  Deletando: {material.name} (ID {material.id})')

        if not dry_run:
            material.delete()
            self.stdout.write(self.style.SUCCESS('  ✓ Deletado!'))
            return True
        else:
            self.stdout.write('  [DRY-RUN] Seria deletado')
            return True
