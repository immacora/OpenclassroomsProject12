from datetime import datetime, timedelta, timezone
import random
import factory
from uuid import uuid4
from factory.fuzzy import FuzzyInteger, FuzzyDateTime
from django.contrib.auth import get_user_model
from faker import Faker

from accounts.models import Employee
from locations.models import Location
from clients.models import Client
from contracts.models import Contract
from events.models import Event

fake = Faker("fr_FR")
CustomUser = get_user_model()


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    user_id = factory.LazyFunction(uuid4)
    email = factory.Sequence(lambda n: "customuser{}@test.com".format(n))
    password = "123456789!"


class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee

    employee_id = factory.LazyFunction(uuid4)
    employee_number = factory.Sequence(lambda n: n)
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    department = factory.Iterator(["MANAGEMENT", "SALES", "SUPPORT"])
    user = factory.SubFactory(CustomUserFactory)


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    location_id = factory.LazyFunction(uuid4)
    street_number = FuzzyInteger(1, 876)
    street_name = factory.LazyAttribute(lambda _: fake.street_name())
    city = factory.LazyAttribute(lambda _: fake.city())
    zip_code = factory.Sequence(lambda n: "{:05}".format(random.randrange(100000)))
    country = "FRANCE"


class SalesContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee

    employee_id = factory.LazyFunction(uuid4)
    employee_number = factory.Sequence(lambda n: n + 100)
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    department = "SALES"
    user = factory.SubFactory(CustomUserFactory)


class SupportContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee

    employee_id = factory.LazyFunction(uuid4)
    employee_number = factory.Sequence(lambda n: n + 200)
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    department = "SUPPORT"
    user = factory.SubFactory(CustomUserFactory)


class ClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Client

    client_id = factory.LazyFunction(uuid4)
    company_name = factory.LazyAttribute(lambda _: fake.street_name())
    siren = factory.Sequence(lambda n: "{:09}".format(random.randrange(1000000000)))
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    email = factory.Sequence(lambda n: "client{}@test.com".format(n))
    phone_number = fake.phone_number()
    contract_requested = False
    sales_contact = factory.SubFactory(SalesContactFactory)
    locations = factory.RelatedFactoryList(
        LocationFactory, factory_related_name="client_locations"
    )

    @factory.post_generation
    def locations(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for location in extracted:
                self.locations.add(location)


class ContractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contract

    contract_id = factory.LazyFunction(uuid4)
    contract_description = factory.Faker("text", max_nb_chars=2000)
    amount = factory.Faker("random_number", digits=5)
    payment_due = factory.Faker("random_number", digits=5)
    is_signed = False
    client = factory.SubFactory(ClientFactory)


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    event_id = factory.LazyFunction(uuid4)
    event_name = "TEST event name"
    start_date = FuzzyDateTime(
        datetime.utcnow().replace(tzinfo=timezone.utc),
        datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(days=30),
    )
    end_date = factory.LazyAttribute(
        lambda obj: FuzzyDateTime(
            obj.start_date, obj.start_date + timedelta(days=1)
        ).fuzz()
    )
    attendees = factory.Faker("random_number", digits=3)
    notes = factory.Faker("text", max_nb_chars=2000)
    contract = factory.SubFactory(ContractFactory)
    support_contact = factory.SubFactory(SupportContactFactory)
    locations = factory.RelatedFactoryList(
        LocationFactory, factory_related_name="event_locations"
    )

    @factory.post_generation
    def locations(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for location in extracted:
                self.locations.add(location)
