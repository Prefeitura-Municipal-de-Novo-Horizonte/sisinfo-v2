from django.test import TestCase, RequestFactory
from django.template.loader import render_to_string
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.core.paginator import Paginator

from organizational_structure.models import Direction, Sector
from organizational_structure.forms import SectorForm, DirectionForm
from bidding_supplier.models import Supplier
from bidding_supplier.forms import SupplierForm
from bidding_procurement.models import Material, Bidding
from reports.models import Report
from authenticate.models import ProfessionalUser
from authenticate.forms import UserCreationForm, LoginForm

class TemplateRenderingTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = ProfessionalUser.objects.create_user(username='testuser', password='password')
        
        # Create dummy data
        self.direction = Direction.objects.create(name="Diretoria Teste", slug="diretoria-teste")
        self.sector = Sector.objects.create(name="Setor Teste", slug="setor-teste", direction=self.direction)
        self.supplier = Supplier.objects.create(trade_name="Fornecedor Teste", slug="fornecedor-teste")
        self.material = Material.objects.create(name="Material Teste", slug="material-teste")
        self.bidding = Bidding.objects.create(name="Licitacao Teste", slug="licitacao-teste")
        
    def render_template(self, template_name, context=None):
        if context is None:
            context = {}
        request = self.factory.get('/')
        request.user = self.user
        context['request'] = request
        return render_to_string(template_name, context)

    def test_organizational_structure_diretorias(self):
        context = {
            'directions': Direction.objects.all(),
            'form': DirectionForm(),
            'total_directions': 1,
            'total_sectors': 1,
        }
        try:
            self.render_template('organizational_structure/diretorias.html', context)
        except Exception as e:
            self.fail(f"Failed to render diretorias.html: {e}")

    def test_organizational_structure_setores(self):
        paginator = Paginator(Sector.objects.all(), 10)
        page_obj = paginator.get_page(1)
        context = {
            'page_obj': page_obj,
            'form': SectorForm(),
            # Mocking filter form which is usually passed via myFilter.form
            'myFilter': type('obj', (object,), {'form': SectorForm()}), 
        }
        try:
            self.render_template('organizational_structure/setores.html', context)
        except Exception as e:
            self.fail(f"Failed to render setores.html: {e}")

    def test_organizational_structure_setor_detail(self):
        context = {
            'sector': self.sector,
            'reports': [],
        }
        try:
            self.render_template('organizational_structure/setor_detail.html', context)
        except Exception as e:
            self.fail(f"Failed to render setor_detail.html: {e}")

    def test_bidding_procurement_materials(self):
        paginator = Paginator(Material.objects.all(), 10)
        page_obj = paginator.get_page(1)
        # Mocking a filter object with a form attribute
        class MockFilter:
            form = type('obj', (object,), {'as_p': lambda: ''}) # Minimal mock
            qs = Material.objects.all()
            
        context = {
            'page_obj': page_obj,
            'myFilter': MockFilter(),
        }
        # Note: materials.html might expect specific form fields in myFilter.form
        # If it fails, we'll need to import the actual MaterialFilter
        
        try:
            self.render_template('bidding_procurement/materials.html', context)
        except Exception as e:
            self.fail(f"Failed to render materials.html: {e}")

    def test_bidding_supplier_suppliers(self):
        paginator = Paginator(Supplier.objects.all(), 10)
        page_obj = paginator.get_page(1)
        context = {
            'page_obj': page_obj,
            'form': SupplierForm(),
            'formset': None, # suppliers.html checks for formset
        }
        try:
            self.render_template('bidding_supplier/suppliers.html', context)
        except Exception as e:
            self.fail(f"Failed to render suppliers.html: {e}")

    def test_bidding_supplier_supllier_detail(self):
        context = {
            'supplier': self.supplier,
        }
        try:
            self.render_template('bidding_supplier/supllier.html', context)
        except Exception as e:
            self.fail(f"Failed to render supllier.html: {e}")

    def test_reports_reports(self):
        paginator = Paginator(Report.objects.all(), 10)
        page_obj = paginator.get_page(1)
        
        # We need the actual filter form here because the template renders specific fields
        from reports.filters import ReportFilter
        f = ReportFilter(queryset=Report.objects.all())
        
        context = {
            'page_obj': page_obj,
            'myFilter': f,
        }
        try:
            self.render_template('reports/templates/reports.html', context)
        except Exception as e:
            # Try without 'templates/' prefix if configured that way
            try:
                self.render_template('reports.html', context)
            except Exception as e2:
                 self.fail(f"Failed to render reports.html: {e} | {e2}")

    def test_authenticate_users(self):
        context = {
            'users': ProfessionalUser.objects.all(),
        }
        try:
            self.render_template('authenticate/users.html', context)
        except Exception as e:
            self.fail(f"Failed to render users.html: {e}")

    def test_bidding_procurement_bidding_detail(self):
        context = {
            'licitacao': self.bidding,
            'material_associations': [],
            'total_materiais': 0,
            'btn': 'Vincular Material',
        }
        try:
            self.render_template('bidding_procurement/bidding_detail.html', context)
        except Exception as e:
            self.fail(f"Failed to render bidding_detail.html: {e}")

    def test_authenticate_login(self):
        context = {
            'form': LoginForm(),
        }
        try:
            self.render_template('authenticate/login.html', context)
        except Exception as e:
            self.fail(f"Failed to render login.html: {e}")
