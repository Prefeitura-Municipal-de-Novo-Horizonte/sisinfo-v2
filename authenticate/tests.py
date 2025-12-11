from django.test import TestCase

from authenticate.models import ProfessionalUser


class PermissionsModelTest(TestCase):
    def setUp(self):
        self.non_admin_user = ProfessionalUser.objects.create_user(
            email='testuser@example.com',
            first_name='Test',
            last_name='User',
            password='password123'
        )

        self.admin_user = ProfessionalUser.objects.create_superuser(
            email='adminuser@example.com',
            first_name='Admin',
            last_name='User',
            password='password123'
        )

    def test_non_admin_has_no_permissions(self):
        """
        Garante que um usuário não-admin não tenha permissões.
        """
        self.assertFalse(self.non_admin_user.has_perm('any.permission'))
        self.assertFalse(self.non_admin_user.has_module_perms('any_app'))

    def test_admin_has_all_permissions(self):
        """
        Garante que um usuário admin tenha todas as permissões.
        """
        self.assertTrue(self.admin_user.has_perm('any.permission'))
        self.assertTrue(self.admin_user.has_module_perms('any_app'))

    def test_get_absolute_url(self):
        """
        Testa se o método get_absolute_url retorna a URL correta para o perfil do usuário.
        """
        expected_url = f'/authenticate/profile_user/{self.non_admin_user.slug}'
        self.assertEqual(self.non_admin_user.get_absolute_url(), expected_url)

from django.test import Client
from django.urls import reverse

class AuthenticationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = ProfessionalUser.objects.create_user(
            email='testuser@example.com',
            first_name='Test',
            last_name='User',
            password='password123'
        )
        # A view that requires login. 'show_users' is a good candidate.
        self.protected_url = reverse('authenticate:show_users')
        self.login_url = reverse('authenticate:login')

    def test_redirect_if_not_logged_in(self):
        """
        Garante que o usuário seja redirecionado para a página de login se não estiver autenticado.
        """
        response = self.client.get(self.protected_url)
        # Check for redirect, status code 302
        self.assertEqual(response.status_code, 302)
        # Check if it redirects to the correct login page
        self.assertRedirects(response, f'{self.login_url}?next={self.protected_url}')
