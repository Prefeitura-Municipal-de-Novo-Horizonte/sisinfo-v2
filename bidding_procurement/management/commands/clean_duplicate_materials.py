from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count
from bidding_procurement.models import Bidding, MaterialBidding

class Command(BaseCommand):
    help = 'Remove materiais duplicados dentro da mesma licitação, mantendo o mais antigo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem executar'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.WARNING('\n=== LIMPEZA DE MATERIAIS DUPLICADOS ===\n'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita\n'))
        
        total_removed = 0
        
        for bidding in Bidding.objects.all():
            self.stdout.write(f'Analisando: {bidding.name}...')
            
            # Encontrar nomes duplicados
            duplicates = MaterialBidding.objects.filter(bidding=bidding)\
                .values('material__name')\
                .annotate(count=Count('id'))\
                .filter(count__gt=1)
            
            for dup in duplicates:
                name = dup['material__name']
                count = dup['count']
                
                self.stdout.write(f'  Duplicado ({count}x): {name[:50]}...')
                
                # Pegar todas as instâncias
                instances = list(MaterialBidding.objects.filter(
                    bidding=bidding,
                    material__name=name
                ).order_by('id'))
                
                keep = instances[0]
                remove_list = instances[1:]
                
                if not dry_run:
                    with transaction.atomic():
                        for item in remove_list:
                            # Verificar se tem uso em Laudos (Reports)
                            # Se tiver, precisamos re-apontar para o 'keep' antes de deletar
                            if hasattr(item, 'materiais_laudos'):
                                for report_item in item.materiais_laudos.all():
                                    report_item.material_bidding = keep
                                    report_item.save()
                                    self.stdout.write(f'    -> Re-apontado laudo {report_item.id} para ID {keep.id}')
                            
                            item.delete()
                            total_removed += 1
                else:
                    self.stdout.write(f'    [DRY-RUN] Removeria {len(remove_list)} itens')

        if total_removed > 0:
            self.stdout.write(self.style.SUCCESS(f'\n✓ {total_removed} materiais duplicados removidos'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ Nenhum material duplicado encontrado'))
