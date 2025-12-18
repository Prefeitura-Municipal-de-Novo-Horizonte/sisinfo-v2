from django.test import TestCase
from fiscal.models import Invoice
from bidding_supplier.models import Supplier
from bidding_procurement.models import Material, Bidding, MaterialBidding
from organizational_structure.models import Sector, Direction
from authenticate.models import ProfessionalUser
from datetime import date, datetime


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

        # Criar Material, Bidding e MaterialBidding para testes de preço
        self.material = Material.objects.create(name="Material Teste")
        self.bidding = Bidding.objects.create(name="Licitação Teste", date=date.today())
        self.material_bidding = MaterialBidding.objects.create(
            material=self.material,
            bidding=self.bidding,
            price="100.00",
            readjustment=10.0, # 10% de reajuste, total deve ser 110.00
            supplier=self.supplier
        )

    def test_report_identifier_generation(self):
        """
        Signal deve gerar number_report e slug automaticamente.
        """
        report = Report.objects.create(
            sector=self.sector,
            employee="Outro Funcionário",
            justification="Teste ID",
            professional=self.user,
            pro_accountable=self.user
        )
        self.assertIsNotNone(report.number_report)
        self.assertIsNotNone(report.slug)
        # Formato esperado: YYYYMMDD + sector_id(3) + count(3)
        expected_prefix = datetime.now().strftime('%Y%m%d')
        self.assertTrue(report.number_report.startswith(expected_prefix))

    def test_material_report_price_setting(self):
        """
        Signal deve definir unitary_price do MaterialReport baseado no MaterialBidding.
        """
        material_report = MaterialReport.objects.create(
            report=self.report,
            material_bidding=self.material_bidding,
            quantity=2
        )
        # Preço base 100 + 10% = 110.00
        self.assertEqual(float(material_report.unitary_price), 110.00)
        
        # Total deve ser 2 * 110 = 220.00
        self.assertEqual(float(material_report.total_price()), 220.00)

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
