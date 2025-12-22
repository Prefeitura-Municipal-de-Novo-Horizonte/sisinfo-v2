import uuid
from django.db import models
from django.utils import timezone


class BackupJob(models.Model):
    """
    Job de backup assíncrono.
    Permite contornar o limite de 10s da Vercel dividindo o processo em múltiplas requests.
    """
    STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField('status', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Resultado do backup (JSON string)
    result = models.TextField('resultado', blank=True)
    error_message = models.TextField('mensagem de erro', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    started_at = models.DateTimeField('iniciado em', null=True, blank=True)
    completed_at = models.DateTimeField('concluído em', null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'job de backup'
        verbose_name_plural = 'jobs de backup'
    
    def __str__(self):
        return f"Backup Job {self.id} ({self.get_status_display()})"
    
    def mark_processing(self):
        """Marca o job como em processamento."""
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
    
    def mark_completed(self, result: str):
        """Marca o job como concluído com sucesso."""
        self.status = 'completed'
        self.result = result
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'result', 'completed_at'])
    
    def mark_failed(self, error: str):
        """Marca o job como falhou."""
        self.status = 'failed'
        self.error_message = error
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])
