#!/usr/bin/env python3
"""
Script para encontrar TODAS as variáveis Django quebradas em múltiplas linhas.
"""
import re
from pathlib import Path

def find_broken_django_vars(file_path):
    """Encontra variáveis Django quebradas em múltiplas linhas."""
    problems = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrão 1: {{ na linha, mas }} não está
    # Padrão 2: }} na linha, mas {{ não está
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Contar {{ e }} na linha
        open_count = line.count('{{')
        close_count = line.count('}}')
        
        # Se tem {{ mas não fecha na mesma linha
        if open_count > close_count:
            # Verificar se fecha nas próximas linhas
            remaining_closes_needed = open_count - close_count
            next_line_idx = i
            found_close = False
            
            while next_line_idx < len(lines) and remaining_closes_needed > 0:
                next_line = lines[next_line_idx]
                remaining_closes_needed -= next_line.count('}}')
                if '}}' in next_line:
                    found_close = True
                    break
                next_line_idx += 1
            
            if found_close:
                problems.append({
                    'line': i,
                    'type': 'broken_open',
                    'content': line.strip()
                })
        
        # Se tem }} mas não abre na mesma linha
        if close_count > open_count:
            problems.append({
                'line': i,
                'type': 'broken_close',
                'content': line.strip()
            })
    
    return problems

def main():
    """Função principal."""
    # Procurar em TODO o projeto
    base_path = Path('.')
    all_problems = {}
    total_files = 0
    total_problems = 0
    
    # Buscar todos os arquivos HTML
    for html_file in base_path.rglob('*.html'):
        # Ignorar node_modules, .venv, etc
        if any(part in str(html_file) for part in ['node_modules', '.venv', 'staticfiles', '.git']):
            continue
        
        total_files += 1
        problems = find_broken_django_vars(html_file)
        
        if problems:
            all_problems[str(html_file)] = problems
            total_problems += len(problems)
    
    # Exibir resultados
    print("=" * 80)
    print("VARREDURA COMPLETA - VARIÁVEIS DJANGO QUEBRADAS")
    print("=" * 80)
    print(f"\nArquivos analisados: {total_files}")
    print(f"Arquivos com problemas: {len(all_problems)}")
    print(f"Total de problemas: {total_problems}")
    
    if all_problems:
        print("\n" + "=" * 80)
        print("DETALHES DOS PROBLEMAS")
        print("=" * 80)
        
        for file_path, problems in sorted(all_problems.items()):
            print(f"\n📄 {file_path}")
            print(f"   {len(problems)} problema(s) encontrado(s)")
            for problem in problems:
                tipo = "{{ sem }}" if problem['type'] == 'broken_open' else "}} sem {{"
                print(f"   Linha {problem['line']:4d}: [{tipo}] {problem['content'][:80]}")
    else:
        print("\n✅ Nenhuma variável Django quebrada encontrada!")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
