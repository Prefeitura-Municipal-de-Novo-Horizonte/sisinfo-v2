"""
Comando Django para consolidar materiais duplicados.

Atualiza MaterialReport.material_bidding para garantir integridade referencial.
Verifica duplicatas de MaterialBidding antes de consolidar.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from bidding_procurement.models import Material, MaterialBidding
from reports.models import MaterialReport
from collections import defaultdict


class Command(BaseCommand):
    help = 'Consolida materiais duplicados atualizando todas as referências'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula execução sem fazer alterações'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS('\n🔍 Buscando materiais duplicados...\n'))

        # Encontrar duplicatas
        duplicates = self._find_duplicates()
        
        if not duplicates:
            self.stdout.write(self.style.SUCCESS('✅ Nenhum material duplicado encontrado!'))
            return

        self.stdout.write(f'\n📊 Encontrados {len(duplicates)} grupos de duplicatas\n')

        total_consolidated = 0
        for master, duplicates_list in duplicates.items():
            count = self._consolidate_group(master, duplicates_list, dry_run)
            total_consolidated += count

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\n[DRY-RUN] {total_consolidated} materiais seriam consolidados')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ {total_consolidated} materiais consolidados com sucesso!')
            )

    def _find_duplicates(self):
        """Encontra materiais duplicados por nome normalizado."""
        materials = Material.objects.all()
        groups = defaultdict(list)
        
        for material in materials:
            # Normalizar nome (lowercase, sem espaços extras)
            normalized = ' '.join(material.name.lower().split())
            groups[normalized].append(material)
        
        # Retornar apenas grupos com duplicatas
        duplicates = {}
        for normalized, group in groups.items():
            if len(group) > 1:
                # Primeiro da lista é o master (mais antigo = menor ID)
                master = min(group, key=lambda m: m.id)
                others = [m for m in group if m.id != master.id]
                duplicates[master] = others
        
        return duplicates

    def _consolidate_group(self, master, duplicates, dry_run):
        """Consolida um grupo de materiais duplicados."""
        self.stdout.write(f'\n🔄 Consolidando: {master.name} (ID: {master.id})')
        
        consolidated_count = 0
        
        for dup in duplicates:
            self.stdout.write(f'  ⚠️  Duplicata: {dup.name} (ID: {dup.id})')
            
            if dry_run:
                # Apenas contar o que seria atualizado
                dup_mbs = MaterialBidding.objects.filter(material=dup)
                self.stdout.write(f'    • {dup_mbs.count()} MaterialBiddings seriam processados')
                
                for dup_mb in dup_mbs:
                    master_mb = MaterialBidding.objects.filter(
                        material=master,
                        bidding=dup_mb.bidding
                    ).first()
                    
                    if master_mb:
                        mr_count = MaterialReport.objects.filter(material_bidding=dup_mb).count()
                        self.stdout.write(
                            f'      • {mr_count} MaterialReports seriam movidos para MB {master_mb.id}'
                        )
                    else:
                        self.stdout.write(f'      • MaterialBidding seria atualizado para Material {master.id}')
                
                self.stdout.write(f'    • Material {dup.id} seria removido')
            else:
                # Executar consolidação real
                try:
                    with transaction.atomic():
                        # Processar cada MaterialBidding do material duplicado
                        dup_mbs = MaterialBidding.objects.filter(material=dup)
                        
                        for dup_mb in dup_mbs:
                            # Verificar se master já tem MaterialBidding para essa licitação
                            master_mb = MaterialBidding.objects.filter(
                                material=master,
                                bidding=dup_mb.bidding
                            ).first()
                            
                            if master_mb:
                                # Já existe, mover MaterialReports e deletar duplicata
                                mr_count = MaterialReport.objects.filter(
                                    material_bidding=dup_mb
                                ).update(material_bidding=master_mb)
                                
                                if mr_count > 0:
                                    self.stdout.write(
                                        self.style.SUCCESS(
                                            f'    ✓ {mr_count} MaterialReports movidos para MB {master_mb.id}'
                                        )
                                    )
                                
                                # Deletar MaterialBidding duplicado
                                dup_mb.delete()
                                self.stdout.write(
                                    self.style.SUCCESS(f'    ✓ MaterialBidding {dup_mb.id} removido')
                                )
                            else:
                                # Não existe, apenas atualizar material
                                dup_mb.material = master
                                dup_mb.save()
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'    ✓ MaterialBidding {dup_mb.id} atualizado para Material {master.id}'
                                    )
                                )
                        
                        # Deletar material duplicado
                        dup.delete()
                        self.stdout.write(
                            self.style.SUCCESS(f'    ✓ Material {dup.id} removido')
                        )
                        
                        consolidated_count += 1
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'    ❌ Erro ao consolidar: {str(e)}')
                    )
        
        return consolidated_count if not dry_run else len(duplicates)
