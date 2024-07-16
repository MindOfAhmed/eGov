from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from .services import *

# TODO check error handling when creating models

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
def citizen_info_validation(request):
    # create a serializer instance and pass the data from the request
    serializer = CitizenValidationSerializer(data=request.data)
    if serializer.is_valid():
        return Response({"message": "The data you entered matches our records."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''This function will be used to validate the citizen's address information from the form'''
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # only authenticated users can access this view
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