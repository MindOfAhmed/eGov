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
    previous_owner_id = serializers.CharField(max_length=30)
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
    proof_document = serializers.FileField()