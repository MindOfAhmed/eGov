from rest_framework import serializers
from .models import *

# serialize the citizens model then inlcude it in the serialization of the user model
class CitizensSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizens
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    citizen = CitizensSerializer()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'citizen']

'''This serializer will be used to validate the citizen's personal information from the form'''
class CitizenValidationSerializer(serializers.Serializer):
    national_id = serializers.CharField(max_length=30)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    date_of_birth = serializers.CharField(max_length=30)
    SEX_CHOICES = [ 
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    sex = serializers.ChoiceField(choices=SEX_CHOICES)

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
    blood_type = serializers.ChoiceField(choices=BLOOD_TYPES) 

    # check if this citizen exists in the database
    def validate(self, data):
        national_id = data['national_id']
        first_name = data['first_name']
        last_name = data['last_name']
        date_of_birth = data['date_of_birth']
        sex = data['sex']
        blood_type = data['blood_type']

        if not Citizens.objects.filter(
                                        national_id=national_id, 
                                        first_name=first_name, 
                                        last_name=last_name, 
                                        date_of_birth=date_of_birth, 
                                        sex=sex, 
                                        blood_type=blood_type
                                    ).exists():
            # if the citizen does not exist in the database, raise an error
            raise serializers.ValidationError('The data you entered does not match our records.')
        return data

'''This serializer will be used to validate the citizen's address information from the form in the api view'''
class AddressValidationSerializer(serializers.Serializer):
    country = serializers.CharField(max_length=30)
    city = serializers.CharField(max_length=30)
    street = serializers.CharField(max_length=30)
    building_number = serializers.IntegerField()
    floor_number = serializers.IntegerField()
    apartment_number = serializers.IntegerField()

'''This serializer will be used to validate the passport information from the form in the api view'''
class PassportValidationSerializer(serializers.Serializer):
    # the following fields will be used for validation
    passport_number = serializers.CharField(max_length=9)
    issue_date = serializers.CharField(max_length=10)
    expiry_date = serializers.CharField(max_length=10)
    # the following fields will be used for the renewal request
    picture = serializers.ImageField()
    reason = serializers.CharField(required=False, allow_blank=True)
    proof_document = serializers.FileField(required=False)

    def validate(self, data):
        # set default values for 'reason' and 'proof_document' if they are not provided or are empty
        data['reason'] = data.get('reason', None) if data.get('reason', '') != '' else None
        data['proof_document'] = data.get('proof_document', None) if data.get('proof_document', '') != '' else None
        return data
    # copilot ^_^

class DrivingLicenseSerializer(serializers.Serializer):
    # the following fields will be used for validation
    license_number = serializers.CharField(max_length=30)
    issue_date = serializers.CharField(max_length=10)
    expiry_date = serializers.CharField(max_length=10)
    nationality = serializers.CharField(max_length=30)
    CLASS_TYPES = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    license_class = serializers.ChoiceField(choices=CLASS_TYPES)
    # the following fields will be used for the renewal request
    picture = serializers.ImageField()
    emergency_contact = serializers.CharField(max_length=30)
    reason = serializers.CharField(required=False, allow_blank=True)
    proof_document = serializers.FileField(required=False)

    def validate(self, data):
        # set default values for 'reason' and 'proof_document' if they are not provided or are empty
        data['reason'] = data.get('reason', None) if data.get('reason', '') != '' else None
        data['proof_document'] = data.get('proof_document', None) if data.get('proof_document', '') != '' else None
        return data
    
'''This serializer will be used to collect the address to be registered in the api view from the form'''
class AddressRegistrationSerializer(serializers.Serializer):
    country = serializers.CharField(max_length=30)
    city = serializers.CharField(max_length=30)
    street = serializers.CharField(max_length=30)
    building_number = serializers.IntegerField()
    floor_number = serializers.IntegerField()
    apartment_number = serializers.IntegerField()
    proof_document = serializers.FileField()

'''This serializer will be used to collect the property information to be registered in the api view from the form'''
class PropertyRegistrationSerializer(serializers.Serializer):
    property_id = serializers.CharField(max_length=30)
    location = serializers.CharField(max_length=30)
    PROPERTY_TYPES = [
        ('Residential', 'Residential'), 
        ('Commercial', 'Commercial'), 
        ('Industrial', 'Industrial'), 
        ('Agricultural', 'Agricultural'),
        ('Land', 'Land'), 
        ('Intellectual', 'Intellectual')
    ]
    property_type = serializers.ChoiceField(choices=PROPERTY_TYPES)
    description = serializers.CharField()
    size = serializers.CharField(max_length=30)
    picture = serializers.ImageField()
    # the following fields will be used for the registration request
    previous_owner_id = serializers.CharField(max_length=30)
    proof_document = serializers.FileField()

'''This serializer will be used to collect the vehicle information to be registered in the api view from the form'''
class VehicleRegistrationSerializer(serializers.Serializer):
    serial_number = serializers.IntegerField()
    model = serializers.CharField(max_length=30)
    manufacturer = serializers.CharField(max_length=30)
    year = serializers.IntegerField()
    VEHICLE_TYPES = [
        ('SUV', 'SUV'),
        ('Sedan', 'Sedan'), 
        ('Truck', 'Truck'), 
        ('Van', 'Van'), 
        ('Bus', 'Bus'),
        ('Sports Car', 'Sports Car'),
        ('Motorcycle', 'Motorcycle')
    ]
    vehicle_type = serializers.ChoiceField(choices=VEHICLE_TYPES)
    picture = serializers.ImageField()
    plate_number = serializers.CharField(max_length=30)
    # the following fields will be used for the registration request
    proof_document = serializers.FileField()
    previous_owner_id = serializers.CharField(max_length=30)

'''The following 2 serializers will be used to add the passport and driving license to the renewal requests serializer as related fields'''
class PassportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passports
        fields = '__all__'

class DrivingLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrivingLicenses
        fields = '__all__'
# copilot ^_^

'''
These serializers will be used as a related field in the renewal requests serializer. 
Only the field needed in the request will be included.
'''
class CitizenPassportInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizens
        fields = ['national_id', 'first_name', 'last_name', 'date_of_birth', 'sex']

class CitizenDrivingLicenseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizens
        fields = ['national_id', 'first_name', 'last_name', 'blood_type']

'''This serializer will be used to send the renewal requests to the frontend'''
class RenewalRequestsSerializer(serializers.ModelSerializer):
    # these fields will contain the doc information and the appropriate citizen info
    passport_info = PassportsSerializer(source="citizen.passports_set", many=True, read_only=True)
    license_info = DrivingLicenseSerializer(source="citizen.drivinglicenses_set", many=True, read_only=True)
    citizen_passport_info = CitizenPassportInfoSerializer(source="citizen", read_only=True)
    citizen_license_info = CitizenDrivingLicenseInfoSerializer(source="citizen", read_only=True)

    class Meta:
        model = RenewalRequests
        fields = '__all__'

    '''
    Only include the passport info if the request type is passport and the license info if the request type 
    is license. The citizen information is also adjusted based on request type. This avoids the redundant data in the response
    '''
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.request_type == 'Passport':
            # move the info fields from their original location to the top level of the representation dictionary
            representation['passport_info'] = representation.pop('passport_info', None)
            representation['citizen_info'] = representation.pop('citizen_passport_info', None)
             # remove the unnecessary fields
            representation.pop('license_info', None)
            representation.pop('citizen_license_info', None)
        elif instance.request_type == "Driver's License":
            # move the info fields from their original location to the top level of the representation dictionary
            representation['license_info'] = representation.pop('license_info', None)
            representation['citizen_info'] = representation.pop('citizen_license_info', None)
             # remove the unnecessary fields
            representation.pop('passport_info', None)
            representation.pop('citizen_passport_info', None)
        return representation

# copilot ^_^ helped refactor the code to avoid redundant data in the response