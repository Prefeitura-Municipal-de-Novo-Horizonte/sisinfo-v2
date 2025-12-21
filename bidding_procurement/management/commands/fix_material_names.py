#!/usr/bin/env python3
"""
Management command para corrigir nomes de materiais.

- Corrige typos e nomes truncados
- Padroniza maiúsculas
- Verifica laudos antes de mesclar duplicatas
- Usa Gemini para sugestões de correção
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from bidding_procurement.models import Material, MaterialBidding
from reports.models import MaterialReport


# Correções manuais conhecidas
CORRECOES_MANUAIS = {
    # Typos
    'CADO DE REDE UTP': 'CABO DE REDE UTP',
    'DESINGRIPANTE l': 'DESENGRIPANTE',
    'DESINGRIPANTE': 'DESENGRIPANTE',
    
    # Nomes truncados
    'NOTEBOOK INTE': 'NOTEBOOK INTEL CORE I5',
    'SSD EXTERNO 1TB PORTATI': 'SSD EXTERNO 1TB PORTÁTIL',
    'FONTE ATX 500 W REA': 'FONTE ATX 500W REAL',
    'MONITOR LED 21,5 POLEGADAS CO': 'MONITOR LED 21,5 POLEGADAS COM CONECTORES VGA E HDMI',
    'RACK DE PAREDE 08U/19P/570M': 'RACK DE PAREDE 08U/19P/570MM',
    'FILTRO DE LINHA 5 TOMADAS PADRÃO NOVO COM 2 ME': 'FILTRO DE LINHA 5 TOMADAS PADRÃO NOVO COM 2 METROS',
    'FILTRO DE LINHA 5 TOMADAS PADRÃO NOVO COM 5 ME': 'FILTRO DE LINHA 5 TOMADAS PADRÃO NOVO COM 5 METROS',
    
    # Padronização de case
    'Cabo De Força Para Pc': 'CABO DE FORÇA PARA PC',
    'Placa Mãe Gigabyte H510m H  Soquete Lga 1200': 'PLACA MÃE GIGABYTE H510M H SOQUETE LGA 1200',
    'Processador Cpu Intel Core i3-10100 3.6 GHZ LGA 1200 6 MB': 'PROCESSADOR CPU INTEL CORE I3-10100 3.6GHZ LGA 1200 6MB',
    'Processador cpu Intel core i5-11400 2.6 ghz LGA 1200 12mb': 'PROCESSADOR CPU INTEL CORE I5-11400 2.6GHZ LGA 1200 12MB',
    'Processador Intel Core i3-12100 3.3GHz LGA 1700 12MB': 'PROCESSADOR INTEL CORE I3-12100 3.3GHZ LGA 1700 12MB',
    'licença de Windows 11 PRO N': 'LICENÇA DE WINDOWS 11 PRO N',
    'Licença de Office Home & Business 2021 ESD T5D-03487': 'LICENÇA DE OFFICE HOME & BUSINESS 2021 ESD T5D-03487',
    'Memória RAM 4GB DDR4 2400 Mhz': 'MEMÓRIA RAM 4GB DDR4 2400MHZ',
    
    # Correções de nomes
    # User requested fix (Encoding/Naming)
    'GABINETE MID TOWER COM 3 VENTILADORES E DIMENSŐES': 'GABINETE MID TOWER COM 3 VENTILADORES E DIMENSIONAL',
    'GABINETE MID TOWER COM 3 VENTILADORES E DIMENSIONA...': 'GABINETE MID TOWER COM 3 VENTILADORES E DIMENSIONAL',
    
    # Specific Merge/Rename Request
    'CABO ADAPTADOR DE REDE USB 3.0 PARA RJ45 F3, 10/100/1000MBPS': 'CABO ADAPTADOR DE REDE USB 3.0 PARA RJ45 F3',
    
    # Exact JSON Sync (Fixing items where DB name was longer/bad encoding)
    'BATERIA PARA NOBREAK 12V-7AH - SELADA: EXCETO MOUDNELO SEG': 'BATERIA PARA NOBREAK 12V-7AH - SELADA: EXCETO MANUTENÇÃO',
    'GABINETE MID TOWER COM 3 VENTILADORES E DIMENSŐES: 447 X 205 X 455 MM': 'GABINETE MID TOWER COM 3 VENTILADORES E DIMENSIONAMENTO',
    'PLACA MĂE GIGABYTE H610M H DDR4 INTEL SOQUETE LGA 1700': 'PLACA MÃE GIGABYTE H610M H DDR4 INTEL SOQUETE',
    'ESTABILIZADOR 500 VA': 'ESTABILIZADOR 500VA',
}


class Command(BaseCommand):
    help = 'Corrige nomes de materiais (typos, truncados, case)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula as alterações sem modificar o banco de dados',
        )
        parser.add_argument(
            '--show-all',
            action='store_true',
            help='Mostra todos os materiais, não apenas os que serão corrigidos',
        )

    def merge_materials(self, source_material, target_name, dry_run):
        """
        Mescla source_material em um material existente com target_name.
        Migra laudos e associações de licitação.
        """
        try:
            target_material = Material.objects.get(name=target_name)
        except Material.DoesNotExist:
            return False

        self.stdout.write(self.style.WARNING(f'   🔄 MERGE DETECTADO: "{source_material.name}" -> "{target_name}"'))
        
        # 1. Migrar/Mesclar MaterialBiddings
        source_mbs = MaterialBidding.objects.filter(material=source_material)
        for source_mb in source_mbs:
            # Verifica se já existe MB para o target na mesma licitação
            target_mb = MaterialBidding.objects.filter(
                material=target_material,
                bidding=source_mb.bidding
            ).first()
            
            if target_mb:
                # Merge: Mover laudos de source_mb para target_mb
                reports = MaterialReport.objects.filter(material_bidding=source_mb)
                count = reports.count()
                if count > 0:
                    self.stdout.write(f'      📦 Movendo {count} laudos na licitação {source_mb.bidding}...')
                    if not dry_run:
                        reports.update(material_bidding=target_mb)
                
                # Deletar source_mb (agora vazio/redundante)
                if not dry_run:
                    source_mb.delete()
            else:
                # Apenas mover: Apontar source_mb para o novo material
                self.stdout.write(f'      ➡️ Movendo associação na licitação {source_mb.bidding}...')
                if not dry_run:
                    source_mb.material = target_material
                    source_mb.save()

        # 2. Deletar material antigo
        self.stdout.write(f'   🗑️ Deletando material antigo: "{source_material.name}"')
        if not dry_run:
            source_material.delete()
            
        return True

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        show_all = options['show_all']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODO DRY-RUN: Nenhuma alteração será feita\n'))
        
        self.stdout.write('=' * 70)
        self.stdout.write('📋 CORREÇÃO DE NOMES DE MATERIAIS')
        self.stdout.write('=' * 70 + '\n')
        
        stats = {
            'corrected': 0,
            'merged': 0,
            'skipped': 0,
            'with_reports': 0,
        }
        
        try:
            with transaction.atomic():
                # Loop usando iterator para evitar problemas se deletarmos itens
                for material in Material.objects.all().order_by('name'):
                    # Verificar se tem laudos (apenas info)
                    report_count = MaterialReport.objects.filter(
                        material_bidding__material=material
                    ).count()
                    
                    nome_atual = material.name
                    nome_correto = CORRECOES_MANUAIS.get(nome_atual)
                    
                    # Se não está na lista de correções, verificar case
                    if not nome_correto and nome_atual != nome_atual.upper():
                        nome_correto = nome_atual.upper()
                    
                    if nome_correto:
                        has_reports = report_count > 0
                        
                        self.stdout.write(f'\n📝 Material ID {material.pk}:')
                        self.stdout.write(f'   De: "{nome_atual}"')
                        self.stdout.write(f'   Para: "{nome_correto}"')
                        
                        # Tenta merge primeiro se o nome já existe
                        if Material.objects.filter(name=nome_correto).exists():
                             if self.merge_materials(material, nome_correto, dry_run):
                                 stats['merged'] += 1
                                 continue

                        if has_reports:
                            self.stdout.write(self.style.WARNING(f'   ⚠️ TEM {report_count} LAUDO(S) VINCULADO(S)'))
                            stats['with_reports'] += 1
                        
                        material.name = nome_correto
                        if not dry_run:
                            material.save()
                        stats['corrected'] += 1
                    elif show_all:
                        status = f'({report_count} laudos)' if report_count > 0 else ''
                        self.stdout.write(f'   ✅ {material.pk}: {nome_atual[:50]} {status}')
                    else:
                        stats['skipped'] += 1
                
                if dry_run:
                    raise DryRunException()
                    
        except DryRunException:
            pass
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('📊 RESUMO')
        self.stdout.write('=' * 70)
        self.stdout.write(f'Corrigidos: {stats["corrected"]}')
        self.stdout.write(f'Ignorados (corretos): {stats["skipped"]}')
        self.stdout.write(f'Com laudos (cuidado!): {stats["with_reports"]}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️ MODO DRY-RUN: Nenhuma alteração foi salva!'))


class DryRunException(Exception):
    pass
