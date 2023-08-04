from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .models import Employee
from .forms import CustomUserCreationForm, CustomUserChangeForm

CustomUser = get_user_model()


class EmployeeAdmin(admin.ModelAdmin):
    """Define admin model for employee model."""

    list_display = ["last_name", "first_name", "employee_number", "department", "user", "created_at", "updated_at"]
    readonly_fields = ("created_at", "updated_at")


class CustomUserAdmin(UserAdmin):
    """Define admin model for custom User model with no username field."""

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Permissions"), {
            "fields": ("is_active", "is_staff", "groups", "user_permissions")
            }),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions"
                    )}),
    )
    list_display = (
        "email",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    search_fields = ("email",)
    ordering = ("email",)
    readonly_fields = ("last_login", "date_joined")


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Employee, EmployeeAdmin)
