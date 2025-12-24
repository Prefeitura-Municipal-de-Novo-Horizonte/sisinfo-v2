from django.test import TestCase
from django.utils import timezone
from fiscal.models import Invoice, DeliveryNote
from bidding_supplier.models import Supplier
from organizational_structure.models import Sector
from authenticate.models import ProfessionalUser

class InvoiceLogicTestCase(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(company="Test Supplier", cnpj="00000000000000", trade="Test")
        self.user = ProfessionalUser.objects.create_user(email="test@example.com", password="password", first_name="Test", last_name="User")
        self.sector = Sector.objects.create(name="Test Sector")
        self.invoice = Invoice.objects.create(
            number="123",
            supplier=self.supplier,
            issue_date=timezone.now().date()
        )

    def test_status_preparing(self):
        """Test status is 'preparing' when no deliveries exist."""
        self.assertEqual(self.invoice.delivery_process_status, 'preparing')

    def test_status_on_way_pending(self):
        """Test status is 'on_way' when a pending delivery exists."""
        DeliveryNote.objects.create(
            invoice=self.invoice,
            sector=self.sector,
            delivered_by=self.user,
            status='P'
        )
        self.assertEqual(self.invoice.delivery_process_status, 'on_way')

    def test_status_on_way_active(self):
        """Test status is 'on_way' when an active (A) delivery exists."""
        DeliveryNote.objects.create(
            invoice=self.invoice,
            sector=self.sector,
            delivered_by=self.user,
            status='A'
        )
        self.assertEqual(self.invoice.delivery_process_status, 'on_way')

    def test_status_delivered(self):
        """Test status is 'delivered' when all deliveries are completed."""
        DeliveryNote.objects.create(
            invoice=self.invoice,
            sector=self.sector,
            delivered_by=self.user,
            status='C'
        )
        self.assertEqual(self.invoice.delivery_process_status, 'delivered')

    def test_status_mixed_on_way(self):
        """Test status is 'on_way' if any delivery is not completed."""
        # One completed
        DeliveryNote.objects.create(
            invoice=self.invoice,
            sector=self.sector,
            delivered_by=self.user,
            status='C'
        )
        # One pending
        DeliveryNote.objects.create(
            invoice=self.invoice,
            sector=self.sector,
            delivered_by=self.user,
            status='P'
        )
        self.assertEqual(self.invoice.delivery_process_status, 'on_way')
