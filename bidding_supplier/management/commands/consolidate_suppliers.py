"""
Comando Django para consolidar fornecedores duplicados.

Atualiza TODAS as Foreign Keys para garantir integridade referencial:
- MaterialBidding.supplier
- Contact.supplier
- Invoice.supplier
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from bidding_supplier.models import Supplier, Contact
from bidding_procurement.models import MaterialBidding
from fiscal.models import Invoice
from bidding_supplier.utils.name_normalizer import normalize_supplier_name


class Command(BaseCommand):
    help = 'Consolida fornecedores duplicados atualizando todas as referências'

    def add_arguments(self, parser):
        parser.add_argument(
            '--threshold',
            type=float,
            default=0.90,
            help='Threshold de similaridade (0.0-1.0)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula execução sem fazer alterações'
        )

    def handle(self, *args, **options):
        threshold = options['threshold']
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS('\n🔍 Buscando fornecedores duplicados...\n'))

        # Encontrar duplicatas
        duplicates = self._find_duplicates()
        
        if not duplicates:
            self.stdout.write(self.style.SUCCESS('✅ Nenhum fornecedor duplicado encontrado!'))
            return

        self.stdout.write(f'\n📊 Encontrados {len(duplicates)} grupos de duplicatas\n')

        total_consolidated = 0
        for master, duplicates_list in duplicates.items():
            count = self._consolidate_group(master, duplicates_list, dry_run)
            total_consolidated += count

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\n[DRY-RUN] {total_consolidated} fornecedores seriam consolidados')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ {total_consolidated} fornecedores consolidados com sucesso!')
            )

    def _find_duplicates(self):
        """Encontra fornecedores duplicados por nome normalizado."""
        suppliers = Supplier.objects.all()
        groups = {}
        
        for supplier in suppliers:
            normalized = normalize_supplier_name(supplier.company)
            if normalized not in groups:
                groups[normalized] = []
            groups[normalized].append(supplier)
        
        # Retornar apenas grupos com duplicatas
        duplicates = {}
        for normalized, group in groups.items():
            if len(group) > 1:
                # Primeiro da lista é o master (mais antigo = menor ID)
                master = min(group, key=lambda s: s.id)
                others = [s for s in group if s.id != master.id]
                duplicates[master] = others
        
        return duplicates

    def _consolidate_group(self, master, duplicates, dry_run):
        """Consolida um grupo de fornecedores duplicados."""
        self.stdout.write(f'\n🔄 Consolidando: {master.company} (ID: {master.id})')
        
        consolidated_count = 0
        
        for dup in duplicates:
            self.stdout.write(f'  ⚠️  Duplicata: {dup.company} (ID: {dup.id})')
            
            if dry_run:
                # Apenas contar o que seria atualizado
                mb_count = MaterialBidding.objects.filter(supplier=dup).count()
                contact_count = Contact.objects.filter(supplier=dup).count()
                invoice_count = Invoice.objects.filter(supplier=dup).count()
                
                self.stdout.write(f'    • {mb_count} MaterialBiddings seriam atualizados')
                self.stdout.write(f'    • {contact_count} Contacts seriam atualizados')
                self.stdout.write(f'    • {invoice_count} Invoices seriam atualizados')
                self.stdout.write(f'    • Fornecedor {dup.id} seria removido')
            else:
                # Executar consolidação real
                try:
                    with transaction.atomic():
                        # 1. Atualizar MaterialBidding
                        mb_count = MaterialBidding.objects.filter(supplier=dup).update(supplier=master)
                        if mb_count > 0:
                            self.stdout.write(
                                self.style.SUCCESS(f'    ✓ {mb_count} MaterialBiddings atualizados')
                            )
                        
                        # 2. Atualizar Contacts
                        contact_count = Contact.objects.filter(supplier=dup).update(supplier=master)
                        if contact_count > 0:
                            self.stdout.write(
                                self.style.SUCCESS(f'    ✓ {contact_count} Contacts atualizados')
                            )
                        
                        # 3. Atualizar Invoices
                        invoice_count = Invoice.objects.filter(supplier=dup).update(supplier=master)
                        if invoice_count > 0:
                            self.stdout.write(
                                self.style.SUCCESS(f'    ✓ {invoice_count} Invoices atualizados')
                            )
                        
                        # 4. Deletar duplicata
                        dup.delete()
                        self.stdout.write(
                            self.style.SUCCESS(f'    ✓ Fornecedor {dup.id} removido')
                        )
                        
                        consolidated_count += 1
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'    ❌ Erro ao consolidar: {str(e)}')
                    )
        
        return consolidated_count if not dry_run else len(duplicates)
