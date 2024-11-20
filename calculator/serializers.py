from rest_framework import serializers
from .models import *

# Serializer for UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

# Serializer for PregnancyCheckup


class PregnancyCheckupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PregnancyCheckup
        fields = '__all__'

# Serializer for CheckupVisit


class CheckupVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckupVisit
        fields = '__all__'
