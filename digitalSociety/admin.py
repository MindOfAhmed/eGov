from django.contrib import admin
from .models import *

class CitizensAdmin(admin.ModelAdmin):
    list_display = ('national_id', 'first_name', 'last_name', 'date_of_birth', 'nationality', 'sex', 'blood_type')

class AddressesAdmin(admin.ModelAdmin):
    list_display = ('citizen', 'country', 'city', 'street', 'building_number', 'floor_number', 'apartment_number')

class PassportsAdmin(admin.ModelAdmin):
    list_display = ('citizen', 'passport_number', 'issue_date', 'expiry_date', 'picture')

class RenewalRequestsAdmin(admin.ModelAdmin):
    list_display = ('citizen', 'request_type', 'reason', 'proof_document', 'status', 'picture', 'submitted_at', 'reviewed_at')


admin.site.register(Citizens, CitizensAdmin)
admin.site.register(Addresses, AddressesAdmin)
admin.site.register(Passports, PassportsAdmin)
admin.site.register(RenewalRequests, RenewalRequestsAdmin)
