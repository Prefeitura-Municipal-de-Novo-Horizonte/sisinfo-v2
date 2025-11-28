from django.core.management.base import BaseCommand
from django.db import transaction
from bidding_procurement.models import Bidding, MaterialBidding
from collections import defaultdict


class Command(BaseCommand):
    help = 'Remove licitações duplicadas, mantendo a mais antiga'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem executar'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.WARNING('\n=== LIMPEZA DE LICITAÇÕES DUPLICADAS ===\n'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita\n'))
        
        # Agrupar por nome (que inclui o processo)
        biddings_by_name = defaultdict(list)
        for bidding in Bidding.objects.all():
            biddings_by_name[bidding.name].append(bidding)
        
        total_removed = 0
        
        for name, biddings in biddings_by_name.items():
            if len(biddings) <= 1:
                continue
            
            # Ordenar por ID (mais antigo primeiro)
            biddings.sort(key=lambda b: b.id)
            
            keep = biddings[0]
            duplicates = biddings[1:]
            
            self.stdout.write(f'\n📋 {name}')
            self.stdout.write(f'  Manter: ID {keep.id} ({keep.material_associations.count()} materiais)')
            
            for dup in duplicates:
                mat_count = dup.material_associations.count()
                self.stdout.write(f'  Remover: ID {dup.id} ({mat_count} materiais)')
                
                if not dry_run:
                    with transaction.atomic():
                        # Mover materiais para a licitação que será mantida
                        for mat_bidding in MaterialBidding.objects.filter(bidding=dup):
                            # Verificar se já existe
                            existing = MaterialBidding.objects.filter(
                                material=mat_bidding.material,
                                bidding=keep
                            ).first()
                            
                            if existing:
                                # Já existe, apenas deletar
                                mat_bidding.delete()
                            else:
                                # Mover para a licitação mantida
                                mat_bidding.bidding = keep
                                mat_bidding.save()
                        
                        # Deletar licitação duplicada
                        dup.delete()
                        
                        self.stdout.write(self.style.SUCCESS(f'    ✓ Removido e materiais consolidados'))
                        total_removed += 1
                else:
                    self.stdout.write(self.style.WARNING(f'    [DRY-RUN] Seria removido'))
        
        if total_removed > 0:
            self.stdout.write(self.style.SUCCESS(f'\n✓ {total_removed} licitações duplicadas removidas'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ Nenhuma duplicata encontrada'))
