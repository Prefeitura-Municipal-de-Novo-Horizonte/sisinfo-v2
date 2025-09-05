from django.test import TestCase

from authenticate.models import ProfessionalUser


class PermissionsModelTest(TestCase):
    def setUp(self):
        self.non_admin_user = ProfessionalUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            first_name='Test',
            last_name='User',
            password='password123'
        )

        self.admin_user = ProfessionalUser.objects.create_superuser(
            username='adminuser',
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