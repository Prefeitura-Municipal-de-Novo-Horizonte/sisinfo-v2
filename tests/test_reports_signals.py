from django.test import TestCase
from reports.models import Report, InterestRequestMaterial, Invoice
from bidding_supplier.models import Supplier
from organizational_structure.models import Sector, Direction
from authenticate.models import ProfessionalUser


class ReportSignalsTestCase(TestCase):
    """
    Testes para os signals do app reports.
    """

    def setUp(self):
        """Configuração inicial para os testes."""
        # Criar usuário
        self.user = ProfessionalUser.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
        
        # Criar direção e setor
        self.direction = Direction.objects.create(
            name="Diretoria de TI",
            accountable="João Silva"
        )
        self.sector = Sector.objects.create(
            name="Setor de Manutenção",
            direction=self.direction,
            accountable="Maria Santos"
        )
        
        # Criar report com status Aberto
        self.report = Report.objects.create(
            sector=self.sector,
            employee="Funcionário Teste",
            status='1',  # Aberto
            justification="Teste de justificativa",
            professional=self.user,
            pro_accountable=self.user
        )
        
        # Criar fornecedor e nota fiscal
        self.supplier = Supplier.objects.create(
            company="Test Supplier LTDA",
            cnpj="12345678000190",
            trade="Test Supplier"
        )
        self.invoice = Invoice.objects.create(
            note_number="123",
            supplier=self.supplier,
            note_issuance_date="2025-01-01"
        )

    def test_creating_interest_request_updates_report_status(self):
        """
        Signal deve atualizar Report.status para '2' (Aguardando) 
        ao criar InterestRequestMaterial.
        """
        # Verificar status inicial
        self.assertEqual(self.report.status, '1')
        
        # Criar InterestRequestMaterial
        interest = InterestRequestMaterial.objects.create(
            value="1000.00",
            kind='E',  # Empenho
            report=self.report,
            invoice=self.invoice
        )
        
        # Recarregar report do banco de dados
        self.report.refresh_from_db()
        
        # Verificar que o status foi atualizado
        self.assertEqual(self.report.status, '2')

    def test_updating_interest_request_does_not_change_report_status(self):
        """
        Signal não deve alterar status ao atualizar InterestRequestMaterial existente.
        """
        # Criar InterestRequestMaterial
        interest = InterestRequestMaterial.objects.create(
            value="1000.00",
            kind='E',
            report=self.report,
            invoice=self.invoice
        )
        
        # Mudar status do report manualmente para Finalizado
        self.report.status = '3'
        self.report.save()
        
        # Atualizar o InterestRequestMaterial
        interest.value = "2000.00"
        interest.save()
        
        # Recarregar report do banco de dados
        self.report.refresh_from_db()
        
        # Verificar que o status NÃO mudou (continua Finalizado)
        self.assertEqual(self.report.status, '3')

    def test_creating_interest_request_without_report_does_not_crash(self):
        """
        Signal não deve causar erro se InterestRequestMaterial for criado sem Report.
        """
        try:
            interest = InterestRequestMaterial.objects.create(
                value="1000.00",
                kind='S',  # Solicitação
                report=None,  # Sem report
                invoice=self.invoice
            )
            # Se chegou aqui, não houve erro
            self.assertIsNone(interest.report)
        except Exception as e:
            self.fail(f"Signal causou erro ao criar InterestRequestMaterial sem Report: {e}")
