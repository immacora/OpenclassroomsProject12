import factory
from django.contrib.auth import get_user_model
from faker import Faker

fake = Faker()
CustomUser = get_user_model()


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: 'customuser{}@example.com'.format(n))
    password = "123456789!"
