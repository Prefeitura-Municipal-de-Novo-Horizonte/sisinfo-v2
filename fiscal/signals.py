import cloudinary.uploader
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.conf import settings
from pathlib import Path
from fiscal.models import Invoice, InvoiceItem, DeliveryNoteItem, StockItem

@receiver(post_delete, sender=Invoice)
def delete_image_on_invoice_delete(sender, instance, **kwargs):
    """
    Deleta a imagem quando a Nota Fiscal é deletada.
    - Em prod (USE_CLOUDINARY=True): deleta do Cloudinary
    - Em dev (USE_CLOUDINARY=False): deleta arquivo local
    """
    if not instance.photo:
        return
    
    try:
        public_id = str(instance.photo)
        
        if settings.USE_CLOUDINARY and not public_id.startswith('local/'):
            # Produção: deletar do Cloudinary
            cloudinary.uploader.destroy(instance.photo.public_id)
        elif public_id.startswith('local/'):
            # Dev: deletar arquivo local
            filename = public_id.replace('local/', '')
            file_path = settings.MEDIA_ROOT / 'invoices' / filename
            if file_path.exists():
                file_path.unlink()
    except Exception as e:
        print(f"Erro ao deletar imagem para NF {instance.number}: {e}")

@receiver(post_delete, sender=InvoiceItem)
def restore_material_balance_on_item_delete(sender, instance, **kwargs):
    """
    1. Estorna o saldo FINANCEIRO do material (quantity_purchased).
    2. Decrementa o estoque FÍSICO (StockItem) pois a entrada foi cancelada.
    """
    # Skip durante loaddata
    if kwargs.get('raw', False):
        return
    
    try:
        if instance.material_bidding:
            # 1. Estorno Financeiro (MaterialBidding)
            material = instance.material_bidding
            current_purchased = material.quantity_purchased or 0
            new_purchased = max(0, current_purchased - instance.quantity)
            material.quantity_purchased = new_purchased
            material.save(update_fields=['quantity_purchased'])
            
            # 2. Estorno Físico (StockItem)
            stock_item, created = StockItem.objects.get_or_create(material_bidding=material)
            stock_item.quantity = max(0, stock_item.quantity - instance.quantity)
            stock_item.save(update_fields=['quantity'])
    except Exception:
        pass  # Ignora erros durante loaddata

@receiver(post_save, sender=InvoiceItem)
def update_stock_on_invoice_item_save(sender, instance, created, **kwargs):
    """
    Atualiza o estoque FÍSICO (StockItem) quando um item entra via Nota Fiscal.
    NOTA: A atualização do FINANCEIRO (MaterialBidding) já é feita no save() do model.
    """
    # Skip durante loaddata
    if kwargs.get('raw', False):
        return
    
    try:
        if created and instance.material_bidding:
            stock_item, _ = StockItem.objects.get_or_create(material_bidding=instance.material_bidding)
            stock_item.quantity += instance.quantity
            stock_item.save(update_fields=['quantity'])
    except Exception:
        pass  # Ignora erros durante loaddata

@receiver(post_save, sender=DeliveryNoteItem)
def decrease_stock_on_delivery(sender, instance, created, **kwargs):
    """
    Decrementa o estoque FÍSICO quando há uma saída (Entrega).
    """
    # Skip durante loaddata
    if kwargs.get('raw', False):
        return
    
    try:
        if created:
            invoice_item = instance.invoice_item
            if invoice_item.material_bidding:
                stock_item, _ = StockItem.objects.get_or_create(material_bidding=invoice_item.material_bidding)
                stock_item.quantity = max(0, stock_item.quantity - instance.quantity_delivered)
                stock_item.save(update_fields=['quantity'])
    except Exception:
        pass  # Ignora erros durante loaddata

@receiver(post_delete, sender=DeliveryNoteItem)
def restore_stock_on_delivery_delete(sender, instance, **kwargs):
    """
    Restaura o estoque FÍSICO se uma entrega for cancelada/deletada.
    """
    # Skip durante loaddata
    if kwargs.get('raw', False):
        return
    
    try:
        invoice_item = instance.invoice_item
        if invoice_item.material_bidding:
            stock_item, _ = StockItem.objects.get_or_create(material_bidding=invoice_item.material_bidding)
            stock_item.quantity += instance.quantity_delivered
            stock_item.save(update_fields=['quantity'])
    except Exception:
        pass  # Ignora erros durante loaddata
