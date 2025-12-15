from typing import Dict, Any, List
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

from organizational_structure.models import Sector
from reports.models import Report, MaterialReport
from authenticate.models import ProfessionalUser
from bidding_supplier.models import Supplier

class DashboardService:
    """
    Serviço responsável pela agregação de dados para o Dashboard.
    """

    @staticmethod
    def get_dashboard_data(user: ProfessionalUser) -> Dict[str, Any]:
        """
        Retorna os dados consolidados para o dashboard do usuário.
        
        Args:
            user (ProfessionalUser): O usuário logado.
            
        Returns:
            dict: Dicionário contendo estatísticas e dados para gráficos.
        """
        # Contadores para cards
        total_reports = Report.objects.count()
        total_reports_user = Report.objects.filter(professional=user).count()
        pending_reports = Report.objects.filter(status='P').count()
        total_suppliers = Supplier.objects.count()
        total_sectors = Sector.objects.count()
        
        return {
            'total_reports': total_reports,
            'total_reports_user': total_reports_user,
            'pending_reports': pending_reports,
            'total_suppliers': total_suppliers,
            'total_sectors': total_sectors,
        }

    @staticmethod
    def get_reports_by_sector(period_days: int = 30) -> List[Dict[str, Any]]:
        """
        Retorna a contagem de laudos por setor.
        """
        start_date = timezone.now() - timedelta(days=period_days)

        stats = Report.objects.filter(
            created_at__gte=start_date
        ).values('sector__name').annotate(
            count=Count('id')
        ).order_by('-count')

        return list(stats)

    @staticmethod
    def get_top_materials(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retorna os materiais mais utilizados nos laudos.
        """
        stats = MaterialReport.objects.values(
            'material_bidding__material__name'
        ).annotate(
            total_qty=Sum('quantity')
        ).order_by('-total_qty')[:limit]

        return [
            {
                'name': item['material_bidding__material__name'],
                'qty': item['total_qty']
            }
            for item in stats if item['material_bidding__material__name']
        ]

    @staticmethod
    def get_recent_reports_for_calendar() -> List[Dict[str, Any]]:
        """
        Retorna laudos para o calendário.
        """
        reports = Report.objects.select_related('sector').all()
        events = []
        for report in reports:
            events.append({
                'title': f"Laudo {report.number_report}",
                'start': report.created_at.isoformat(),
                'url': report.get_absolute_url(),
                'extendedProps': {
                    'sector': report.sector.name if report.sector else 'Sem Setor',
                    'status': report.get_status_display()
                }
            })
        return events

    @staticmethod
    def get_top_materials_by_period(period_days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retorna os materiais mais utilizados nos laudos em um período específico.
        """
        start_date = timezone.now() - timedelta(days=period_days)
        
        stats = MaterialReport.objects.filter(
            report__created_at__gte=start_date
        ).values(
            'material_bidding__material__name'
        ).annotate(
            total_qty=Sum('quantity')
        ).order_by('-total_qty')[:limit]

        return [
            {
                'name': item['material_bidding__material__name'],
                'qty': item['total_qty']
            }
            for item in stats if item['material_bidding__material__name']
        ]
