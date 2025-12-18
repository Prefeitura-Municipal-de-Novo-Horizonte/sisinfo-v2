from django.test import TestCase, RequestFactory
from django.urls import reverse
from fiscal.models import Invoice
from bidding_supplier.models import Supplier
from organizational_structure.models import Sector, Direction
from authenticate.models import ProfessionalUser
from reports.views import generate_pdf_report
from unittest.mock import patch, MagicMock

class PDFGenerationTestCase(TestCase):
    def setUp(self):
        # Setup similar to signals test
        self.user = ProfessionalUser.objects.create_user(
            email="pdf_test@example.com",
            password="testpass123",
            first_name="PDF",
            last_name="Tester"
        )
        self.direction = Direction.objects.create(name="Diretoria PDF", accountable="João PDF")
        self.sector = Sector.objects.create(name="Setor PDF", direction=self.direction, accountable="Maria PDF")
        self.report = Report.objects.create(
            sector=self.sector,
            employee="Funcionario PDF",
            status='1',
            justification="Teste PDF",
            professional=self.user,
            pro_accountable=self.user
        )
        self.factory = RequestFactory()

    @patch('reports.pdf_generator.PDFGenerator.generate_report_pdf')
    def test_generate_pdf_view_success(self, mock_generate_pdf):
        """
        Testa se a view chama o gerador de PDF e retorna o arquivo corretamente.
        """
        # Mock do retorno do gerador (bytes de um PDF fake)
        mock_generate_pdf.return_value = b'%PDF-1.4 fake content'
        
        request = self.factory.get(reverse('reports:generate_pdf', kwargs={'slug': self.report.slug}))
        request.user = self.user
        
        response = generate_pdf_report(request, slug=self.report.slug)
        
        # Verifica se o gerador foi chamado com o report correto
        mock_generate_pdf.assert_called_once_with(self.report)
        
        # Verifica a resposta HTTP
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn(f'filename="laudo_{self.report.number_report}.pdf"', response['Content-Disposition'])

    @patch('reports.pdf_generator.PDFGenerator.generate_report_pdf')
    def test_generate_pdf_view_error(self, mock_generate_pdf):
        """
        Testa se a view lida corretamente com erros na geração do PDF.
        """
        # Mock para lançar exceção
        mock_generate_pdf.side_effect = Exception("Browserless error")
        
        request = self.factory.get(reverse('reports:generate_pdf', kwargs={'slug': self.report.slug}))
        request.user = self.user
        
        # Precisamos configurar o messages framework para o request mockado
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        response = generate_pdf_report(request, slug=self.report.slug)
        
        # Deve redirecionar de volta para o report_view em caso de erro
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('reports:report_view', kwargs={'slug': self.report.slug})))
