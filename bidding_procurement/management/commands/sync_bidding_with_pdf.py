from django.core.management.base import BaseCommand
from django.db import transaction
from bidding_procurement.models import Bidding, MaterialBidding
from bidding_procurement.utils.pdf_extractor import BiddingPDFExtractor


class Command(BaseCommand):
    help = 'Sincroniza licitação com PDF, removendo materiais que não pertencem'

    def add_arguments(self, parser):
        parser.add_argument('pdf_file', type=str, help='Caminho para o arquivo PDF')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem executar'
        )

    def handle(self, *args, **options):
        pdf_file = options['pdf_file']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.WARNING(f'\n=== SINCRONIZANDO COM PDF ==='))
        self.stdout.write(f'Arquivo: {pdf_file}\n')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita\n'))
        
        # Extrair dados do PDF
        try:
            extractor = BiddingPDFExtractor(pdf_file)
            data = extractor.extract()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao extrair PDF: {e}'))
            return
        
        if not data['administrative_process']:
            self.stdout.write(self.style.ERROR('Não foi possível identificar o processo administrativo'))
            return
        
        # Buscar licitação
        try:
            bidding = Bidding.objects.get(administrative_process=data['administrative_process'])
        except Bidding.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Licitação {data["administrative_process"]} não encontrada'))
            return
        
        self.stdout.write(f'Licitação: {bidding.name}')
        
        # Obter materiais atuais
        current_materials = MaterialBidding.objects.filter(bidding=bidding)
        current_count = current_materials.count()
        
        self.stdout.write(f'Materiais no banco: {current_count}')
        self.stdout.write(f'Materiais no PDF: {len(data["materials"])}\n')
        
        # Criar set de códigos de materiais do PDF
        pdf_material_codes = set()
        for mat in data['materials']:
            if mat.get('code'):
                pdf_material_codes.add(mat['code'])
        
        # Identificar materiais que NÃO estão no PDF
        to_remove = []
        for mat_bidding in current_materials:
            # Tentar encontrar código do material
            # (assumindo que o código está na descrição ou em um campo específico)
            material_desc = mat_bidding.material.name
            
            # Procurar código na descrição (formato XXX.XXX.XXX)
            import re
            code_match = re.search(r'(\d{3}\.\d{3}\.\d{3})', material_desc)
            
            if code_match:
                material_code = code_match.group(1)
                if material_code not in pdf_material_codes:
                    to_remove.append(mat_bidding)
            else:
                # Se não tem código, verificar por nome similar
                found = False
                for pdf_mat in data['materials']:
                    if pdf_mat['description'][:50].lower() in material_desc.lower():
                        found = True
                        break
                
                if not found:
                    to_remove.append(mat_bidding)
        
        # Mostrar o que será removido
        if to_remove:
            self.stdout.write(self.style.WARNING(f'\n{len(to_remove)} materiais NÃO encontrados no PDF:'))
            for mat_bidding in to_remove[:10]:  # Mostrar primeiros 10
                self.stdout.write(f'  - {mat_bidding.material.name[:60]}...')
            
            if len(to_remove) > 10:
                self.stdout.write(f'  ... e mais {len(to_remove) - 10} materiais')
            
            if not dry_run:
                response = input('\nRemover estes materiais? [S/n]: ')
                if response.lower() != 'n':
                    with transaction.atomic():
                        for mat_bidding in to_remove:
                            mat_bidding.delete()
                    
                    self.stdout.write(self.style.SUCCESS(f'\n✓ {len(to_remove)} materiais removidos'))
                    self.stdout.write(f'Materiais restantes: {current_count - len(to_remove)}')
                else:
                    self.stdout.write(self.style.WARNING('Operação cancelada'))
            else:
                self.stdout.write(self.style.WARNING(f'\n[DRY-RUN] {len(to_remove)} materiais seriam removidos'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ Todos os materiais estão no PDF'))
            self.stdout.write('Nenhuma ação necessária')
