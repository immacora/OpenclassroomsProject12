from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    LogoutAPIView,
    EmployeeListAPIView,
    EmployeeDetailAPIView,
    ClientListAPIView,
    ClientDetailAPIView,
)


urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("employees/", EmployeeListAPIView.as_view(), name="employees"),
    path(
        "employees/<uuid:employee_id>/",
        EmployeeDetailAPIView.as_view(),
        name="employee_detail",
    ),
    path("clients/", ClientListAPIView.as_view(), name="clients"),
    path(
        "clients/<uuid:client_id>/",
        ClientDetailAPIView.as_view(),
        name="client_id",
    ),
]
