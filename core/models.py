"""
Models centralizados do projeto.
"""
from django.db import models


class BaseModel(models.Model):
    """
    Model abstrato base com campos comuns.
    
    Todos os novos models devem herdar desta classe para garantir
    consistência nos campos de timestamp.
    
    Exemplo:
        class MyModel(BaseModel):
            name = models.CharField(max_length=100)
            
            class Meta(BaseModel.Meta):
                verbose_name = 'meu model'
    """
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']


class DeploymentProcedure(models.Model):
    """
    Rastreia procedimentos executados durante deploy.
    Previne execução duplicada de comandos de manutenção.
    """
    name = models.CharField(
        "nome do procedimento",
        max_length=100,
        unique=True,
        help_text="Identificador único do procedimento (ex: consolidate_duplicates_v1)"
    )
    executed_at = models.DateTimeField(
        "executado em",
        auto_now_add=True
    )
    success = models.BooleanField(
        "sucesso",
        default=True,
        help_text="Se o procedimento foi executado com sucesso"
    )
    notes = models.TextField(
        "notas",
        blank=True,
        help_text="Informações adicionais sobre a execução"
    )
    
    class Meta:
        ordering = ['-executed_at']
        verbose_name = "procedimento de deploy"
        verbose_name_plural = "procedimentos de deploy"
    
    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.name} ({self.executed_at.strftime('%Y-%m-%d %H:%M')})"
