from django.db import models

from authenticate.models import ProfessionalUser
from dashboard.models import Sector


# Create your models here.
class Service(models.Model):
    sector = models.ForeignKey(
        Sector, on_delete=models.DO_NOTHING, blank=True, verbose_name="setor"
    )
    employeer = models.CharField("funcionario", max_length=150)
    room = models.CharField("sala", max_length=100)
    slug = models.SlugField("slug")
    professional = models.ForeignKey(
        ProfessionalUser,
        on_delete=models.DO_NOTHING,
        verbose_name="profissional",
        related_name="profissional",
    )
    pro_accountable = models.ForeignKey(
        ProfessionalUser,
        on_delete=models.DO_NOTHING,
        verbose_name="profissional responsável",
        related_name="responsável",
    )
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)



class OrderOfService(models.Model):
    pass
