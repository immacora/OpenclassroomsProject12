import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from faker import Faker

from clients.models import Client
from locations.models import Location

fake = Faker()
CustomUser = get_user_model()


class TestClients:
    def test_create_client(self, new_sales_contact, new_location):
        """Tests client creation."""

        client = Client.objects.create(
            company_name="Test Company",
            siren="123456789",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email="client@test.com",
            phone_number="+33654871599",
            sales_contact=new_sales_contact,
        )
        client.locations.add(new_location)
        assert Client.objects.count() == 1
        assert client.locations.count() == 1
        assert client.contract_requested is False

    def test_create_client_with_not_unique_siren_raises_error(self, new_client):
        """Tests if client creation raise IntegrityError with not unique siren."""

        with pytest.raises(IntegrityError):
            Client.objects.create(
                company_name="Test Company",
                siren=new_client.siren,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email="client@test.com",
                phone_number="1234567890",
                sales_contact=new_client.sales_contact,
            )
            assert Client.objects.count() == 0
            assert Location.objects.count() == 0

    def test_delete_client_and_his_location(self, new_client):
        """Tests if client deletion delete his location.."""

        assert Client.objects.count() == 1
        assert Location.objects.count() == 1
        new_client.delete()
        assert Client.objects.count() == 0
        assert Location.objects.count() == 0
