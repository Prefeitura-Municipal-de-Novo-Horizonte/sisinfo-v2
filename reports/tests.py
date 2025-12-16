from django.test import TestCase, Client
from django.urls import reverse
from authenticate.models import ProfessionalUser
from reports.models import Report
from organizational_structure.models import Sector

class ReportViewTests(TestCase):
    def setUp(self):
        # Create a professional user
        self.user = ProfessionalUser.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='password123',
            is_tech=True
        )
        self.sector = Sector.objects.create(name='Test Sector', slug='test-sector')
        self.report = Report.objects.create(
            number_report='001/2024',
            slug='001-2024',
            sector=self.sector,
            justification='Test justification',
            professional=self.user,
            pro_accountable=self.user,
            status='1'
        )
        self.client = Client()
        
    def test_report_list_view_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('reports:reports'))
        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(response.status_code in [301, 302])

    def test_report_list_view_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('reports:reports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports.html')
        self.assertContains(response, '001/2024')

    def test_report_detail_view_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('reports:report_view', kwargs={'slug': self.report.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'report.html')
        self.assertEqual(response.context['report'], self.report)

    def test_report_pdf_view_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('reports:pdf_report', kwargs={'slug': self.report.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pdf_template.html')

    def test_report_update_view_permission(self):
        # Test permission: only professional/pro_accountable can edit
        other_user = ProfessionalUser.objects.create_user(
            email='other@example.com', first_name='Other', last_name='User', password='password'
        )
        self.client.force_login(other_user)
        response = self.client.get(reverse('reports:report_update', kwargs={'slug': self.report.slug}))
        # Expect redirect or warning (from code implementation)
        # Note: Code redirects to reports:reports with warning
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('reports:reports'))
        
        self.client.force_login(self.user)
        response = self.client.get(reverse('reports:report_update', kwargs={'slug': self.report.slug}))
        self.assertEqual(response.status_code, 200)
