from django.contrib import admin
from .models import *

class CitizensAdmin(admin.ModelAdmin):
    list_display = ('national_id', 'first_name', 'last_name', 'date_of_birth', 'sex', 'blood_type')

class AddressesAdmin(admin.ModelAdmin):
    list_display = ('citizen', 'country', 'city', 'street', 'building_number', 'floor_number', 'apartment_number', 'state')

class PassportsAdmin(admin.ModelAdmin):
    list_display = ('citizen', 'passport_number', 'issue_date', 'expiry_date', 'picture')

class DrivingLicensesAdmin(admin.ModelAdmin):
    list_display = ('license_number', 'citizen', 'picture', 'issue_date', 'expiry_date', 'nationality', 'emergency_contact', 'license_class')

class RenewalRequestsAdmin(admin.ModelAdmin):
    list_display = ('citizen', 'request_type', 'reason', 'proof_document', 'status', 'picture', 'submitted_at', 'reviewed_at')

class RegistrationRequestsAdmin(admin.ModelAdmin):
    list_display = ('citizen', 'request_type', 'proof_document', 'previous_owner_id', 'status', 'submitted_at', 'reviewed_at')

admin.site.register(Citizens, CitizensAdmin)
admin.site.register(Addresses, AddressesAdmin)
admin.site.register(Passports, PassportsAdmin)
admin.site.register(DrivingLicenses, DrivingLicensesAdmin)
admin.site.register(RenewalRequests, RenewalRequestsAdmin)
admin.site.register(RegistrationRequests, RegistrationRequestsAdmin)