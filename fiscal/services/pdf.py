from django.template.loader import render_to_string
from django.conf import settings
from decouple import config
import logging

logger = logging.getLogger(__name__)

# Região do Browserless (sfo, lon, ams)
BROWSERLESS_REGION = config('BROWSERLESS_REGION', default='sfo')


class DeliveryNotePDFGenerator:
    """Gerador de PDF para Fichas de Entrega usando Browserless.io."""
    
    @staticmethod
    def generate_delivery_pdf(delivery):
        """
        Gera PDF da ficha de entrega.
        
        Args:
            delivery: Instância do modelo DeliveryNote
            
        Returns:
            bytes: Conteúdo do PDF gerado
        """
        from playwright.sync_api import sync_playwright
        
        try:
            api_key = settings.BROWSERLESS_API_KEY
            
            # Detecta se já é uma URL completa (ws:// ou wss://) ou apenas o token
            if api_key.startswith('ws://') or api_key.startswith('wss://'):
                # URL completa fornecida (dev local ou produção com URL completa)
                browserless_url = api_key
            else:
                # Apenas o token foi fornecido - construir URL
                browserless_url = f"wss://production-{BROWSERLESS_REGION}.browserless.io?token={api_key}"
            
            # Renderizar template HTML
            # Ajustado para usar template do app fiscal
            html_content = render_to_string('fiscal/delivery/pdf_template.html', {
                'delivery': delivery,
                'items': delivery.items.all(),
            })
            
            logger.info(f"Gerando PDF para ficha de entrega #{delivery.pk}")
            
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(browserless_url, timeout=8000)
                page = browser.new_page()
                page.set_content(html_content, wait_until='load', timeout=5000)
                
                pdf_bytes = page.pdf(
                    format='A4',
                    print_background=True,
                    display_header_footer=True,
                    header_template=f'''
                        <div style="font-size: 10px; width: 100%; padding: 5px 15mm; display: flex; justify-content: space-between;">
                            <span>Ficha de Entrega #{delivery.pk}</span>
                            <span>Página <span class="pageNumber"></span> de <span class="totalPages"></span></span>
                        </div>
                    ''',
                    footer_template='<div></div>',
                    margin={
                        'top': '20mm',
                        'bottom': '20mm',
                        'left': '10mm',
                        'right': '10mm'
                    }
                )
                
                browser.close()
                logger.info(f"PDF gerado com sucesso para ficha de entrega #{delivery.pk}")
                return pdf_bytes
                
        except Exception as e:
            logger.error(f"Erro ao gerar PDF para ficha de entrega #{delivery.pk}: {str(e)}")
            raise
