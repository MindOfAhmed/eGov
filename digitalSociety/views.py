from django.shortcuts import render
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from .services import *
from django.contrib.auth.decorators import user_passes_test 
from rest_framework import generics

# TODO check error handling when creating models

'''This function uses the user_passes_test decorator to restrict view access based on user groups'''
def group_required(group_name):
    def in_group(u):
        return u.is_authenticated and u.groups.filter(name=group_name).exists()
    return user_passes_test(in_group)

'''This view will return a list of groups the user is in'''
@api_view(['GET']) # only allow GET requests
@permission_classes([IsAuthenticated]) # only authenticated users can access this view
def user_groups(request):
    if request.user.is_authenticated:
        groups = request.user.groups.values_list('name', flat=True)
        return Response({"groups" : list(groups)})
    else:
        return Response({"detail": "Not authenticated"})

'''This function will be used to send the user data to the frontend'''
@api_view(['GET']) # only allow GET requests
@permission_classes([IsAuthenticated]) # only authenticated users can access this view
def user_data(request):
    user = request.user
    serializer = UserSerializer(user)
    # return the user data in JSON format
    return Response(serializer.data)

def index(request):
    return render(request, "index.html")

'''This function will be used to validate the citizen's personal information from the form'''
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # only authenticated users can access this view
@group_required('Citizens') # only citizens can access this view
def citizen_info_validation(request):
    # create a serializer instance and pass the data from the request
    serializer = CitizenValidationSerializer(data=request.data)
    if serializer.is_valid():
        return Response({"message": "The data you entered matches our records."}, status=status.HTTP_200_OK)
    return Response({"message": "The data you entered does not match our records", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

'''This function will be used to validate the citizen's address information from the form'''
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # only authenticated users can access this view
@group_required('Citizens') # only citizens can access this view
def address_info_validation(request):
    # create a serializer instance and pass the data from the request
    serializer = AddressValidationSerializer(data=request.data)
    if serializer.is_valid(): 
        # retrieve the data from the serializer
        data = serializer.validated_data
        print(data)
        # check if the address exists and belongs to the logged in user
        try:
            address = Addresses.objects.get(
                country=data['country'],
                city=data['city'],
                street=data['street'],
                building_number=data['building_number'],
                floor_number=data['floor_number'],
                apartment_number=data['apartment_number'],
                citizen = request.user.citizen
            )
            if address:
                return Response({"message": "The data you entered matches our records."}, status=status.HTTP_200_OK)
        except Addresses.DoesNotExist:
            return Response({"message": "The data you entered does not match our records."}, status=status.HTTP_400_BAD_REQUEST)
            
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''This function will be used to validate the passport information from the form and to create a new renewal request'''
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # only authenticated users can access this view
@group_required('Citizens') # only citizens can access this view
def passport_info_validation(request):
    # create a serializer instance and pass the data from the request
    serializer = PassportValidationSerializer(data=request.data)
    if serializer.is_valid():
        # retrieve the data from the serializer
        data = serializer.validated_data
        # check if the passport exists and belongs to the logged in user
        try:
            passport = Passports.objects.get(
                passport_number=data['passport_number'],
                issue_date=data['issue_date'],
                expiry_date=data['expiry_date'],
                citizen = request.user.citizen
            )
            # check if the passport has been renewed within the last 3 years
            issue_date = datetime.strptime(data['issue_date'], "%Y-%m-%d").date()
            if (datetime.now().date() - issue_date) < timedelta(days=1095):
                # ensure the reason and proof document for early renewal are submitted
                if not data['reason'] or not data['proof_document']:
                    return Response({"message": "You need to provide a reason and a proof document to renew your passport early."}, status=status.HTTP_400_BAD_REQUEST)
            
            # check if the uploaded image is valid
            is_valid, message = validate_uploaded_photo(data['picture'])
            if is_valid:
                # check if the user already has a request pending
                if not RenewalRequests.objects.filter(citizen=passport.citizen, request_type="Passport", status="Pending").exists(): # copilot helped correct this 
                # create a new renewal request
                    if not data['reason'] and not data['proof_document']:
                        renewal_request = RenewalRequests(
                            citizen = passport.citizen,
                            request_type = "Passport",
                            picture = data['picture']
                        )
                    else:
                        renewal_request = RenewalRequests(
                            citizen = passport.citizen,
                            request_type = "Passport",
                            picture = data['picture'],
                            reason = data['reason'],
                            proof_document = data['proof_document']
                        )
                    renewal_request.save()
                    '''TODO: send user notification about the request status'''
                    return Response({"message": "The proccess is successful and the request is pending."}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "You already have a pending request."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
        except Passports.DoesNotExist:
            return Response({"message": "The passport does not exist. Please check your information again"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''This function will be used to validate the driver's license information from the form and to create a new renewal request'''
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # only authenticated users can access this view
@group_required('Citizens') # only citizens can access this view
def license_info_validation(request):
    # create a serializer instance and pass the data from the request
    serializer = DrivingLicenseSerializer(data=request.data)
    if serializer.is_valid():
        # retrieve the data from the serializer
        data = serializer.validated_data
        # check if the license exists and belongs to the logged in user
        try:
            driversLicense = DrivingLicenses.objects.get(
                license_number=data['license_number'],
                citizen = request.user.citizen,
                issue_date = data['issue_date'],
                expiry_date = data['expiry_date'],
                nationality = data['nationality'],
                license_class = data['license_class']
            )
            # update the emergency contact number
            driversLicense.emergency_contact = data['emergency_contact']
            driversLicense.save()

            # check if the license has been renewed within the last 5 years
            issue_date = datetime.strptime(data['issue_date'], "%Y-%m-%d").date()
            if (datetime.now().date() - issue_date) < timedelta(days=1825):
                # ensure the reason and proof document for early renewal are submitted
                if not data['reason'] or not data['proof_document']:
                    return Response({"message": "You need to provide a reason and a proof document to renew your license early."}, status=status.HTTP_400_BAD_REQUEST)
            
            # check if the uploaded image is valid
            is_valid, message = validate_uploaded_photo(data['picture'])
            if is_valid:
                # check if the user already has a request pending
                if not RenewalRequests.objects.filter(citizen=driversLicense.citizen, request_type="Driver's License", status="Pending").exists():
                    # create a new renewal request
                    if not data['reason'] and not data['proof_document']:
                        renewal_request = RenewalRequests(
                            citizen = driversLicense.citizen,
                            request_type = "Driver's License",
                            picture = data['picture'],
                        )
                    else: 
                        renewal_request = RenewalRequests(
                            citizen = driversLicense.citizen,
                            request_type = "Driver's License",
                            picture = data['picture'],
                            reason = data['reason'],
                            proof_document = data['proof_document']
                        )
                    renewal_request.save()
                    '''TODO: send user notification about the request status'''
                    return Response({"message": "The proccess is successful and the request is pending."}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "You already have a pending request."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
        except DrivingLicenses.DoesNotExist:
            return Response({"message": "The license does not exist. Please check your information again"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''This function will be used to register a new address'''
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # only authenticated users can access this view
@group_required('Citizens') # only citizens can access this view
def register_address(request):
    # create a new serializer instance and pass the data from the request
    serializer = AddressRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        # retrieve the data from the serializer
        data = serializer.validated_data
        # ensure that the user doesn't already have a pending address registration request
        if not RegistrationRequests.objects.filter(citizen=request.user.citizen, request_type='Address Registration', status='Pending').exists():
            try:
                # create a new pending address for the gov inspector to confirm if it doesn't already exist
                if not Addresses.objects.filter(
                    citizen=request.user.citizen,
                    country=data['country'],
                    city=data['city'],
                    street=data['street'],
                    building_number=data['building_number'],
                    floor_number=data['floor_number'],
                    apartment_number=data['apartment_number']
                ).exists():
                    address = Addresses(
                        citizen = request.user.citizen,
                        country = data['country'],
                        city = data['city'],
                        street = data['street'],
                        building_number = data['building_number'],
                        floor_number = data['floor_number'],
                        apartment_number = data['apartment_number'],
                        state = 'Pending Request'
                    )
                    address.save()
                    # create a new request
                    address_request = RegistrationRequests(
                        citizen = request.user.citizen,
                        request_type = 'Address Registration',
                        proof_document = data['proof_document']
                    )
                    address_request.save()
                else:
                    return Response({"message": "This is already your registered address."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "The proccess is successful and the request is pending."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You already have a pending request."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''This function will be used to register a new property'''    
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # only authenticated users can access this view
@group_required('Citizens') # only citizens can access this view
def register_property(request):
    # create a new serializer instance and pass the data from the request
    serializer = PropertyRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        # retrieve the data from the serializer
        data = serializer.validated_data
        # ensure that the user doesn't already have a pending property registration request
        if not RegistrationRequests.objects.filter(citizen=request.user.citizen, request_type='Property Registration', status='Pending').exists():
            try:
                # create a new pending property, if it doesn't already exist, for the gov inspector to confirm
                if not Properties.objects.filter(citizen=request.user.citizen, property_id=data['property_id']).exists():
                    property = Properties(
                        citizen = request.user.citizen,
                        property_id = data['property_id'],
                        size = data['size'],
                        location = data['location'],
                        property_type = data['property_type'],
                        description = data['description'],
                        picture = data['picture'],
                        is_under_transfer = True
                    )
                    property.save()
                    # create a new request
                    property_request = RegistrationRequests(
                        citizen = request.user.citizen,
                        request_type = 'Property Registration',
                        proof_document = data['proof_document'],
                        previous_owner_id = data['previous_owner_id']
                    )
                    property_request.save()
                else:
                    return Response({"message": "This property is already registered."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "The proccess is successful and the request is pending."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You already have a pending request."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
'''This function will be used to register a new vehicle'''
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # only authenticated users can access this view
@group_required('Citizens') # only citizens can access this view
def register_vehicle(request):
    # create a new serializer instance and pass the data from the request
    serializer = VehicleRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        # retrieve the data from the serializer
        data = serializer.validated_data
        # ensure that there are no pending requests already
        if not RegistrationRequests.objects.filter(citizen=request.user.citizen, request_type='Vehicle Registration', status='Pending').exists():
            try:
                # create a new pending vehicle, if it doesn't already exist, for the gov inspector to confirm
                if not Vehicles.objects.filter(citizen=request.user.citizen, serial_number=data['serial_number']).exists():
                    vehicle = Vehicles(
                        citizen = request.user.citizen,
                        serial_number = data['serial_number'],
                        model = data['model'],
                        manufacturer = data['manufacturer'],
                        year = data['year'],
                        vehicle_type = data['vehicle_type'],
                        picture = data['picture'],
                        plate_number = data['plate_number'],
                        is_under_transfer = True
                    )
                    vehicle.save()
                    # create a new request
                    vehicle_request = RegistrationRequests(
                        citizen = request.user.citizen,
                        request_type = 'Vehicle Registration',
                        proof_document = data['proof_document'],
                        previous_owner_id = data['previous_owner_id']
                    )
                    vehicle_request.save()
                else:
                    return Response({"message": "This vehicle is already registered."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "The proccess is successful and the request is pending."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You already have a pending request."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
'''This function will be used to retrieve the pending renewal requests that will be displayed to the inspector'''
class RenewalRequestsAPIView(generics.ListAPIView):
    serializer_class = RenewalRequestsSerializer
    queryset = RenewalRequests.objects.filter(status='Pending')

'''This view will accept the renewal requests'''
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # only authenticated users can access this view
@group_required('Inspectors') # only inspectors can access this view
def accept_renewal_request(request, id):
    try:
        # retrieve the renewal request
        renewal_request = RenewalRequests.objects.get(id=id)
        today = datetime.now().date()

        # update the passport information
        if (renewal_request.request_type == 'Passport'):
            # retrieve the associated passport
            passport = Passports.objects.get(citizen=renewal_request.citizen)
            # set the new passport picture to the uploaded picture
            passport.picture = renewal_request.picture
            # update the issue and expiry dates
            passport.issue_date = today
            passport.expiry_date = today + timedelta(days=365*5)
            passport.save()
        else: # driver's license
            # retrieve the associated driver's license
            license = DrivingLicenses.objects.get(citizen=renewal_request.citizen)
            # set the new license picture to the uploaded picture
            license.picture = renewal_request.picture
            # update the issue and expiry dates
            license.issue_date = today
            license.expiry_date = today + timedelta(days=365*10)
            license.save()

        # update the renewal request status
        renewal_request.status = 'Approved'
        renewal_request.reviewed_at = today
        renewal_request.save()

        # send a notification to the citizen
        message = f"Your {renewal_request.request_type} renewal request has been approved."
        Notifications.objects.create(citizen=renewal_request.citizen, message=message)
    except RenewalRequests.DoesNotExist:
        return Response({"message": "The request does not exist."}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "The request has been accepted."}, status=status.HTTP_200_OK)

'''This view will reject the renewal requests'''
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # only authenticated users can access this view
@group_required('Inspectors') # only inspectors can access this view
def reject_renewal_request(request, id):
    try:
        # retrieve the renewal request
        renewal_request=RenewalRequests.objects.get(id=id)

        # update the renewal request status
        renewal_request.status = 'Rejected'
        renewal_request.reviewed_at = datetime.now().date()

        # retrieve the rejection reason from the request and set it in the renewal request
        rejection_reason = request.data.get('rejectionReason', '') # copilot ^_^
        renewal_request.rejection_reason = rejection_reason
        renewal_request.save()

        # send a notification to the citizen
        message = f"Your {renewal_request.request_type} renewal request has been rejected. Reason: {rejection_reason}"
        Notifications.objects.create(citizen=renewal_request.citizen, message=message)
    except RenewalRequests.DoesNotExist:
        return Response({"message": "The request does not exist."}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "The request has successfuly been rejected."}, status=status.HTTP_200_OK)
    
'''This function will be used to retrieve the pending registration requests that will be displayed to the inspector'''
class RegistrationRequestsAPIView(generics.ListAPIView):
    serializer_class = RegistrationRequestsSerializer
    queryset = RegistrationRequests.objects.filter(status='Pending')
        
'''This view will accept the registration requests'''
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # only authenticated users can access this view
@group_required('Inspectors') # only inspectors can access this view
def accept_registration_request(request, id):
    try:
        # retrieve the registration request
        registration_request = RegistrationRequests.objects.get(id=id)

        # update the registration request status to Approved
        registration_request.status = 'Approved'
        registration_request.reviewed_at = datetime.now().date()
        registration_request.save()

        # send a notification to the citizen
        message = f"Your {registration_request.request_type} registration request has been approved."
        Notifications.objects.create(citizen=registration_request.citizen, message=message)

        # update the placeholder data in the database
        if registration_request.request_type == 'Address Registration':
            # retrive the placeholder address and update its state
            address = Addresses.objects.get(citizen=registration_request.citizen, state='Pending Request')
            address.state = 'Active'
            address.save()
        elif registration_request.request_type == 'Property Registration':
            # transfer the property to the new owner
            property = Properties.objects.get(citizen=registration_request.citizen, is_under_transfer=True)
            property.is_under_transfer = False
            property.save()
            # retrieve the property registered under the former owner delete it
            try:
                prev_registration = Properties.objects.get(citizen=registration_request.previous_owner_id, property_id=property.property_id)
                prev_registration.delete()
            except Properties.DoesNotExist:
                pass
        else:
            # transfer the vehicle to the new owner
            vehicle = Vehicles.objects.get(citizen=registration_request.citizen, is_under_transfer=True)
            vehicle.is_under_transfer = False
            vehicle.save()
            # retrieve the vehicle registered under the former owner delete it
            try:
                prev_registration = Vehicles.objects.get(citizen=registration_request.previous_owner_id, serial_number=vehicle.serial_number)
                prev_registration.delete()
            except Vehicles.DoesNotExist:
                pass
        
        return Response({"message": "The registration request has been accepted successfully."}, status=status.HTTP_200_OK)
    except RegistrationRequests.DoesNotExist:
        return Response({"message": "The request does not exist."}, status=status.HTTP_400_BAD_REQUEST)

'''This view will reject the registration requests'''
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # only authenticated users can access this view
@group_required('Inspectors') # only inspectors can access this view
def reject_registration_request(request, id):
    try:
        # retrieve the registration request
        registration_request = RegistrationRequests.objects.get(id=id)

        # update the registration request status to rejected
        registration_request.status = 'Rejected'
        registration_request.reviewed_at = datetime.now().date()

        # retrieve the rejection reason from the request and set it in the registration request
        rejection_reason = request.data.get('rejectionReason', '')
        registration_request.rejection_reason = rejection_reason

        registration_request.save()

        # send a notification to the citizen
        message = f"Your {registration_request.request_type} registration request has been rejected. Reason: {rejection_reason}"
        Notifications.objects.create(citizen=registration_request.citizen, message=message)

        # delete the placeholder data from the database
        if registration_request.request_type == 'Address Registration':
            address = Addresses.objects.get(citizen=registration_request.citizen, state='Pending Request')
            address.delete()
        elif registration_request.request_type == 'Property Registration':
            property = Properties.objects.get(citizen=registration_request.citizen, is_under_transfer=True)
            property.delete()
        else:
            vehicle = Vehicles.objects.get(citizen=registration_request.citizen, is_under_transfer=True)
            vehicle.delete()
        
        return Response({"message": "The registration request has been rejected successfully."}, status=status.HTTP_200_OK)
    except RegistrationRequests.DoesNotExist:
        return Response({"message": "The request does not exist."}, status=status.HTTP_400_BAD_REQUEST)