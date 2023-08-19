import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from helpers.validators import unicodealphavalidator
from helpers.models import TimestampedModel
from .permissions import add_default_permissions_to_groups


class CustomUserManager(BaseUserManager):
    """
    Custom user model handler where email is the identifier
    for authentication instead of username.
    """

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a user with the given email, and password."""

        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("is_active") is not True:
            raise ValueError(_("Superuser must have is_active=True."))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    EPIC Event CRM users.
    Email and password are required.
    """

    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    username = None
    email = models.EmailField(_("email address"), unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Employee(TimestampedModel):
    """
    Epic Events employee profile model for CustomUser.
    A post_save signal sets groups with default permissions for the linked user.
    A post_delete signal deletes the linked user when deleting the employee.
    """

    DEPARTMENT = [
        ("MANAGEMENT", "Gestion"),
        ("SALES", "Commercial"),
        ("SUPPORT", "Support"),
    ]
    employee_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_number = models.PositiveIntegerField(
        "Numéro d'employé",
        unique=True,
    )
    first_name = models.CharField(
        "Prénom", max_length=100, validators=[unicodealphavalidator]
    )
    last_name = models.CharField(
        "Nom", max_length=100, validators=[unicodealphavalidator]
    )
    department = models.CharField("Département ", max_length=10, choices=DEPARTMENT)
    user = models.OneToOneField(
        to=CustomUser, on_delete=models.PROTECT, verbose_name="utilisateur"
    )

    def __str__(self):
        return f"Employé {self.last_name} {self.first_name} du département {self.department}"


@receiver(post_save, sender=Employee)
def add_groups_with_default_permissions(sender, instance, **kwargs):
    """
    Create users groups if they don't exist.
    Remove user from all groups if change (the user can only be part of one).
    Add a user to the group based on their department with their default permissions.
    Add is_staff permission to linked users if the employee's department is MANAGEMENT.
    """

    groups = Group.objects.all()
    if len(groups) == 0:
        management_group = Group.objects.create(name="management")
        sales_group = Group.objects.create(name="sales")
        support_group = Group.objects.create(name="support")
        add_default_permissions_to_groups(management_group, sales_group, support_group)

    user_groups = instance.user.groups.all()
    for group in user_groups:
        group.user_set.remove(instance.user)

    if instance.department == "MANAGEMENT":
        instance.user.groups.add(Group.objects.get(name="management"))
        instance.user.is_staff = True
    else:
        if instance.department == "SALES":
            instance.user.groups.add(Group.objects.get(name="sales"))
        elif instance.department == "SUPPORT":
            instance.user.groups.add(Group.objects.get(name="support"))
        instance.user.is_staff = False
    instance.user.save()


@receiver(post_delete, sender=Employee)
def delete_linked_user(sender, instance, **kwargs):
    instance.user.delete()
