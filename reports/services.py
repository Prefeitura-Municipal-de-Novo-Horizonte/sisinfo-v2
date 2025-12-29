"""
Serviço para operações com Laudos (Reports).

Este módulo contém a lógica de negócio de Report,
usando ServiceResult para retornos padronizados.
"""
from typing import Optional
from django.db.models import QuerySet
from django.forms import BaseInlineFormSet

from core.services import ServiceResult
from .models import Report, MaterialReport
from .forms import ReportForm, ReportUpdateForm


class ReportService:
    """
    Serviço responsável pela lógica de negócios relacionada a Laudos.
    
    Usa ServiceResult para retornos padronizados.
    """

    @staticmethod
    def get_all_reports() -> QuerySet[Report]:
        """Retorna todos os laudos cadastrados com otimização."""
        return Report.objects.select_related(
            'sector', 'professional', 'pro_accountable'
        ).prefetch_related('invoice_links').all()

    @staticmethod
    def get_report_by_slug(slug: str) -> ServiceResult:
        """
        Retorna um laudo específico pelo slug.
        
        Args:
            slug: Slug do laudo
            
        Returns:
            ServiceResult com Report ou erro
        """
        try:
            report = Report.objects.select_related(
                'sector', 'professional', 'pro_accountable'
            ).get(slug=slug)
            return ServiceResult.ok(data=report)
        except Report.DoesNotExist:
            return ServiceResult.fail(error="Laudo não encontrado.")

    @staticmethod
    def create_report(form: ReportForm, form_material: BaseInlineFormSet) -> ServiceResult:
        """
        Cria um novo laudo e seus materiais associados.
        
        Args:
            form: Formulário do laudo
            form_material: Formset de materiais
            
        Returns:
            ServiceResult com Report criado ou erros
        """
        if not form.is_valid():
            return ServiceResult.fail(
                error="Dados do laudo inválidos.",
                errors=list(form.errors.values())
            )
        
        if not form_material.is_valid():
            return ServiceResult.fail(
                error="Dados dos materiais inválidos.",
                errors=list(form_material.errors)
            )
        
        try:
            report = form.save()
            form_material.instance = report
            form_material.save()
            return ServiceResult.ok(
                data=report,
                message=f"Laudo {report.number_report} criado com sucesso!"
            )
        except Exception as e:
            return ServiceResult.fail(error=str(e))

    @staticmethod
    def update_report(form: ReportUpdateForm, form_material: BaseInlineFormSet) -> ServiceResult:
        """
        Atualiza um laudo existente e seus materiais.
        
        Args:
            form: Formulário de atualização do laudo
            form_material: Formset de materiais
            
        Returns:
            ServiceResult com Report atualizado ou erros
        """
        if not form.is_valid():
            return ServiceResult.fail(
                error="Dados do laudo inválidos.",
                errors=list(form.errors.values())
            )
        
        if not form_material.is_valid():
            return ServiceResult.fail(
                error="Dados dos materiais inválidos.",
                errors=list(form_material.errors)
            )
        
        try:
            report = form.save()
            form_material.instance = report
            form_material.save()
            return ServiceResult.ok(
                data=report,
                message=f"Laudo {report.number_report} atualizado com sucesso!"
            )
        except Exception as e:
            return ServiceResult.fail(error=str(e))

    @staticmethod
    def delete_material_report(material_report_id: int) -> ServiceResult:
        """
        Exclui um item (material) de um laudo.
        
        Args:
            material_report_id: ID do MaterialReport
            
        Returns:
            ServiceResult com Report e mensagem
        """
        try:
            material_report = MaterialReport.objects.select_related(
                'report', 'material_bidding__material'
            ).get(id=material_report_id)
            report = material_report.report
            material_name = material_report.material_bidding.material.name
            material_report.delete()
            return ServiceResult.ok(
                data=report,
                message=f"Item {material_name} excluído do laudo {report.number_report}!"
            )
        except MaterialReport.DoesNotExist:
            return ServiceResult.fail(error="Material do laudo não encontrado.")
        except Exception as e:
            return ServiceResult.fail(error=str(e))

    @staticmethod
    def get_report_details(slug: str) -> ServiceResult:
        """
        Retorna detalhes do laudo e o preço total calculado.
        
        Args:
            slug: Slug do laudo
            
        Returns:
            ServiceResult com contexto ou erro
        """
        try:
            report = Report.objects.get(slug=slug)
        except Report.DoesNotExist:
            return ServiceResult.fail(error="Laudo não encontrado.")
        
        materiais_report = MaterialReport.objects.filter(
            report=report
        ).exclude(
            material_bidding__material__name__icontains='Perdido'
        ).select_related('material_bidding__material')
        
        total_price = sum(material.total_price for material in materiais_report)
        
        return ServiceResult.ok(data={
            'report': report,
            'materiais': materiais_report,
            'total_price': total_price,
        })

    @staticmethod
    def finalize_report(slug: str, closing_reason: str = None) -> ServiceResult:
        """
        Finaliza um laudo, marcando-o como fechado.
        
        Args:
            slug: Slug do laudo
            closing_reason: Motivo opcional do fechamento
            
        Returns:
            ServiceResult com Report finalizado ou erro
        """
        try:
            report = Report.objects.get(slug=slug)
        except Report.DoesNotExist:
            return ServiceResult.fail(error="Laudo não encontrado.")
        
        if report.status == '3':
            return ServiceResult.fail(error="Este laudo já está finalizado.")
        
        report.status = '3'
        if closing_reason:
            report.closing_reason = closing_reason
        report.save()
        
        return ServiceResult.ok(
            data=report,
            message=f"Laudo {report.number_report} finalizado com sucesso!"
        )
