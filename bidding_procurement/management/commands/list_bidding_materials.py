from django.core.management.base import BaseCommand
from django.db import transaction
from bidding_procurement.models import Bidding, MaterialBidding


class Command(BaseCommand):
    help = 'Lista todos os materiais de uma licitação para revisão manual'

    def add_arguments(self, parser):
        parser.add_argument('administrative_process', type=str, help='Processo administrativo (ex: 121/25)')

    def handle(self, *args, **options):
        process = options['administrative_process']
        
        try:
            bidding = Bidding.objects.get(administrative_process=process)
        except Bidding.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Licitação {process} não encontrada'))
            return
        
        materials = MaterialBidding.objects.filter(bidding=bidding).order_by('id')
        
        self.stdout.write(self.style.WARNING(f'\n=== MATERIAIS DA LICITAÇÃO {bidding.name} ===\n'))
        self.stdout.write(f'Total: {materials.count()} materiais\n')
        
        for i, mat_bidding in enumerate(materials, 1):
            self.stdout.write(f'{i}. ID {mat_bidding.id}: {mat_bidding.material.name[:80]}')
            if mat_bidding.supplier:
                self.stdout.write(f'   Fornecedor: {mat_bidding.supplier.company}')
            self.stdout.write(f'   Qtd: {mat_bidding.quantity} | Preço: R$ {mat_bidding.price}')
            self.stdout.write('')
        
        # Perguntar se quer remover algum
        self.stdout.write(self.style.WARNING('\nDeseja remover algum material?'))
        response = input('Digite os IDs separados por vírgula (ou Enter para cancelar): ')
        
        if response.strip():
            ids_to_remove = [int(id.strip()) for id in response.split(',')]
            
            self.stdout.write(f'\nMateriais a remover:')
            for mat_id in ids_to_remove:
                mat = MaterialBidding.objects.get(id=mat_id)
                self.stdout.write(f'  - ID {mat.id}: {mat.material.name[:60]}...')
            
            confirm = input('\nConfirmar remoção? [S/n]: ')
            if confirm.lower() != 'n':
                with transaction.atomic():
                    MaterialBidding.objects.filter(id__in=ids_to_remove).delete()
                
                self.stdout.write(self.style.SUCCESS(f'\n✓ {len(ids_to_remove)} materiais removidos'))
                self.stdout.write(f'Materiais restantes: {materials.count() - len(ids_to_remove)}')
            else:
                self.stdout.write(self.style.WARNING('Operação cancelada'))
        else:
            self.stdout.write(self.style.WARNING('Nenhum material removido'))
