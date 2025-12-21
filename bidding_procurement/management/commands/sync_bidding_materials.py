#!/usr/bin/env python3
"""
Management command para sincronizar MaterialBiddings com os JSONs das licitações.

Este script:
1. Lê os JSONs das licitações extraídas
2. Remove MaterialBiddings duplicados (qty=0) migrando laudos
3. Atualiza nomes e quantidades dos MaterialBiddings existentes
4. Cria novos MaterialBiddings para itens que não existem

O JSON é a FONTE ÚNICA DE VERDADE para nomes e quantidades.
"""

import json
import os
from difflib import SequenceMatcher
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from bidding_procurement.models import Material, MaterialBidding, Bidding
from bidding_supplier.models import Supplier
from reports.models import MaterialReport


class Command(BaseCommand):
    help = 'Sincroniza MaterialBiddings com JSONs das licitações (fonte única de verdade)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula as alterações sem modificar o banco de dados',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODO DRY-RUN: Nenhuma alteração será feita\n'))
        
        self.stdout.write('=' * 70)
        self.stdout.write('🔄 SINCRONIZAÇÃO DE MATERIAIS COM JSONs')
        self.stdout.write('=' * 70 + '\n')
        
        # Diretório dos JSONs
        json_dir = Path(settings.BASE_DIR) / 'docs' / 'licitacoes-extraidas'
        
        stats = {
            'reports_migrated': 0,
            'mb_deleted': 0,
            'mb_created': 0,
            'mb_updated': 0,
            'materials_created': 0,
            'names_fixed': 0,
        }
        
        try:
            with transaction.atomic():
                # Processar cada JSON
                for json_file in sorted(json_dir.glob('licitacao-*.json')):
                    self.process_json(json_file, stats, dry_run)
                
                if dry_run:
                    raise DryRunException()
                    
        except DryRunException:
            pass
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('📊 RESUMO')
        self.stdout.write('=' * 70)
        self.stdout.write(f'Laudos migrados: {stats["reports_migrated"]}')
        self.stdout.write(f'MaterialBiddings removidos: {stats["mb_deleted"]}')
        self.stdout.write(f'MaterialBiddings criados: {stats["mb_created"]}')
        self.stdout.write(f'MaterialBiddings atualizados: {stats["mb_updated"]}')
        self.stdout.write(f'Materiais criados: {stats["materials_created"]}')
        self.stdout.write(f'Nomes corrigidos: {stats["names_fixed"]}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️ MODO DRY-RUN: Nenhuma alteração foi salva!'))

    def process_json(self, json_file, stats, dry_run):
        """Processa um arquivo JSON de licitação."""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        num_licitacao = data.get('numero_licitacao', '')
        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(f'📂 Processando: {json_file.name} ({num_licitacao})')
        self.stdout.write(f'{"="*60}')
        
        # Encontrar licitação
        bidding = self.find_bidding(num_licitacao, data.get('objeto', ''))
        if not bidding:
            self.stdout.write(self.style.WARNING(f'   ⚠️ Licitação não encontrada: {num_licitacao}'))
            return
        
        self.stdout.write(f'   ✅ Licitação: {bidding.name} (ID: {bidding.pk})')
        
        touched_mb_ids = set()
        
        # Processar cada item do JSON
        for item in data.get('itens', []):
            mb_id = self.process_item(item, bidding, stats, dry_run)
            if mb_id:
                touched_mb_ids.add(mb_id)
        
        # Limpar órfãos (itens q não estão no JSON e tem qty=0)
        self.cleanup_orphans(bidding, touched_mb_ids, stats, dry_run)

    def cleanup_orphans(self, bidding, touched_ids, stats, dry_run):
        """
        Remove itens do banco que não estão no JSON.
        Se o item não foi 'tocado' (touched_ids), significa que não está no JSON.
        """
        orphans = MaterialBidding.objects.filter(bidding=bidding).exclude(pk__in=touched_ids)
        
        for orphan in orphans:
            reports = MaterialReport.objects.filter(material_bidding=orphan)
            report_count = reports.count()
            
            if report_count > 0:
                self.stdout.write(self.style.WARNING(f'   ⚠️ ÓRFÃO COM LAUDOS: {orphan.material.name[:40]}... (qty={orphan.quantity}, {report_count} laudos) - REMOVENDO TUDO (STRICT SYNC)'))
                if not dry_run:
                    # Deletar laudos primeiro para evitar Proteção do Signal
                    reports.delete()
            
            self.stdout.write(f'   🗑️ Removendo excedente (não está no JSON): {orphan.material.name[:40]}... (qty={orphan.quantity})')
            material = orphan.material
            if not dry_run:
                orphan.delete()
                # Remover material órfão se não usado em outras licitações
                if not MaterialBidding.objects.filter(material=material).exists():
                    material.delete()
            stats['mb_deleted'] += 1

    def find_bidding(self, numero, objeto):
        """Encontra a licitação pelo número."""
        # Extrair número curto (ex: "121/25" de "000121/25")
        import re
        match = re.search(r'(\d+)/(\d+)', numero)
        if match:
            num, ano = match.groups()
            num_short = f"{int(num)}/{ano}"
            # Buscar por nome que contenha o número
            bidding = Bidding.objects.filter(name__icontains=num_short).first()
            if bidding:
                return bidding
        return None

    def process_item(self, item, bidding, stats, dry_run):
        """Processa um item do JSON."""
        descricao = item.get('descricao', '').strip()
        quantidade = item.get('quantidade', 0)
        valor_unitario = item.get('valor_unitario', 0)
        unidade = item.get('unidade', 'UN')
        marca = item.get('marca', '')
        fornecedor_data = item.get('fornecedor', {})
        
        if not descricao:
            return None
        
        # Buscar fornecedor
        supplier = None
        if fornecedor_data.get('razao_social'):
            supplier = Supplier.objects.filter(
                company__icontains=fornecedor_data['razao_social'][:30]
            ).first()
        
        # Buscar MaterialBidding existente
        existing_mb = self.find_existing_mb(descricao, bidding)
        
        resulting_mb = None
        
        if existing_mb:
            # Atualizar existente
            if existing_mb.quantity != quantidade or existing_mb.price != valor_unitario:
                self.stdout.write(f'\n📝 Atualizando: {descricao[:50]}...')
                if existing_mb.quantity != quantidade:
                    self.stdout.write(f'   Quantidade: {existing_mb.quantity} → {quantidade}')
                if existing_mb.price != valor_unitario:
                    self.stdout.write(f'   Preço: R$ {existing_mb.price} → R$ {valor_unitario}')
                
                if not dry_run:
                    existing_mb.quantity = quantidade
                    existing_mb.price = valor_unitario
                    existing_mb.brand = marca or existing_mb.brand
                    if supplier:
                        existing_mb.supplier = supplier
                    existing_mb.save()
                stats['mb_updated'] += 1
            
            # Verificar se nome do Material precisa de correção
            if existing_mb.material.name.upper() != descricao.upper():
                old_name = existing_mb.material.name
                # Só atualizar se o novo nome é mais completo
                if len(descricao) >= len(old_name):
                    self.stdout.write(f'   📝 Nome: "{old_name[:40]}..." → "{descricao[:40]}..."')
                    if not dry_run:
                        existing_mb.material.name = descricao
                        existing_mb.material.unit = unidade
                        existing_mb.material.save()
                    stats['names_fixed'] += 1
            
            # Verificar duplicados com qty=0
            self.handle_duplicates(descricao, bidding, existing_mb, stats, dry_run)
            resulting_mb = existing_mb
        else:
            # Criar novo MaterialBidding
            self.stdout.write(f'\n✨ Criando: {descricao[:50]}...')
            self.stdout.write(f'   Quantidade: {quantidade}, Preço: R$ {valor_unitario}')
            
            # Buscar ou criar Material
            material = Material.objects.filter(name__iexact=descricao).first()
            if not material:
                if not dry_run:
                    material = Material.objects.create(
                        name=descricao,
                        unit=unidade
                    )
                    stats['materials_created'] += 1
                else:
                    self.stdout.write(f'   [dry-run] Criaria novo Material')
                    stats['materials_created'] += 1
            
            if not dry_run and material:
                resulting_mb = MaterialBidding.objects.create(
                    material=material,
                    bidding=bidding,
                    supplier=supplier,
                    quantity=quantidade,
                    price=valor_unitario,
                    brand=marca
                )
            stats['mb_created'] += 1
            
        return resulting_mb.pk if resulting_mb else None

    def normalize_name(self, name):
        """
        Normaliza nome para comparação, tratando:
        - Encoding (MĂE → MÃE)
        - Espaços em especificações (500 VA → 500VA)
        - Espaços em códigos (RJ 45 → RJ45, CAT 5E → CAT5E)
        - Case
        """
        import re
        import unicodedata
        
        # Normalizar unicode (NFKC combina caracteres compostos)
        normalized = unicodedata.normalize('NFKC', name.upper())
        
        # Corrigir encoding quebrado comum
        replacements = {
            'MĂ': 'MÃ',
            'Ă': 'Ã',
            'Ç': 'Ç',
            'Ő': 'Õ',
            'Ű': 'Ü',
            'DIMENSŐES': 'DIMENSIONAMENTO',
            'DIMENSIONA...': 'DIMENSIONAMENTO',
        }
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Remover espaços antes de unidades/specs numéricas
        normalized = re.sub(r'(\d+)\s*(VA|W|GB|TB|MB|MHZ|V|AH?|PORTAS?)\b', r'\1\2', normalized)
        
        # Normalizar códigos comuns (RJ 45 → RJ45, CAT 5E → CAT5E)
        normalized = re.sub(r'RJ\s*45', 'RJ45', normalized)
        normalized = re.sub(r'CAT\s*(\d+)\s*([E]?)', r'CAT\1\2', normalized)
        normalized = re.sub(r'USB\s*(\d+\.?\d*)', r'USB\1', normalized)
        
        # Remover múltiplos espaços
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized

    def find_existing_mb(self, descricao, bidding):
        """Busca MaterialBidding existente com nome similar."""
        import re
        
        def extract_specs(text):
            """Extrai especificações do nome para comparação."""
            patterns = [
                r'\d+\s*VA',       # 500VA
                r'\d+\s*W\b',      # 500W
                r'\d+\s*GB',       # 8GB
                r'\d+\s*TB',       # 1TB
                r'\d+\s*MB',       # 512MB
                r'\d+\s*MHZ',      # 2666 MHZ
                r'\d+\s*V\b',      # 12V
                r'\d+\s*AH?',      # 7AH
                r'\d+\s*PORTAS?',  # 16 PORTAS
                r'\d+\s*METROS?',  # 305 METROS
                r'DDR\d',          # DDR4, DDR5
                r'CAT\s*\d+\s*E?', # CAT5E, CAT6, CAT 5E
                r'RJ\s*45',        # RJ45, RJ 45
            ]
            specs = []
            text_upper = text.upper()
            for pattern in patterns:
                matches = re.findall(pattern, text_upper)
                # Normalizar espaços
                specs.extend([re.sub(r'\s+', '', m) for m in matches])
            return set(specs)
        
        descricao_norm = self.normalize_name(descricao)
        specs_json = extract_specs(descricao)
        
        # Ordenar por quantidade DESC para priorizar o que tem quantidade
        for mb in MaterialBidding.objects.filter(bidding=bidding).order_by('-quantity'):
            name_db = mb.material.name
            name_db_norm = self.normalize_name(name_db)
            specs_db = extract_specs(name_db)
            
            # Strict Spec Check:
            # Se as especificações extraídas forem diferentes, trata como materiais distintos
            # Isso evita que "Cabo UTP" (sem specs) faça merge com "Cabo UTP CAT6E" (com specs)
            if specs_json != specs_db:
                continue
            
            # Nome exato normalizado
            if name_db_norm == descricao_norm:
                return mb
            
            # Um contém o outro (normalizado)
            if name_db_norm in descricao_norm or descricao_norm in name_db_norm:
                return mb
            
            # Primeiras 4 palavras iguais (normalizado)
            words_db = name_db_norm.split()[:4]
            words_json = descricao_norm.split()[:4]
            if words_db == words_json:
                return mb
            
            # Similaridade alta (normalizado)
            ratio = SequenceMatcher(None, name_db_norm, descricao_norm).ratio()
            if ratio >= 0.9:
                return mb
        
        return None



    def handle_duplicates(self, descricao, bidding, correct_mb, stats, dry_run):
        """Remove duplicados com qty=0, migrando laudos para o correto."""
        import re
        
        def extract_specs(text):
            """Extrai especificações numéricas do nome."""
            patterns = [
                r'\d+\s*VA',      # 500VA, 2000 VA
                r'\d+\s*W\b',     # 500W, 450 W
                r'\d+\s*GB',      # 8GB, 16 GB
                r'\d+\s*TB',      # 1TB
                r'\d+\s*MB',      # 512MB
                r'\d+\s*MHZ',     # 2666 MHZ
                r'\d+\s*V\b',     # 12V, 48V
                r'\d+\s*AH?',     # 7AH, 18A
                r'\d+\s*PORTAS?', # 16 PORTAS, 8 PORTAS
                r'\d+,?\d*\s*POLEGADAS?',  # 21,5 POLEGADAS
                r'DDR\d',         # DDR4, DDR5
                r'CAT\d+E?',      # CAT5E, CAT6
                r'i\d-\d+',       # i5-12400
            ]
            specs = []
            text_upper = text.upper()
            for pattern in patterns:
                matches = re.findall(pattern, text_upper)
                specs.extend(matches)
            return set(specs)
        
        specs_json = extract_specs(descricao)
        descricao_norm = self.normalize_name(descricao)
        
        # Buscar todos os MaterialBiddings similares nesta licitação
        for mb in MaterialBidding.objects.filter(bidding=bidding):
            if mb.pk == correct_mb.pk:
                continue
            
            name_db = mb.material.name
            name_db_norm = self.normalize_name(name_db)
            specs_db = extract_specs(name_db)
            
            # Se ambos têm specs, elas devem ser EXATAMENTE iguais para considerar duplicado
            if specs_json and specs_db:
                if specs_json != specs_db:
                    continue  # Especificações diferentes, NÃO é duplicado
            
            # Verificar se é duplicado (nome similar usando normalização)
            is_duplicate = False
            if name_db_norm in descricao_norm or descricao_norm in name_db_norm:
                is_duplicate = True
            elif SequenceMatcher(None, name_db_norm, descricao_norm).ratio() >= 0.85:
                is_duplicate = True
            
            if is_duplicate and mb.quantity == 0:
                # Migrar laudos
                reports = MaterialReport.objects.filter(material_bidding=mb)
                report_count = reports.count()
                
                if report_count > 0:
                    self.stdout.write(f'   🔄 Migrando {report_count} laudo(s) de "{mb.material.name[:30]}..."')
                    if not dry_run:
                        reports.update(material_bidding=correct_mb)
                    stats['reports_migrated'] += report_count
                
                # Remover duplicado
                self.stdout.write(f'   🗑️ Removendo duplicado: {mb.material.name[:40]}... (qty=0)')
                material = mb.material
                if not dry_run:
                    mb.delete()
                    # Remover material órfão
                    if not MaterialBidding.objects.filter(material=material).exists():
                        material.delete()
                stats['mb_deleted'] += 1


class DryRunException(Exception):
    pass
