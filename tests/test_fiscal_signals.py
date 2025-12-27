from django.test import TestCase
from unittest.mock import patch, MagicMock
from decimal import Decimal
from fiscal.models import Invoice, InvoiceItem, DeliveryNote, DeliveryNoteItem, StockItem
from bidding_supplier.models import Supplier
from bidding_procurement.models import Material, Bidding, MaterialBidding
from organizational_structure.models import Sector
from authenticate.models import ProfessionalUser
from datetime import date
from django.utils import timezone

class FiscalSignalsTestCase(TestCase):
    def setUp(self):
        # Setup básico
        self.supplier = Supplier.objects.create(
            company="Test Supplier", cnpj="12345678000100", trade="Test")
        
        self.bidding = Bidding.objects.create(name="Licitação 01", date=date.today())
        self.material = Material.objects.create(name="Material A")
        
        # MaterialBidding com quantidade comprada inicial de 0
        self.material_bidding = MaterialBidding.objects.create(
            material=self.material,
            bidding=self.bidding,
            supplier=self.supplier,
            price="10.00",
            quantity_purchased=0,
            quantity=100  # Limite de 100
        )
        
        self.invoice = Invoice.objects.create(
            number="100",
            supplier=self.supplier,
            issue_date=date.today()
        )

    def test_invoice_item_creation_updates_financial_and_physical(self):
        """Testa se criar item atualiza MaterialBidding (Financeiro) e StockItem (Físico)."""
        item = InvoiceItem.objects.create(
            invoice=self.invoice,
            material_bidding=self.material_bidding,
            quantity=10,
            unit_price=Decimal("10.00")
        )
        
        # 1. Verifica Financeiro (MaterialBidding)
        self.material_bidding.refresh_from_db()
        self.assertEqual(self.material_bidding.quantity_purchased, 10)
        
        # 2. Verifica Físico (StockItem)
        stock_item = StockItem.objects.get(material_bidding=self.material_bidding)
        self.assertEqual(stock_item.quantity, 10)

    def test_invoice_item_deletion_restores_financial_and_physical(self):
        """Testa se excluir item estorna ambos os saldos."""
        item = InvoiceItem.objects.create(
            invoice=self.invoice,
            material_bidding=self.material_bidding,
            quantity=5,
            unit_price=Decimal("10.00")
        )
        
        # Deleta o item
        item.delete()
        
        # 1. Verifica Financeiro (estornado para 0)
        self.material_bidding.refresh_from_db()
        self.assertEqual(self.material_bidding.quantity_purchased, 0)
        
        # 2. Verifica Físico (estornado para 0)
        stock_item = StockItem.objects.get(material_bidding=self.material_bidding)
        self.assertEqual(stock_item.quantity, 0)

    def test_delivery_decreases_physical_stock_only(self):
        """Testa se Entrega diminui APENAS o StockItem, mantendo MaterialBidding intacto."""
        # Compra 10 itens
        inv_item = InvoiceItem.objects.create(
            invoice=self.invoice,
            material_bidding=self.material_bidding,
            quantity=10,
            unit_price=Decimal("10.00")
        )
        
        # Cria Entrega de 3 itens
        delivery = DeliveryNote.objects.create(
            invoice=self.invoice,
            sector=Sector.objects.create(name="Setor X"), # Mock setor se precisar
            received_by="João",
            received_at=timezone.now(),
            delivered_by=ProfessionalUser.objects.create_user(email="t-user", password="p", first_name="Test", last_name="User")
        )
        
        del_item = DeliveryNoteItem.objects.create(
            delivery_note=delivery,
            invoice_item=inv_item,
            quantity_delivered=3
        )
        
        # 1. Verifica Financeiro (NÃO deve mudar, continua 10 comprados)
        self.material_bidding.refresh_from_db()
        self.assertEqual(self.material_bidding.quantity_purchased, 10)
        
        # 2. Verifica Físico (Deve cair para 7)
        stock_item = StockItem.objects.get(material_bidding=self.material_bidding)
        self.assertEqual(stock_item.quantity, 7)

    @patch('fiscal.services.storage.delete_image_from_storage')
    def test_invoice_deletion_removes_supabase_image(self, mock_delete):
        """Testa se excluir a nota deleta a imagem do Supabase Storage."""
        # Simula uma imagem do Supabase Storage (UUID.jpg)
        self.invoice.photo = "a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg"
        self.invoice.save()
        
        # Deleta a nota
        self.invoice.delete()
        
        # Verifica se o método delete foi chamado com o path correto
        mock_delete.assert_called_once_with("a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg")
