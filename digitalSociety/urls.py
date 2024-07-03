from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("", views.index, name="index"),
    path("services/passport_renewal", views.citizen_info_validation, name="citizen_info_validation"),
    path("address_info_validation/", views.address_info_validation, name="address_info_validation"),
    path("passport_info_validation/", views.passport_info_validation, name="passport_info_validation"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
''' 
    When a POST request is made to /token/ with valid user credentials (username and password),
    the TokenObtainPairView will validate the credentials against the user model. If the credentials are valid,
    it will return a response containing an access token and a refresh token in JSON format. 
'''