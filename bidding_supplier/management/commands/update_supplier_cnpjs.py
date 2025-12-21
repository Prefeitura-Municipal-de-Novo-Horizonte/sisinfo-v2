#!/usr/bin/env python3
"""
Management command para atualizar dados dos fornecedores.

Usa dados pesquisados na web para:
- Corrigir CNPJs duplicados/errados
- Adicionar endereços
- Adicionar contatos (telefone, email)
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from bidding_supplier.models import Supplier, Contact


# Dados completos dos fornecedores (buscados na web)
FORNECEDORES_DADOS = {
    'DIGIART INFORMATICA NOVO HORIZONTE LTDA': {
        'cnpj': '02228550000198',
        'trade': 'DIGIART INFORMATICA',
        'address': 'Rua Dr. Altino Arantes, 761 - Centro, Novo Horizonte/SP - CEP 14960-000',
        'phone': None,
        'email': None,
    },
    'PROSUN INFORMATICA LTDA': {
        'cnpj': '60023231000142',
        'trade': 'PROSUN',
        'address': 'Av. Sampaio Vidal, 299A - Centro, Marília/SP - CEP 17500-020',
        'phone': '(14) 3402-1010',
        'email': 'prosun@prosun.com.br',
    },
    'LEGACY DISTRIBUIDORA DE INFORMATICA E EL': {
        'cnpj': '52504817000109',
        'trade': 'LEGACY',
        'address': 'Av. Liberdade, 3230 - Galpão G3 - Centro, Bayeux/PB - CEP 58111-400',
        'phone': None,
        'email': None,
    },
    'ACSMA COMERCIO LTDA': {
        'cnpj': '04001695000187',
        'trade': 'ACSMA',
        'address': 'São Paulo/SP',
        'phone': None,
        'email': None,
    },
    'SINCES TECNOLOGIA COMERCIO E SERVICOS LT': {
        'cnpj': '33615509000106',
        'trade': 'SINCES TECNOLOGIA',
        'address': 'Ribeirão Preto/SP',
        'phone': None,
        'email': None,
    },
    'CHERUBINI INFORMÁTICA ME': {
        'cnpj': '33112901000124',
        'trade': 'CHERUBINI INFORMATICA',
        'address': None,
        'phone': None,
        'email': None,
    },
    'INFOSAT GAMERS LTDA': {
        'cnpj': '48147534000171',
        'trade': 'INFOSAT GAMERS',
        'address': None,
        'phone': None,
        'email': None,
    },
    'REI DOS CARTUCHOS EQUIPAMENTOS E SUPRIME': {
        'cnpj': '04500648000188',
        'trade': 'MOGITECH INFORMATICA',
        'address': 'Mogi das Cruzes/SP',
        'phone': None,
        'email': None,
    },
    'RIO PRETO DISTRIBUICAO DE EQUIPAMENTOS D': {
        'cnpj': '33937002000160',
        'trade': 'RIO PRETO DISTRIBUICAO',
        'address': 'São José do Rio Preto/SP',
        'phone': None,
        'email': None,
    },
    'CENTER COPY INFORMÁTICA LTDA ME': {
        'cnpj': '11268379000131',
        'trade': 'CENTER COPY',
        'address': 'Rua Dr. Valentim Gentil, 140 - Centro, Borborema/SP - CEP 14955-000',
        'phone': '(16) 3266-2593',
        'email': 'center-copy@hotmail.com',
    },
    'LLX DISTRIBUIDORA LTDA': {
        'cnpj': '43696821000117',
        'trade': 'LLX DISTRIBUIDORA',
        'address': None,
        'phone': None,
        'email': None,
    },
    'EXATA COMERCIO DE EQUIPAMENTOS E ELETRON': {
        'cnpj': '45864530000116',
        'trade': 'EXATA COMERCIO',
        'address': None,
        'phone': None,
        'email': None,
    },
    'T. GUIMARAES - INFORMATICA': {
        'cnpj': '07274334000100',
        'trade': 'GUIMALL SOLUCOES',
        'address': 'R 01, 490-A - Jardim Parisi, Orlândia/SP - CEP 14620-000',
        'phone': '(16) 3826-5688',
        'email': None,
    },
    'MAC COPIADORA E COMERCIO DE EQUIPAMENTOS': {
        'cnpj': '24501724000187',
        'trade': 'MAC COPIADORA',
        'address': None,
        'phone': None,
        'email': None,
    },
}


class Command(BaseCommand):
    help = 'Atualiza dados dos fornecedores (CNPJ, endereço, contatos)'

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
        
        self.stdout.write('=' * 60)
        self.stdout.write('📋 ATUALIZANDO DADOS DOS FORNECEDORES')
        self.stdout.write('=' * 60 + '\n')
        
        stats = {
            'cnpj_updated': 0,
            'address_updated': 0,
            'contacts_added': 0,
            'not_found': 0,
        }
        
        try:
            with transaction.atomic():
                for supplier in Supplier.objects.all():
                    # Buscar por nome exato ou parcial
                    dados = None
                    for nome, d in FORNECEDORES_DADOS.items():
                        if supplier.company.upper().startswith(nome[:30]):
                            dados = d
                            break
                    
                    if not dados:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️ Não encontrado: {supplier.company}')
                        )
                        stats['not_found'] += 1
                        continue
                    
                    updated = False
                    
                    # Atualizar CNPJ
                    if dados['cnpj'] and supplier.cnpj != dados['cnpj']:
                        self.stdout.write(f'📝 {supplier.company[:40]}')
                        self.stdout.write(f'   CNPJ: {supplier.cnpj or "VAZIO"} → {dados["cnpj"]}')
                        supplier.cnpj = dados['cnpj']
                        stats['cnpj_updated'] += 1
                        updated = True
                    
                    # Atualizar nome fantasia se diferente
                    if dados.get('trade') and supplier.trade != dados['trade']:
                        if not updated:
                            self.stdout.write(f'📝 {supplier.company[:40]}')
                        self.stdout.write(f'   Nome Fantasia: {supplier.trade} → {dados["trade"]}')
                        supplier.trade = dados['trade']
                        updated = True
                    
                    # Atualizar endereço
                    if dados.get('address') and supplier.address != dados['address']:
                        if not updated:
                            self.stdout.write(f'📝 {supplier.company[:40]}')
                        self.stdout.write(f'   Endereço: {dados["address"][:50]}...')
                        supplier.address = dados['address']
                        stats['address_updated'] += 1
                        updated = True
                    
                    if updated and not dry_run:
                        supplier.save()
                    
                    # Adicionar contatos (telefone e email)
                    if dados.get('phone'):
                        # Verificar se já existe
                        exists = Contact.objects.filter(
                            supplier=supplier,
                            kind=Contact.PHONE,
                            value=dados['phone']
                        ).exists()
                        if not exists:
                            self.stdout.write(f'   📞 Telefone: {dados["phone"]}')
                            if not dry_run:
                                Contact.objects.create(
                                    supplier=supplier,
                                    kind=Contact.PHONE,
                                    value=dados['phone']
                                )
                            stats['contacts_added'] += 1
                    
                    if dados.get('email'):
                        exists = Contact.objects.filter(
                            supplier=supplier,
                            kind=Contact.EMAIL,
                            value=dados['email']
                        ).exists()
                        if not exists:
                            self.stdout.write(f'   📧 Email: {dados["email"]}')
                            if not dry_run:
                                Contact.objects.create(
                                    supplier=supplier,
                                    kind=Contact.EMAIL,
                                    value=dados['email']
                                )
                            stats['contacts_added'] += 1
                
                if dry_run:
                    raise DryRunException()
                    
        except DryRunException:
            pass
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('📊 RESUMO')
        self.stdout.write('=' * 60)
        self.stdout.write(f'CNPJs atualizados: {stats["cnpj_updated"]}')
        self.stdout.write(f'Endereços atualizados: {stats["address_updated"]}')
        self.stdout.write(f'Contatos adicionados: {stats["contacts_added"]}')
        self.stdout.write(f'Não encontrados: {stats["not_found"]}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️ MODO DRY-RUN: Nenhuma alteração foi salva!'))


class DryRunException(Exception):
    pass
