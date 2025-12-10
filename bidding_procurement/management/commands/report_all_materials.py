"""
Comando para gerar relatório completo de todos os materiais.

Mostra:
- Material
- Usado em laudos? (Sim/Não)
- Licitações onde aparece
- Fornecedores
- Status de uso
"""
from django.core.management.base import BaseCommand
from bidding_procurement.models import Material, MaterialBidding
from reports.models import MaterialReport
import csv


class Command(BaseCommand):
    help = 'Gera relatório completo de todos os materiais'

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, default='relatorio_materiais_completo.csv')

    def handle(self, *args, **options):
        output_file = options['output']

        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('RELATÓRIO COMPLETO DE MATERIAIS'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))

        # Todos os materiais
        all_materials = Material.objects.all().order_by('name')
        
        relatorio = []
        
        for material in all_materials:
            # Verificar laudos
            laudos = MaterialReport.objects.filter(
                material_bidding__material=material
            ).count()
            
            # Buscar MaterialBiddings
            mbs = MaterialBidding.objects.filter(material=material).select_related(
                'bidding', 'supplier'
            )
            
            # Licitações
            licitacoes = []
            fornecedores = []
            total_quantidade = 0
            total_valor = 0
            
            for mb in mbs:
                bid_name = mb.bidding.administrative_process or mb.bidding.name
                licitacoes.append(bid_name)
                
                if mb.supplier:
                    fornecedores.append(mb.supplier.trade or mb.supplier.company)
                
                total_quantidade += mb.quantity or 0
                total_valor += (mb.quantity or 0) * (mb.price or 0)
            
            # Status
            if laudos > 0:
                status = 'EM_USO_LAUDOS'
            elif mbs.exists():
                status = 'EM_USO_LICITACOES'
            else:
                status = 'NAO_USADO'
            
            relatorio.append({
                'id': material.id,
                'nome': material.name,
                'marca': material.brand or '',
                'unidade': material.unit or '',
                'status': status,
                'laudos_count': laudos,
                'licitacoes': ', '.join(set(licitacoes)) if licitacoes else '',
                'fornecedores': ', '.join(set(fornecedores)) if fornecedores else '',
                'quantidade_total': total_quantidade,
                'valor_total': f'{total_valor:.2f}',
                'num_licitacoes': len(set(licitacoes))
            })

        # Salvar CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if relatorio:
                writer = csv.DictWriter(f, fieldnames=relatorio[0].keys())
                writer.writeheader()
                writer.writerows(relatorio)

        # Estatísticas
        em_uso_laudos = sum(1 for r in relatorio if r['status'] == 'EM_USO_LAUDOS')
        em_uso_licitacoes = sum(1 for r in relatorio if r['status'] == 'EM_USO_LICITACOES')
        nao_usados = sum(1 for r in relatorio if r['status'] == 'NAO_USADO')
        
        # Materiais nas licitações específicas
        mat_121 = sum(1 for r in relatorio if '121/2025' in r['licitacoes'])
        mat_223 = sum(1 for r in relatorio if '223/2025' in r['licitacoes'])

        self.stdout.write('\n' + '='*80)
        self.stdout.write('ESTATÍSTICAS')
        self.stdout.write('='*80)
        self.stdout.write(f'\n📦 Total de materiais: {len(relatorio)}')
        self.stdout.write(f'\n✅ Em uso (laudos): {em_uso_laudos}')
        self.stdout.write(f'✅ Em uso (licitações): {em_uso_licitacoes}')
        self.stdout.write(f'⚠️  Não usados: {nao_usados}')
        self.stdout.write(f'\n📋 Licitação 121/2025: {mat_121} materiais')
        self.stdout.write(f'📋 Licitação 223/2025: {mat_223} materiais')
        self.stdout.write(f'\n📄 Relatório salvo em: {output_file}\n')
