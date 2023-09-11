import factory
from django.contrib.auth import get_user_model
from faker import Faker

from accounts.models import Employee

fake = Faker()
CustomUser = get_user_model()


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: "customuser{}@example.com".format(n))
    password = "123456789!"


class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee

    employee_number = factory.Sequence(lambda n: n)
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    department = factory.Iterator(["MANAGEMENT", "SALES", "SUPPORT"])
    user = factory.SubFactory(CustomUserFactory)
