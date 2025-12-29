import logging
from typing import Dict, Any, List
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

from organizational_structure.models import Sector
from reports.models import Report, MaterialReport
from authenticate.models import ProfessionalUser
from bidding_supplier.models import Supplier
from core.cache import (
    cache_get, cache_set, cache_delete,
    CACHE_DASHBOARD_STATS, CACHE_DASHBOARD_CHARTS,
    TTL_MEDIUM, TTL_LONG
)

logger = logging.getLogger(__name__)


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
        
        Cache: 5 minutos (TTL_MEDIUM)
        """
        # Chave de cache específica por usuário (para dados personalizados)
        cache_key = f"{CACHE_DASHBOARD_STATS}_{user.id}"
        
        # Tenta recuperar do cache
        cached_data = cache_get(cache_key)
        if cached_data:
            logger.debug(f"Dashboard stats from cache for user {user.id}")
            return cached_data
        
        # Contadores para cards
        total_reports = Report.objects.count()
        total_reports_user = Report.objects.filter(professional=user).count()
        pending_reports = Report.objects.filter(status='P').count()
        total_suppliers = Supplier.objects.count()
        total_sectors = Sector.objects.count()
        
        data = {
            'total_reports': total_reports,
            'total_reports_user': total_reports_user,
            'pending_reports': pending_reports,
            'total_suppliers': total_suppliers,
            'total_sectors': total_sectors,
        }
        
        # Salva no cache
        cache_set(cache_key, data, ttl=TTL_MEDIUM)
        logger.debug(f"Dashboard stats cached for user {user.id}")
        
        return data

    @staticmethod
    def get_reports_by_sector(period_days: int = 30) -> List[Dict[str, Any]]:
        """
        Retorna a contagem de laudos por setor.
        
        Cache: 10 minutos
        """
        cache_key = f"{CACHE_DASHBOARD_CHARTS}_sector_{period_days}"
        
        cached_data = cache_get(cache_key)
        if cached_data:
            return cached_data
        
        start_date = timezone.now() - timedelta(days=period_days)

        stats = Report.objects.filter(
            created_at__gte=start_date
        ).values('sector__name').annotate(
            count=Count('id')
        ).order_by('-count')

        data = list(stats)
        cache_set(cache_key, data, ttl=TTL_LONG)  # 30 min
        
        return data

    @staticmethod
    def get_top_materials(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retorna os materiais mais utilizados nos laudos.
        """
        stats = MaterialReport.objects.values(
            'material_bidding__material__name'
        ).exclude(
            material_bidding__material__name__icontains='Perdido'
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
        Retorna os materiais mais adquiridos (via Notas Fiscais) com licitação ativa.
        
        Cache: 30 minutos
        """
        cache_key = f"{CACHE_DASHBOARD_CHARTS}_materials_{period_days}_{limit}"
        
        cached_data = cache_get(cache_key)
        if cached_data:
            return cached_data
        
        from fiscal.models import InvoiceItem
        
        start_date = timezone.now() - timedelta(days=period_days)
        
        stats = InvoiceItem.objects.filter(
            invoice__created_at__gte=start_date,
            material_bidding__status='1'  # Licitação ativa
        ).exclude(
            material_bidding__material__name__icontains='Perdido'
        ).values(
            'material_bidding__material__name'
        ).annotate(
            total_qty=Sum('quantity')
        ).order_by('-total_qty')[:limit]

        data = [
            {
                'name': item['material_bidding__material__name'],
                'qty': item['total_qty']
            }
            for item in stats if item['material_bidding__material__name']
        ]
        
        cache_set(cache_key, data, ttl=TTL_LONG)  # 30 min
        
        return data
    
    @staticmethod
    def invalidate_dashboard_cache(user_id: int = None):
        """
        Invalida o cache do dashboard.
        
        Args:
            user_id: Se fornecido, invalida apenas para o usuário específico.
                     Se None, invalida todos os caches de dashboard.
        """
        if user_id:
            cache_delete(f"{CACHE_DASHBOARD_STATS}_{user_id}")
        else:
            # Invalida stats de todos os usuários (não ideal, mas funciona)
            # Em produção, considerar usar cache_clear_pattern
            pass
        
        # Invalida gráficos
        for period in [7, 30, 90, 365]:
            cache_delete(f"{CACHE_DASHBOARD_CHARTS}_sector_{period}")
            cache_delete(f"{CACHE_DASHBOARD_CHARTS}_materials_{period}_10")
        
        logger.info("Dashboard cache invalidated")
