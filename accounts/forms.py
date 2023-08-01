from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

CustomUser = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """A Custom form for creating new custom users."""

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):
    """A Custom form for updating custom users."""

    class Meta(UserChangeForm):
        model = CustomUser
        fields = ("email",)
