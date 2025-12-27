"""
Serviço de envio de emails para o módulo fiscal.
"""
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from decouple import config

logger = logging.getLogger(__name__)


def send_delivery_notification(delivery):
    """
    Envia email notificando Patrimônio sobre entrega de materiais.
    CC para TI Documentação.
    
    Args:
        delivery: Instância de DeliveryNote com status 'C' (Concluída)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    email_patrimonio = config('EMAIL_PATRIMONIO', default='patrimonio@novohorizonte.sp.gov.br')
    email_ti_doc = config('EMAIL_TI_DOC', default='ti@novohorizonte.sp.gov.br')
    from_email = config('DEFAULT_FROM_EMAIL', default='ti@novohorizonte.sp.gov.br')
    
    subject = f'[SISInfo] Entrega de Materiais - {delivery.sector}'
    
    logger.info(f"Preparando email de entrega #{delivery.pk}")
    logger.info(f"  De: {from_email}")
    logger.info(f"  Para: {email_patrimonio}")
    logger.info(f"  CC: {email_ti_doc}")
    
    # Buscar itens com relacionamentos para evitar N+1
    items = delivery.items.select_related(
        'invoice_item__material_bidding__material'
    ).all()
    
    context = {
        'delivery': delivery,
        'items': items,
    }
    
    try:
        html_content = render_to_string('fiscal/email/delivery_notification.html', context)
        text_content = render_to_string('fiscal/email/delivery_notification.txt', context)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[email_patrimonio],
            cc=[email_ti_doc],
        )
        email.attach_alternative(html_content, 'text/html')
        
        # Enviar e capturar resultado
        sent_count = email.send(fail_silently=False)
        
        if sent_count > 0:
            logger.info(f"✅ Email de entrega #{delivery.pk} enviado com sucesso!")
            logger.info(f"   Destinatário: {email_patrimonio}")
            logger.info(f"   CC: {email_ti_doc}")
            return True, f"Email enviado para {email_patrimonio}"
        else:
            logger.warning(f"⚠️ Email de entrega #{delivery.pk} retornou sent_count=0")
            return False, "Email não foi enviado (sent_count=0)"
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Erro ao enviar email de entrega #{delivery.pk}: {error_msg}")
        return False, f"Erro: {error_msg}"
