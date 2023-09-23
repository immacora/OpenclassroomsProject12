import pytest
from django.db.utils import IntegrityError

from clients.models import Client
from locations.models import Location


class TestClients:
    def test_create_client(self, new_sales_contact, new_location):
        """Tests client creation."""

        client = Client.objects.create(
            company_name="TEST Create company",
            siren="123456789",
            first_name="TEST Create first name",
            last_name="TEST Create last name",
            email="TESTCREATEclient@test.com",
            phone_number="+33654871599",
            sales_contact=new_sales_contact,
        )
        client.locations.add(new_location)
        assert Client.objects.count() == 1
        assert client.locations.count() == 1
        assert client.client_id is not None
        assert client.company_name == "TEST Create company"
        assert client.siren == "123456789"
        assert client.first_name == "TEST Create first name"
        assert client.last_name == "TEST Create last name"
        assert client.email == "TESTCREATEclient@test.com"
        assert client.phone_number == "+33654871599"
        assert client.sales_contact == new_sales_contact

    def test_create_client_with_not_unique_siren_raises_error(self, new_client):
        """Tests if client creation raise IntegrityError with not unique siren."""

        with pytest.raises(IntegrityError):
            Client.objects.create(
                company_name="TEST Create Company",
                siren=new_client.siren,
                first_name="TEST Create first name",
                last_name="TEST Create last name",
                email="TESTCREATEclient@test.com",
                phone_number="+33654871599",
                sales_contact=new_client.sales_contact,
            )
            assert Client.objects.count() == 0
            assert Location.objects.count() == 0

    def test_delete_client_and_his_location(self, new_client_with_location):
        """Tests if client deletion delete his location.."""

        assert Client.objects.count() == 1
        assert Location.objects.count() == 1
        new_client_with_location.delete()
        assert Client.objects.count() == 0
        assert Location.objects.count() == 0
