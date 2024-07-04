from rest_framework import serializers
from .models import *

# serialize the citizens model then inlcude it in the serialization of the user model
class CitizensSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizens
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    citizens = CitizensSerializer()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'citizens']