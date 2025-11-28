from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from bidding_procurement.models import Bidding, Material, MaterialBidding
from bidding_supplier.models import Supplier
from bidding_procurement.utils.pdf_extractor import BiddingPDFExtractor
from bidding_procurement.utils.fuzzy_matcher import find_similar_suppliers
from datetime import datetime


class Command(BaseCommand):
    help = 'Importa licitação de um arquivo PDF'

    def add_arguments(self, parser):
        parser.add_argument('pdf_file', type=str, help='Caminho para o arquivo PDF')
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Modo interativo (pergunta antes de criar/atualizar)'
        )
        parser.add_argument(
            '--auto-merge',
            action='store_true',
            help='Automaticamente mescla fornecedores similares'
        )

    def handle(self, *args, **options):
        pdf_file = options['pdf_file']
        interactive = options['interactive']
        auto_merge = options['auto_merge']
        
        self.stdout.write(self.style.WARNING(f'\n=== IMPORTANDO LICITAÇÃO DE PDF ==='))
        self.stdout.write(f'Arquivo: {pdf_file}\n')
        
        # Extrair dados do PDF
        try:
            extractor = BiddingPDFExtractor(pdf_file)
            data = extractor.extract()
        except Exception as e:
            raise CommandError(f'Erro ao extrair PDF: {e}')
        
        # Mostrar resumo
        self.stdout.write(extractor.get_summary())
        
        if not data['administrative_process']:
            raise CommandError('Não foi possível identificar o processo administrativo no PDF')
        
        # Processar importação
        with transaction.atomic():
            bidding = self._process_bidding(data, interactive)
            suppliers_map = self._process_suppliers(data, interactive, auto_merge)
            materials_created = self._process_materials(data, bidding, suppliers_map, interactive)
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ Importação concluída!'))
            self.stdout.write(f'✓ Licitação: {bidding.name}')
            self.stdout.write(f'✓ Fornecedores: {len(suppliers_map)} processados')
            self.stdout.write(f'✓ Materiais: {materials_created} vinculados')
    
    def _process_bidding(self, data, interactive):
        """Cria ou atualiza licitação."""
        # Procurar licitação existente por processo administrativo
        try:
            bidding = Bidding.objects.get(administrative_process=data['administrative_process'])
            self.stdout.write(self.style.WARNING(f'\n⚠ Licitação já existe: {bidding.name}'))
            
            if interactive:
                response = input('Atualizar dados? [S/n]: ')
                if response.lower() == 'n':
                    return bidding
            
            # Atualizar
            bidding.name = data['bidding_name']
            bidding.modality = data['modality']
            bidding.modality_number = data['modality_number']
            bidding.validity_date = data['validity_date']
            bidding.object_description = data['object_description']
            bidding.save()
            
            self.stdout.write(self.style.SUCCESS('✓ Licitação atualizada'))
            
        except Bidding.DoesNotExist:
            # Criar nova
            bidding = Bidding.objects.create(
                name=data['bidding_name'],
                administrative_process=data['administrative_process'],
                modality=data['modality'],
                modality_number=data['modality_number'],
                validity_date=data['validity_date'],
                object_description=data['object_description'],
                date=datetime.now().date(),
                status='1'
            )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Licitação criada: {bidding.name}'))
        
        return bidding
    
    def _process_suppliers(self, data, interactive, auto_merge):
        """Processa fornecedores do PDF."""
        suppliers_map = {}  # Map: nome_fornecedor -> Supplier object
        
        if not data['suppliers']:
            self.stdout.write(self.style.WARNING('\n⚠ Nenhum fornecedor encontrado no PDF'))
            return suppliers_map
        
        self.stdout.write(f'\n=== PROCESSANDO FORNECEDORES ===')
        
        # Obter fornecedores existentes
        existing_suppliers = list(Supplier.objects.values_list('company', flat=True))
        
        for supplier_name in data['suppliers']:
            self.stdout.write(f'\nFornecedor: {supplier_name}')
            
            # Procurar similares
            similar = find_similar_suppliers(supplier_name, existing_suppliers, threshold=0.8)
            
            if similar:
                self.stdout.write(self.style.WARNING(f'  Fornecedores similares encontrados:'))
                for sim_name, score in similar[:3]:  # Mostrar top 3
                    self.stdout.write(f'    - {sim_name} (similaridade: {score:.0%})')
                
                if interactive:
                    response = input(f'  Usar fornecedor existente "{similar[0][0]}"? [S/n]: ')
                    if response.lower() != 'n':
                        supplier = Supplier.objects.get(company=similar[0][0])
                        # Atualizar nome para padronizar com PDF (apenas se diferente)
                        if supplier.company != supplier_name:
                            supplier.company = supplier_name
                            supplier.save()
                            self.stdout.write(self.style.SUCCESS(f'  ✓ Usando fornecedor existente (nome atualizado)'))
                        else:
                            self.stdout.write(self.style.SUCCESS(f'  ✓ Usando fornecedor existente'))
                        suppliers_map[supplier_name] = supplier
                        continue
                elif auto_merge and similar[0][1] >= 0.9:  # Auto-merge se >90% similar
                    supplier = Supplier.objects.get(company=similar[0][0])
                    # Atualizar nome para padronizar com PDF (apenas se diferente)
                    if supplier.company != supplier_name:
                        supplier.company = supplier_name
                        supplier.save()
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Auto-merge: usando fornecedor existente (nome atualizado)'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Auto-merge: usando fornecedor existente'))
                    suppliers_map[supplier_name] = supplier
                    continue
            
            # Criar novo fornecedor
            if interactive:
                response = input(f'  Criar novo fornecedor "{supplier_name}"? [S/n]: ')
                if response.lower() == 'n':
                    continue
            
            supplier = Supplier.objects.create(company=supplier_name)
            self.stdout.write(self.style.SUCCESS(f'  ✓ Fornecedor criado'))
            suppliers_map[supplier_name] = supplier
        
        return suppliers_map
    
    def _process_materials(self, data, bidding, suppliers_map, interactive):
        """Processa materiais do PDF e cria MaterialBidding."""
        if not data['materials']:
            self.stdout.write(self.style.WARNING('\n⚠ Nenhum material encontrado no PDF'))
            return 0
        
        self.stdout.write(f'\n=== PROCESSANDO MATERIAIS ===')
        self.stdout.write(f'Total de materiais: {len(data["materials"])}')
        
        from bidding_procurement.utils.fuzzy_matcher import find_similar_materials
        
        materials_created = 0
        existing_materials = list(Material.objects.values_list('name', flat=True))
        
        for mat_data in data['materials']:
            description = mat_data['description']
            supplier_name = mat_data['supplier']
            
            # Verificar se fornecedor foi processado
            if supplier_name not in suppliers_map:
                self.stdout.write(self.style.WARNING(f'  ⚠ Fornecedor não encontrado: {supplier_name}'))
                continue
            
            supplier = suppliers_map[supplier_name]
            
            # Procurar material similar
            similar = find_similar_materials(description, existing_materials, threshold=0.9)
            
            if similar and interactive:
                self.stdout.write(f'\nMaterial: {description[:60]}...')
                self.stdout.write(f'  Similar encontrado: {similar[0][0]} ({similar[0][1]:.0%})')
                response = input('  Usar material existente? [S/n]: ')
                if response.lower() != 'n':
                    material = Material.objects.get(name=similar[0][0])
                else:
                    material = Material.objects.create(name=description)
            elif similar and similar[0][1] >= 0.95:  # Auto-merge se >95% similar
                material = Material.objects.get(name=similar[0][0])
            else:
                # Criar novo material
                material = Material.objects.create(name=description)
            
            # Criar ou atualizar MaterialBidding
            mat_bidding, created = MaterialBidding.objects.get_or_create(
                material=material,
                bidding=bidding,
                defaults={
                    'supplier': supplier,
                    'price': mat_data['unit_price'],
                    'quantity': mat_data['quantity'],
                    'status': '1'
                }
            )
            
            if not created:
                # Atualizar se já existe
                mat_bidding.supplier = supplier
                mat_bidding.price = mat_data['unit_price']
                mat_bidding.quantity = mat_data['quantity']
                mat_bidding.save()
            
            materials_created += 1
        
        return materials_created
