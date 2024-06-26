from django.urls import path
from . import views

urlpatterns = [
    path("", views.citizen_info_validation, name="citizen_info_validation"),
    path("address_info_validation/", views.address_info_validation, name="address_info_validation"),
    path("passport_info_validation/", views.passport_info_validation, name="passport_info_validation"),
]