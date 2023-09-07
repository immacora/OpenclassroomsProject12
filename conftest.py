import pytest
from pytest_factoryboy import register
from tests.factories import CustomUserFactory

register(CustomUserFactory)


@pytest.fixture
def new_custom_user(db, custom_user_factory):
    user = custom_user_factory.create()
    return user


@pytest.fixture
def new_superuser(db, custom_user_factory):
    superuser = custom_user_factory.create(is_staff=True, is_superuser=True)
    return superuser
