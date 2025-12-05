#!/usr/bin/env python3
"""
Script para analisar templates HTML e identificar problemas de formatação.
"""
import re
from pathlib import Path

def analyze_template(file_path):
    """Analisa um template HTML e retorna problemas encontrados."""
    problems = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # 1. Procurar variáveis Django quebradas em múltiplas linhas
    # Padrão: {{ algo\n ou \n}}
    for i, line in enumerate(lines, 1):
        # Variável que começa mas não termina na mesma linha
        if '{{' in line and '}}' not in line:
            # Verificar se fecha na próxima linha
            if i < len(lines) and '}}' in lines[i]:
                problems.append({
                    'line': i,
                    'type': 'django_var_multiline',
                    'content': line.strip()
                })
        
        # Variável que termina mas não começou na mesma linha
        if '}}' in line and '{{' not in line:
            if i > 1 and '{{' in lines[i-2]:
                problems.append({
                    'line': i,
                    'type': 'django_var_multiline_end',
                    'content': line.strip()
                })
    
    # 2. Procurar labels mal formatadas (inline quando deveriam ser multiline)
    for i, line in enumerate(lines, 1):
        # Label com conteúdo muito longo inline
        if '<label' in line and '</label>' in line:
            if len(line) > 150:  # Linha muito longa
                problems.append({
                    'line': i,
                    'type': 'label_too_long',
                    'content': line.strip()[:100] + '...'
                })
    
    return problems

def main():
    """Função principal."""
    base_paths = [
        Path('bidding_procurement/templates'),
        Path('bidding_supplier/templates'),
    ]
    
    all_problems = {}
    
    for base_path in base_paths:
        if not base_path.exists():
            continue
            
        for html_file in base_path.rglob('*.html'):
            problems = analyze_template(html_file)
            if problems:
                all_problems[str(html_file)] = problems
    
    # Exibir resultados
    if all_problems:
        print("=" * 80)
        print("PROBLEMAS DE FORMATAÇÃO ENCONTRADOS")
        print("=" * 80)
        
        for file_path, problems in all_problems.items():
            print(f"\n📄 {file_path}")
            for problem in problems:
                print(f"  Linha {problem['line']}: [{problem['type']}]")
                print(f"    {problem['content']}")
        
        print(f"\n\nTotal: {sum(len(p) for p in all_problems.values())} problemas em {len(all_problems)} arquivos")
    else:
        print("✅ Nenhum problema de formatação encontrado!")

if __name__ == '__main__':
    main()
