#!/usr/bin/env python
"""
Script para verificar materiais duplicados no banco de dados.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db.models import Count
from dashboard.models import Material

# Buscar materiais com nomes duplicados
duplicates = Material.objects.values('name', 'supplier__trade').annotate(
    total=Count('id')
).filter(total__gt=1).order_by('-total')

print("=" * 80)
print("ANÁLISE DE MATERIAIS DUPLICADOS")
print("=" * 80)
print()

if duplicates:
    print(f"✗ Encontrados {len(duplicates)} materiais com nomes duplicados:\n")
    
    for index, dup in enumerate(duplicates[:30], 1):  # Mostra os 30 primeiros
        supplier = dup['supplier__trade'] or "Sem fornecedor"
        print(f"{index}. '{dup['name']}' ({supplier}): {dup['total']} ocorrências")
    
    if len(duplicates) > 30:
        print(f"\n... e mais {len(duplicates) - 30} duplicatas")
    
    print(f"\n{'=' * 80}")
    print("DETALHES DAS DUPLICATAS (top 5):")
    print("=" * 80)
    
    for index, dup in enumerate(duplicates[:5], 1):
        print(f"\n{index}. Material: '{dup['name']}'")
        materials = Material.objects.filter(
            name=dup['name'],
            supplier__trade=dup['supplier__trade']
        )
        
        for mat in materials:
            print(f"   - ID: {mat.id}, Slug: {mat.slug}, Fornecedor: {mat.supplier.trade if mat.supplier else 'N/A'}")
            if hasattr(mat, 'bidding') and mat.bidding:
                print(f"     Licitação: {mat.bidding.name}")
            if hasattr(mat, 'status'):
                print(f"     Status: {mat.get_status_display()}")

else:
    print("✓ Nenhum material duplicado encontrado!")

print(f"\n{'=' * 80}")
print(f"Total de materiais no sistema: {Material.objects.count()}")
print("=" * 80)
