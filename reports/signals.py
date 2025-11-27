from datetime import date, datetime
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from reports.models import Report, MaterialReport, InterestRequestMaterial


@receiver(pre_save, sender=Report)
def generate_report_identifier(sender, instance, **kwargs):
    """
    Gera identificador único (number_report) e slug para o Report.
    """
    if not instance.slug:
        if not instance.number_report:
            reports_count = Report.objects.filter(created_at__date=date.today()).count()
            # Garante que sector existe antes de acessar id
            sector_id = instance.sector.id if instance.sector else 0
            instance.number_report = datetime.now().strftime('%Y%m%d') + \
                f"{sector_id:03}" + f"{(reports_count + 1):03}"
        instance.slug = slugify(instance.number_report)


@receiver(pre_save, sender=MaterialReport)
def set_material_report_price(sender, instance, **kwargs):
    """
    Define o preço unitário do MaterialReport baseado no MaterialBidding associado.
    """
    if not instance.unitary_price and instance.material_bidding:
        # Usa o preço total (com reajuste) do MaterialBidding
        instance.unitary_price = instance.material_bidding.total_price()


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
    if created and instance.report and instance.report.status == '1':
        instance.report.status = '2'  # Aguardando
        instance.report.save(update_fields=['status'])
