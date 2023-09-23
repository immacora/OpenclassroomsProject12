import pytest
from django.db.utils import IntegrityError

from clients.models import Client
from contracts.models import Contract


class TestContracts:
    """Tests contract model."""

    def test_create_contract(self, new_client):
        """Tests contract creation."""

        contract = Contract.objects.create(
            contract_description="TEST Create contract description",
            amount=1542.25,
            payment_due=1542.25,
            client=new_client,
        )
        assert Client.objects.count() == 1
        assert Contract.objects.count() == 1
        assert contract.contract_id is not None
        assert contract.contract_description == "TEST Create contract description"
        assert contract.amount == 1542.25
        assert contract.payment_due == 1542.25
        assert not contract.is_signed
        assert contract.client == new_client

    def test_create_contract_with_no_client_raises_error(self, new_client):
        """Tests if contract creation raise IntegrityError with no client."""

        with pytest.raises(IntegrityError):
            Contract.objects.create()
            assert Client.objects.count() == 1
            assert Contract.objects.count() == 0
