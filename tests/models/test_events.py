import pytest
from django.db.utils import IntegrityError

from events.models import Event
from contracts.models import Contract
from locations.models import Location


class TestEvents:
    """Tests event model."""

    def test_create_event(self, new_contract):
        """Tests event creation."""

        event = Event.objects.create(
            event_name="TEST Create event",
            start_date="2023-12-15T12:00:00+01:00",
            end_date="2023-12-16T12:00:00+01:00",
            attendees=25,
            notes="TEST de notes sur l'événement.",
            contract=new_contract,
        )
        assert Event.objects.count() == 1
        assert event.event_id is not None
        assert event.start_date == "2023-12-15T12:00:00+01:00"
        assert event.end_date == "2023-12-16T12:00:00+01:00"
        assert event.attendees == 25
        assert event.notes == "TEST de notes sur l'événement."
        assert event.contract == new_contract

    def test_create_event_with_no_contract_raises_error(self, db):
        """Tests if event creation raise IntegrityError with no contract."""

        with pytest.raises(IntegrityError):
            Event.objects.create()
            assert Contract.objects.count() == 1
            assert Event.objects.count() == 0

    def test_create_event_with_existing_contract_raises_error(
        self, new_contract, new_event
    ):
        """Tests if event creation raises IntegrityError with existing contract."""
        new_event.contract = new_contract
        new_event.save()

        with pytest.raises(IntegrityError):
            Event.objects.create(contract=new_contract)
            assert Contract.objects.count() == 1
            assert Event.objects.count() == 1

    def test_delete_event_and_his_location(self, new_event_with_location):
        """Tests if event deletion delete his location.."""

        assert Event.objects.count() == 1
        assert Location.objects.count() == 1
        new_event_with_location.delete()
        assert Event.objects.count() == 0
        assert Location.objects.count() == 0
