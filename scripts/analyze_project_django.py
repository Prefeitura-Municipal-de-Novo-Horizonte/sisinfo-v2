#!/usr/bin/env python
"""
Script Django para análise completa de modelos, formulários e templates.
Executa dentro do contexto Django para acesso direto aos modelos.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from django.apps import apps
from django.conf import settings
from pathlib import Path
import importlib

def analyze_models(app_config):
    """Analisa modelos de um app"""
    models = app_config.get_models()
    result = {}
    
    for model in models:
        fields = []
        for field in model._meta.get_fields():
            field_info = {
                'name': field.name,
                'type': field.get_internal_type() if hasattr(field, 'get_internal_type') else 'Relation',
                'required': getattr(field, 'blank', True) == False,
                'null': getattr(field, 'null', False),
            }
            fields.append(field_info)
        
        result[model.__name__] = {
            'fields': fields,
            'field_count': len(fields),
        }
    
    return result

def analyze_forms(app_name):
    """Analisa formulários de um app"""
    try:
        forms_module = importlib.import_module(f'{app_name}.forms')
        forms = {}
        
        for name in dir(forms_module):
            obj = getattr(forms_module, name)
            if isinstance(obj, type) and hasattr(obj, 'base_fields'):
                # É um Form ou ModelForm
                form_info = {
                    'fields': list(obj.base_fields.keys()) if hasattr(obj, 'base_fields') else [],
                    'is_model_form': hasattr(obj, '_meta') and hasattr(obj._meta, 'model'),
                    'model': obj._meta.model.__name__ if (hasattr(obj, '_meta') and hasattr(obj._meta, 'model')) else None,
                }
                forms[name] = form_info
        
        return forms
    except (ImportError, AttributeError) as e:
        return {}

def count_templates(app_name):
    """Conta templates de um app"""
    app_path = Path(settings.BASE_DIR) / app_name / 'templates'
    if not app_path.exists():
        return 0, []
    
    templates = []
    for root, dirs, files in os.walk(app_path):
        for file in files:
            if file.endswith('.html'):
                rel_path = Path(root).relative_to(app_path) / file
                templates.append(str(rel_path))
    
    return len(templates), templates

def count_urls(app_name):
    """Conta URLs de um app"""
    try:
        urls_module = importlib.import_module(f'{app_name}.urls')
        if hasattr(urls_module, 'urlpatterns'):
            return len(urls_module.urlpatterns)
        return 0
    except ImportError:
        return 0

def compare_model_form(model_fields, form_fields, form_model_name, model_name):
    """Compara campos de modelo com formulário"""
    if form_model_name != model_name:
        return []
    
    model_field_names = {f['name'] for f in model_fields}
    form_field_names = set(form_fields)
    
    # Excluir campos automáticos
    excluded = {'id', 'created_at', 'updated_at', 'slug'}
    model_field_names = model_field_names - excluded
    
    missing = model_field_names - form_field_names
    return list(missing)

def generate_markdown_report():
    """Gera relatório em Markdown"""
    output = []
    output.append("# 📊 Relatório de Análise - SISInfo V2\n")
    output.append(f"**Data:** {os.popen('date').read().strip()}\n")
    output.append("---\n\n")
    
    # Apps configurados
    my_apps = [app for app in settings.INSTALLED_APPS if not app.startswith('django.') and app not in ['django_extensions', 'django_filters', 'core']]
    
    total_models = 0
    total_forms = 0
    total_urls = 0
    total_templates = 0
    
    for app_name in my_apps:
        app_label = app_name.split('.')[-2] if '.' in app_name else app_name
        
        output.append(f"## 📦 App: `{app_label}`\n\n")
        
        try:
            app_config = apps.get_app_config(app_label)
            
            # Modelos
            models = analyze_models(app_config)
            total_models += len(models)
            
            output.append(f"### Modelos ({len(models)})\n\n")
            if models:
                for model_name, model_data in models.items():
                    output.append(f"#### `{model_name}` ({model_data['field_count']} campos)\n\n")
                    output.append("| Campo | Tipo | Obrigatório | Null |\n")
                    output.append("|-------|------|-------------|------|\n")
                    for field in model_data['fields'][:10]:  # Limitar a 10
                        req = "✅" if field['required'] else "❌"
                        null = "✅" if field['null'] else "❌"
                        output.append(f"| `{field['name']}` | {field['type']} | {req} | {null} |\n")
                    if model_data['field_count'] > 10:
                        output.append(f"\n*... e mais {model_data['field_count'] - 10} campos*\n")
                    output.append("\n")
            else:
                output.append("*Nenhum modelo encontrado*\n\n")
            
            # Formulários
            forms = analyze_forms(app_label)
            total_forms += len(forms)
            
            output.append(f"### Formulários ({len(forms)})\n\n")
            if forms:
                for form_name, form_data in forms.items():
                    model_ref = f" → `{form_data['model']}`" if form_data['model'] else ""
                    output.append(f"- **`{form_name}`**{model_ref} ({len(form_data['fields'])} campos)\n")
                    
                    # Comparar com modelo se for ModelForm
                    if form_data['model'] and form_data['model'] in models:
                        missing = compare_model_form(
                            models[form_data['model']]['fields'],
                            form_data['fields'],
                            form_data['model'],
                            form_data['model']
                        )
                        if missing:
                            output.append(f"  - ⚠️ **Campos faltantes:** {', '.join(f'`{f}`' for f in missing)}\n")
                
                output.append("\n")
            else:
                output.append("*Nenhum formulário encontrado*\n\n")
            
            # URLs
            url_count = count_urls(app_label)
            total_urls += url_count
            output.append(f"### URLs: {url_count}\n\n")
            
            # Templates
            template_count, templates = count_templates(app_label)
            total_templates += template_count
            output.append(f"### Templates: {template_count}\n\n")
            if templates:
                for tmpl in templates[:5]:
                    output.append(f"- `{tmpl}`\n")
                if len(templates) > 5:
                    output.append(f"\n*... e mais {len(templates) - 5} templates*\n")
            
            output.append("\n---\n\n")
            
        except Exception as e:
            output.append(f"*Erro ao analisar: {e}*\n\n---\n\n")
    
    # Resumo
    output.append("## 📈 Resumo Geral\n\n")
    output.append(f"- **Total de Modelos:** {total_models}\n")
    output.append(f"- **Total de Formulários:** {total_forms}\n")
    output.append(f"- **Total de URLs:** {total_urls}\n")
    output.append(f"- **Total de Templates:** {total_templates}\n")
    
    return ''.join(output)

if __name__ == '__main__':
    report = generate_markdown_report()
    
    # Salvar em arquivo
    output_file = Path(settings.BASE_DIR) / 'docs' / 'PROJECT_ANALYSIS.md'
    output_file.write_text(report, encoding='utf-8')
    
    print(report)
    print(f"\n✅ Relatório salvo em: {output_file}")
