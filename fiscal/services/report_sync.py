from django.db import transaction
from reports.models import Report
from fiscal.models import InvoiceReportLink, InvoiceItem


def check_report_still_complete(report):
    """
    Verifica se o laudo ainda tem todos os materiais cobertos por notas vinculadas.
    Retorna True se ainda está completo, False caso contrário.
    
    Otimizado: usa values_list direto ao invés de loops.
    """
    # IDs de materiais do laudo (1 query)
    report_material_ids = set(
        report.materiais.values_list('material_bidding_id', flat=True)
    )
    
    if not report_material_ids:
        return False
    
    # IDs de materiais das notas vinculadas (1 query com join)
    linked_invoice_ids = list(
        report.invoice_links.values_list('invoice_id', flat=True)
    )
    
    linked_invoice_material_ids = set(
        InvoiceItem.objects.filter(
            invoice_id__in=linked_invoice_ids
        ).values_list('material_bidding_id', flat=True)
    )
    
    return report_material_ids.issubset(linked_invoice_material_ids)


def check_and_close_report_if_complete(report):
    """
    Verifica se todos os materiais do laudo já foram atendidos por notas fiscais.
    Se sim, fecha o laudo (status='3' = Finalizado).
    
    Retorna True se o laudo foi fechado, False caso contrário.
    
    Otimizado: usa values_list direto ao invés de loops.
    """
    # IDs de materiais do laudo (1 query)
    report_material_ids = set(
        report.materiais.values_list('material_bidding_id', flat=True)
    )
    
    if not report_material_ids:
        return False
    
    # IDs de materiais das notas vinculadas (1 query com join)
    linked_invoice_ids = list(
        report.invoice_links.values_list('invoice_id', flat=True)
    )
    
    linked_invoice_material_ids = set(
        InvoiceItem.objects.filter(
            invoice_id__in=linked_invoice_ids
        ).values_list('material_bidding_id', flat=True)
    )
    
    # Verifica se todos os materiais do laudo estão nas notas vinculadas
    all_materials_covered = report_material_ids.issubset(linked_invoice_material_ids)
    
    if all_materials_covered and report.status == '1':  # Só fecha se estiver aberto ('1')
        report.status = '3'  # Finalizado
        report.save(update_fields=['status'])
        return True
    
    return False
