from django.db import transaction
from reports.models import Report

def check_report_still_complete(report):
    """
    Verifica se o laudo ainda tem todos os materiais cobertos por notas vinculadas.
    Retorna True se ainda está completo, False caso contrário.
    """
    # Materiais do laudo
    report_materials = report.materiais.all()
    
    if not report_materials.exists():
        return False
    
    report_material_ids = set(
        report_materials.values_list('material_bidding_id', flat=True)
    )
    
    # Materiais das notas ainda vinculadas
    linked_invoice_material_ids = set()
    for link in report.invoice_links.all():
        invoice_materials = link.invoice.items.values_list('material_bidding_id', flat=True)
        linked_invoice_material_ids.update(invoice_materials)
    
    return report_material_ids.issubset(linked_invoice_material_ids)


def check_and_close_report_if_complete(report):
    """
    Verifica se todos os materiais do laudo já foram atendidos por notas fiscais.
    Se sim, fecha o laudo (status='3' = Finalizado).
    
    Retorna True se o laudo foi fechado, False caso contrário.
    """
    # Materiais do laudo
    report_materials = report.materiais.all()
    
    if not report_materials.exists():
        return False
    
    # IDs de materiais do laudo
    report_material_ids = set(
        report_materials.values_list('material_bidding_id', flat=True)
    )
    
    # Materiais das notas vinculadas a este laudo
    linked_invoice_material_ids = set()
    for link in report.invoice_links.all():
        invoice_materials = link.invoice.items.values_list('material_bidding_id', flat=True)
        linked_invoice_material_ids.update(invoice_materials)
    
    # Verifica se todos os materiais do laudo estão nas notas vinculadas
    all_materials_covered = report_material_ids.issubset(linked_invoice_material_ids)
    
    if all_materials_covered and report.status == '1':  # Só fecha se estiver aberto ('1')
        report.status = '3'  # Finalizado
        report.save(update_fields=['status'])
        return True
    
    return False
