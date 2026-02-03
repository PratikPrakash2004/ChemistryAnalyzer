"""
Serializers for the Chemical Equipment API.
Handles conversion between Django models and JSON for the REST API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Dataset, Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    """
    Serializer for individual Equipment records.
    Used when returning equipment lists within a dataset.
    """
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'equipment_type', 'flowrate', 'pressure', 'temperature']


class DatasetListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing datasets.
    Shows summary info without loading all equipment records.
    Used in the history/list endpoint.
    """
    # Parse the JSON summary and include it in the response
    summary = serializers.SerializerMethodField()
    equipment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'uploaded_at', 'summary', 'equipment_count']
    
    def get_summary(self, obj):
        """Return the parsed summary dictionary."""
        return obj.summary
    
    def get_equipment_count(self, obj):
        """Return total number of equipment records in this dataset."""
        return obj.equipment.count()


class DatasetDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for a single dataset.
    Includes all equipment records for detailed view.
    Used when viewing a specific dataset.
    """
    summary = serializers.SerializerMethodField()
    equipment = EquipmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'uploaded_at', 'summary', 'equipment']
    
    def get_summary(self, obj):
        """Return the parsed summary dictionary."""
        return obj.summary


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model - used in authentication responses.
    Only exposes safe fields, never the password.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles password hashing and validation.
    """
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def create(self, validated_data):
        """Create a new user with properly hashed password."""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for login requests.
    Validates username and password fields.
    """
    username = serializers.CharField()
    password = serializers.CharField()
