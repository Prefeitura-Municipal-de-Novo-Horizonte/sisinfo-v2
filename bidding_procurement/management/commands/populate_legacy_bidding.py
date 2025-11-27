from django.core.management.base import BaseCommand
from bidding_procurement.models import Bidding, Material, MaterialBidding
from datetime import date

class Command(BaseCommand):
    help = 'Cria uma Licitação Legado e vincula todos os materiais existentes a ela.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando migração para Licitação Legado...'))

        # 1. Criar ou obter a Licitação Legado
        legacy_bidding, created = Bidding.objects.get_or_create(
            name="Licitação Legado",
            defaults={
                'date': date.today(),
                'status': '1',  # Ativo
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Licitação "{legacy_bidding.name}" criada.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Licitação "{legacy_bidding.name}" já existe.'))

        # 2. Vincular materiais órfãos
        materials = Material.objects.all()
        count = 0
        for material in materials:
            # Verifica se já tem vínculo com alguma licitação
            if not MaterialBidding.objects.filter(material=material).exists():
                MaterialBidding.objects.create(
                    material=material,
                    bidding=legacy_bidding,
                    status='1',  # Ativo
                    price=0.00, # Preço zerado pois não sabemos o original
                    readjustment=0
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Sucesso! {count} materiais foram vinculados à "{legacy_bidding.name}".'))
