from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    LogoutAPIView,
    EmployeeListAPIView,
    EmployeeDetailAPIView,
    ClientListAPIView,
    ClientDetailAPIView,
    ClientLocationsListAPIView,
    ClientLocationDetailAPIView,
    ClientContractsListAPIView,
    ContractListAPIView,
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
        name="client_detail",
    ),
    path(
        "clients/<uuid:client_id>/locations/",
        ClientLocationsListAPIView.as_view(),
        name="client_locations",
    ),
    path(
        "clients/<uuid:client_id>/locations/<uuid:location_id>/",
        ClientLocationDetailAPIView.as_view(),
        name="client_location_detail",
    ),
    path(
        "clients/<uuid:client_id>/contracts/",
        ClientContractsListAPIView.as_view(),
        name="client_contracts",
    ),
    path("contracts/", ContractListAPIView.as_view(), name="contracts"),
]
