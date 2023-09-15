import random
import factory
from factory.fuzzy import FuzzyInteger
from django.contrib.auth import get_user_model
from faker import Faker

from accounts.models import Employee
from locations.models import Location
from clients.models import Client

fake = Faker("fr_FR")
CustomUser = get_user_model()


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: "customuser{}@test.com".format(n))
    password = "123456789!"


class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee

    employee_number = factory.Sequence(lambda n: n)
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    department = factory.Iterator(["MANAGEMENT", "SALES", "SUPPORT"])
    user = factory.SubFactory(CustomUserFactory)


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    street_number = FuzzyInteger(1, 876)
    street_name = factory.LazyAttribute(lambda _: fake.street_name())
    city = factory.LazyAttribute(lambda _: fake.city())
    zip_code = factory.Sequence(lambda n: "{:05}".format(random.randrange(100000)))
    country = fake.country()


class SalesContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee

    employee_number = factory.Sequence(lambda n: n + 100)
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    department = "SALES"
    user = factory.SubFactory(CustomUserFactory)


class ClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Client

    company_name = factory.LazyAttribute(lambda _: fake.street_name())
    siren = factory.Sequence(lambda n: "{:09}".format(random.randrange(1000000000)))
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    email = factory.Sequence(lambda n: "client{}@test.com".format(n))
    phone_number = fake.phone_number()
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
