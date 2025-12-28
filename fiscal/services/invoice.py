"""
Serviço para operações com Notas Fiscais.

Este módulo contém a lógica de negócio relacionada a Invoice,
extraída do model para manter separação de responsabilidades.
"""
from decimal import Decimal
from typing import Optional
from django.utils import timezone

from core.services import ServiceResult


class InvoiceService:
    """
    Serviço responsável pela lógica de negócio de Notas Fiscais.
    
    Métodos extraídos do model Invoice para:
    - Manter o model focado em representação de dados
    - Facilitar testes isolados
    - Permitir operações complexas com transações
    """
    
    @staticmethod
    def get_invoice_by_pk(pk: int) -> ServiceResult:
        """
        Busca uma nota fiscal pelo PK.
        
        Args:
            pk: ID da nota fiscal
            
        Returns:
            ServiceResult com Invoice ou erro
        """
        from fiscal.models import Invoice
        
        try:
            invoice = Invoice.objects.select_related(
                'supplier'
            ).prefetch_related(
                'items__material_bidding__material',
                'deliveries'
            ).get(pk=pk)
            return ServiceResult.ok(data=invoice)
        except Invoice.DoesNotExist:
            return ServiceResult.fail(error="Nota fiscal não encontrada.")
    
    @staticmethod
    def mark_as_delivered_to_purchases(invoice) -> ServiceResult:
        """
        Marca a nota como entregue ao setor de compras.
        
        Args:
            invoice: Instância de Invoice
            
        Returns:
            ServiceResult de sucesso ou erro
        """
        try:
            invoice.delivered_to_purchases = True
            invoice.delivered_to_purchases_at = timezone.now()
            invoice.status = 'E'
            invoice.save(update_fields=[
                'delivered_to_purchases', 
                'delivered_to_purchases_at', 
                'status'
            ])
            return ServiceResult.ok(
                data=invoice, 
                message=f"NF {invoice.number} entregue ao setor de compras!"
            )
        except Exception as e:
            return ServiceResult.fail(error=str(e))
    
    @staticmethod
    def check_stock_status(invoice) -> dict:
        """
        Verifica status de estoque dos itens da nota.
        
        Args:
            invoice: Instância de Invoice
            
        Returns:
            dict com informações de estoque
        """
        from fiscal.models import StockItem
        
        items_with_stock = []
        items_without_stock = []
        
        for item in invoice.items.all():
            try:
                stock = StockItem.objects.get(
                    material_bidding=item.material_bidding
                )
                if stock.quantity > 0:
                    items_with_stock.append({
                        'item': item,
                        'stock': stock,
                        'available': stock.quantity
                    })
                else:
                    items_without_stock.append(item)
            except StockItem.DoesNotExist:
                items_without_stock.append(item)
        
        return {
            'has_stock': len(items_with_stock) > 0,
            'items_with_stock': items_with_stock,
            'items_without_stock': items_without_stock,
            'total_items': invoice.items.count(),
        }
    
    @staticmethod
    def get_delivery_status(invoice) -> dict:
        """
        Retorna status detalhado do processo de entrega.
        
        Args:
            invoice: Instância de Invoice
            
        Returns:
            dict com status e contagens
        """
        deliveries = invoice.deliveries.all()
        
        if not deliveries.exists():
            return {
                'status': 'preparing',
                'label': 'Em Preparação',
                'total': 0,
                'pending': 0,
                'on_way': 0,
                'completed': 0,
            }
        
        pending = deliveries.filter(status='P').count()
        on_way = deliveries.filter(status='A').count()
        completed = deliveries.filter(status='C').count()
        total = deliveries.count()
        
        if pending > 0 or on_way > 0:
            status = 'on_way'
            label = 'Em Trânsito'
        else:
            status = 'delivered'
            label = 'Entregue'
        
        return {
            'status': status,
            'label': label,
            'total': total,
            'pending': pending,
            'on_way': on_way,
            'completed': completed,
        }
    
    @staticmethod
    def calculate_totals(invoice) -> dict:
        """
        Calcula totais da nota fiscal.
        
        Args:
            invoice: Instância de Invoice
            
        Returns:
            dict com valores calculados
        """
        items = invoice.items.all()
        
        total_value = Decimal("0.00")
        total_items = 0
        
        for item in items:
            total_value += item.total_price
            total_items += item.quantity
        
        return {
            'total_value': total_value.quantize(Decimal("0.00")),
            'total_items': total_items,
            'item_count': items.count(),
        }
    
    @staticmethod
    def get_invoice_context(pk: int) -> ServiceResult:
        """
        Retorna contexto completo para exibição de uma nota fiscal.
        
        Args:
            pk: ID da nota fiscal
            
        Returns:
            ServiceResult com contexto ou erro
        """
        result = InvoiceService.get_invoice_by_pk(pk)
        
        if not result.success:
            return result
        
        invoice = result.data
        
        context = {
            'invoice': invoice,
            'totals': InvoiceService.calculate_totals(invoice),
            'stock_status': InvoiceService.check_stock_status(invoice),
            'delivery_status': InvoiceService.get_delivery_status(invoice),
            'items': invoice.items.select_related(
                'material_bidding__material'
            ).all(),
            'deliveries': invoice.deliveries.select_related(
                'sector', 'delivered_by'
            ).all(),
        }
        
        # Verificar se tem commitment e report_link
        try:
            context['commitment'] = invoice.commitment
        except:
            context['commitment'] = None
            
        try:
            context['report_link'] = invoice.report_link
        except:
            context['report_link'] = None
        
        return ServiceResult.ok(data=context)
