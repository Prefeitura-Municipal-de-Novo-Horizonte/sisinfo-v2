from datetime import date, datetime

from django.db import models
from django.shortcuts import resolve_url as r
from django.template.defaultfilters import slugify

from authenticate.models import ProfessionalUser
from dashboard.models import Sector


# Create your models here.
class Service(models.Model):
    number_service = models.CharField(
        "identificação do atendimento",
        max_length=20,
        unique=True,
        blank=True,
        null=True,
    )
    slug = models.SlugField("slug")
    sector = models.ForeignKey(
        Sector,
        on_delete=models.DO_NOTHING,
        verbose_name="setor",
        related_name="setor",
    )
    room = models.CharField("sala referente", max_length=20, blank=True)
    details = models.TextField("detalhes do atendimento")
    fullname_employee = models.CharField(
        "nome completo do funcionario", max_length=100, null=True, blank=True
    )
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
    status = models.BooleanField("status", default=True)
    created_at = models.DateTimeField(
        "criado em",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        "atualizado em",
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at", "status", "-updated_at"]
        verbose_name = "atendimento"
        verbose_name_plural = "atendimentos"

    def __str__(self):
        return self.number_service

    def get_absolute_url(self):
        return r("services:service_view", slug=self.slug)

    def save(self, *args, **kwargs):
        service = Service.objects.filter(created_at__date=date.today()).count()
        if not self.slug:
            if not self.number_service:
                self.number_service = (
                    datetime.now().strftime("%Y%m%d")
                    + f"{self.sector.id:03}"
                    + f"{(service + 1):03}"
                )
            self.slug = slugify(self.number_service)
        return super().save()
