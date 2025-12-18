import cloudinary.uploader
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from fiscal.models import Invoice, InvoiceItem, DeliveryNoteItem, StockItem

@receiver(post_delete, sender=Invoice)
def delete_cloudinary_image_on_invoice_delete(sender, instance, **kwargs):
    """
    Deleta a imagem do Cloudinary quando a Nota Fiscal é deletada.
    """
    if instance.photo:
        try:
            cloudinary.uploader.destroy(instance.photo.public_id)
        except Exception as e:
            print(f"Erro ao deletar imagem do Cloudinary para NF {instance.number}: {e}")

@receiver(post_delete, sender=InvoiceItem)
def restore_material_balance_on_item_delete(sender, instance, **kwargs):
    """
    1. Estorna o saldo FINANCEIRO do material (quantity_purchased).
    2. Decrementa o estoque FÍSICO (StockItem) pois a entrada foi cancelada.
    """
    if instance.material_bidding:
        # 1. Estorno Financeiro (MaterialBidding)
        material = instance.material_bidding
        current_purchased = material.quantity_purchased or 0
        new_purchased = max(0, current_purchased - instance.quantity)
        material.quantity_purchased = new_purchased
        material.save(update_fields=['quantity_purchased'])
        
        # 2. Estorno Físico (StockItem)
        # Se deletou o item da nota, o material "sumiu" do estoque
        stock_item, created = StockItem.objects.get_or_create(material_bidding=material)
        stock_item.quantity = max(0, stock_item.quantity - instance.quantity)
        stock_item.save(update_fields=['quantity'])

@receiver(post_save, sender=InvoiceItem)
def update_stock_on_invoice_item_save(sender, instance, created, **kwargs):
    """
    Atualiza o estoque FÍSICO (StockItem) quando um item entra via Nota Fiscal.
    NOTA: A atualização do FINANCEIRO (MaterialBidding) já é feita no save() do model.
    """
    # Se não foi criado agora, precisamos calcular a diferença (update)
    # Mas como o signal não passa o valor 'antigo', e o save() do model já tratou o financeiro,
    # aqui vamos focar apenas no incremento simples se for criado, 
    # ou complexo se quisermos suportar edição de quantidade.
    
    # IMPORTANTE: A lógica de 'update' de quantidade no InvoiceItem é complexa via signal
    # pois não temos o valor anterior facilmente. 
    # Para simplificar e evitar inconsistência, vamos assumir que o sistema
    # prioriza a lógica no .save() do model ou forms. 
    # Mas como StockItem é desacoplado, vamos fazer uma verificação básica.
    
    if created:
        stock_item, _ = StockItem.objects.get_or_create(material_bidding=instance.material_bidding)
        stock_item.quantity += instance.quantity
        stock_item.save(update_fields=['quantity'])
    else:
        # Se for edição, a diferença precisa ser calculada.
        # Uma abordagem melhor seria mover toda lógica de saldo para o Model.save()
        # ou usar uma biblioteca de tracking fields. 
        # Por enquanto, vamos assumir que edições devem ser feitas com cautela.
        pass

@receiver(post_save, sender=DeliveryNoteItem)
def decrease_stock_on_delivery(sender, instance, created, **kwargs):
    """
    Decrementa o estoque FÍSICO quando há uma saída (Entrega).
    """
    if created:
        invoice_item = instance.invoice_item
        if invoice_item.material_bidding:
            stock_item, _ = StockItem.objects.get_or_create(material_bidding=invoice_item.material_bidding)
            stock_item.quantity = max(0, stock_item.quantity - instance.quantity_delivered)
            stock_item.save(update_fields=['quantity'])

@receiver(post_delete, sender=DeliveryNoteItem)
def restore_stock_on_delivery_delete(sender, instance, **kwargs):
    """
    Restaura o estoque FÍSICO se uma entrega for cancelada/deletada.
    """
    invoice_item = instance.invoice_item
    if invoice_item.material_bidding:
        stock_item, _ = StockItem.objects.get_or_create(material_bidding=invoice_item.material_bidding)
        stock_item.quantity += instance.quantity_delivered
        stock_item.save(update_fields=['quantity'])
