from django.contrib.auth import get_user_model
from django.test import TestCase

CustomUser = get_user_model()


class CustomUserTests(TestCase):
    """Test user creation."""

    def test_create_user(self):
        """Tests if default user creation is False for staff and superuser."""

        user = CustomUser.objects.create_user(email="testcreateuser@email.com", password="123456789!")
        self.assertEqual(user.email, "testcreateuser@email.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Tests if default superuser creation is True for staff and superuser."""

        admin_user = CustomUser.objects.create_superuser(email="testcreatesuperuser@email.com", password="123456789!")
        self.assertEqual(admin_user.email, "testcreatesuperuser@email.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
