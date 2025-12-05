#!/usr/bin/env python3
"""
Script para CORRIGIR automaticamente variáveis Django quebradas.
"""
import re
from pathlib import Path

def fix_broken_django_vars(file_path):
    """Corrige variáveis Django quebradas em um arquivo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Padrão para encontrar {{ ... }} quebrado em múltiplas linhas
    # Procura por {{ seguido de qualquer coisa até }}
    pattern = r'\{\{([^}]*?)\n([^}]*?)\}\}'
    
    def replace_multiline(match):
        """Substitui variável quebrada por versão em linha única."""
        full_match = match.group(0)
        # Juntar tudo em uma linha, removendo quebras e espaços extras
        fixed = full_match.replace('\n', ' ')
        # Remover espaços múltiplos
        fixed = re.sub(r'\s+', ' ', fixed)
        return fixed
    
    # Aplicar correção
    content = re.sub(pattern, replace_multiline, content, flags=re.DOTALL)
    
    # Verificar se houve mudanças
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Função principal."""
    base_path = Path('.')
    fixed_files = []
    
    # Lista de arquivos com problemas (baseado na varredura)
    problem_files = [
        'reports/templates/register_reports.html',
        'bidding_procurement/templates/bidding_procurement/bidding_detail.html',
        'bidding_procurement/templates/bidding_procurement/include/_table_material.html',
        'bidding_supplier/templates/supplier_detail.html',
        'dashboard/templates/dashboard/partials/materials_chart.html',
        'organizational_structure/templates/organizational_structure/diretoria_detail.html',
        'organizational_structure/templates/organizational_structure/include/_table_setor.html',
        'organizational_structure/templates/organizational_structure/setor_detail.html',
        'reports/templates/report.html',
    ]
    
    print("=" * 80)
    print("CORRIGINDO VARIÁVEIS DJANGO QUEBRADAS")
    print("=" * 80)
    
    for file_rel_path in problem_files:
        file_path = base_path / file_rel_path
        if file_path.exists():
            if fix_broken_django_vars(file_path):
                fixed_files.append(str(file_rel_path))
                print(f"✅ {file_rel_path}")
            else:
                print(f"⚠️  {file_rel_path} - Nenhuma mudança necessária")
        else:
            print(f"❌ {file_rel_path} - Arquivo não encontrado")
    
    print("\n" + "=" * 80)
    print(f"Total de arquivos corrigidos: {len(fixed_files)}")
    print("=" * 80)

if __name__ == '__main__':
    main()
