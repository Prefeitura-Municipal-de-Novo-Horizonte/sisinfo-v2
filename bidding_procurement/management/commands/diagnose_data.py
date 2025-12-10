"""
Comando Django para diagnosticar problemas no banco de dados.

Identifica:
- Licitações duplicadas
- Fornecedores duplicados
- Materiais duplicados
- MaterialReports órfãos
- Nomes incompletos
"""
from django.core.management.base import BaseCommand
from bidding_procurement.models import Material, Bidding, MaterialBidding
from bidding_supplier.models import Supplier
from bidding_supplier.utils.name_normalizer import normalize_supplier_name
from reports.models import MaterialReport
from collections import Counter


class Command(BaseCommand):
    help = 'Diagnostica problemas no banco de dados'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('\n' + '='*80)
        )
        self.stdout.write(
            self.style.SUCCESS('DIAGNÓSTICO COMPLETO DO BANCO DE DADOS')
        )
        self.stdout.write(
            self.style.SUCCESS('='*80 + '\n')
        )

        # 1. Licitações
        self._check_biddings()
        
        # 2. Fornecedores
        self._check_suppliers()
        
        # 3. Materiais
        self._check_materials()
        
        # 4. Órfãos
        self._check_orphans()
        
        # Resumo
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('DIAGNÓSTICO CONCLUÍDO'))
        self.stdout.write('='*80 + '\n')

    def _check_biddings(self):
        """Verifica licitações duplicadas."""
        self.stdout.write('📋 LICITAÇÕES:')
        self.stdout.write('-'*80)
        
        biddings = Bidding.objects.all()
        self.stdout.write(f'Total: {biddings.count()}\n')
        
        # Agrupar por nome normalizado
        by_name = {}
        for b in biddings:
            name_norm = b.name.lower().strip()
            if name_norm not in by_name:
                by_name[name_norm] = []
            by_name[name_norm].append(b)
        
        # Identificar duplicatas
        duplicates = {k: v for k, v in by_name.items() if len(v) > 1}
        
        if duplicates:
            self.stdout.write(
                self.style.WARNING(f'⚠️  {len(duplicates)} licitações duplicadas:')
            )
            for name, bids in duplicates.items():
                self.stdout.write(f'\n  "{name}":')
                for b in bids:
                    mb_count = MaterialBidding.objects.filter(bidding=b).count()
                    self.stdout.write(
                        f'    ID {b.id}: Status={b.status}, '
                        f'MaterialBiddings={mb_count}'
                    )
        else:
            self.stdout.write('✅ Nenhuma licitação duplicada')
        
        self.stdout.write('\n')

    def _check_suppliers(self):
        """Verifica fornecedores duplicados."""
        self.stdout.write('🏢 FORNECEDORES:')
        self.stdout.write('-'*80)
        
        suppliers = Supplier.objects.all()
        self.stdout.write(f'Total: {suppliers.count()}\n')
        
        # Agrupar por nome normalizado
        by_name = {}
        for s in suppliers:
            name_norm = normalize_supplier_name(s.company)
            if name_norm not in by_name:
                by_name[name_norm] = []
            by_name[name_norm].append(s)
        
        # Identificar duplicatas
        duplicates = {k: v for k, v in by_name.items() if len(v) > 1}
        
        if duplicates:
            self.stdout.write(
                self.style.WARNING(f'⚠️  {len(duplicates)} fornecedores duplicados:')
            )
            for name, sups in list(duplicates.items())[:5]:
                self.stdout.write(f'\n  "{name}":')
                for s in sups:
                    mb_count = MaterialBidding.objects.filter(supplier=s).count()
                    self.stdout.write(
                        f'    ID {s.id}: {s.company} '
                        f'(MaterialBiddings={mb_count})'
                    )
            if len(duplicates) > 5:
                self.stdout.write(f'\n  ... e mais {len(duplicates) - 5} grupos')
        else:
            self.stdout.write('✅ Nenhum fornecedor duplicado')
        
        self.stdout.write('\n')

    def _check_materials(self):
        """Verifica materiais duplicados."""
        self.stdout.write('📦 MATERIAIS:')
        self.stdout.write('-'*80)
        
        materials = Material.objects.all()
        self.stdout.write(f'Total: {materials.count()}\n')
        
        # Agrupar por nome normalizado
        by_name = {}
        for m in materials:
            name_norm = ' '.join(m.name.lower().split())
            if name_norm not in by_name:
                by_name[name_norm] = []
            by_name[name_norm].append(m)
        
        # Identificar duplicatas
        duplicates = {k: v for k, v in by_name.items() if len(v) > 1}
        
        if duplicates:
            self.stdout.write(
                self.style.WARNING(f'⚠️  {len(duplicates)} materiais duplicados:')
            )
            for name, mats in list(duplicates.items())[:5]:
                self.stdout.write(f'\n  "{name[:60]}...":')
                for m in mats:
                    mb_count = MaterialBidding.objects.filter(material=m).count()
                    self.stdout.write(
                        f'    ID {m.id}: MaterialBiddings={mb_count}'
                    )
            if len(duplicates) > 5:
                self.stdout.write(f'\n  ... e mais {len(duplicates) - 5} grupos')
        else:
            self.stdout.write('✅ Nenhum material duplicado')
        
        # Verificar nomes curtos (possível nome incompleto)
        short_names = materials.filter(name__regex=r'^.{1,20}$')
        if short_names.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠️  {short_names.count()} materiais com nomes curtos '
                    f'(possível nome incompleto)'
                )
            )
            for m in short_names[:5]:
                self.stdout.write(f'  - ID {m.id}: "{m.name}"')
        
        self.stdout.write('\n')

    def _check_orphans(self):
        """Verifica MaterialReports órfãos."""
        self.stdout.write('⚠️  ÓRFÃOS:')
        self.stdout.write('-'*80)
        
        orphans = MaterialReport.objects.filter(material_bidding__isnull=True)
        count = orphans.count()
        
        if count > 0:
            self.stdout.write(
                self.style.ERROR(f'❌ {count} MaterialReports órfãos encontrados!')
            )
            
            # Agrupar por report
            by_report = {}
            for orphan in orphans:
                report_id = orphan.report_id
                if report_id not in by_report:
                    by_report[report_id] = []
                by_report[report_id].append(orphan)
            
            self.stdout.write(f'\nDistribuídos em {len(by_report)} laudos:')
            for report_id, orp_list in list(by_report.items())[:5]:
                self.stdout.write(
                    f'  Laudo {report_id}: {len(orp_list)} órfãos'
                )
        else:
            self.stdout.write('✅ Nenhum MaterialReport órfão')
        
        self.stdout.write('\n')
