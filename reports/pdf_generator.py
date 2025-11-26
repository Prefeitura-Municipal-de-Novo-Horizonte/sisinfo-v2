"""
PDF Generator para o app Reports usando Playwright e Browserless.io.

Este módulo fornece funcionalidade para gerar PDFs de laudos técnicos
usando o serviço Browserless.io para renderização de HTML/CSS.
"""
from playwright.sync_api import sync_playwright
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    Gerador de PDFs para laudos técnicos.
    
    Utiliza Playwright conectado ao Browserless.io para renderizar
    templates HTML em PDFs com alta fidelidade.
    """

    @staticmethod
    def generate_report_pdf(report):
        """
        Gera PDF do laudo técnico.
        
        Args:
            report: Instância do modelo Report
            
        Returns:
            bytes: Conteúdo do PDF gerado
            
        Raises:
            Exception: Se houver erro na geração do PDF
        """
        try:
            # URL do Browserless com API key (novo endpoint de produção)
            browserless_url = f"wss://production-sfo.browserless.io?token={settings.BROWSERLESS_API_KEY}"
            
            # Renderizar template HTML com CSS inline
            html_content = render_to_string('pdf_download_template.html', {'report': report})
            
            logger.info(f"Gerando PDF para laudo {report.number_report}")
            
            with sync_playwright() as p:
                # Conectar ao Browserless via WebSocket
                browser = p.chromium.connect_over_cdp(browserless_url)
                page = browser.new_page()
                
                # Carregar conteúdo HTML
                page.set_content(html_content, wait_until='networkidle')
                
                # Gerar PDF com configurações A4
                pdf_bytes = page.pdf(
                    format='A4',
                    print_background=True,
                    margin={
                        'top': '20mm',
                        'bottom': '20mm',
                        'left': '10mm',
                        'right': '10mm'
                    }
                )
                
                browser.close()
                logger.info(f"PDF gerado com sucesso para laudo {report.number_report}")
                return pdf_bytes
                
        except Exception as e:
            logger.error(f"Erro ao gerar PDF para laudo {report.number_report}: {str(e)}")
            raise
