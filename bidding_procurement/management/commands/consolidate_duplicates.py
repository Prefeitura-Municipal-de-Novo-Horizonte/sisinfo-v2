from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count
from bidding_procurement.models import Material, MaterialBidding
from bidding_supplier.models import Supplier
from reports.models import MaterialReport
from bidding_procurement.utils.fuzzy_matcher import FuzzyMatcher


class Command(BaseCommand):
    help = 'Consolida materiais e fornecedores duplicados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem executar'
        )
        parser.add_argument(
            '--threshold',
            type=float,
            default=0.9,
            help='Threshold de similaridade (0.0 a 1.0)'
        )
        parser.add_argument(
            '--auto',
            action='store_true',
            help='Consolida automaticamente sem perguntar'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        threshold = options['threshold']
        auto = options['auto']
        
        self.stdout.write(self.style.WARNING('\n=== CONSOLIDAÇÃO DE DUPLICATAS ===\n'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita\n'))
        
        # Consolidar fornecedores
        self._consolidate_suppliers(threshold, dry_run, auto)
        
        # Consolidar materiais
        self._consolidate_materials(threshold, dry_run, auto)
        
        self.stdout.write(self.style.SUCCESS('\n✓ Consolidação concluída!'))
    
    def _consolidate_suppliers(self, threshold, dry_run, auto):
        """Consolida fornecedores duplicados."""
        self.stdout.write('\n=== FORNECEDORES ===\n')
        
        suppliers = list(Supplier.objects.all())
        matcher = FuzzyMatcher(threshold=threshold)
        
        consolidated = set()
        total_merged = 0
        
        for i, supplier in enumerate(suppliers):
            if supplier.id in consolidated:
                continue
            
            # Procurar similares
            similar_names = [s.company for s in suppliers[i+1:] if s.id not in consolidated]
            matches = matcher.find_similar(supplier.company, similar_names)
            
            if not matches:
                continue
            
            self.stdout.write(f'\nFornecedor: {supplier.company} (ID: {supplier.id})')
            self.stdout.write(f'  Similares encontrados:')
            
            for similar_name, score in matches:
                similar_supplier = Supplier.objects.get(company=similar_name)
                self.stdout.write(f'    - {similar_name} (ID: {similar_supplier.id}, {score:.0%})')
                
                # Contar usos
                mb_count = MaterialBidding.objects.filter(supplier=similar_supplier).count()
                self.stdout.write(f'      Usado em {mb_count} MaterialBiddings')
                
                # Decidir se consolida
                should_merge = auto or (not dry_run and self._ask_merge(supplier.company, similar_name))
                
                if should_merge:
                    if not dry_run:
                        # Atualizar referências
                        MaterialBidding.objects.filter(supplier=similar_supplier).update(supplier=supplier)
                        
                        # Deletar duplicata
                        similar_supplier.delete()
                        
                        self.stdout.write(self.style.SUCCESS(f'      ✓ Consolidado em "{supplier.company}"'))
                    else:
                        self.stdout.write(self.style.WARNING(f'      [DRY-RUN] Seria consolidado'))
                    
                    consolidated.add(similar_supplier.id)
                    total_merged += 1
        
        self.stdout.write(f'\nTotal de fornecedores consolidados: {total_merged}')
    
    def _consolidate_materials(self, threshold, dry_run, auto):
        """Consolida materiais duplicados."""
        self.stdout.write('\n=== MATERIAIS ===\n')
        
        materials = list(Material.objects.all())
        matcher = FuzzyMatcher(threshold=threshold)
        
        consolidated = set()
        total_merged = 0
        
        for i, material in enumerate(materials):
            if material.id in consolidated:
                continue
            
            # Procurar similares
            similar_names = [m.name for m in materials[i+1:] if m.id not in consolidated]
            matches = matcher.find_similar(material.name, similar_names)
            
            if not matches:
                continue
            
            self.stdout.write(f'\nMaterial: {material.name} (ID: {material.id})')
            self.stdout.write(f'  Similares encontrados:')
            
            for similar_name, score in matches:
                similar_material = Material.objects.filter(name=similar_name).first()
                if not similar_material:
                    continue
                    
                self.stdout.write(f'    - {similar_name} (ID: {similar_material.id}, {score:.0%})')
                
                # Contar usos
                mb_count = MaterialBidding.objects.filter(material=similar_material).count()
                mr_count = MaterialReport.objects.filter(material_bidding__material=similar_material).count()
                self.stdout.write(f'      Usado em {mb_count} MaterialBiddings, {mr_count} MaterialReports')
                
                # Decidir se consolida
                should_merge = auto or (not dry_run and self._ask_merge(material.name, similar_name))
                
                if should_merge:
                    if not dry_run:
                        # Atualizar referências em MaterialBidding
                        MaterialBidding.objects.filter(material=similar_material).update(material=material)
                        
                        # Deletar duplicata
                        similar_material.delete()
                        
                        self.stdout.write(self.style.SUCCESS(f'      ✓ Consolidado em "{material.name}"'))
                    else:
                        self.stdout.write(self.style.WARNING(f'      [DRY-RUN] Seria consolidado'))
                    
                    consolidated.add(similar_material.id)
                    total_merged += 1
        
        self.stdout.write(f'\nTotal de materiais consolidados: {total_merged}')
    
    def _ask_merge(self, keep_name, merge_name):
        """Pergunta ao usuário se deve consolidar."""
        response = input(f'      Consolidar "{merge_name}" em "{keep_name}"? [S/n]: ')
        return response.lower() != 'n'
