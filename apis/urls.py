from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import LogoutAPIView, EmployeeListAPIView, EmployeeDetailAPIView


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
]
