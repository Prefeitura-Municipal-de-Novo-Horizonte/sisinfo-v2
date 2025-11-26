from django.db.models.signals import post_save
from django.dispatch import receiver
from reports.models import InterestRequestMaterial


@receiver(post_save, sender=InterestRequestMaterial)
def update_report_status_on_interest_request(sender, instance, created, **kwargs):
    """
    Atualiza o status do Report para 'Aguardando' quando um InterestRequestMaterial é criado.
    
    Signal disparado após salvar um InterestRequestMaterial. Se for uma nova instância
    (created=True) e houver um Report associado, atualiza o status do Report para '2' (Aguardando).
    
    Args:
        sender: O modelo que enviou o signal (InterestRequestMaterial)
        instance: A instância do InterestRequestMaterial que foi salva
        created: Boolean indicando se é uma nova instância
        **kwargs: Argumentos adicionais do signal
    """
    if created and instance.report:
        instance.report.status = '2'  # Aguardando
        instance.report.save(update_fields=['status'])
