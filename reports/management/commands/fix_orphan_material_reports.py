from django.core.management.base import BaseCommand
from reports.models import MaterialReport
from bidding_procurement.models import Material, Bidding, MaterialBidding
from datetime import date

class Command(BaseCommand):
    help = 'Corrige MaterialReports órfãos vinculando-os à Licitação Legado'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando correção de MaterialReports...'))

        # Criar ou obter licitação legado
        legacy_bidding, created = Bidding.objects.get_or_create(
            name="Licitação Legado - Migração",
            defaults={
                'date': date.today(),
                'status': '1',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Licitação "{legacy_bidding.name}" criada.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Licitação "{legacy_bidding.name}" já existe.'))

        # Contar MaterialReports órfãos
        orphan_reports = MaterialReport.objects.filter(material_bidding__isnull=True)
        total_orphans = orphan_reports.count()
        
        if total_orphans == 0:
            self.stdout.write(self.style.SUCCESS('Nenhum MaterialReport órfão encontrado!'))
            return

        self.stdout.write(self.style.WARNING(f'Encontrados {total_orphans} MaterialReports órfãos.'))
        self.stdout.write(self.style.WARNING('ATENÇÃO: Os dados originais de material foram perdidos na migração.'))
        self.stdout.write(self.style.WARNING('Será criado um MaterialBidding genérico para cada um.'))
        
        # Criar material genérico se não existir
        generic_material, _ = Material.objects.get_or_create(
            name="Material Perdido - Migração",
            defaults={'slug': 'material-perdido-migracao'}
        )
        
        # Criar MaterialBidding genérico
        generic_material_bidding, _ = MaterialBidding.objects.get_or_create(
            material=generic_material,
            bidding=legacy_bidding,
            defaults={
                'status': '1',
                'price': 0,
                'readjustment': 0
            }
        )
        
        # Vincular todos os órfãos
        count = 0
        for material_report in orphan_reports:
            material_report.material_bidding = generic_material_bidding
            material_report.save()
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Sucesso! {count} MaterialReports foram corrigidos.'))
        self.stdout.write(self.style.WARNING('IMPORTANTE: Revise os laudos e atualize manualmente os materiais corretos!'))
