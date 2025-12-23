from datetime import date, datetime
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.core.exceptions import PermissionDenied
from reports.models import Report, MaterialReport


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
    # Skip se está carregando dados via loaddata (raw=True)
    if kwargs.get('raw', False):
        return
    
    try:
        if not instance.unitary_price and instance.material_bidding:
            # Usa o preço total (com reajuste) do MaterialBidding
            instance.unitary_price = instance.material_bidding.total_price()
    except Exception:
        # Ignora erro durante loaddata quando objetos relacionados não existem ainda
        pass


@receiver(pre_delete, sender='bidding_procurement.MaterialBidding')
def protect_material_reports(sender, instance, **kwargs):
    """
    Previne deleção de MaterialBidding que tem MaterialReports associados.
    
    Este signal protege a integridade dos laudos, impedindo que MaterialBiddings
    sejam deletados quando há laudos dependentes.
    """
    # Verificar se há MaterialReports usando este MaterialBidding
    reports = MaterialReport.objects.filter(material_bidding=instance)
    
    if reports.exists():
        raise PermissionDenied(
            f'❌ Não é possível deletar MaterialBidding {instance.id} '
            f'({instance.material.name}) pois há {reports.count()} laudos associados! '
            f'Para deletar, primeiro remova ou reatribua os laudos.'
        )

