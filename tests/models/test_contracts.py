import pytest
from django.db.utils import IntegrityError

from clients.models import Client
from contracts.models import Contract


class TestContracts:
    def test_create_contract(self, new_client):
        """Tests contract creation."""

        new_client.contract_requested = True
        contract = Contract.objects.create(client=new_client)
        new_client.contract_requested = False
        assert Client.objects.count() == 1
        assert Contract.objects.count() == 1
        assert contract.client.contract_requested is False
        assert contract.is_signed is False

    def test_create_contract_with_no_client_raises_error(self, new_client):
        """Tests if contract creation raise IntegrityError with no client."""

        with pytest.raises(IntegrityError):
            Contract.objects.create()
            assert Client.objects.count() == 1
            assert Contract.objects.count() == 0
