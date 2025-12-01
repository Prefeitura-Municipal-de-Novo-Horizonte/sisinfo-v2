from django.core.management.base import BaseCommand
from django.db import transaction
from bidding_procurement.models import Bidding, MaterialBidding, Material
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

    def normalize_text(self, text):
        import unicodedata
        import re
        if not text:
            return ""
        # Remove accents
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        # Lowercase
        text = text.lower()
        # Remove special chars (keep numbers and letters)
        text = re.sub(r'[^a-z0-9\s]', '', text)
        # Remove extra spaces
        return ' '.join(text.split())

    def handle(self, *args, **options):
        from difflib import SequenceMatcher
        
        pdf_file = options['pdf_file']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.WARNING(f'\n=== SINCRONIZANDO COM PDF (SMART SYNC) ==='))
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
        
        # Criar mapa de códigos do PDF para verificação rápida
        pdf_material_map = {mat['code']: mat for mat in data['materials'] if mat.get('code')}
        
        to_remove = []
        to_update = []
        to_create = []
        matched_pdf_codes = set()
        matched_pdf_ids = set()

        for mat_bidding in current_materials:
            material_desc = mat_bidding.material.name
            
            # 1. Tentar encontrar código no nome do material (XXX.XXX.XXX)
            import re
            code_match = re.search(r'(\d{3}\.\d{3}\.\d{3})', material_desc)
            
            match_found = None
            
            if code_match:
                material_code = code_match.group(1)
                if material_code in pdf_material_map:
                    match_found = pdf_material_map[material_code]
            
            # 2. Se não achou por código, tentar Fuzzy Match no nome
            if not match_found:
                db_name_norm = self.normalize_text(material_desc)
                best_ratio = 0.0
                
                for pdf_mat in data['materials']:
                    pdf_desc_norm = self.normalize_text(pdf_mat['description'])
                    
                    # Verificar se um contém o outro
                    if db_name_norm in pdf_desc_norm or pdf_desc_norm in db_name_norm:
                        match_found = pdf_mat
                        best_ratio = 1.0
                        break
                    
                    # Verificar similaridade
                    ratio = SequenceMatcher(None, db_name_norm, pdf_desc_norm).ratio()
                    if ratio > 0.85 and ratio > best_ratio:
                        best_ratio = ratio
                        match_found = pdf_mat
            
            if match_found:
                # Material encontrado! Verificar se precisa atualizar o nome
                matched_pdf_codes.add(match_found.get('code'))
                matched_pdf_ids.add(id(match_found)) # Track the ID of the matched PDF material dict
                
                # User requested to keep only the name without the code
                new_name = match_found['description']
                if mat_bidding.material.name != new_name:
                    to_update.append((mat_bidding, new_name))
            else:
                # Material não encontrado de jeito nenhum
                to_remove.append(mat_bidding)

        # Processar Atualizações
        if to_update:
            self.stdout.write(self.style.SUCCESS(f'\n{len(to_update)} materiais serão ATUALIZADOS (Correção de nome/código):'))
            for item in to_update[:5]:
                self.stdout.write(f'  - DE: {item[0].material.name[:40]}...')
                self.stdout.write(f'    PARA: {item[1][:40]}...')
            if len(to_update) > 5:
                self.stdout.write(f'    ... e mais {len(to_update) - 5}')

            if not dry_run:
                if input('\nConfirmar atualizações? [S/n]: ').lower() != 'n':
                    with transaction.atomic():
                        for mat_bidding, new_name in to_update:
                            mat_bidding.material.name = new_name
                            mat_bidding.material.save()
                    self.stdout.write(self.style.SUCCESS('✓ Materiais atualizados'))

        # 3. Identificar materiais que estão no PDF mas NÃO no banco (para criar)
        to_create = []
        for pdf_mat in data['materials']:
            # Verificar se este material do PDF foi "casado" com algum do banco
            # Usamos o ID do objeto dict para garantir que é exatamente o mesmo item processado antes
            if id(pdf_mat) not in matched_pdf_ids:
                to_create.append(pdf_mat)

        # Processar Criações
        if to_create:
            self.stdout.write(self.style.SUCCESS(f'\n{len(to_create)} materiais NOVOS encontrados no PDF (serão criados):'))
            for item in to_create[:5]:
                code = item.get('code', 'S/C')
                desc = item.get('description', '')[:50]
                self.stdout.write(f'  - {code} - {desc}...')
            if len(to_create) > 5:
                self.stdout.write(f'    ... e mais {len(to_create) - 5}')

            if not dry_run:
                if input('\nConfirmar criação? [S/n]: ').lower() != 'n':
                    with transaction.atomic():
                        # from bidding_procurement.models import Material, MaterialBidding (Already imported globally)
                        count_created = 0
                        for item in to_create:
                            # Criar Material
                            # User requested name without code
                            name = item['description']
                            
                            # Verificar se Material já existe (pode estar em outra licitação)
                            material, created = Material.objects.get_or_create(
                                name=name,
                                defaults={'slug': ''} # Slug é gerado no save
                            )
                            
                            # Criar MaterialBidding
                            MaterialBidding.objects.create(
                                material=material,
                                bidding=bidding,
                                status='1',
                                price=item.get('unit_price', 0),
                                quantity=item.get('quantity', 0),
                                readjustment=0
                            )
                            count_created += 1
                            
                    self.stdout.write(self.style.SUCCESS(f'✓ {count_created} materiais criados'))

        # Processar Remoções
        if to_remove:
            self.stdout.write(self.style.WARNING(f'\n{len(to_remove)} materiais NÃO encontrados no PDF (serão removidos):'))
            for mat_bidding in to_remove[:10]:
                self.stdout.write(f'  - {mat_bidding.material.name[:60]}...')
            
            # Verificar uso em Laudos (Reports)
            safe_to_remove = []
            unsafe_to_remove = []
            
            for mb in to_remove:
                # Verificar se existe MaterialReport apontando para este MaterialBidding
                # Nota: O modelo MaterialReport tem FK para MaterialBidding (related_name='materiais_laudos')
                if hasattr(mb, 'materiais_laudos') and mb.materiais_laudos.exists():
                    unsafe_to_remove.append(mb)
                else:
                    safe_to_remove.append(mb)

            if unsafe_to_remove:
                self.stdout.write(self.style.ERROR(f'\nATENÇÃO: {len(unsafe_to_remove)} materiais estão em uso em LAUDOS e NÃO serão removidos automaticamente:'))
                for mb in unsafe_to_remove[:5]:
                    self.stdout.write(f'  - {mb.material.name} (ID: {mb.id})')
            
            if safe_to_remove:
                if not dry_run:
                    response = input(f'\nRemover {len(safe_to_remove)} materiais seguros? [S/n]: ')
                    if response.lower() != 'n':
                        with transaction.atomic():
                            for mat_bidding in safe_to_remove:
                                mat_bidding.delete()
                        self.stdout.write(self.style.SUCCESS(f'✓ {len(safe_to_remove)} materiais removidos'))
                else:
                    self.stdout.write(self.style.WARNING(f'[DRY-RUN] {len(safe_to_remove)} materiais seriam removidos'))
        
        if not to_update and not to_create and not to_remove:
            self.stdout.write(self.style.SUCCESS('\n✓ Tudo sincronizado! Nenhuma ação necessária.'))
