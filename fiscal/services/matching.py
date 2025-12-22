"""
Serviços para lógica de negócio do app fiscal.
"""
from django.db.models import Count, Q
from reports.models import Report, MaterialReport
from fiscal.models import Invoice, InvoiceItem


def suggest_reports_for_invoice(invoice: Invoice, limit: int = 5) -> list:
    """
    Sugere laudos que podem estar relacionados a uma nota fiscal.
    
    Critérios de matching:
    1. Laudo ABERTO (status='1')
    2. Que tenha materiais em comum com a nota (mesmo material_bidding)
    3. Ordena por quantidade de itens coincidentes (maior primeiro)
    
    Nota: Laudos que já têm notas vinculadas TAMBÉM aparecem, pois um laudo
    pode ter várias notas (a regra 1 nota = 1 laudo é garantida pelo modelo).
    
    Retorna lista de dicts com:
    - report: o objeto Report
    - matching_items: quantidade de itens em comum
    - sector: setor do laudo (para facilitar identificação)
    - total_items: total de itens do laudo
    """
    # Materiais da nota fiscal
    invoice_material_ids = set(
        invoice.items.values_list('material_bidding_id', flat=True)
    )
    
    if not invoice_material_ids:
        return []
    
    # Laudos abertos com materiais em comum
    # Nota: Não excluímos laudos que já têm notas vinculadas, pois um laudo
    # pode ter várias notas (a regra 1 nota = 1 laudo é garantida pelo modelo)
    open_reports = Report.objects.filter(
        status='1'  # Aberto
    ).prefetch_related(
        'materiais', 'sector'
    ).distinct()
    
    suggestions = []
    
    for report in open_reports:
        # Materiais do laudo
        report_material_ids = set(
            report.materiais.values_list('material_bidding_id', flat=True)
        )
        
        # Interseção (materiais em comum)
        common_materials = invoice_material_ids & report_material_ids
        
        if common_materials:
            suggestions.append({
                'report': report,
                'matching_items': len(common_materials),
                'sector': report.sector,
                'sector_name': report.sector.name if report.sector else 'Sem setor',
                'total_items': report.materiais.count(),
                'match_percentage': round(
                    len(common_materials) / len(invoice_material_ids) * 100, 1
                ) if invoice_material_ids else 0
            })
    
    # Ordenar por quantidade de matches (maior primeiro)
    suggestions.sort(key=lambda x: x['matching_items'], reverse=True)
    
    return suggestions[:limit]


def get_invoice_linked_report(invoice: Invoice):
    """
    Retorna o laudo vinculado à nota (via InvoiceReportLink) ou None.
    """
    try:
        return invoice.report_link.report
    except (Invoice.report_link.RelatedObjectDoesNotExist, AttributeError):
        return None
