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
    ClientContractDetailAPIView,
    ClientContractEventCreateAPIView,
    ClientContractEventDetailAPIView,
    EventLocationsListAPIView,
    EventLocationDetailAPIView,
    ContractListAPIView,
    EventListAPIView,
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
    path(
        "clients/<uuid:client_id>/contracts/<uuid:contract_id>/",
        ClientContractDetailAPIView.as_view(),
        name="client_contract_detail",
    ),
    path(
        "clients/<uuid:client_id>/contracts/<uuid:contract_id>/event/",
        ClientContractEventCreateAPIView.as_view(),
        name="client_contract_event",
    ),
    path(
        "clients/<uuid:client_id>/contracts/<uuid:contract_id>/<uuid:event_id>/",
        ClientContractEventDetailAPIView.as_view(),
        name="client_contract_event_detail",
    ),
    path(
        "clients/<uuid:client_id>/contracts/<uuid:contract_id>/<uuid:event_id>/locations/",
        EventLocationsListAPIView.as_view(),
        name="client_contract_event_locations",
    ),
    path(
        "clients/<uuid:client_id>/contracts/<uuid:contract_id>/<uuid:event_id>/locations/<uuid:location_id>/",
        EventLocationDetailAPIView.as_view(),
        name="client_contract_event_location_detail",
    ),
    path("contracts/", ContractListAPIView.as_view(), name="contracts"),
    path("events/", EventListAPIView.as_view(), name="events"),
]
