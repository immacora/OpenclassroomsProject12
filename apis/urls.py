from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

from .views import (
    EmployeeListAPIView,
)


urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="login_refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path("employees/", EmployeeListAPIView.as_view(), name="employees"),
]
