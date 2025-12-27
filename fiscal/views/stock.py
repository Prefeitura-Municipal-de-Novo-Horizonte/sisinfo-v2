"""
Views para visualização de estoque e saldo de materiais.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum, F

from fiscal.models import StockItem
from bidding_procurement.models import MaterialBidding


class StockOverviewView(LoginRequiredMixin, TemplateView):
    """
    Página de visualização do estoque físico e saldo de materiais por licitação.
    """
    template_name = 'fiscal/stock/overview.html'
    login_url = 'authenticate:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estoque Físico (StockItem com quantidade > 0)
        stock_items = StockItem.objects.filter(
            quantity__gt=0
        ).select_related(
            'material_bidding__material',
            'material_bidding__bidding',
            'material_bidding__supplier'
        ).order_by('material_bidding__material__name')
        
        context['stock_items'] = stock_items
        context['total_stock_items'] = stock_items.count()
        
        # Saldo por Licitação (MaterialBidding ativos com saldo disponível)
        materials_balance = MaterialBidding.objects.filter(
            status='1',  # Licitação ativa
        ).select_related(
            'material', 'bidding', 'supplier'
        ).order_by('bidding__name', 'material__name')
        
        # Adicionar anotação para saldo disponível
        context['materials_balance'] = materials_balance
        context['total_materials'] = materials_balance.count()
        
        # Estatísticas
        context['total_near_limit'] = materials_balance.filter(
            quantity_purchased__gte=F('quantity') * 0.8
        ).count()
        
        context['total_at_limit'] = materials_balance.filter(
            quantity_purchased__gte=F('quantity')
        ).count()
        
        return context
