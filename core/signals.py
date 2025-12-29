"""
Signals para invalidação automática de cache.

Quando um modelo é criado, editado ou deletado, o cache correspondente é invalidado.
"""
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from core.cache import CachedLists

logger = logging.getLogger(__name__)


# --- Fornecedores ---
@receiver(post_save, sender='bidding_supplier.Supplier')
@receiver(post_delete, sender='bidding_supplier.Supplier')
def invalidate_supplier_cache(sender, instance, **kwargs):
    """Invalida cache de fornecedores ao criar/editar/deletar."""
    CachedLists.invalidate_suppliers()
    logger.debug(f"Cache de fornecedores invalidado: {instance}")


# --- Setores ---
@receiver(post_save, sender='organizational_structure.Sector')
@receiver(post_delete, sender='organizational_structure.Sector')
def invalidate_sector_cache(sender, instance, **kwargs):
    """Invalida cache de setores ao criar/editar/deletar."""
    CachedLists.invalidate_sectors()
    logger.debug(f"Cache de setores invalidado: {instance}")


# --- Diretorias ---
@receiver(post_save, sender='organizational_structure.Direction')
@receiver(post_delete, sender='organizational_structure.Direction')
def invalidate_direction_cache(sender, instance, **kwargs):
    """Invalida cache de diretorias ao criar/editar/deletar."""
    CachedLists.invalidate_directions()
    logger.debug(f"Cache de diretorias invalidado: {instance}")


# --- Materiais ---
@receiver(post_save, sender='bidding_procurement.Material')
@receiver(post_delete, sender='bidding_procurement.Material')
def invalidate_material_cache(sender, instance, **kwargs):
    """Invalida cache de materiais ao criar/editar/deletar."""
    CachedLists.invalidate_materials()
    logger.debug(f"Cache de materiais invalidado: {instance}")


# --- Licitações ---
@receiver(post_save, sender='bidding_procurement.Bidding')
@receiver(post_delete, sender='bidding_procurement.Bidding')
def invalidate_bidding_cache(sender, instance, **kwargs):
    """Invalida cache de licitações ao criar/editar/deletar."""
    CachedLists.invalidate_biddings()
    logger.debug(f"Cache de licitações invalidado: {instance}")


# --- Laudos (invalida dashboard) ---
@receiver(post_save, sender='reports.Report')
@receiver(post_delete, sender='reports.Report')
def invalidate_dashboard_on_report_change(sender, instance, **kwargs):
    """Invalida cache do dashboard quando laudos são alterados."""
    from dashboard.services import DashboardService
    DashboardService.invalidate_dashboard_cache()
    logger.debug(f"Cache do dashboard invalidado por laudo: {instance}")
