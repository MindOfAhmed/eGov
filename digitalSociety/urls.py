from django.urls import path
from . import views
from .views import RenewalRequestsAPIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("", views.index, name="index"),
    path("api/citizen_info_validation/", views.citizen_info_validation, name="citizen_info_validation"),
    path("api/address_info_validation/", views.address_info_validation, name="address_info_validation"),
    path("api/passport_info_validation/", views.passport_info_validation, name="passport_info_validation"),
    path("api/license_info_validation/", views.license_info_validation, name="license_info_validation"),
    path("api/register_address/", views.register_address, name="register_address"),
    path("api/register_property/", views.register_property, name="register_property"),
    path("api/register_vehicle/", views.register_vehicle, name="register_vehicle"),
    path("api/renewal_requests/", RenewalRequestsAPIView.as_view(), name="renewal_request"),
    # path("api/accept_renewal_request/", views.accept_renewal_request, name="accept_renewal_request"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/user/", views.user_data, name="user_data"),
    path("api/user_groups/", views.user_groups, name="user_groups")
]
''' 
    When a POST request is made to /token/ with valid user credentials (username and password),
    the TokenObtainPairView will validate the credentials against the user model. If the credentials are valid,
    it will return a response containing an access token and a refresh token in JSON format. 
'''