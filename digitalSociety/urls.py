from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("", views.index, name="index"),
    path("api/citizen_info_validation/", views.citizen_info_validation, name="citizen_info_validation"),
    path("api/address_info_validation/", views.address_info_validation, name="address_info_validation"),
    path("api/passport_info_validation/", views.passport_info_validation, name="passport_info_validation"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/user/', views.user_data, name='user_data'),
]
''' 
    When a POST request is made to /token/ with valid user credentials (username and password),
    the TokenObtainPairView will validate the credentials against the user model. If the credentials are valid,
    it will return a response containing an access token and a refresh token in JSON format. 
'''