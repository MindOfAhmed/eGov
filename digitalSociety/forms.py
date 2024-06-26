from django import forms
from .models import *

'''This form will be used to validate the citizen's information for the passport renewal request'''
class CitizenValidationForm(forms.Form):
    national_id = forms.CharField(max_length=30)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    date_of_birth = forms.DateField()
    nationality = forms.CharField(max_length=30)
    SEX_CHOICES = [ 
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    sex = forms.ChoiceField(choices=SEX_CHOICES)

    BLOOD_TYPES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    blood_type = forms.ChoiceField(choices=BLOOD_TYPES) 

'''This form will be used to validate the citizen's address for the passport renewal request'''
class AddressValidationForm(forms.Form):
    country = forms.CharField(max_length=30)
    city = forms.CharField(max_length=30)
    street = forms.CharField(max_length=30)
    building_number = forms.IntegerField()
    floor_number = forms.IntegerField()
    apartment_number = forms.IntegerField()

'''This model form will be used to first validate the passport information, then to create a new renewal request'''
class PassportRenewalForm(forms.ModelForm):
    # the following fields will be used for validation
    passport_number = forms.CharField(max_length=9)
    issue_date = forms.DateField(widget=forms.DateInput(attrs={'id': 'id_issue_date'}))
    expiry_date = forms.DateField()
    # the following fields will be used for the renewal request
    picture = forms.ImageField()
    request_type = forms.ChoiceField(choices=[("Passport", "Passport"), ["Driver's License", "Driver's License"]])
    reason = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={
            'id': 'id_renewal_reason', 
            'placeholder': 'Explain why you need to renew your passport early and upload a proof document (eg. police report)',
            'style': 'display: none;'}))
    proof_document = forms.FileField(required=False, widget=forms.FileInput(attrs={'id': 'id_proof_document', 'style': 'display: none;'}))
    
    class Meta:
        model = RenewalRequests
        fields = ['request_type', 'reason', 'proof_document', 'picture']