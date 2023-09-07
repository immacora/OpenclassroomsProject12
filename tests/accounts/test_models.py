import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

CustomUser = get_user_model()


class TestCreateUsers:
    """
    GIVEN a new_custom_user fixture
    WHEN user is created
    THEN checks that his permissions are ok
    """

    def test_create_default_user(self, new_custom_user):
        """
        Tests if default user creation :
            is True for is_active,
            is False for is_staff and is_superuser,
            does not have permission.
        """
        assert CustomUser.objects.count() == 1
        assert new_custom_user.is_active
        assert new_custom_user.is_staff is False
        assert new_custom_user.is_superuser is False
        assert new_custom_user.get_all_permissions() == set()

    def test_create_user_with_not_unique_email_raises_error(self, new_custom_user):
        """Tests if user creation raise IntegrityError with not unique email."""
        with pytest.raises(IntegrityError):
            CustomUser.objects.create(
                email=new_custom_user.email, password="123456789!"
            )

    def test_create_superuser(self, new_superuser):
        """Tests if superuser creation has an email and is True for is_active, is_staff and is_superuser."""
        assert CustomUser.objects.count() == 1
        assert new_superuser.email is not None
        assert new_superuser.is_active
        assert new_superuser.is_staff
        assert new_superuser.is_superuser
