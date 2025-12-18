from typing import Optional, Tuple, Dict, Any
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.forms import BaseInlineFormSet

from .models import Report, MaterialReport
from .forms import ReportForm, ReportUpdateForm

class ReportService:
    """
    Serviço responsável pela lógica de negócios relacionada a Laudos (Reports).
    """

    @staticmethod
    def get_all_reports() -> QuerySet[Report]:
        """Retorna todos os laudos cadastrados com otimização."""
        return Report.objects.select_related('sector', 'professional', 'pro_accountable').all()

    @staticmethod
    def get_report_by_slug(slug: str) -> Report:
        """Retorna um laudo específico pelo slug ou 404 se não encontrado."""
        return get_object_or_404(
            Report.objects.select_related('sector', 'professional', 'pro_accountable'), 
            slug=slug
        )

    @staticmethod
    def create_report(form: ReportForm, form_material: BaseInlineFormSet) -> Optional[Report]:
        """
        Cria um novo laudo e seus materiais associados.
        
        Args:
            form (ReportForm): Formulário do laudo.
            form_material (BaseInlineFormSet): Formset de materiais.
            
        Returns:
            Report: O laudo criado se sucesso, None caso contrário.
        """
        if form.is_valid() and form_material.is_valid():
            report = form.save()
            form_material.instance = report
            form_material.save()
            return report
        return None

    @staticmethod
    def update_report(form: ReportUpdateForm, form_material: BaseInlineFormSet) -> Optional[Report]:
        """
        Atualiza um laudo existente e seus materiais.
        
        Args:
            form (ReportUpdateForm): Formulário de atualização do laudo.
            form_material (BaseInlineFormSet): Formset de materiais.
            
        Returns:
            Report: O laudo atualizado se sucesso, None caso contrário.
        """
        if form.is_valid() and form_material.is_valid():
            report = form.save()
            form_material.instance = report
            form_material.save()
            return report
        return None

    @staticmethod
    def delete_material_report(material_report_id: int) -> Tuple[Report, str]:
        """
        Exclui um item (material) de um laudo.
        
        Args:
            material_report_id (int): ID do MaterialReport.
            
        Returns:
            tuple: (Report instance, str message)
        """
        material_report = get_object_or_404(MaterialReport, id=material_report_id)
        report = material_report.report
        material_name = material_report.material.name
        material_report.delete()
        msg = f'O Item {material_name} foi excluido do laudo {report.number_report} com sucesso.'
        return report, msg

    @staticmethod
    def get_report_details(slug: str) -> Dict[str, Any]:
        """
        Retorna detalhes do laudo e o preço total calculado.
        
        Args:
            slug (str): Slug do laudo.
            
        Returns:
            dict: Contexto com report e total_price.
        """
        report = get_object_or_404(Report, slug=slug)
        materiais_report = MaterialReport.objects.filter(report=report).exclude(
            material_bidding__material__name__icontains='Perdido'
        )
        total_price = sum(material.total_price for material in materiais_report)
        
        return {
            'report': report,
            'total_price': total_price,
        }
