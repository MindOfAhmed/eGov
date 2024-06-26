from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from .forms import *
from .models import *
from .services import *

def index(request):
    return render(request, "index.html")

def citizen_info_validation(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CitizenValidationForm(request.POST)
        if form.is_valid():
            # retrieve the data from the form for validation
            national_id = form.cleaned_data['national_id']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            date_of_birth = form.cleaned_data['date_of_birth']
            nationality = form.cleaned_data['nationality']
            sex = form.cleaned_data['sex']
            blood_type = form.cleaned_data['blood_type']

            # compare the form data with the data in the database
            try:
                citizen = Citizens.objects.get(national_id=national_id)

                if (citizen.first_name == first_name and citizen.last_name == last_name 
                    and citizen.date_of_birth == date_of_birth and citizen.nationality == nationality
                    and citizen.sex == sex and citizen.blood_type == blood_type):
                        # data matches, proceed to next step
                        return redirect('address_info_validation')
                else:
                    form.add_error(None, 'The data you entered does not match our records.')
            except Citizens.DoesNotExist:
                form.add_error(None, 'The data you entered does not match our records.')
    else:
        form = CitizenValidationForm()
        
    # if the method is not post, or the form is not valid, render the form
    return render(request, 'form.html', {'form': form})

def address_info_validation(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddressValidationForm(request.POST)
        if form.is_valid():
            # retrieve the data from the form for validation
            country = form.cleaned_data['country']
            city = form.cleaned_data['city']
            street = form.cleaned_data['street']
            building_number = form.cleaned_data['building_number']
            floor_number = form.cleaned_data['floor_number']
            apartment_number = form.cleaned_data['apartment_number']

            # compare the form data with the data in the database
            try:
                # retrieve the address entered in the form from the database
                Addresses.objects.get(country=country, city=city, street=street,
                                                building_number=building_number, floor_number=floor_number,
                                                apartment_number=apartment_number)
                # if the address exists, proceed to next step. 
                ''' TODO COMPARE AGAINST LOGGED IN USER LATER ''' 
                return redirect('passport_info_validation')
            except Addresses.DoesNotExist:
                form.add_error(None, 'The data you entered does not match our records.')
    else:
        form = AddressValidationForm()
        
    # if the method is not post, or the form is not valid, render the form
    return render(request, 'form.html', {'form': form})

def passport_info_validation(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PassportRenewalForm(request.POST, request.FILES)
        if form.is_valid():
            # retrieve the data from the form for validation
            passport_number = form.cleaned_data['passport_number']
            issue_date = form.cleaned_data['issue_date']
            expiry_date = form.cleaned_data['expiry_date']
            picture = form.cleaned_data['picture']

            # compare the form data with the data in the database
            try:
                # retrieve the passport entered in the form from the database
                passport = Passports.objects.get(passport_number=passport_number, issue_date=issue_date,
                                                 expiry_date=expiry_date)
                # passport exists, proceed to next step.
                ''' TODO COMPARE AGAINST LOGGED IN USER LATER ''' 

                # check if the passport has been renewed within the last 3 years
                if (datetime.now().date() - issue_date) < timedelta(days=1095):
                    # ensure the reason and proof document is submitted
                    if not form.cleaned_data['reason'] or not form.cleaned_data['proof_document']:
                        form.add_error(None, 'You need to provide a reason and a proof document to renew your passport early.')

                # check if the uploaded image is valid
                
                is_valid, message = validate_uploaded_photo(picture)
                if is_valid:
                    '''TODO: SEND USER NOTIFICATION LATER'''
                    # save the renewal request
                    renewal_request = form.save(commit=False)
                    renewal_request.citizen = passport.citizen
                    renewal_request.save() 
                    return render(request, 'index.html')
                else:
                    form.add_error(None, message)
                
            except Passports.DoesNotExist:
                form.add_error(None, 'The data you entered does not match our records.')
    else:
        form = PassportRenewalForm()
        
    # if the method is not post, or the form is not valid, render the form
    return render(request, 'form.html', {'form': form})