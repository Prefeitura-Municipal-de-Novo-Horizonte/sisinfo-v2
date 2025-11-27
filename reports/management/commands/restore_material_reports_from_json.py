from django.core.management.base import BaseCommand
from reports.models import MaterialReport
from bidding_procurement.models import Material, Bidding, MaterialBidding
import json

class Command(BaseCommand):
    help = 'Restaura dados de MaterialReport de um backup JSON'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Caminho para o arquivo JSON de backup')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        
        self.stdout.write(self.style.WARNING(f'Carregando backup de: {json_file}'))
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Arquivo não encontrado: {json_file}'))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Erro ao ler JSON: {e}'))
            return
        
        # Filtrar apenas MaterialReports
        material_reports_data = [
            item for item in data 
            if item.get('model') == 'reports.materialreport'
        ]
        
        if not material_reports_data:
            self.stdout.write(self.style.ERROR('Nenhum MaterialReport encontrado no JSON!'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Encontrados {len(material_reports_data)} MaterialReports no backup.'))
        
        # Criar licitação legado se não existir
        from datetime import date
        legacy_bidding, _ = Bidding.objects.get_or_create(
            name="Licitação Legado - Migração",
            defaults={'date': date.today(), 'status': '1'}
        )
        
        restored_count = 0
        skipped_count = 0
        error_count = 0
        
        for item in material_reports_data:
            try:
                fields = item['fields']
                pk = item['pk']
                
                # Tentar encontrar o MaterialReport
                try:
                    material_report = MaterialReport.objects.get(pk=pk)
                except MaterialReport.DoesNotExist:
                    skipped_count += 1
                    continue
                
                # Se já tem material_bidding, pular
                if material_report.material_bidding:
                    skipped_count += 1
                    continue
                
                # Pegar o ID do material do backup
                material_id = fields.get('material')
                if not material_id:
                    error_count += 1
                    continue
                
                # Tentar encontrar o material
                try:
                    material = Material.objects.get(pk=material_id)
                except Material.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Material ID {material_id} não encontrado, pulando...'))
                    error_count += 1
                    continue
                
                # Procurar ou criar MaterialBidding
                material_bidding = MaterialBidding.objects.filter(material=material).first()
                
                if not material_bidding:
                    # Criar novo MaterialBidding vinculado à licitação legado
                    material_bidding = MaterialBidding.objects.create(
                        material=material,
                        bidding=legacy_bidding,
                        status='1',
                        price=fields.get('unitary_price', 0) or 0,
                        readjustment=0
                    )
                
                # Atualizar MaterialReport
                material_report.material_bidding = material_bidding
                material_report.save()
                restored_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro ao processar item {item.get("pk")}: {e}'))
                error_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n=== RESUMO ==='))
        self.stdout.write(self.style.SUCCESS(f'Restaurados: {restored_count}'))
        self.stdout.write(self.style.WARNING(f'Pulados (já tinham material_bidding): {skipped_count}'))
        self.stdout.write(self.style.ERROR(f'Erros: {error_count}'))
