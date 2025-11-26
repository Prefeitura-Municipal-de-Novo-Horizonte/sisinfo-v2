#!/usr/bin/env python
"""Analisa materiais duplicados antes da consolidação"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db.models import Count
from bidding_procurement.models import Material

print("="*80)
print("ANÁLISE DE MATERIAIS DUPLICADOS")
print("="*80)

# Agrupar por nome + fornecedor (critério de duplicata)
duplicates = Material.objects.values(
    'name', 'supplier__trade', 'supplier_id'
).annotate(
    total=Count('id')
).filter(total__gt=1).order_by('-total')

print(f"\nTotal de grupos duplicados: {len(duplicates)}\n")

total_to_remove = 0
for index, dup in enumerate(duplicates, 1):
    materials = Material.objects.filter(
        name=dup['name'],
        supplier_id=dup['supplier_id']
    ).order_by('id')
    
    count = materials.count()
    total_to_remove += (count - 1)  # Mantém 1, remove os outros
    
    supplier_name = dup['supplier__trade'] or "Sem fornecedor"
    print(f"{index}. '{dup['name']}' ({supplier_name}): {count} → manter 1, remover {count-1}")
    
    # Mostrar detalhes dos primeiros 5 grupos
    if index <= 5:
        for mat in materials:
            keeper = "✓ MANTER" if mat.id == materials.first().id else "✗ REMOVER"
            bidding_name = mat.bidding.name if mat.bidding else "Sem licitação"
            status_display = mat.get_status_display() if hasattr(mat, 'get_status_display') else "N/A"
            print(f"  ID={mat.id:3d} {keeper:10s} | Licitação: {bidding_name:30s} | Status: {status_display}")
        print()

print(f"\n{'='*80}")
print(f"RESUMO:")
print(f"  Total de materiais atuais: {Material.objects.count()}")
print(f"  Materiais a remover: {total_to_remove}")
print(f"  Materiais após consolidação: {Material.objects.count() - total_to_remove}")
print("="*80)
