#!/usr/bin/env python
"""
Script para análise completa de modelos, formulários e templates do projeto SISInfo V2.
Gera relatório detalhado de páginas, formulários e campos faltantes.
"""

import os
import re
import ast
from pathlib import Path
from collections import defaultdict

# Configuração
BASE_DIR = Path(__file__).parent
APPS = [
    'authenticate',
    'bidding_procurement',
    'bidding_supplier',
    'dashboard',
    'organizational_structure',
    'reports',
]

def extract_model_fields(model_file):
    """Extrai campos de um arquivo models.py"""
    try:
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        models = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Verificar se herda de models.Model
                is_model = any(
                    (isinstance(base, ast.Attribute) and 
                     isinstance(base.value, ast.Name) and 
                     base.value.id == 'models' and 
                     base.attr == 'Model')
                    for base in node.bases
                )
                
                if is_model:
                    fields = []
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    field_name = target.name
                                    if not field_name.startswith('_'):
                                        fields.append(field_name)
                    
                    models[node.name] = fields
        
        return models
    except Exception as e:
        print(f"Erro ao processar {model_file}: {e}")
        return {}

def extract_form_fields(form_file):
    """Extrai campos de um arquivo forms.py"""
    try:
        with open(form_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        forms = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Verificar se é um Form
                is_form = any(
                    (isinstance(base, ast.Attribute) and 
                     base.attr in ['ModelForm', 'Form'])
                    for base in node.bases
                )
                
                if is_form:
                    fields = []
                    model_name = None
                    
                    # Procurar classe Meta
                    for item in node.body:
                        if isinstance(item, ast.ClassDef) and item.name == 'Meta':
                            for meta_item in item.body:
                                if isinstance(meta_item, ast.Assign):
                                    for target in meta_item.targets:
                                        if isinstance(target, ast.Name) and target.name == 'model':
                                            if isinstance(meta_item.value, ast.Name):
                                                model_name = meta_item.value.id
                                        elif isinstance(target, ast.Name) and target.name == 'fields':
                                            if isinstance(meta_item.value, ast.List):
                                                fields = [elt.s for elt in meta_item.value.elts if isinstance(elt, ast.Str)]
                                            elif isinstance(meta_item.value, ast.Constant):
                                                if meta_item.value.value == '__all__':
                                                    fields = ['__all__']
                    
                    forms[node.name] = {
                        'fields': fields,
                        'model': model_name
                    }
        
        return forms
    except Exception as e:
        print(f"Erro ao processar {form_file}: {e}")
        return {}

def count_templates(app_dir):
    """Conta templates de um app"""
    templates_dir = app_dir / 'templates'
    if not templates_dir.exists():
        return 0
    
    count = 0
    for root, dirs, files in os.walk(templates_dir):
        count += len([f for f in files if f.endswith('.html')])
    
    return count

def extract_urls(urls_file):
    """Extrai padrões de URL de um arquivo urls.py"""
    try:
        with open(urls_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex para encontrar path() ou re_path()
        pattern = r"path\(['\"]([^'\"]+)['\"]"
        urls = re.findall(pattern, content)
        
        return urls
    except Exception as e:
        print(f"Erro ao processar {urls_file}: {e}")
        return []

def analyze_app(app_name):
    """Analisa um app completo"""
    app_dir = BASE_DIR / app_name
    
    result = {
        'name': app_name,
        'models': {},
        'forms': {},
        'urls': [],
        'templates_count': 0,
        'has_models': False,
        'has_forms': False,
        'has_urls': False,
    }
    
    # Analisar models.py
    models_file = app_dir / 'models.py'
    if models_file.exists():
        result['models'] = extract_model_fields(models_file)
        result['has_models'] = bool(result['models'])
    
    # Analisar forms.py
    forms_file = app_dir / 'forms.py'
    if forms_file.exists():
        result['forms'] = extract_form_fields(forms_file)
        result['has_forms'] = bool(result['forms'])
    
    # Analisar urls.py
    urls_file = app_dir / 'urls.py'
    if urls_file.exists():
        result['urls'] = extract_urls(urls_file)
        result['has_urls'] = bool(result['urls'])
    
    # Contar templates
    result['templates_count'] = count_templates(app_dir)
    
    return result

def compare_model_form_fields(models, forms):
    """Compara campos de modelos com formulários"""
    missing_fields = {}
    
    for form_name, form_data in forms.items():
        if form_data['model'] and form_data['model'] in models:
            model_fields = set(models[form_data['model']])
            
            if '__all__' in form_data['fields']:
                # Formulário usa todos os campos
                missing_fields[form_name] = []
            else:
                form_fields = set(form_data['fields'])
                missing = model_fields - form_fields
                
                # Filtrar campos que geralmente não aparecem em forms
                excluded = {'id', 'created_at', 'updated_at', 'slug', 'objects'}
                missing = missing - excluded
                
                if missing:
                    missing_fields[form_name] = list(missing)
    
    return missing_fields

def generate_report():
    """Gera relatório completo"""
    print("=" * 80)
    print("RELATÓRIO DE ANÁLISE - SISInfo V2")
    print("=" * 80)
    print()
    
    all_results = {}
    
    for app_name in APPS:
        print(f"\n{'=' * 80}")
        print(f"APP: {app_name.upper()}")
        print(f"{'=' * 80}\n")
        
        result = analyze_app(app_name)
        all_results[app_name] = result
        
        # Modelos
        print(f"📦 MODELOS ({len(result['models'])} encontrados):")
        for model_name, fields in result['models'].items():
            print(f"  ├─ {model_name} ({len(fields)} campos)")
            for field in fields[:5]:  # Mostrar apenas 5 primeiros
                print(f"  │  ├─ {field}")
            if len(fields) > 5:
                print(f"  │  └─ ... e mais {len(fields) - 5} campos")
        
        if not result['models']:
            print("  └─ Nenhum modelo encontrado")
        
        print()
        
        # Formulários
        print(f"📝 FORMULÁRIOS ({len(result['forms'])} encontrados):")
        for form_name, form_data in result['forms'].items():
            model_ref = f" -> {form_data['model']}" if form_data['model'] else ""
            fields_info = "__all__" if '__all__' in form_data['fields'] else f"{len(form_data['fields'])} campos"
            print(f"  ├─ {form_name}{model_ref} ({fields_info})")
        
        if not result['forms']:
            print("  └─ Nenhum formulário encontrado")
        
        print()
        
        # Comparar campos
        if result['models'] and result['forms']:
            missing = compare_model_form_fields(result['models'], result['forms'])
            if missing:
                print("⚠️  CAMPOS FALTANTES NOS FORMULÁRIOS:")
                for form_name, fields in missing.items():
                    if fields:
                        print(f"  ├─ {form_name}:")
                        for field in fields:
                            print(f"  │  ├─ {field}")
                print()
        
        # URLs
        print(f"🔗 URLS ({len(result['urls'])} encontradas):")
        for url in result['urls'][:10]:  # Mostrar apenas 10 primeiras
            print(f"  ├─ /{url}")
        if len(result['urls']) > 10:
            print(f"  └─ ... e mais {len(result['urls']) - 10} URLs")
        
        if not result['urls']:
            print("  └─ Nenhuma URL encontrada")
        
        print()
        
        # Templates
        print(f"🎨 TEMPLATES: {result['templates_count']} arquivos .html")
        print()
    
    # Resumo geral
    print(f"\n{'=' * 80}")
    print("RESUMO GERAL")
    print(f"{'=' * 80}\n")
    
    total_models = sum(len(r['models']) for r in all_results.values())
    total_forms = sum(len(r['forms']) for r in all_results.values())
    total_urls = sum(len(r['urls']) for r in all_results.values())
    total_templates = sum(r['templates_count'] for r in all_results.values())
    
    print(f"📦 Total de Modelos: {total_models}")
    print(f"📝 Total de Formulários: {total_forms}")
    print(f"🔗 Total de URLs: {total_urls}")
    print(f"🎨 Total de Templates: {total_templates}")
    print()
    
    # Apps sem formulários
    apps_without_forms = [name for name, r in all_results.items() if not r['has_forms']]
    if apps_without_forms:
        print(f"⚠️  Apps SEM formulários: {', '.join(apps_without_forms)}")
    
    # Apps sem templates
    apps_without_templates = [name for name, r in all_results.items() if r['templates_count'] == 0]
    if apps_without_templates:
        print(f"⚠️  Apps SEM templates: {', '.join(apps_without_templates)}")
    
    print()

if __name__ == '__main__':
    generate_report()
